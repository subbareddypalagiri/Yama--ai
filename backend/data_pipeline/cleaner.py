"""
YAMA AI — Legal Data Cleaner
=============================================================================
Production-grade data cleaning module that takes raw or crawled legal records
and produces normalized, deduplicated, amendment-aware, keyword-enriched
entries ready for direct database storage.

Pipeline stages (run in order):
    1. TEXT NORMALIZATION   — Unicode, HTML, whitespace, legal-specific fixes
    2. FIELD NORMALIZATION  — Act names, section numbers, jurisdiction, law_type
    3. AMENDMENT DETECTION  — Identify amended/substituted/repealed provisions
    4. DUPLICATE REMOVAL    — Content-hash exact dedup + fuzzy near-dedup
    5. KEYWORD GENERATION   — TF-based extraction + legal domain boosting
    6. CATEGORY TAGGING     — Auto-classify into 12 legal categories
    7. CROSS-REFERENCE      — Old law ↔ new law mapping (IPC↔BNS, CrPC↔BNSS)
    8. VALIDATION           — Reject incomplete/corrupt records

Output: list of LegalRecord objects (from data_pipeline.crawler) or dicts
        matching the LawSection DB schema, ready for insert/upsert.

Usage:
    from data_pipeline.cleaner import LegalDataCleaner

    cleaner = LegalDataCleaner()

    # Clean a batch of raw dicts
    cleaned = cleaner.clean_batch(raw_records)

    # Clean a single record
    record = cleaner.clean_record(raw)

    # Full pipeline: clean → dedup → enrich → validate
    ready = cleaner.process(raw_records)

    # Get cleaning report
    print(cleaner.report())

CLI:
    cd backend
    python -m data_pipeline.cleaner --input raw_data.json --output cleaned.json
    python -m data_pipeline.cleaner --input raw.csv --output cleaned.json --stats
=============================================================================
"""

import csv
import hashlib
import json
import logging
import math
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Set, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("yama_ai.cleaner")

# Backend root for app.* imports
_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)


# ═══════════════════════════════════════════════════════════════════════════
#  CONSTANTS & REFERENCE DATA
# ═══════════════════════════════════════════════════════════════════════════

# ── Canonical act name aliases ──
ACT_NAME_ALIASES: Dict[str, str] = {
    # New criminal laws (2023)
    "bharatiya nyaya sanhita":            "Bharatiya Nyaya Sanhita, 2023",
    "bns":                                "Bharatiya Nyaya Sanhita, 2023",
    "bns 2023":                           "Bharatiya Nyaya Sanhita, 2023",
    "bharatiya nagarik suraksha sanhita": "Bharatiya Nagarik Suraksha Sanhita, 2023",
    "bnss":                               "Bharatiya Nagarik Suraksha Sanhita, 2023",
    "bnss 2023":                          "Bharatiya Nagarik Suraksha Sanhita, 2023",
    "bharatiya sakshya adhiniyam":        "Bharatiya Sakshya Adhiniyam, 2023",
    "bsa":                                "Bharatiya Sakshya Adhiniyam, 2023",
    "bsa 2023":                           "Bharatiya Sakshya Adhiniyam, 2023",
    # Old criminal laws
    "indian penal code":                  "Indian Penal Code, 1860",
    "ipc":                                "Indian Penal Code, 1860",
    "ipc 1860":                           "Indian Penal Code, 1860",
    "code of criminal procedure":         "Code of Criminal Procedure, 1973",
    "crpc":                               "Code of Criminal Procedure, 1973",
    "criminal procedure code":            "Code of Criminal Procedure, 1973",
    "indian evidence act":                "Indian Evidence Act, 1872",
    "evidence act":                       "Indian Evidence Act, 1872",
    # Other major acts
    "information technology act":         "Information Technology Act, 2000",
    "it act":                             "Information Technology Act, 2000",
    "it act 2000":                        "Information Technology Act, 2000",
    "consumer protection act":            "Consumer Protection Act, 2019",
    "motor vehicles act":                 "Motor Vehicles Act, 1988",
    "mv act":                             "Motor Vehicles Act, 1988",
    "constitution of india":              "Constitution of India",
    "constitution":                       "Constitution of India",
    "indian constitution":                "Constitution of India",
    "right to information act":           "Right to Information Act, 2005",
    "rti act":                            "Right to Information Act, 2005",
    "protection of women from domestic violence act":
        "Protection of Women from Domestic Violence Act, 2005",
    "domestic violence act":              "Protection of Women from Domestic Violence Act, 2005",
    "dv act":                             "Protection of Women from Domestic Violence Act, 2005",
    "hindu marriage act":                 "Hindu Marriage Act, 1955",
    "transfer of property act":           "Transfer of Property Act, 1882",
    "indian contract act":                "Indian Contract Act, 1872",
    "contract act":                       "Indian Contract Act, 1872",
    "negotiable instruments act":         "Negotiable Instruments Act, 1881",
    "ni act":                             "Negotiable Instruments Act, 1881",
    "companies act":                      "Companies Act, 2013",
    "insolvency and bankruptcy code":     "Insolvency and Bankruptcy Code, 2016",
    "ibc":                                "Insolvency and Bankruptcy Code, 2016",
    "arbitration and conciliation act":   "Arbitration and Conciliation Act, 1996",
    "specific relief act":                "Specific Relief Act, 1963",
    "limitation act":                     "Limitation Act, 1963",
    "prevention of corruption act":       "Prevention of Corruption Act, 1988",
    "narcotics act":                      "Narcotic Drugs and Psychotropic Substances Act, 1985",
    "ndps act":                           "Narcotic Drugs and Psychotropic Substances Act, 1985",
    "pocso act":                          "Protection of Children from Sexual Offences Act, 2012",
    "pocso":                              "Protection of Children from Sexual Offences Act, 2012",
    "sc st atrocities act":               "Scheduled Castes and Scheduled Tribes (Prevention of Atrocities) Act, 1989",
}

# ── Old law ↔ New law section mapping (IPC→BNS, CrPC→BNSS, Evidence→BSA) ──
OLD_NEW_SECTION_MAP: Dict[Tuple[str, str], Tuple[str, str]] = {
    # IPC → BNS
    ("Indian Penal Code, 1860", "302"):  ("Bharatiya Nyaya Sanhita, 2023", "100"),
    ("Indian Penal Code, 1860", "304"):  ("Bharatiya Nyaya Sanhita, 2023", "101"),
    ("Indian Penal Code, 1860", "304A"): ("Bharatiya Nyaya Sanhita, 2023", "285"),
    ("Indian Penal Code, 1860", "304B"): ("Bharatiya Nyaya Sanhita, 2023", "105"),
    ("Indian Penal Code, 1860", "307"):  ("Bharatiya Nyaya Sanhita, 2023", "109"),
    ("Indian Penal Code, 1860", "323"):  ("Bharatiya Nyaya Sanhita, 2023", "115"),
    ("Indian Penal Code, 1860", "325"):  ("Bharatiya Nyaya Sanhita, 2023", "117"),
    ("Indian Penal Code, 1860", "354"):  ("Bharatiya Nyaya Sanhita, 2023", "74"),
    ("Indian Penal Code, 1860", "376"):  ("Bharatiya Nyaya Sanhita, 2023", "63"),
    ("Indian Penal Code, 1860", "378"):  ("Bharatiya Nyaya Sanhita, 2023", "303"),
    ("Indian Penal Code, 1860", "379"):  ("Bharatiya Nyaya Sanhita, 2023", "303"),
    ("Indian Penal Code, 1860", "384"):  ("Bharatiya Nyaya Sanhita, 2023", "308"),
    ("Indian Penal Code, 1860", "392"):  ("Bharatiya Nyaya Sanhita, 2023", "305"),
    ("Indian Penal Code, 1860", "395"):  ("Bharatiya Nyaya Sanhita, 2023", "306"),
    ("Indian Penal Code, 1860", "405"):  ("Bharatiya Nyaya Sanhita, 2023", "329"),
    ("Indian Penal Code, 1860", "406"):  ("Bharatiya Nyaya Sanhita, 2023", "330"),
    ("Indian Penal Code, 1860", "415"):  ("Bharatiya Nyaya Sanhita, 2023", "316"),
    ("Indian Penal Code, 1860", "420"):  ("Bharatiya Nyaya Sanhita, 2023", "318"),
    ("Indian Penal Code, 1860", "463"):  ("Bharatiya Nyaya Sanhita, 2023", "336"),
    ("Indian Penal Code, 1860", "498A"): ("Bharatiya Nyaya Sanhita, 2023", "85"),
    ("Indian Penal Code, 1860", "499"):  ("Bharatiya Nyaya Sanhita, 2023", "356"),
    ("Indian Penal Code, 1860", "503"):  ("Bharatiya Nyaya Sanhita, 2023", "351"),
    ("Indian Penal Code, 1860", "506"):  ("Bharatiya Nyaya Sanhita, 2023", "351"),
    ("Indian Penal Code, 1860", "509"):  ("Bharatiya Nyaya Sanhita, 2023", "79"),
    # CrPC → BNSS
    ("Code of Criminal Procedure, 1973", "125"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "144"),
    ("Code of Criminal Procedure, 1973", "154"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "173"),
    ("Code of Criminal Procedure, 1973", "155"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "174"),
    ("Code of Criminal Procedure, 1973", "156"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "175"),
    ("Code of Criminal Procedure, 1973", "161"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "180"),
    ("Code of Criminal Procedure, 1973", "164"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "183"),
    ("Code of Criminal Procedure, 1973", "167"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "187"),
    ("Code of Criminal Procedure, 1973", "173"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "193"),
    ("Code of Criminal Procedure, 1973", "200"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "223"),
    ("Code of Criminal Procedure, 1973", "302"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "339"),
    ("Code of Criminal Procedure, 1973", "313"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "351"),
    ("Code of Criminal Procedure, 1973", "354"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "392"),
    ("Code of Criminal Procedure, 1973", "436"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "480"),
    ("Code of Criminal Procedure, 1973", "437"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "482"),
    ("Code of Criminal Procedure, 1973", "438"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "483"),
    ("Code of Criminal Procedure, 1973", "439"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "484"),
    ("Code of Criminal Procedure, 1973", "482"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "528"),
    # Evidence Act → BSA
    ("Indian Evidence Act, 1872", "3"):   ("Bharatiya Sakshya Adhiniyam, 2023", "2"),
    ("Indian Evidence Act, 1872", "25"):  ("Bharatiya Sakshya Adhiniyam, 2023", "23"),
    ("Indian Evidence Act, 1872", "27"):  ("Bharatiya Sakshya Adhiniyam, 2023", "25"),
    ("Indian Evidence Act, 1872", "32"):  ("Bharatiya Sakshya Adhiniyam, 2023", "26"),
    ("Indian Evidence Act, 1872", "45"):  ("Bharatiya Sakshya Adhiniyam, 2023", "39"),
    ("Indian Evidence Act, 1872", "65B"): ("Bharatiya Sakshya Adhiniyam, 2023", "63"),
    ("Indian Evidence Act, 1872", "101"): ("Bharatiya Sakshya Adhiniyam, 2023", "104"),
    ("Indian Evidence Act, 1872", "114"): ("Bharatiya Sakshya Adhiniyam, 2023", "117"),
}

# ── Category keyword bank (12 legal domains) ──
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "criminal": [
        "penal", "offence", "offense", "punishment", "murder", "theft", "assault",
        "robbery", "criminal", "bail", "fir", "arrest", "kidnapping", "rape",
        "fraud", "nyaya sanhita", "bns", "ipc", "extortion", "cheating",
        "forgery", "dacoity", "hurt", "grievous", "intimidation", "defamation",
        "abetment", "conspiracy", "culpable homicide", "mischief", "trespass",
        "rioting", "unlawful assembly", "sedition", "waging war",
    ],
    "civil": [
        "contract", "tort", "damages", "civil", "suit", "decree",
        "specific relief", "limitation", "agreement", "breach", "injunction",
        "restitution", "mesne profits", "plaint", "written statement",
    ],
    "constitutional": [
        "constitution", "fundamental", "article", "amendment", "directive",
        "writ", "habeas corpus", "mandamus", "certiorari", "quo warranto",
        "prohibition", "preamble", "schedule", "fundamental right",
        "fundamental duty", "state policy", "emergency", "citizenship",
    ],
    "consumer": [
        "consumer", "deficiency", "goods", "services", "complaint",
        "redressal", "product liability", "misleading advertisement",
        "unfair trade", "consumer forum", "district commission",
    ],
    "cyber": [
        "information technology", "cyber", "computer", "electronic", "data",
        "hacking", "it act", "identity theft", "phishing", "digital",
        "electronic record", "electronic signature", "intermediary",
    ],
    "family": [
        "marriage", "divorce", "maintenance", "custody", "adoption", "dowry",
        "domestic violence", "hindu", "muslim", "christian", "restitution of conjugal",
        "judicial separation", "alimony", "guardianship", "matrimonial",
    ],
    "motor_vehicle": [
        "motor", "vehicle", "driving", "accident", "licence", "license",
        "traffic", "road", "insurance", "drunk driving", "speed",
        "hit and run", "third party", "fitness certificate",
    ],
    "labour": [
        "labour", "labor", "worker", "employment", "wage", "industrial",
        "factory", "trade union", "provident fund", "gratuity", "bonus",
        "workmen", "compensation", "retrenchment", "strike", "lockout",
    ],
    "property": [
        "property", "land", "registration", "transfer", "tenancy", "rent",
        "succession", "inheritance", "easement", "mortgage", "lease",
        "conveyance", "partition", "encumbrance", "title deed",
    ],
    "tax": [
        "tax", "income", "gst", "customs", "excise", "revenue",
        "assessment", "return", "deduction", "exemption", "penalty",
    ],
    "environmental": [
        "environment", "pollution", "forest", "wildlife", "water", "air",
        "biodiversity", "hazardous waste", "eia", "green tribunal",
    ],
    "corporate": [
        "company", "corporate", "director", "shareholder", "insolvency",
        "bankruptcy", "sebi", "securities", "merger", "winding up",
        "annual return", "board meeting", "resolution",
    ],
}

# ── Stopwords for keyword extraction ──
STOPWORDS: Set[str] = {
    "the", "of", "and", "in", "to", "a", "is", "or", "for", "be", "an",
    "as", "by", "on", "at", "it", "that", "this", "with", "any", "shall",
    "may", "such", "which", "who", "not", "from", "under", "been", "has",
    "have", "his", "her", "its", "was", "were", "are", "being", "into",
    "than", "them", "then", "there", "these", "they", "upon", "where",
    "whether", "whom", "will", "would", "every", "person", "section",
    "act", "sub", "clause", "provided", "notwithstanding", "aforesaid",
    "hereinafter", "hereinbefore", "thereof", "therein", "thereto",
    "whereas", "hereby", "hereunder", "abovementioned", "said",
    "whatsoever", "whosoever", "can", "could", "should", "must",
    "also", "other", "each", "all", "both", "more", "most", "own",
    "same", "just", "only", "very", "about", "after", "before", "between",
    "but", "during", "through", "above", "below", "further", "once",
}

# ── Legal domain boosting terms (worth double weight in keyword scoring) ──
LEGAL_BOOST_TERMS: Set[str] = {
    "offence", "punishment", "imprisonment", "fine", "bail", "cognizable",
    "non-cognizable", "bailable", "non-bailable", "compoundable", "summons",
    "warrant", "complaint", "investigation", "prosecution", "conviction",
    "acquittal", "sentence", "appeal", "revision", "review", "writ",
    "petition", "jurisdiction", "limitation", "evidence", "witness",
    "examination", "cross-examination", "affidavit", "decree", "order",
    "injunction", "damages", "compensation", "restitution", "penalty",
    "abetment", "conspiracy", "attempt", "negligence", "defamation",
    "fraud", "forgery", "theft", "robbery", "extortion", "cheating",
    "trespass", "mischief", "grievous", "culpable", "homicide", "murder",
    "kidnapping", "trafficking", "assault", "battery", "intimidation",
    "maintenance", "divorce", "custody", "adoption", "dowry", "cruelty",
}

# ── Indian states for jurisdiction detection ──
INDIAN_STATES: Dict[str, str] = {
    "andhra pradesh": "Andhra Pradesh", "arunachal pradesh": "Arunachal Pradesh",
    "assam": "Assam", "bihar": "Bihar", "chhattisgarh": "Chhattisgarh",
    "goa": "Goa", "gujarat": "Gujarat", "haryana": "Haryana",
    "himachal pradesh": "Himachal Pradesh", "jharkhand": "Jharkhand",
    "karnataka": "Karnataka", "kerala": "Kerala",
    "madhya pradesh": "Madhya Pradesh", "maharashtra": "Maharashtra",
    "manipur": "Manipur", "meghalaya": "Meghalaya", "mizoram": "Mizoram",
    "nagaland": "Nagaland", "odisha": "Odisha", "punjab": "Punjab",
    "rajasthan": "Rajasthan", "sikkim": "Sikkim", "tamil nadu": "Tamil Nadu",
    "telangana": "Telangana", "tripura": "Tripura",
    "uttar pradesh": "Uttar Pradesh", "uttarakhand": "Uttarakhand",
    "west bengal": "West Bengal", "delhi": "Delhi",
    "jammu and kashmir": "Jammu and Kashmir", "ladakh": "Ladakh",
    "chandigarh": "Chandigarh", "puducherry": "Puducherry",
}

# ── Amendment detection patterns ──
AMENDMENT_PATTERNS = [
    re.compile(r"\[(?:Ins(?:erted)?\.?\s+by|Added\s+by)\s+(?:Act|Ordinance)\s+(?:No\.?\s*)?\d+\s+of\s+\d{4}[^\]]*\]", re.I),
    re.compile(r"\[(?:Subs(?:tituted)?\.?\s+by)\s+(?:Act|Ordinance)\s+(?:No\.?\s*)?\d+\s+of\s+\d{4}[^\]]*\]", re.I),
    re.compile(r"\[(?:Omitted|Repealed|Deleted)\s+by\s+(?:Act|Ordinance)\s+(?:No\.?\s*)?\d+\s+of\s+\d{4}[^\]]*\]", re.I),
    re.compile(r"\[(?:Amended|Modified)\s+by\s+(?:Act|Ordinance)\s+(?:No\.?\s*)?\d+\s+of\s+\d{4}[^\]]*\]", re.I),
    re.compile(r"\[(?:Renumbered|Relettered)\s+by\s+(?:Act|Ordinance)[^\]]*\]", re.I),
    re.compile(r"\[Vide\s+(?:Notification|Order)[^\]]*\]", re.I),
    re.compile(r"\[(?:w\.?e\.?f\.?|with effect from)\s+\d{1,2}[.\-/]\d{1,2}[.\-/]\d{4}[^\]]*\]", re.I),
    re.compile(r"\[As amended up to\s+(?:Act|date)[^\]]*\]", re.I),
]

# ── Amendment year extractor ──
AMENDMENT_YEAR_RE = re.compile(r"(?:Act|Ordinance)\s+(?:No\.?\s*)?\d+\s+of\s+(\d{4})", re.I)
AMENDMENT_TYPE_RE = re.compile(
    r"\[(Ins(?:erted)?|Subs(?:tituted)?|Omitted|Repealed|Deleted|Amended|Added|Modified|Renumbered)",
    re.I,
)


# ═══════════════════════════════════════════════════════════════════════════
#  CLEANING REPORT
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class CleaningReport:
    """Statistics from a cleaning run."""
    input_count: int = 0
    output_count: int = 0
    exact_duplicates_removed: int = 0
    fuzzy_duplicates_removed: int = 0
    invalid_rejected: int = 0
    text_normalized: int = 0
    act_names_standardized: int = 0
    amendments_detected: int = 0
    keywords_generated: int = 0
    categories_assigned: int = 0
    cross_references_added: int = 0
    errors: int = 0
    error_details: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            "═" * 60,
            "  YAMA AI — Data Cleaning Report",
            "═" * 60,
            f"  Input records:        {self.input_count}",
            f"  Output records:       {self.output_count}",
            f"  Exact duplicates:     {self.exact_duplicates_removed}",
            f"  Fuzzy duplicates:     {self.fuzzy_duplicates_removed}",
            f"  Invalid rejected:     {self.invalid_rejected}",
            f"  Text normalized:      {self.text_normalized}",
            f"  Act names fixed:      {self.act_names_standardized}",
            f"  Amendments found:     {self.amendments_detected}",
            f"  Keywords generated:   {self.keywords_generated}",
            f"  Categories assigned:  {self.categories_assigned}",
            f"  Cross-refs added:     {self.cross_references_added}",
            f"  Errors:               {self.errors}",
            "═" * 60,
        ]
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════
#  CORE CLEANER
# ═══════════════════════════════════════════════════════════════════════════

class LegalDataCleaner:
    """
    Complete legal data cleaning pipeline.

    Processes raw records (dicts or LegalRecords) through normalization,
    deduplication, amendment detection, keyword generation, and validation.

    All methods are stateless except for the accumulated CleaningReport.
    """

    def __init__(
        self,
        min_description_length: int = 20,
        fuzzy_threshold: float = 0.92,
        max_keywords: int = 20,
    ):
        """
        Args:
            min_description_length: Minimum characters for description to pass validation.
            fuzzy_threshold: SequenceMatcher ratio above which two records are considered duplicates.
            max_keywords: Maximum keywords to generate per record.
        """
        self.min_description_length = min_description_length
        self.fuzzy_threshold = fuzzy_threshold
        self.max_keywords = max_keywords
        self.report = CleaningReport()

    # ══════════════════════════════════════════════════════════════════════
    #  MAIN ENTRY POINT
    # ══════════════════════════════════════════════════════════════════════

    def process(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Full cleaning pipeline: normalize → validate → dedup → enrich.

        Args:
            records: Raw record dicts. Must have at least:
                     act_name, section_number, title, description (or section_text)

        Returns:
            Cleaned, deduplicated, enriched records ready for DB insert.
        """
        self.report = CleaningReport(input_count=len(records))
        logger.info("Processing %d records...", len(records))

        # Stage 1: Normalize each record
        normalized = []
        for raw in records:
            try:
                cleaned = self.clean_record(raw)
                if cleaned:
                    normalized.append(cleaned)
            except Exception as exc:
                self.report.errors += 1
                self.report.error_details.append(
                    f"Clean error on '{raw.get('act_name', '?')}' S.{raw.get('section_number', '?')}: {exc}"
                )

        # Stage 2: Validate
        valid = [r for r in normalized if self._validate(r)]
        self.report.invalid_rejected = len(normalized) - len(valid)
        logger.info("Validation: %d valid / %d rejected", len(valid), self.report.invalid_rejected)

        # Stage 3: Exact deduplication (content hash)
        deduped = self._deduplicate_exact(valid)
        self.report.exact_duplicates_removed = len(valid) - len(deduped)

        # Stage 4: Fuzzy deduplication
        final = self._deduplicate_fuzzy(deduped)
        self.report.fuzzy_duplicates_removed = len(deduped) - len(final)

        logger.info(
            "Dedup: %d exact + %d fuzzy removed → %d remaining",
            self.report.exact_duplicates_removed,
            self.report.fuzzy_duplicates_removed,
            len(final),
        )

        # Stage 5: Enrich (keywords, category, cross-ref)
        enriched = [self._enrich(r) for r in final]

        self.report.output_count = len(enriched)
        logger.info("Cleaning complete: %d → %d records", self.report.input_count, self.report.output_count)
        return enriched

    # ══════════════════════════════════════════════════════════════════════
    #  STAGE 1: RECORD-LEVEL CLEANING
    # ══════════════════════════════════════════════════════════════════════

    def clean_record(self, raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Clean a single raw record dict.

        Normalizes text, standardizes act name & section number,
        detects amendments, and computes content hash.

        Returns:
            Cleaned dict, or None if critically malformed.
        """
        # Accept both 'description' and 'section_text' keys
        description = raw.get("description") or raw.get("section_text") or ""
        act_name = raw.get("act_name", "")
        section_number = raw.get("section_number", "")
        title = raw.get("title", "")

        if not act_name or not description:
            return None

        # ── Text normalization ──
        act_name = self._normalize_act_name(act_name)
        section_number = self._normalize_section_number(section_number)
        title = self._normalize_text(title)
        description = self._normalize_text(description)
        self.report.text_normalized += 1

        # ── Amendment detection ──
        amendments = self._detect_amendments(description)
        amendment_info = {}
        if amendments:
            self.report.amendments_detected += 1
            amendment_info = {
                "amendment_notes": [a["raw"] for a in amendments],
                "amendment_types": list({a["type"] for a in amendments}),
                "amendment_years": sorted({a["year"] for a in amendments if a["year"]}),
                "is_amended": True,
            }

        # ── Content hash ──
        content_hash = hashlib.sha256(
            f"{act_name}|{section_number}|{title}|{description}".encode("utf-8")
        ).hexdigest()

        cleaned: Dict[str, Any] = {
            "act_name": act_name,
            "section_number": section_number,
            "title": title,
            "description": description,
            "keywords": raw.get("keywords", ""),
            "category": raw.get("category", ""),
            "punishment": self._normalize_text(raw.get("punishment") or ""),
            "old_law_reference": raw.get("old_law_reference"),
            "jurisdiction": self._normalize_jurisdiction(raw.get("jurisdiction", "central")),
            "state_name": self._normalize_state_name(raw.get("state_name")),
            "law_type": self._normalize_law_type(raw.get("law_type", "act")),
            "source_url": (raw.get("source_url") or "").strip(),
            "content_hash": content_hash,
            "is_active": raw.get("is_active", True),
        }
        cleaned.update(amendment_info)
        return cleaned

    # ══════════════════════════════════════════════════════════════════════
    #  STAGE 2: VALIDATION
    # ══════════════════════════════════════════════════════════════════════

    def _validate(self, record: Dict[str, Any]) -> bool:
        """
        Validate a cleaned record meets quality thresholds.

        Rejects:
            - Missing act_name / section_number / title
            - Description shorter than min_description_length
            - Garbage / non-text content
        """
        if not record.get("act_name"):
            return False
        if not record.get("section_number"):
            return False
        if not record.get("title"):
            return False

        desc = record.get("description", "")
        if len(desc) < self.min_description_length:
            return False

        # Reject if description is >80% non-alphabetic (likely garbage)
        alpha_ratio = sum(1 for c in desc if c.isalpha()) / max(len(desc), 1)
        if alpha_ratio < 0.3:
            return False

        return True

    # ══════════════════════════════════════════════════════════════════════
    #  STAGE 3: EXACT DEDUPLICATION
    # ══════════════════════════════════════════════════════════════════════

    def _deduplicate_exact(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove exact duplicates by content_hash.
        Keeps the first occurrence.
        """
        seen: Set[str] = set()
        unique: List[Dict[str, Any]] = []
        for r in records:
            h = r.get("content_hash", "")
            if h and h in seen:
                continue
            seen.add(h)
            unique.append(r)
        return unique

    # ══════════════════════════════════════════════════════════════════════
    #  STAGE 4: FUZZY DEDUPLICATION
    # ══════════════════════════════════════════════════════════════════════

    def _deduplicate_fuzzy(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove near-duplicate records using fuzzy text comparison.

        Compares records sharing the same act_name. If two descriptions
        have a SequenceMatcher ratio >= fuzzy_threshold, the shorter one
        is dropped (the longer one is assumed more complete).
        """
        if len(records) < 2:
            return records

        # Group by act_name for O(n*k) instead of O(n²)
        groups: Dict[str, List[int]] = {}
        for i, r in enumerate(records):
            key = r.get("act_name", "").lower()
            groups.setdefault(key, []).append(i)

        drop_indices: Set[int] = set()

        for act_key, indices in groups.items():
            if len(indices) < 2:
                continue
            for i in range(len(indices)):
                if indices[i] in drop_indices:
                    continue
                for j in range(i + 1, len(indices)):
                    if indices[j] in drop_indices:
                        continue
                    ri = records[indices[i]]
                    rj = records[indices[j]]
                    # Only compare if section numbers differ (same section → already deduped by hash)
                    if ri.get("section_number") == rj.get("section_number"):
                        continue
                    # Compare titles first (cheap)
                    title_ratio = SequenceMatcher(
                        None, ri.get("title", "").lower(), rj.get("title", "").lower()
                    ).ratio()
                    if title_ratio < 0.8:
                        continue
                    # Compare descriptions
                    desc_ratio = SequenceMatcher(
                        None,
                        ri.get("description", "")[:500].lower(),
                        rj.get("description", "")[:500].lower(),
                    ).ratio()
                    if desc_ratio >= self.fuzzy_threshold:
                        # Drop the shorter record
                        shorter = indices[i] if len(ri.get("description", "")) < len(rj.get("description", "")) else indices[j]
                        drop_indices.add(shorter)

        return [r for i, r in enumerate(records) if i not in drop_indices]

    # ══════════════════════════════════════════════════════════════════════
    #  STAGE 5: ENRICHMENT
    # ══════════════════════════════════════════════════════════════════════

    def _enrich(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a cleaned record with:
            - Auto-generated keywords
            - Category classification
            - Old↔new law cross-reference
        """
        act = record.get("act_name", "")
        title = record.get("title", "")
        desc = record.get("description", "")
        sec = record.get("section_number", "")

        # Keywords
        if not record.get("keywords"):
            record["keywords"] = self._generate_keywords(title, desc)
            self.report.keywords_generated += 1

        # Category
        if not record.get("category") or record["category"] == "general":
            record["category"] = self._classify_category(act, title, desc)
            self.report.categories_assigned += 1

        # Cross-reference
        if not record.get("old_law_reference"):
            ref = self._find_cross_reference(act, sec)
            if ref:
                record["old_law_reference"] = ref
                self.report.cross_references_added += 1

        # Detect jurisdiction from act name / state_name
        if not record.get("state_name"):
            state = self._detect_state(act, desc)
            if state:
                record["state_name"] = state
                record["jurisdiction"] = "state"

        return record

    # ══════════════════════════════════════════════════════════════════════
    #  TEXT NORMALIZATION HELPERS
    # ══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _normalize_text(text: str) -> str:
        """
        Clean arbitrary text:
        - Strip HTML tags
        - Fix Unicode characters
        - Collapse whitespace
        - Normalize quotes and dashes
        """
        if not text:
            return ""
        # HTML tags
        text = re.sub(r"<[^>]+>", " ", text)
        # Unicode fixes
        replacements = {
            "\u00a0": " ", "\u2018": "'", "\u2019": "'",
            "\u201c": '"', "\u201d": '"', "\u2014": " — ",
            "\u2013": " – ", "\u2026": "...", "\u200b": "",
            "\u200c": "", "\u200d": "", "\ufeff": "",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        # Control chars
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
        # Whitespace
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @staticmethod
    def _normalize_act_name(name: str) -> str:
        """Standardize act name to canonical form."""
        if not name:
            return ""
        # Strip HTML and excess whitespace
        name = re.sub(r"<[^>]+>", "", name)
        name = re.sub(r"\s+", " ", name).strip()
        # Remove leading "The"
        name = re.sub(r"^The\s+", "", name, flags=re.I).rstrip(" .,;:")

        # Lookup in alias table
        key = name.lower().strip()
        if key in ACT_NAME_ALIASES:
            return ACT_NAME_ALIASES[key]
        # Partial match
        for alias, canonical in ACT_NAME_ALIASES.items():
            if alias in key:
                return canonical

        # Title-case if not matched
        if name == name.lower() or name == name.upper():
            name = name.title()
        return name

    @staticmethod
    def _normalize_section_number(raw: str) -> str:
        """Normalize section number: 'Section 302A' → '302A'."""
        if not raw:
            return ""
        raw = raw.strip()
        raw = re.sub(r"^(?:Section|Sec\.?|Article|Art\.?|Rule)\s*", "", raw, flags=re.I)
        raw = raw.strip("()[]., ")
        return raw

    @staticmethod
    def _normalize_jurisdiction(val: str) -> str:
        """Normalize jurisdiction to 'central' or 'state'."""
        if not val:
            return "central"
        val = val.strip().lower()
        if val in ("state", "state-level"):
            return "state"
        return "central"

    @staticmethod
    def _normalize_state_name(val: Optional[str]) -> Optional[str]:
        """Normalize state name to proper casing."""
        if not val:
            return None
        key = val.strip().lower()
        return INDIAN_STATES.get(key, val.strip().title())

    @staticmethod
    def _normalize_law_type(val: str) -> str:
        """Normalize law_type field."""
        if not val:
            return "act"
        val = val.strip().lower()
        valid = {"act", "article", "rule", "amendment", "notification", "judgment", "ordinance", "regulation"}
        return val if val in valid else "act"

    # ══════════════════════════════════════════════════════════════════════
    #  AMENDMENT DETECTION
    # ══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _detect_amendments(text: str) -> List[Dict[str, Any]]:
        """
        Detect all amendment notes in the text.

        Returns:
            List of dicts with keys: raw, type, year
        """
        results: List[Dict[str, Any]] = []
        for pattern in AMENDMENT_PATTERNS:
            for match in pattern.finditer(text):
                raw = match.group(0)
                # Extract type
                type_match = AMENDMENT_TYPE_RE.search(raw)
                amend_type = type_match.group(1).lower() if type_match else "amended"
                # Normalize type
                type_map = {
                    "ins": "inserted", "inserted": "inserted",
                    "subs": "substituted", "substituted": "substituted",
                    "omitted": "omitted", "repealed": "repealed",
                    "deleted": "deleted", "amended": "amended",
                    "added": "inserted", "modified": "amended",
                    "renumbered": "renumbered",
                }
                amend_type = type_map.get(amend_type, amend_type)

                # Extract year
                year_match = AMENDMENT_YEAR_RE.search(raw)
                year = year_match.group(1) if year_match else ""

                results.append({
                    "raw": raw,
                    "type": amend_type,
                    "year": year,
                })
        return results

    # ══════════════════════════════════════════════════════════════════════
    #  KEYWORD GENERATION
    # ══════════════════════════════════════════════════════════════════════

    def _generate_keywords(self, title: str, description: str) -> str:
        """
        Generate keywords using TF-based scoring with legal domain boosting.

        Strategy:
            1. Tokenize title + description
            2. Remove stopwords
            3. Score by frequency, boost legal domain terms
            4. Return top N as comma-separated string
        """
        combined = f"{title} {description[:1500]}".lower()
        words = re.findall(r"[a-z]{3,}", combined)

        # Term frequency
        tf = Counter(w for w in words if w not in STOPWORDS)

        # Boost legal terms
        scored: List[Tuple[str, float]] = []
        for word, count in tf.items():
            score = count
            if word in LEGAL_BOOST_TERMS:
                score *= 2.0
            # Boost terms from title (more significant)
            if word in title.lower():
                score *= 1.5
            scored.append((word, score))

        # Sort by score descending, then alphabetical for ties
        scored.sort(key=lambda x: (-x[1], x[0]))

        keywords = [w for w, _ in scored[:self.max_keywords]]
        return ", ".join(keywords)

    # ══════════════════════════════════════════════════════════════════════
    #  CATEGORY CLASSIFICATION
    # ══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _classify_category(act_name: str, title: str, description: str) -> str:
        """
        Auto-classify into one of 12 legal categories.

        Uses weighted keyword scoring across act name, title, and description.
        """
        act_lower = act_name.lower()
        title_lower = title.lower()
        desc_lower = description[:800].lower()

        best_cat = "general"
        best_score = 0

        for category, kw_list in CATEGORY_KEYWORDS.items():
            score = 0.0
            for kw in kw_list:
                # Act name match (highest weight)
                if kw in act_lower:
                    score += 3.0
                # Title match
                if kw in title_lower:
                    score += 2.0
                # Description match
                if kw in desc_lower:
                    score += 1.0
            if score > best_score:
                best_score = score
                best_cat = category

        return best_cat

    # ══════════════════════════════════════════════════════════════════════
    #  CROSS-REFERENCE (OLD ↔ NEW LAW)
    # ══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _find_cross_reference(act_name: str, section_number: str) -> Optional[str]:
        """
        Look up old ↔ new law mapping.
        Works bidirectionally: IPC→BNS and BNS→IPC.
        """
        key = (act_name, section_number)
        if key in OLD_NEW_SECTION_MAP:
            ref_act, ref_sec = OLD_NEW_SECTION_MAP[key]
            return f"{ref_act}, Section {ref_sec}"
        # Reverse lookup
        for (old_act, old_sec), (new_act, new_sec) in OLD_NEW_SECTION_MAP.items():
            if act_name == new_act and section_number == new_sec:
                return f"{old_act}, Section {old_sec}"
        return None

    # ══════════════════════════════════════════════════════════════════════
    #  STATE DETECTION
    # ══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _detect_state(act_name: str, description: str) -> Optional[str]:
        """Detect state name from act name or description."""
        text = f"{act_name} {description[:300]}".lower()
        for key, canonical in INDIAN_STATES.items():
            # Only match as a distinct word/phrase in the act name
            if re.search(rf"\b{re.escape(key)}\b", act_name.lower()):
                return canonical
        return None

    # ══════════════════════════════════════════════════════════════════════
    #  CONVENIENCE: CLEAN BATCH → LegalRecord
    # ══════════════════════════════════════════════════════════════════════

    def process_to_records(self, raw_records: List[Dict[str, Any]]) -> list:
        """
        Full pipeline → output as LegalRecord objects (for crawler.store_records).
        """
        from data_pipeline.crawler import LegalRecord

        cleaned = self.process(raw_records)
        records = []
        for d in cleaned:
            rec = LegalRecord(
                act_name=d["act_name"],
                section_number=d["section_number"],
                title=d["title"],
                section_text=d["description"],
                source_url=d.get("source_url", ""),
                keywords=d.get("keywords", ""),
                category=d.get("category", "general"),
                jurisdiction=d.get("jurisdiction", "central"),
                state_name=d.get("state_name"),
                law_type=d.get("law_type", "act"),
                punishment=d.get("punishment"),
                old_law_reference=d.get("old_law_reference"),
                content_hash=d.get("content_hash", ""),
            )
            records.append(rec)
        return records


# ═══════════════════════════════════════════════════════════════════════════
#  FILE I/O HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def load_records_from_file(filepath: str) -> List[Dict[str, Any]]:
    """Load raw records from JSON or CSV file."""
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".json":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Support both {"laws": [...]} and bare [...]
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("laws") or data.get("records") or data.get("sections") or []
        return []

    if ext == ".csv":
        records = []
        with open(filepath, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(dict(row))
        return records

    raise ValueError(f"Unsupported file format: {ext}. Use .json or .csv")


def save_records_to_file(records: List[Dict[str, Any]], filepath: str):
    """Save cleaned records to JSON file."""
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    output = {
        "metadata": {
            "cleaned_at": datetime.utcnow().isoformat(),
            "total_records": len(records),
            "source": "YAMA AI Data Cleaner",
        },
        "laws": records,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    logger.info("Saved %d records → %s", len(records), filepath)


# ═══════════════════════════════════════════════════════════════════════════
#  CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

def main():
    import argparse

    ap = argparse.ArgumentParser(
        prog="python -m data_pipeline.cleaner",
        description="YAMA AI — Legal Data Cleaner: Normalize, dedup, detect amendments, generate keywords.",
    )
    ap.add_argument("--input", "-i", required=True, help="Input file (JSON or CSV)")
    ap.add_argument("--output", "-o", default=None, help="Output JSON file")
    ap.add_argument("--stats", action="store_true", help="Print cleaning report")
    ap.add_argument("--store", action="store_true", help="Store cleaned records into DB + ChromaDB")
    ap.add_argument("--min-length", type=int, default=20, help="Min description length (default: 20)")
    ap.add_argument("--fuzzy-threshold", type=float, default=0.92, help="Fuzzy dedup threshold (default: 0.92)")
    args = ap.parse_args()

    print()
    print("═" * 60)
    print("  YAMA AI — Legal Data Cleaner")
    print("═" * 60)
    print(f"  Input:           {args.input}")
    print(f"  Output:          {args.output or '(none)'}")
    print(f"  Min desc length: {args.min_length}")
    print(f"  Fuzzy threshold: {args.fuzzy_threshold}")
    print("═" * 60)
    print()

    # Load
    raw_records = load_records_from_file(args.input)
    print(f"📥 Loaded {len(raw_records)} raw records from {args.input}")

    # Clean
    cleaner = LegalDataCleaner(
        min_description_length=args.min_length,
        fuzzy_threshold=args.fuzzy_threshold,
    )
    cleaned = cleaner.process(raw_records)
    print(f"\n✅ Cleaned: {len(raw_records)} → {len(cleaned)} records")

    # Report
    if args.stats:
        print()
        print(cleaner.report.summary())

    # Save
    if args.output:
        save_records_to_file(cleaned, args.output)
        print(f"\n📄 Saved → {args.output}")

    # Store
    if args.store:
        print("\n💾 Storing into database + ChromaDB...")
        records = cleaner.process_to_records(raw_records)
        from data_pipeline.crawler import LegalCrawler
        with LegalCrawler() as crawler:
            stats = crawler.store_records(records, source_name="cleaner")
        print(f"   Inserted: {stats['inserted']}, Updated: {stats['updated']}, Skipped: {stats['skipped']}")

    print("\n✅ Done!")


if __name__ == "__main__":
    main()
