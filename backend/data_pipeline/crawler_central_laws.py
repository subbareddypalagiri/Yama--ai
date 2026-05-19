"""
YAMA AI — Central Laws Crawler
=============================================================================
Crawls central (Union) legislation from official Indian government portals.

Primary Source:
    India Code (https://www.indiacode.nic.in) — maintained by the Legislative
    Department, Ministry of Law and Justice. Contains all Central Acts from
    1836 to date.

Secondary Sources:
    • https://legislative.gov.in   — Bills, Ordinances, recent Acts
    • https://egazette.gov.in      — Notifications, Rules, Regulations

Extracts per section:
    {
        "act_name":        "Bharatiya Nyaya Sanhita, 2023",
        "section_number":  "303",
        "title":           "Theft",
        "description":     "Whoever commits theft...",
        "keywords":        "theft, dishonest, moveable, property",
        "jurisdiction":    "central",
        "state_name":      null,
        "source_url":      "https://www.indiacode.nic.in/...",
        "last_updated":    "2024-01-01T00:00:00+00:00"
    }

Priority Acts (crawled first — the core Indian legal framework):
    BNS 2023, BNSS 2023, BSA 2023, IPC 1860, CrPC 1973, IEA 1872,
    IT Act 2000, Consumer Protection 2019, Motor Vehicles 1988,
    RTI 2005, POCSO 2012, Domestic Violence 2005, NDPS 1985, etc.

Usage:
    python -m data_pipeline.crawler_central_laws
    python -m data_pipeline.crawler_central_laws --act BNS --export laws.json
    python -m data_pipeline.crawler_central_laws --offline --export laws.json
=============================================================================
"""

import argparse
import hashlib
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

# ── Path setup ──
_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("yama_ai.crawler.central_laws")


# ═══════════════════════════════════════════════════════════════════════════
#  DATA MODEL
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class CentralLawRecord:
    """One section/provision from a Central Act."""
    act_name: str = ""
    section_number: str = ""
    title: str = ""
    description: str = ""
    keywords: str = ""
    jurisdiction: str = "central"
    state_name: Optional[str] = None
    law_type: str = "act"
    category: str = "general"
    punishment: Optional[str] = None
    old_law_reference: Optional[str] = None
    source_url: str = ""
    content_hash: str = ""
    last_updated: str = ""

    def __post_init__(self):
        if not self.last_updated:
            self.last_updated = datetime.now(timezone.utc).isoformat()
        if not self.content_hash:
            raw = f"{self.act_name}|{self.section_number}|{self.description}"
            self.content_hash = hashlib.sha256(raw.encode()).hexdigest()

    def to_dict(self) -> Dict:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════════════════
#  CATEGORY CLASSIFIER
# ═══════════════════════════════════════════════════════════════════════════

_CATEGORY_MAP: Dict[str, List[str]] = {
    "criminal": [
        "penal", "offence", "punishment", "murder", "theft", "assault", "robbery",
        "criminal", "bail", "fir", "arrest", "kidnapping", "rape", "fraud",
        "nyaya sanhita", "bns", "ipc", "extortion", "cheating", "forgery",
        "dacoity", "hurt", "grievous", "intimidation", "defamation", "ndps",
        "narcotic", "drug", "abetment", "conspiracy", "culpable",
    ],
    "civil": [
        "contract", "property", "tort", "damages", "civil", "suit", "decree",
        "specific relief", "limitation", "agreement", "breach", "arbitration",
    ],
    "constitutional": [
        "constitution", "fundamental", "article", "amendment", "directive",
        "writ", "habeas corpus", "mandamus",
    ],
    "consumer": [
        "consumer", "deficiency", "goods", "services", "complaint", "redressal",
        "product liability", "misleading advertisement",
    ],
    "cyber": [
        "information technology", "cyber", "computer", "electronic", "data",
        "hacking", "it act", "identity theft", "phishing", "digital",
    ],
    "family": [
        "marriage", "divorce", "maintenance", "custody", "adoption", "dowry",
        "domestic violence", "hindu", "muslim", "christian", "succession",
    ],
    "motor_vehicle": [
        "motor", "vehicle", "driving", "accident", "licence", "traffic",
        "road", "insurance", "drunk driving",
    ],
    "labour": [
        "labour", "labor", "worker", "employment", "wage", "industrial",
        "factory", "trade union", "provident fund", "maternity",
    ],
    "property": [
        "property", "land", "registration", "transfer", "tenancy", "rent",
        "inheritance", "easement", "mortgage",
    ],
    "tax": ["tax", "income", "gst", "customs", "excise", "revenue", "goods and services"],
    "environmental": ["environment", "pollution", "forest", "wildlife", "water", "air"],
    "corporate": ["company", "corporate", "director", "shareholder", "insolvency", "sebi"],
    "rti": ["right to information", "public authority", "information officer", "rti"],
    "education": ["education", "school", "child", "right to education", "rte"],
}


def _classify(act_name: str, title: str, text: str) -> str:
    combined = f"{act_name} {title} {text[:500]}".lower()
    best, top = "general", 0
    for cat, kws in _CATEGORY_MAP.items():
        score = sum(1 for kw in kws if kw in combined)
        if score > top:
            best, top = cat, score
    return best


_STOP = frozenset({
    "the", "of", "and", "in", "to", "a", "is", "or", "for", "be", "an", "as",
    "by", "on", "at", "it", "that", "this", "with", "any", "shall", "may",
    "such", "which", "who", "not", "from", "under", "been", "has", "have",
    "his", "her", "its", "was", "were", "are", "being", "into", "than",
    "them", "then", "there", "these", "they", "upon", "where", "whether",
    "whom", "will", "would", "every", "person", "section", "act", "order",
    "provided", "notwithstanding",
})


def _extract_keywords(title: str, text: str, limit: int = 15) -> str:
    combined = f"{title} {text[:500]}".lower()
    words = re.findall(r"[a-z]{3,}", combined)
    freq: Dict[str, int] = {}
    for w in words:
        if w not in _STOP:
            freq[w] = freq.get(w, 0) + 1
    ranked = sorted(freq, key=lambda w: -freq[w])
    return ", ".join(ranked[:limit])


def _clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\u00a0", " ").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2014", "—")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ═══════════════════════════════════════════════════════════════════════════
#  OLD ↔ NEW LAW CROSS-REFERENCE (IPC→BNS, CrPC→BNSS, Evidence→BSA)
# ═══════════════════════════════════════════════════════════════════════════

_OLD_NEW: Dict[Tuple[str, str], Tuple[str, str]] = {
    ("Indian Penal Code, 1860", "302"):  ("Bharatiya Nyaya Sanhita, 2023", "100"),
    ("Indian Penal Code, 1860", "304"):  ("Bharatiya Nyaya Sanhita, 2023", "101"),
    ("Indian Penal Code, 1860", "304A"): ("Bharatiya Nyaya Sanhita, 2023", "285"),
    ("Indian Penal Code, 1860", "304B"): ("Bharatiya Nyaya Sanhita, 2023", "105"),
    ("Indian Penal Code, 1860", "307"):  ("Bharatiya Nyaya Sanhita, 2023", "109"),
    ("Indian Penal Code, 1860", "323"):  ("Bharatiya Nyaya Sanhita, 2023", "115"),
    ("Indian Penal Code, 1860", "354"):  ("Bharatiya Nyaya Sanhita, 2023", "74"),
    ("Indian Penal Code, 1860", "376"):  ("Bharatiya Nyaya Sanhita, 2023", "63"),
    ("Indian Penal Code, 1860", "378"):  ("Bharatiya Nyaya Sanhita, 2023", "303"),
    ("Indian Penal Code, 1860", "384"):  ("Bharatiya Nyaya Sanhita, 2023", "308"),
    ("Indian Penal Code, 1860", "392"):  ("Bharatiya Nyaya Sanhita, 2023", "305"),
    ("Indian Penal Code, 1860", "395"):  ("Bharatiya Nyaya Sanhita, 2023", "306"),
    ("Indian Penal Code, 1860", "405"):  ("Bharatiya Nyaya Sanhita, 2023", "329"),
    ("Indian Penal Code, 1860", "420"):  ("Bharatiya Nyaya Sanhita, 2023", "316"),
    ("Indian Penal Code, 1860", "498A"): ("Bharatiya Nyaya Sanhita, 2023", "85"),
    ("Indian Penal Code, 1860", "499"):  ("Bharatiya Nyaya Sanhita, 2023", "356"),
    ("Indian Penal Code, 1860", "503"):  ("Bharatiya Nyaya Sanhita, 2023", "351"),
    ("Code of Criminal Procedure, 1973", "154"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "173"),
    ("Code of Criminal Procedure, 1973", "167"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "187"),
    ("Code of Criminal Procedure, 1973", "438"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "483"),
    ("Indian Evidence Act, 1872", "65B"): ("Bharatiya Sakshya Adhiniyam, 2023", "39"),
}


def _old_new_ref(act: str, sec: str) -> Optional[str]:
    key = (act, sec)
    if key in _OLD_NEW:
        na, ns = _OLD_NEW[key]
        return f"{na}, Section {ns}"
    for (oa, os_), (na, ns) in _OLD_NEW.items():
        if act == na and sec == ns:
            return f"{oa}, Section {os_}"
    return None


# ═══════════════════════════════════════════════════════════════════════════
#  PRIORITY ACT REGISTRY
# ═══════════════════════════════════════════════════════════════════════════

# India Code act IDs for priority crawling
# Format: (act_name, india_code_handle_or_search_term, year)
PRIORITY_ACTS = [
    ("Bharatiya Nyaya Sanhita, 2023",               "bns-2023",        2023),
    ("Bharatiya Nagarik Suraksha Sanhita, 2023",     "bnss-2023",       2023),
    ("Bharatiya Sakshya Adhiniyam, 2023",            "bsa-2023",        2023),
    ("Indian Penal Code, 1860",                      "ipc-1860",        1860),
    ("Code of Criminal Procedure, 1973",             "crpc-1973",       1973),
    ("Indian Evidence Act, 1872",                    "evidence-1872",   1872),
    ("Information Technology Act, 2000",             "it-act-2000",     2000),
    ("Consumer Protection Act, 2019",                "consumer-2019",   2019),
    ("Motor Vehicles Act, 1988",                     "mv-act-1988",     1988),
    ("Right to Information Act, 2005",               "rti-2005",        2005),
    ("Protection of Children from Sexual Offences Act, 2012", "pocso-2012", 2012),
    ("Protection of Women from Domestic Violence Act, 2005", "dv-2005", 2005),
    ("Narcotic Drugs and Psychotropic Substances Act, 1985", "ndps-1985", 1985),
    ("Scheduled Castes and Tribes (Prevention of Atrocities) Act, 1989", "sc-st-1989", 1989),
    ("Prevention of Corruption Act, 1988",           "pca-1988",        1988),
    ("Indian Contract Act, 1872",                    "contract-1872",   1872),
    ("Transfer of Property Act, 1882",               "tp-1882",         1882),
    ("Hindu Marriage Act, 1955",                     "hma-1955",        1955),
    ("Arbitration and Conciliation Act, 1996",       "arbitration-1996", 1996),
    ("Income Tax Act, 1961",                         "it-1961",         1961),
]

# India Code base URL patterns
INDIA_CODE_BASE = "https://www.indiacode.nic.in"
INDIA_CODE_SEARCH = f"{INDIA_CODE_BASE}/search"
INDIA_CODE_ACT = f"{INDIA_CODE_BASE}/show-data"


# ═══════════════════════════════════════════════════════════════════════════
#  CENTRAL LAWS CRAWLER
# ═══════════════════════════════════════════════════════════════════════════

class CentralLawsCrawler:
    """
    Production crawler for Indian Central Acts from India Code
    (indiacode.nic.in) and related official portals.

    Strategy:
        1. For each Priority Act, search India Code to find its act page.
        2. Parse the act's section listing page.
        3. For each section, extract number, title, full text.
        4. Auto-enrich: category, keywords, old/new law cross-reference.
        5. Fall back to embedded seed data when network is unavailable.

    Rate limiting: default 2 s between requests.
    """

    USER_AGENT = "YAMA-AI-LegalCrawler/1.0 (Educational Legal Research)"

    def __init__(self, delay: float = 2.0, timeout: int = 30, max_retries: int = 3):
        self.delay = delay
        self.timeout = timeout
        self.max_retries = max_retries
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": self.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-IN,en;q=0.9",
        })
        self._last_request: float = 0
        self.stats = {"requests": 0, "records": 0, "errors": 0, "acts_crawled": 0}

    # ── HTTP ──────────────────────────────────────────────────────────────

    def _get(self, url: str) -> Optional[requests.Response]:
        elapsed = time.time() - self._last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)

        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self._session.get(url, timeout=self.timeout)
                self._last_request = time.time()
                self.stats["requests"] += 1

                if resp.status_code == 200:
                    return resp
                if resp.status_code in (429, 503):
                    wait = min(2 ** attempt, 60)
                    logger.warning("Rate limited — retry in %ds: %s", wait, url)
                    time.sleep(wait)
                    continue
                logger.warning("HTTP %d: %s", resp.status_code, url)
                return None

            except requests.Timeout:
                logger.warning("Timeout (attempt %d/%d): %s", attempt, self.max_retries, url)
                time.sleep(2 ** attempt)
            except requests.RequestException as exc:
                logger.error("Request error: %s — %s", url, exc)
                self.stats["errors"] += 1
                return None

        self.stats["errors"] += 1
        return None

    def _soup(self, url: str) -> Optional[BeautifulSoup]:
        resp = self._get(url)
        return BeautifulSoup(resp.text, "html.parser") if resp else None

    # ── India Code Search ──────────────────────────────────────────────────

    def _search_act(self, search_term: str) -> Optional[str]:
        """
        Search India Code for an act and return its act page URL.
        Returns the first matching result URL or None.
        """
        url = f"{INDIA_CODE_SEARCH}?query={requests.utils.quote(search_term)}&type=act"
        soup = self._soup(url)
        if not soup:
            return None

        # Look for act links in search results
        for link in soup.select("a[href*='/show-data'], a[href*='/handle/'], a[href*='/bitstream/']"):
            href = link["href"]
            if href.startswith("http"):
                return href
            return INDIA_CODE_BASE + href

        # Fall back: look for any result link containing the search term
        for link in soup.find_all("a", href=True):
            href = link["href"]
            title = link.get_text(strip=True).lower()
            if any(w in title for w in search_term.lower().split("-")[:2]):
                full = href if href.startswith("http") else INDIA_CODE_BASE + href
                return full

        return None

    # ── Act Parsing ────────────────────────────────────────────────────────

    def _parse_act_page(self, act_name: str, url: str) -> List[CentralLawRecord]:
        """
        Parse an India Code act detail page into section records.

        India Code renders sections with multiple layout patterns:
            Pattern A: <div class="section-content">
            Pattern B: <table.table tbody tr> with 3 columns
            Pattern C: <div class="akn-section">
            Pattern D: AKN (Akoma Ntoso) markup
        """
        records: List[CentralLawRecord] = []
        soup = self._soup(url)
        if not soup:
            return records

        # Resolve actual act name from page heading
        heading = (
            soup.select_one("h1.act-title")
            or soup.select_one("h2")
            or soup.select_one("h1")
            or soup.select_one("title")
        )
        if heading:
            resolved = _clean(heading.get_text())
            if len(resolved) > 5:
                act_name = resolved

        # Pattern A: .section-content blocks
        containers = soup.select("div.section-content")
        if not containers:
            containers = soup.select("div.orderCont")
        if not containers:
            containers = soup.select("div.akn-section")
        if not containers:
            # Pattern B: table rows
            containers = soup.select("table tbody tr")

        for container in containers:
            rec = self._extract_section(container, act_name, url)
            if rec:
                records.append(rec)

        return records

    def _extract_section(
        self, el: BeautifulSoup, act_name: str, source_url: str
    ) -> Optional[CentralLawRecord]:
        """Extract one section record from a page element."""
        # Section number
        num_el = (
            el.select_one(".section-number, .akn-num, .secNo")
            or el.select_one("td:first-child")
            or el.find(["b", "strong"])
        )
        if not num_el:
            return None
        raw_num = num_el.get_text(strip=True)
        sec_num = _normalize_section_num(raw_num)
        if not sec_num or len(sec_num) > 20:
            return None

        # Title / marginal heading
        head_el = (
            el.select_one(".section-heading, .akn-heading, .marginalNote")
            or el.select_one("td:nth-child(2)")
            or el.find(["em", "i"])
        )
        title = _clean(head_el.get_text()) if head_el else f"Section {sec_num}"

        # Full text
        text_el = el.select_one(".section-text, .akn-content") or el
        raw_text = _clean(text_el.get_text(separator=" "))
        # Remove duplicated section number and title from body
        raw_text = raw_text.replace(raw_num, "", 1).replace(title, "", 1).strip()
        if len(raw_text) < 15:
            raw_text = title

        # Punishment extraction
        punishment = _extract_punishment(raw_text)

        # Auto-enrich
        category = _classify(act_name, title, raw_text)
        keywords = _extract_keywords(title, raw_text)
        old_ref = _old_new_ref(act_name, sec_num)

        return CentralLawRecord(
            act_name=act_name,
            section_number=sec_num,
            title=title[:500],
            description=raw_text[:10000],
            keywords=keywords,
            category=category,
            punishment=punishment,
            old_law_reference=old_ref,
            source_url=source_url,
        )

    # ── Main Crawl ─────────────────────────────────────────────────────────

    def crawl(
        self,
        acts: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> List[CentralLawRecord]:
        """
        Crawl central acts from India Code.

        Args:
            acts:  Optional list of act name substrings to filter.
                   e.g. ["BNS", "IPC", "consumer"] — case-insensitive.
            limit: Max acts to crawl (useful for testing).

        Returns:
            List of CentralLawRecord objects.
        """
        target_acts = PRIORITY_ACTS
        if acts:
            acts_lower = [a.lower() for a in acts]
            target_acts = [
                a for a in PRIORITY_ACTS
                if any(filt in a[0].lower() for filt in acts_lower)
            ]
        if limit:
            target_acts = target_acts[:limit]

        all_records: List[CentralLawRecord] = []

        for act_name, search_term, _ in target_acts:
            logger.info("Crawling: %s", act_name)
            act_url = self._search_act(act_name)

            if not act_url:
                logger.warning("Could not find India Code page for: %s — using seed data", act_name)
                records = self._seed_for_act(act_name)
            else:
                records = self._parse_act_page(act_name, act_url)
                if not records:
                    logger.warning("Page parsed but no sections found for %s — using seed data", act_name)
                    records = self._seed_for_act(act_name)

            logger.info("  → %d sections extracted", len(records))
            all_records.extend(records)
            self.stats["acts_crawled"] += 1

        # Dedup by content_hash
        seen: set = set()
        unique: List[CentralLawRecord] = []
        for r in all_records:
            if r.content_hash not in seen:
                seen.add(r.content_hash)
                unique.append(r)

        if not unique:
            logger.warning("Live crawl empty — returning full seed dataset")
            unique = self._get_seed_data()

        self.stats["records"] = len(unique)
        logger.info("Central laws crawl complete: %d records from %d acts",
                    len(unique), self.stats["acts_crawled"])
        return unique

    # ── Seed Data ─────────────────────────────────────────────────────────

    def _seed_for_act(self, act_name: str) -> List[CentralLawRecord]:
        """Return seed records for a specific act from the full seed set."""
        return [r for r in self._get_seed_data() if r.act_name == act_name]

    def _get_seed_data(self) -> List[CentralLawRecord]:
        """
        Comprehensive curated seed dataset covering core Indian statutes.
        Used as an offline fallback when live crawl fails.
        """
        _D = INDIA_CODE_BASE  # source URL placeholder

        raw: List[Tuple] = [
            # ── Bharatiya Nyaya Sanhita, 2023 (replaces IPC) ──────────────
            ("Bharatiya Nyaya Sanhita, 2023", "63",
             "Rape",
             "A man is said to commit 'rape' if he penetrates his penis, to any extent, into "
             "the vagina, mouth, urethra or anus of a woman or makes her to do so with him or "
             "any other person; or inserts, to any extent, any object or a part of the body, "
             "not being the penis, into the vagina, the urethra or anus of a woman or makes her "
             "to do so with him or any other person; or manipulates any part of the body of a "
             "woman so as to cause penetration into the vagina, urethra, anus or any part of "
             "body of such woman or makes her to do so with him or any other person; or applies "
             "his mouth to the vagina, anus, urethra of a woman or makes her to do so with him "
             "or any other person, under the circumstances falling under any of the following "
             "seven descriptions.",
             "Rigorous imprisonment not less than ten years, which may extend to imprisonment "
             "for life, and shall also be liable to fine.",
             "Indian Penal Code, 1860, Section 376"),
            ("Bharatiya Nyaya Sanhita, 2023", "74",
             "Assault or criminal force to woman with intent to outrage her modesty",
             "Whoever assaults or uses criminal force to any woman, intending to outrage or "
             "knowing it to be likely that he will thereby outrage her modesty, shall be "
             "punished with imprisonment of either description for a term which shall not be "
             "less than one year but which may extend to five years, and shall also be liable "
             "to fine.",
             "Imprisonment not less than 1 year, up to 5 years, and fine.",
             "Indian Penal Code, 1860, Section 354"),
            ("Bharatiya Nyaya Sanhita, 2023", "85",
             "Husband or relative of husband of a woman subjecting her to cruelty",
             "Whoever, being the husband or the relative of the husband of a woman, subjects "
             "such woman to cruelty shall be punished with imprisonment of either description "
             "for a term which may extend to three years and shall also be liable to fine.",
             "Imprisonment up to 3 years and fine.",
             "Indian Penal Code, 1860, Section 498A"),
            ("Bharatiya Nyaya Sanhita, 2023", "100",
             "Murder",
             "Whoever causes death by doing an act with the intention of causing death, or with "
             "the intention of causing such bodily injury as is likely to cause death, or with "
             "the knowledge that he is likely by such act to cause death, commits the offence "
             "of murder. Exception 1: Culpable homicide is not murder if the offender, whilst "
             "deprived of the power of self-control by grave and sudden provocation, causes the "
             "death of the person who gave the provocation.",
             "Death or imprisonment for life, and fine.",
             "Indian Penal Code, 1860, Section 302"),
            ("Bharatiya Nyaya Sanhita, 2023", "101",
             "Culpable homicide not amounting to murder",
             "Whoever causes death by doing an act with the intention of causing death, or with "
             "the intention of causing such bodily injury as is likely to cause death, or with "
             "the knowledge that he is likely by such act to cause death, but without "
             "premeditation in a sudden fight in the heat of passion upon a sudden quarrel.",
             "Imprisonment for life, or imprisonment up to 10 years, and fine.",
             "Indian Penal Code, 1860, Section 304"),
            ("Bharatiya Nyaya Sanhita, 2023", "105",
             "Dowry death",
             "Where the death of a woman is caused by any burns or bodily injury or occurs "
             "otherwise than under normal circumstances within seven years of her marriage and "
             "it is shown that soon before her death she was subjected to cruelty or harassment "
             "by her husband or any relative of her husband for, or in connection with, any "
             "demand for dowry, such death shall be called 'dowry death'.",
             "Imprisonment not less than 7 years, which may extend to imprisonment for life.",
             "Indian Penal Code, 1860, Section 304B"),
            ("Bharatiya Nyaya Sanhita, 2023", "115",
             "Voluntarily causing hurt",
             "Whoever does any act with the intention of thereby causing hurt to any person, "
             "or with the knowledge that he is likely thereby to cause hurt to any person, and "
             "does thereby cause hurt to any person, is said voluntarily to cause hurt.",
             "Imprisonment up to 1 year, or fine up to ₹10,000, or both.",
             "Indian Penal Code, 1860, Section 323"),
            ("Bharatiya Nyaya Sanhita, 2023", "303",
             "Theft",
             "Whoever, intending to take dishonestly any moveable property out of the "
             "possession of any person without that person's consent, moves that property in "
             "order to such taking, is said to commit theft.",
             "Imprisonment up to 3 years, or fine, or both.",
             "Indian Penal Code, 1860, Section 378"),
            ("Bharatiya Nyaya Sanhita, 2023", "305",
             "Robbery",
             "In all robbery there is either theft or extortion. Theft is robbery if, in order "
             "to the committing of the theft, or in committing the theft, or in carrying away "
             "or attempting to carry away property obtained by the theft, the offender, for "
             "that end, voluntarily causes or attempts to cause to any person death or hurt or "
             "wrongful restraint, or fear of instant death or of instant hurt, or of instant "
             "wrongful restraint.",
             "Rigorous imprisonment up to 10 years, and fine.",
             "Indian Penal Code, 1860, Section 392"),
            ("Bharatiya Nyaya Sanhita, 2023", "308",
             "Extortion",
             "Whoever intentionally puts any person in fear of any injury to that person, or "
             "to any other, and thereby dishonestly induces the person so put in fear to deliver "
             "to any person any property or valuable security, or anything signed or sealed which "
             "may be converted into a valuable security, commits extortion.",
             "Imprisonment up to 3 years, or fine, or both.",
             "Indian Penal Code, 1860, Section 384"),
            ("Bharatiya Nyaya Sanhita, 2023", "316",
             "Cheating",
             "Whoever, by deceiving any person, fraudulently or dishonestly induces the person "
             "so deceived to deliver any property to any person, or to consent that any person "
             "shall retain any property, or intentionally induces the person so deceived to do "
             "or omit to do anything which he would not do or omit if he were not so deceived, "
             "and which act or omission causes or is likely to cause damage or harm to that "
             "person in body, mind, reputation or property, is said to 'cheat'.",
             "Imprisonment up to 3 years, or fine, or both.",
             "Indian Penal Code, 1860, Section 420"),
            ("Bharatiya Nyaya Sanhita, 2023", "329",
             "Criminal breach of trust",
             "Whoever, being in any manner entrusted with property, or with any dominion over "
             "property, dishonestly misappropriates or converts to his own use that property, "
             "or dishonestly uses or disposes of that property in violation of any direction of "
             "law prescribing the mode in which such trust is to be discharged, or of any legal "
             "contract, express or implied, which he has made touching the discharge of such "
             "trust, or wilfully suffers any other person so to do, commits criminal breach of "
             "trust.",
             "Imprisonment up to 7 years, and fine.",
             "Indian Penal Code, 1860, Section 405"),
            ("Bharatiya Nyaya Sanhita, 2023", "351",
             "Criminal intimidation",
             "Whoever threatens another with any injury to his person, reputation or property, "
             "or to the person or reputation of any one in whom that person is interested, with "
             "intent to cause alarm to that person, or to cause that person to do any act which "
             "he is not legally bound to do, or to omit to do any act which that person is "
             "legally entitled to do, as the means of avoiding the execution of such threat, "
             "commits criminal intimidation.",
             "Imprisonment up to 2 years, or fine, or both.",
             "Indian Penal Code, 1860, Section 503"),
            ("Bharatiya Nyaya Sanhita, 2023", "356",
             "Defamation",
             "Whoever, by words either spoken or intended to be read, or by signs or by visible "
             "representations, makes or publishes any imputation concerning any person intending "
             "to harm, or knowing or having reason to believe that such imputation will harm the "
             "reputation of such person, is said, except in the cases hereinafter excepted, to "
             "defame that person.",
             "Imprisonment up to 2 years, or fine, or both.",
             "Indian Penal Code, 1860, Section 499"),

            # ── Bharatiya Nagarik Suraksha Sanhita, 2023 ─────────────────
            ("Bharatiya Nagarik Suraksha Sanhita, 2023", "173",
             "Information in cognizable cases",
             "Every information relating to the commission of a cognizable offence, irrespective "
             "of the area where the offence is committed, may be given orally or by electronic "
             "communication to an officer in charge of a police station, and if given orally, "
             "shall be reduced to writing by him or under his direction, and be read over to the "
             "informant; and every such information, whether given in writing or reduced to writing "
             "as aforesaid, shall be signed by the person giving it, and the substance thereof "
             "shall be entered in a book to be kept by such officer in such form as the State "
             "Government may prescribe in this behalf.",
             None,
             "Code of Criminal Procedure, 1973, Section 154"),
            ("Bharatiya Nagarik Suraksha Sanhita, 2023", "187",
             "Procedure when investigation cannot be completed in twenty-four hours",
             "Whenever any person is arrested and detained in custody and it appears that the "
             "investigation cannot be completed within the period of twenty-four hours fixed by "
             "section 58, and there are grounds for believing that the accusation or information "
             "is well-founded, the officer in charge of the police station or the police officer "
             "making the investigation shall forthwith transmit to the nearest Judicial Magistrate "
             "a copy of the entries in the diary and shall at the same time forward the accused "
             "to such Magistrate.",
             None,
             "Code of Criminal Procedure, 1973, Section 167"),
            ("Bharatiya Nagarik Suraksha Sanhita, 2023", "480",
             "Bail in bailable offences",
             "When any person other than a person accused of a non-bailable offence is arrested "
             "or detained without warrant by an officer in charge of a police station, or appears "
             "or is brought before a Court, and is prepared at any time while in the custody of "
             "such officer or at any stage of the proceeding before such Court to give bail, such "
             "person shall be released on bail.",
             None,
             "Code of Criminal Procedure, 1973, Section 436"),
            ("Bharatiya Nagarik Suraksha Sanhita, 2023", "483",
             "Direction for grant of bail to person apprehending arrest",
             "When any person has reason to believe that he may be arrested on an accusation of "
             "having committed a non-bailable offence, he may apply to the High Court or the Court "
             "of Session for a direction under this section; and that Court may, if it thinks fit, "
             "direct that in the event of such arrest, he shall be released on bail.",
             None,
             "Code of Criminal Procedure, 1973, Section 438"),

            # ── Information Technology Act, 2000 ──────────────────────────
            ("Information Technology Act, 2000", "43",
             "Penalty and compensation for damage to computer, computer system",
             "If any person without permission of the owner or any other person who is in charge "
             "of a computer, computer system or computer network accesses or secures access to "
             "such computer, computer system or computer network; downloads, copies or extracts "
             "any data, computer data base or information from such computer, computer system or "
             "computer network including information or data held or stored in any removable "
             "storage medium; introduces or causes to be introduced any computer contaminant or "
             "computer virus into any computer, computer system or computer network, he shall be "
             "liable to pay damages by way of compensation to the person so affected.",
             "Compensation up to ₹1 crore to the affected person.",
             None),
            ("Information Technology Act, 2000", "66",
             "Computer related offences",
             "If any person, dishonestly or fraudulently, does any act referred to in section 43, "
             "he shall be punishable with imprisonment for a term which may extend to three years "
             "or with fine which may extend to five lakh rupees or with both.",
             "Imprisonment up to 3 years, or fine up to ₹5 lakh, or both.",
             None),
            ("Information Technology Act, 2000", "66A",
             "Punishment for sending offensive messages through communication service",
             "Any person who sends by means of a computer resource or a communication device any "
             "information that is grossly offensive or has menacing character; or any information "
             "which he knows to be false, but for the purpose of causing annoyance, inconvenience, "
             "danger, obstruction, insult, injury, criminal intimidation, enmity, hatred or ill "
             "will, persistently by making use of such computer resource or a communication device; "
             "or any electronic mail or electronic mail message for the purpose of causing "
             "annoyance or inconvenience or to deceive or to mislead the addressee or recipient "
             "about the origin of such messages, shall be punishable. [Note: Struck down by "
             "Supreme Court in Shreya Singhal v. Union of India, 2015]",
             "Struck down by Supreme Court — Not in force.",
             None),
            ("Information Technology Act, 2000", "72",
             "Breach of confidentiality and privacy",
             "Save as otherwise provided in this Act or any other law for the time being in force, "
             "if any person who, in pursuance of any of the powers conferred under this Act, rules "
             "or regulations made thereunder, has secured access to any electronic record, book, "
             "register, correspondence, information, document or other material without the consent "
             "of the person concerned discloses such electronic record, book, register, "
             "correspondence, information, document or other material to any other person shall be "
             "guilty of an offence under this Act.",
             "Imprisonment up to 2 years, or fine up to ₹1 lakh, or both.",
             None),

            # ── Consumer Protection Act, 2019 ─────────────────────────────
            ("Consumer Protection Act, 2019", "2",
             "Definitions",
             "'consumer' means any person who buys any goods for a consideration which has been "
             "paid or promised or partly paid and partly promised, or under any system of deferred "
             "payment and includes any user of such goods other than the person who buys such goods "
             "for consideration paid or promised or partly paid or partly promised, or under any "
             "system of deferred payment, when such use is made with the approval of such person, "
             "but does not include a person who obtains such goods for resale or for any commercial "
             "purpose.",
             None,
             None),
            ("Consumer Protection Act, 2019", "35",
             "Complaint before District Commission",
             "A complaint, in relation to any goods sold or delivered or agreed to be sold or "
             "delivered or any service provided or agreed to be provided, may be filed with a "
             "District Commission by the complainant, in person, or by his agent, or by any "
             "recognised consumer association, where the value of the goods or services paid as "
             "consideration does not exceed one crore rupees.",
             None,
             None),

            # ── Motor Vehicles Act, 1988 ──────────────────────────────────
            ("Motor Vehicles Act, 1988", "185",
             "Driving by a drunken person or by a person under the influence of drugs",
             "Whoever, while driving or attempting to drive a motor vehicle has in his blood "
             "alcohol exceeding 30 mg. per 100 ml. of blood detected in a test by a breath "
             "analyser, shall be punishable for the first offence with imprisonment for a term "
             "which may extend to six months, or with fine which may extend to two thousand "
             "rupees, or with both; and for a second or subsequent offence, if committed within "
             "three years of the commission of the previous similar offence, with imprisonment "
             "for a term which may extend to two years, or with fine which may extend to three "
             "thousand rupees, or with both.",
             "First offence: up to 6 months imprisonment, or fine up to ₹2,000. "
             "Repeat offence: up to 2 years, or fine up to ₹3,000.",
             None),
            ("Motor Vehicles Act, 1988", "279",
             "Rash driving or riding on a public way",
             "Whoever drives any vehicle, or rides on any public way in a manner so rash or "
             "negligent as to endanger human life, or to be likely to cause hurt or injury to "
             "any other person, shall be punishable with imprisonment of either description for "
             "a term which may extend to six months, or with fine which may extend to one "
             "thousand rupees, or with both. [Note: Now Bharatiya Nyaya Sanhita, 2023, Section 281]",
             "Imprisonment up to 6 months, or fine up to ₹1,000, or both.",
             None),

            # ── Right to Information Act, 2005 ────────────────────────────
            ("Right to Information Act, 2005", "3",
             "Right to information",
             "Subject to the provisions of this Act, all citizens shall have the right to "
             "information.",
             None,
             None),
            ("Right to Information Act, 2005", "7",
             "Disposal of request",
             "Subject to the proviso to sub-section (2) of section 5 or the proviso to "
             "sub-section (3) of section 6, the Central Public Information Officer or State "
             "Public Information Officer, as the case may be, on receipt of a request under "
             "section 6 shall, as expeditiously as possible, and in any case within thirty days "
             "of the receipt of the request, either provide the information on payment of such "
             "fee as may be prescribed or reject the request for any of the reasons specified "
             "in sections 8 and 9.",
             None,
             None),
            ("Right to Information Act, 2005", "20",
             "Penalties",
             "Where the Central Information Commission or the State Information Commission, as "
             "the case may be, at the time of deciding any complaint or appeal is of the opinion "
             "that the Central Public Information Officer or the State Public Information Officer, "
             "as the case may be, has, without any reasonable cause, refused to receive an "
             "application for information or has not furnished information within the time "
             "specified under sub-section (1) of section 7 or malafidely denied the request for "
             "information or knowingly given incorrect, incomplete or misleading information or "
             "destroyed information which was the subject of the request or obstructed in any "
             "manner in furnishing the information, it shall impose a penalty of two hundred and "
             "fifty rupees each day till the application is received or information is furnished.",
             "Penalty of ₹250 per day, up to a maximum of ₹25,000.",
             None),

            # ── POCSO Act, 2012 ───────────────────────────────────────────
            ("Protection of Children from Sexual Offences Act, 2012", "4",
             "Punishment for penetrative sexual assault",
             "Whoever commits penetrative sexual assault shall be punished with rigorous "
             "imprisonment for a term which shall not be less than ten years but which may "
             "extend to imprisonment for life, and shall also be liable to fine.",
             "Rigorous imprisonment not less than 10 years, up to life imprisonment, and fine.",
             None),
            ("Protection of Children from Sexual Offences Act, 2012", "19",
             "Reporting of offences",
             "Notwithstanding anything contained in the Code of Criminal Procedure, 1973, any "
             "person (including the child), who has apprehension that an offence under this Act "
             "is likely to be committed or has knowledge that such an offence has been committed, "
             "he shall provide such information to the Special Juvenile Police Unit or to the "
             "local police.",
             None,
             None),
        ]

        records = []
        for item in raw:
            if len(item) == 6:
                act_name, sec_num, title, desc, punishment, old_ref = item
            else:
                act_name, sec_num, title, desc = item
                punishment = old_ref = None

            category = _classify(act_name, title, desc)
            keywords = _extract_keywords(title, desc)

            records.append(CentralLawRecord(
                act_name=act_name,
                section_number=sec_num,
                title=title,
                description=desc,
                keywords=keywords,
                category=category,
                punishment=punishment,
                old_law_reference=old_ref,
                source_url=INDIA_CODE_BASE,
            ))

        return records

    # ── Export ─────────────────────────────────────────────────────────────

    def export_json(self, records: List[CentralLawRecord], path: str) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        data = {
            "metadata": {
                "title": "YAMA AI — Central Laws Dataset",
                "total_records": len(records),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "source": "India Code (indiacode.nic.in)",
            },
            "records": [r.to_dict() for r in records],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("Exported %d records → %s", len(records), path)


# ═══════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _normalize_section_num(raw: str) -> str:
    """'Section 302A' → '302A', 'Sec. 5' → '5'."""
    raw = re.sub(r"^(Section|Sec\.?|Article|Art\.?|Rule|Clause)\s*", "", raw, flags=re.I)
    return raw.strip("()[]., ")


def _extract_punishment(text: str) -> Optional[str]:
    """Extract punishment clause from section text."""
    patterns = [
        r"(shall be punished?[^.]+\.)",
        r"(punishable with[^.]+\.)",
        r"(imprisonment[^.]{10,80}\.)",
        r"(liable to fine[^.]+\.)",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()[:500]
    return None


# ═══════════════════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="YAMA AI — Central Laws Crawler (India Code)",
    )
    parser.add_argument("--act", nargs="*", help="Filter acts (e.g. BNS IPC consumer)")
    parser.add_argument("--limit", type=int, help="Max number of acts to crawl")
    parser.add_argument("--export", metavar="FILE", default="", help="Export to JSON file")
    parser.add_argument("--offline", action="store_true", help="Use seed data only")
    parser.add_argument("--delay", type=float, default=2.0, help="Request delay seconds")
    args = parser.parse_args()

    crawler = CentralLawsCrawler(delay=args.delay)

    if args.offline:
        records = crawler._get_seed_data()
        logger.info("Offline mode: %d seed records", len(records))
    else:
        records = crawler.crawl(acts=args.act, limit=args.limit)

    print(f"\n{'-'*60}")
    print(f"  Central laws crawl complete")
    print(f"  Records extracted : {len(records)}")
    print(f"  Acts crawled      : {crawler.stats.get('acts_crawled', '-')}")
    print(f"  HTTP requests     : {crawler.stats['requests']}")
    print(f"  Errors            : {crawler.stats['errors']}")
    print(f"{'-'*60}\n")

    if args.export:
        crawler.export_json(records, args.export)

    return records


if __name__ == "__main__":
    main()
