"""
YAMA AI — Metadata Tagger
Automatically tags legal records with:
    - Legal category (criminal, civil, constitutional, etc.)
    - Jurisdiction (central / state)
    - Law type (act, rule, article, amendment, judgment, notification)
    - Keywords (extracted from text)
    - Old/new law mapping (IPC ↔ BNS, CrPC ↔ BNSS, etc.)
"""

import re
import logging
from typing import Dict, List, Optional

from ingestion.config import CATEGORY_KEYWORDS

logger = logging.getLogger("yama_ai.ingestion.tagger")

# ── Old → New Law Mapping (2023 Criminal Law Reforms) ──
OLD_NEW_LAW_MAP = {
    "Indian Penal Code, 1860": "Bharatiya Nyaya Sanhita, 2023",
    "Code of Criminal Procedure, 1973": "Bharatiya Nagarik Suraksha Sanhita, 2023",
    "Indian Evidence Act, 1872": "Bharatiya Sakshya Adhiniyam, 2023",
}

# Known section mappings (IPC → BNS)
SECTION_MAPPING = {
    ("Indian Penal Code, 1860", "302"): ("Bharatiya Nyaya Sanhita, 2023", "100"),
    ("Indian Penal Code, 1860", "304"): ("Bharatiya Nyaya Sanhita, 2023", "101"),
    ("Indian Penal Code, 1860", "323"): ("Bharatiya Nyaya Sanhita, 2023", "115"),
    ("Indian Penal Code, 1860", "378"): ("Bharatiya Nyaya Sanhita, 2023", "303"),
    ("Indian Penal Code, 1860", "384"): ("Bharatiya Nyaya Sanhita, 2023", "308"),
    ("Indian Penal Code, 1860", "498A"): ("Bharatiya Nyaya Sanhita, 2023", "85"),
    ("Indian Penal Code, 1860", "503"): ("Bharatiya Nyaya Sanhita, 2023", "351"),
    ("Indian Penal Code, 1860", "506"): ("Bharatiya Nyaya Sanhita, 2023", "351"),
    ("Indian Penal Code, 1860", "420"): ("Bharatiya Nyaya Sanhita, 2023", "316"),
    ("Indian Penal Code, 1860", "354"): ("Bharatiya Nyaya Sanhita, 2023", "74"),
    ("Indian Penal Code, 1860", "376"): ("Bharatiya Nyaya Sanhita, 2023", "63"),
}

# Jurisdiction detection patterns
STATE_PATTERNS = {
    state: re.compile(rf"\b{re.escape(state)}\b", re.IGNORECASE)
    for state in [
        "Andhra Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat",
        "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
        "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
        "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
        "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
        "Delhi", "Jammu and Kashmir", "Puducherry",
    ]
}


class MetadataTagger:
    """
    Enriches legal records with auto-generated metadata.
    Call `tag_record()` on each record after cleaning.
    """

    def tag_record(self, record: Dict) -> Dict:
        """
        Add/refine metadata on a legal record.

        Auto-fills:
            - category (if missing or 'general')
            - jurisdiction
            - state_name (if state-level)
            - law_type (if missing)
            - keywords (appends auto-extracted)
            - old_law_reference (if known mapping exists)
        """
        # 1. Auto-classify category
        if not record.get("category") or record["category"] == "general":
            record["category"] = self._classify(record)

        # 2. Detect jurisdiction
        if not record.get("jurisdiction"):
            record["jurisdiction"], record["state_name"] = self._detect_jurisdiction(record)

        # 3. Infer law type
        if not record.get("law_type"):
            record["law_type"] = self._infer_law_type(record)

        # 4. Auto-generate keywords
        existing_kw = record.get("keywords", "")
        auto_kw = self._generate_keywords(record)
        if auto_kw:
            combined = f"{existing_kw}, {auto_kw}" if existing_kw else auto_kw
            # Deduplicate
            kw_list = list(dict.fromkeys(kw.strip() for kw in combined.split(",") if kw.strip()))
            record["keywords"] = ", ".join(kw_list[:20])

        # 5. Map old law reference
        if not record.get("old_law_reference"):
            record["old_law_reference"] = self._find_old_law_mapping(record)

        return record

    def tag_batch(self, records: List[Dict]) -> List[Dict]:
        """Tag all records in a batch."""
        return [self.tag_record(r) for r in records]

    # ── Classification ──

    @staticmethod
    def _classify(record: Dict) -> str:
        """Classify a record into a legal category."""
        combined = (
            f"{record.get('act_name', '')} "
            f"{record.get('title', '')} "
            f"{record.get('description', '')[:500]} "
            f"{record.get('keywords', '')}"
        ).lower()

        best = "general"
        best_score = 0
        for category, keywords in CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in combined)
            if score > best_score:
                best_score = score
                best = category

        return best

    @staticmethod
    def _detect_jurisdiction(record: Dict) -> tuple:
        """Detect if the record is central or state-level."""
        combined = f"{record.get('act_name', '')} {record.get('description', '')[:300]}"

        for state_name, pattern in STATE_PATTERNS.items():
            if pattern.search(combined):
                return "state", state_name

        # Explicit jurisdiction in act name
        if re.search(r"(central|union|india|parliament)", combined, re.IGNORECASE):
            return "central", None

        return "central", None

    @staticmethod
    def _infer_law_type(record: Dict) -> str:
        """Infer the type of legal document."""
        act_name = record.get("act_name", "").lower()
        sec_num = record.get("section_number", "").lower()

        if "judgment" in act_name or "judgment" in sec_num:
            return "judgment"
        if "constitution" in act_name:
            return "article" if "article" in sec_num.lower() else "constitutional"
        if "rule" in act_name:
            return "rule"
        if "amendment" in act_name:
            return "amendment"
        if "notification" in act_name or "gazette" in act_name:
            return "notification"
        if "ordinance" in act_name:
            return "ordinance"
        return "act"

    @staticmethod
    def _generate_keywords(record: Dict) -> str:
        """Auto-extract keywords from title and description."""
        text = f"{record.get('title', '')} {record.get('description', '')[:300]}".lower()
        stop = {"the", "of", "and", "in", "to", "a", "is", "or", "for", "be", "an",
                "as", "by", "on", "at", "it", "that", "this", "with", "any", "shall",
                "may", "such", "which", "who", "not", "from", "under", "been", "has",
                "have", "his", "her", "its"}
        words = re.findall(r"[a-z]{4,}", text)
        kw = [w for w in dict.fromkeys(words) if w not in stop]
        return ", ".join(kw[:8])

    @staticmethod
    def _find_old_law_mapping(record: Dict) -> Optional[str]:
        """Check if this section has a known old-law ↔ new-law mapping."""
        act = record.get("act_name", "")
        sec = record.get("section_number", "")

        # Check forward mapping (old → new)
        key = (act, sec)
        if key in SECTION_MAPPING:
            new_act, new_sec = SECTION_MAPPING[key]
            return f"{new_act}, Section {new_sec}"

        # Check reverse mapping (new → old)
        for (old_act, old_sec), (new_act, new_sec) in SECTION_MAPPING.items():
            if act == new_act and sec == new_sec:
                return f"{old_act}, Section {old_sec}"

        return None
