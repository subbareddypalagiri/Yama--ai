"""
YAMA AI — Legal Data Crawler
=============================================================================
Production-grade crawler for Indian legal data from official government sources.

Targets:
    1. India Code       — https://www.indiacode.nic.in   (all central acts)
    2. Legislative Dept  — https://legislative.gov.in      (bills, ordinances)
    3. eGazette          — https://egazette.gov.in         (notifications, rules)
    4. Supreme Court     — https://main.sci.gov.in         (judgments)
    5. High Courts       — various state HC portals        (judgments)
    6. Constitution      — india.gov.in                    (articles, amendments)
    7. State Portals     — state law department sites       (state acts)

Uses: requests + BeautifulSoup (no browser automation needed for most sources).

Collects per record:
    - act_name          Full name of the act/statute
    - section_number    Section, Article, or Rule number
    - title             Marginal heading
    - section_text      Full text of the provision
    - source_url        Official URL from which data was extracted

Usage:
    from data_pipeline.crawler import LegalCrawler

    crawler = LegalCrawler()

    # Crawl India Code
    records = crawler.crawl_india_code()

    # Crawl Constitution
    records = crawler.crawl_constitution()

    # Crawl Supreme Court judgments
    records = crawler.crawl_supreme_court()

    # Crawl everything
    all_records = crawler.crawl_all()

    # Store into database + ChromaDB
    crawler.store_records(records)

CLI:
    cd backend
    python -m data_pipeline.crawler --source india_code
    python -m data_pipeline.crawler --source all
    python -m data_pipeline.crawler --source constitution --export json
=============================================================================
"""

import hashlib
import json
import csv
import logging
import os
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup, Tag

# ── Ensure backend root is on sys.path for app.* imports ──
_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("yama_ai.crawler")


# ═══════════════════════════════════════════════════════════════════════════
#  DATA MODEL
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class LegalRecord:
    """
    A single, self-contained legal provision extracted from any source.
    This is the universal exchange format for the entire pipeline.
    """
    act_name: str                              # "Bharatiya Nyaya Sanhita, 2023"
    section_number: str                        # "303", "Article 21", "Rule 5"
    title: str                                 # "Theft"
    section_text: str                          # Full provision text
    source_url: str                            # Official URL

    # ── Auto-enriched fields ──
    keywords: str = ""                         # Comma-separated
    category: str = "general"                  # criminal, civil, constitutional, etc.
    jurisdiction: str = "central"              # central / state
    state_name: Optional[str] = None           # Only if jurisdiction == "state"
    law_type: str = "act"                      # act / article / rule / judgment / notification
    punishment: Optional[str] = None
    old_law_reference: Optional[str] = None    # IPC ↔ BNS mapping
    content_hash: str = ""                     # SHA-256 for dedup

    def __post_init__(self):
        """Auto-compute content hash after creation."""
        if not self.content_hash:
            self.content_hash = self._hash()

    def _hash(self) -> str:
        blob = f"{self.act_name}|{self.section_number}|{self.title}|{self.section_text}"
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict:
        d = asdict(self)
        # Rename section_text → description for DB compatibility
        d["description"] = d.pop("section_text")
        return d


# ═══════════════════════════════════════════════════════════════════════════
#  CATEGORY CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "criminal": [
        "penal", "offence", "punishment", "murder", "theft", "assault", "robbery",
        "criminal", "bail", "fir", "arrest", "kidnapping", "rape", "fraud",
        "nyaya sanhita", "bns", "ipc", "extortion", "cheating", "forgery",
        "dacoity", "hurt", "grievous", "intimidation", "defamation",
    ],
    "civil": [
        "contract", "property", "tort", "damages", "civil", "suit", "decree",
        "specific relief", "limitation", "agreement", "breach",
    ],
    "constitutional": [
        "constitution", "fundamental", "article", "amendment", "directive",
        "writ", "habeas corpus", "mandamus", "certiorari", "quo warranto",
    ],
    "consumer": [
        "consumer", "deficiency", "goods", "services", "complaint",
        "redressal", "product liability", "misleading advertisement",
    ],
    "cyber": [
        "information technology", "cyber", "computer", "electronic", "data",
        "hacking", "it act", "identity theft", "phishing",
    ],
    "family": [
        "marriage", "divorce", "maintenance", "custody", "adoption", "dowry",
        "domestic violence", "hindu", "muslim", "christian",
    ],
    "motor_vehicle": [
        "motor", "vehicle", "driving", "accident", "licence", "traffic",
        "road", "insurance", "drunk driving", "speed",
    ],
    "labour": [
        "labour", "labor", "worker", "employment", "wage", "industrial",
        "factory", "trade union", "provident fund",
    ],
    "property": [
        "property", "land", "registration", "transfer", "tenancy", "rent",
        "succession", "inheritance", "easement",
    ],
    "tax": [
        "tax", "income", "gst", "customs", "excise", "revenue",
    ],
    "environmental": [
        "environment", "pollution", "forest", "wildlife", "water", "air",
    ],
    "corporate": [
        "company", "corporate", "director", "shareholder", "insolvency",
        "bankruptcy", "sebi", "securities",
    ],
}


def classify_category(act_name: str, title: str, text: str) -> str:
    """Auto-classify a provision into a legal category by keyword scoring."""
    combined = f"{act_name} {title} {text[:600]}".lower()
    best, best_score = "general", 0
    for cat, kws in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in kws if kw in combined)
        if score > best_score:
            best, best_score = cat, score
    return best


def extract_keywords(title: str, text: str, limit: int = 15) -> str:
    """Auto-extract meaningful keywords from title + text."""
    combined = f"{title} {text[:500]}".lower()
    stop = {
        "the", "of", "and", "in", "to", "a", "is", "or", "for", "be",
        "an", "as", "by", "on", "at", "it", "that", "this", "with",
        "any", "shall", "may", "such", "which", "who", "not", "from",
        "under", "been", "has", "have", "his", "her", "its", "was",
        "were", "are", "been", "being", "into", "than", "them", "then",
        "there", "these", "they", "upon", "where", "whether", "whom",
        "will", "would", "every", "person", "section", "act",
    }
    words = re.findall(r"[a-z]{3,}", combined)
    unique = list(dict.fromkeys(w for w in words if w not in stop))
    return ", ".join(unique[:limit])


# ═══════════════════════════════════════════════════════════════════════════
#  OLD LAW ↔ NEW LAW MAPPING  (IPC → BNS, CrPC → BNSS, Evidence → BSA)
# ═══════════════════════════════════════════════════════════════════════════

OLD_NEW_MAP = {
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
    ("Indian Penal Code, 1860", "384"):  ("Bharatiya Nyaya Sanhita, 2023", "308"),
    ("Indian Penal Code, 1860", "392"):  ("Bharatiya Nyaya Sanhita, 2023", "305"),
    ("Indian Penal Code, 1860", "395"):  ("Bharatiya Nyaya Sanhita, 2023", "306"),
    ("Indian Penal Code, 1860", "405"):  ("Bharatiya Nyaya Sanhita, 2023", "329"),
    ("Indian Penal Code, 1860", "420"):  ("Bharatiya Nyaya Sanhita, 2023", "316"),
    ("Indian Penal Code, 1860", "463"):  ("Bharatiya Nyaya Sanhita, 2023", "336"),
    ("Indian Penal Code, 1860", "498A"): ("Bharatiya Nyaya Sanhita, 2023", "85"),
    ("Indian Penal Code, 1860", "499"):  ("Bharatiya Nyaya Sanhita, 2023", "356"),
    ("Indian Penal Code, 1860", "503"):  ("Bharatiya Nyaya Sanhita, 2023", "351"),
    # CrPC → BNSS
    ("Code of Criminal Procedure, 1973", "154"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "173"),
    ("Code of Criminal Procedure, 1973", "156"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "175"),
    ("Code of Criminal Procedure, 1973", "167"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "187"),
    ("Code of Criminal Procedure, 1973", "173"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "210"),
    ("Code of Criminal Procedure, 1973", "436"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "480"),
    ("Code of Criminal Procedure, 1973", "437"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "482"),
    ("Code of Criminal Procedure, 1973", "438"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "483"),
    ("Code of Criminal Procedure, 1973", "482"): ("Bharatiya Nagarik Suraksha Sanhita, 2023", "528"),
    # Evidence → BSA
    ("Indian Evidence Act, 1872", "25"):  ("Bharatiya Sakshya Adhiniyam, 2023", "57"),
    ("Indian Evidence Act, 1872", "32"):  ("Bharatiya Sakshya Adhiniyam, 2023", "47"),
    ("Indian Evidence Act, 1872", "65B"): ("Bharatiya Sakshya Adhiniyam, 2023", "39"),
    ("Indian Evidence Act, 1872", "101"): ("Bharatiya Sakshya Adhiniyam, 2023", "101"),
}


def find_old_law_reference(act_name: str, section_number: str) -> Optional[str]:
    """Look up old ↔ new law mapping in either direction."""
    key = (act_name, section_number)
    if key in OLD_NEW_MAP:
        new_act, new_sec = OLD_NEW_MAP[key]
        return f"{new_act}, Section {new_sec}"
    # Reverse lookup
    for (old_act, old_sec), (new_act, new_sec) in OLD_NEW_MAP.items():
        if act_name == new_act and section_number == new_sec:
            return f"{old_act}, Section {old_sec}"
    return None


# ═══════════════════════════════════════════════════════════════════════════
#  DATA CLEANER
# ═══════════════════════════════════════════════════════════════════════════

ACT_NAME_ALIASES = {
    "bharatiya nyaya sanhita":            "Bharatiya Nyaya Sanhita, 2023",
    "bns":                                "Bharatiya Nyaya Sanhita, 2023",
    "indian penal code":                  "Indian Penal Code, 1860",
    "ipc":                                "Indian Penal Code, 1860",
    "bharatiya nagarik suraksha sanhita": "Bharatiya Nagarik Suraksha Sanhita, 2023",
    "bnss":                               "Bharatiya Nagarik Suraksha Sanhita, 2023",
    "code of criminal procedure":         "Code of Criminal Procedure, 1973",
    "crpc":                               "Code of Criminal Procedure, 1973",
    "bharatiya sakshya adhiniyam":        "Bharatiya Sakshya Adhiniyam, 2023",
    "bsa":                                "Bharatiya Sakshya Adhiniyam, 2023",
    "indian evidence act":                "Indian Evidence Act, 1872",
    "information technology act":         "Information Technology Act, 2000",
    "it act":                             "Information Technology Act, 2000",
    "consumer protection act":            "Consumer Protection Act, 2019",
    "motor vehicles act":                 "Motor Vehicles Act, 1988",
    "constitution of india":              "Constitution of India",
    "constitution":                       "Constitution of India",
}


def clean_text(text: str) -> str:
    """Strip HTML, fix encoding, collapse whitespace."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\u00a0", " ")
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2014", " — ").replace("\u2013", " – ")
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_section_number(raw: str) -> str:
    """Normalize 'Section 302A' → '302A'."""
    raw = raw.strip()
    raw = re.sub(r"^(Section|Sec\.?|Article|Art\.?|Rule)\s*", "", raw, flags=re.I)
    return raw.strip("()[]., ")


def standardize_act_name(name: str) -> str:
    """Map aliases → canonical name."""
    name = re.sub(r"<[^>]+>", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    name = re.sub(r"^The\s+", "", name, flags=re.I).rstrip(" .,;:")
    key = name.lower().strip()
    if key in ACT_NAME_ALIASES:
        return ACT_NAME_ALIASES[key]
    for alias, canonical in ACT_NAME_ALIASES.items():
        if alias in key:
            return canonical
    return name


def enrich_record(rec: LegalRecord) -> LegalRecord:
    """Auto-fill keywords, category, and old-law reference."""
    rec.act_name = standardize_act_name(rec.act_name)
    rec.title = clean_text(rec.title)
    rec.section_text = clean_text(rec.section_text)
    rec.section_number = clean_section_number(rec.section_number)
    rec.keywords = extract_keywords(rec.title, rec.section_text)
    rec.category = classify_category(rec.act_name, rec.title, rec.section_text)
    rec.old_law_reference = find_old_law_reference(rec.act_name, rec.section_number)
    rec.content_hash = rec._hash()
    return rec


# ═══════════════════════════════════════════════════════════════════════════
#  CORE CRAWLER ENGINE
# ═══════════════════════════════════════════════════════════════════════════

# Portal registry for High Courts
HIGH_COURT_PORTALS = {
    "Delhi":              "https://delhihighcourt.nic.in",
    "Bombay":             "https://bombayhighcourt.nic.in",
    "Madras":             "https://www.mhc.tn.gov.in",
    "Calcutta":           "https://calcuttahighcourt.gov.in",
    "Karnataka":          "https://karnatakajudiciary.kar.nic.in",
    "Allahabad":          "https://www.allahabadhighcourt.in",
    "Kerala":             "https://highcourtofkerala.nic.in",
    "Gujarat":            "https://gujarathighcourt.nic.in",
    "Punjab and Haryana": "https://phhc.gov.in",
    "Telangana":          "https://tshc.gov.in",
}

# State law department portals
STATE_LAW_PORTALS = {
    "Maharashtra":   "https://bombayhighcourt.nic.in/stateacts.php",
    "Karnataka":     "https://dpal.karnataka.gov.in",
    "Tamil Nadu":    "https://www.tn.gov.in/laws",
    "Kerala":        "https://www.keralalegislature.org",
    "Gujarat":       "https://legal.gujarat.gov.in",
    "Rajasthan":     "https://law.rajasthan.gov.in",
    "Uttar Pradesh": "https://updpadirector.up.nic.in",
    "Delhi":         "https://legislative.gov.in/state-legislation-delhi",
    "Telangana":     "https://legislation.telangana.gov.in",
}


class LegalCrawler:
    """
    Production legal data crawler for Indian government sources.

    Features:
        • Polite crawling — configurable delay between requests (default 2 s)
        • Automatic retry with exponential back-off on 429/503
        • User-Agent identification
        • Content-hash dedup (same provision won't be re-inserted)
        • Auto-enrichment (category, keywords, old↔new law mapping)
        • Direct integration with YAMA AI database + ChromaDB

    Example:
        crawler = LegalCrawler(delay=2.0)
        records = crawler.crawl_india_code()
        crawler.store_records(records)
    """

    USER_AGENT = (
        "YAMA-AI-LegalCrawler/1.0 "
        "(Educational Legal Research; +https://github.com/yama-ai)"
    )

    def __init__(self, delay: float = 2.0, max_retries: int = 3, timeout: int = 30):
        self.delay = delay
        self.max_retries = max_retries
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": self.USER_AGENT})
        self._last_request: float = 0
        self.stats = {"requests": 0, "records": 0, "errors": 0}

    # ── HTTP Layer ──

    def _get(self, url: str) -> Optional[requests.Response]:
        """
        GET with polite delay, retry, and back-off.
        Returns None on permanent failure.
        """
        # Polite delay
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
                    wait = min(2 ** attempt, 30)
                    logger.warning("HTTP %d on %s — retry in %ds", resp.status_code, url, wait)
                    time.sleep(wait)
                    continue

                logger.warning("HTTP %d on %s", resp.status_code, url)
                return None

            except requests.Timeout:
                logger.warning("Timeout on %s (attempt %d/%d)", url, attempt, self.max_retries)
                time.sleep(2 ** attempt)
            except requests.RequestException as exc:
                logger.error("Request error: %s", exc)
                self.stats["errors"] += 1
                return None

        self.stats["errors"] += 1
        logger.error("Failed after %d retries: %s", self.max_retries, url)
        return None

    def _soup(self, url: str) -> Optional[BeautifulSoup]:
        """GET + parse to BeautifulSoup."""
        resp = self._get(url)
        if not resp:
            return None
        return BeautifulSoup(resp.text, "html.parser")

    # ══════════════════════════════════════════════════════════════════════
    #  1. INDIA CODE CRAWLER
    # ══════════════════════════════════════════════════════════════════════

    INDIA_CODE_BASE = "https://www.indiacode.nic.in"

    def crawl_india_code(self, act_ids: Optional[List[str]] = None) -> List[LegalRecord]:
        """
        Crawl central acts from India Code (indiacode.nic.in).

        If act_ids are provided, fetches only those acts.
        Otherwise fetches the public act listing and crawls each.

        Returns:
            List of enriched LegalRecord objects.
        """
        logger.info("Starting India Code crawl...")
        records: List[LegalRecord] = []

        if act_ids:
            for aid in act_ids:
                records.extend(self._india_code_crawl_act(aid))
        else:
            act_list = self._india_code_get_act_listing()
            logger.info("Found %d acts in India Code listing", len(act_list))
            for act_info in act_list:
                records.extend(self._india_code_crawl_act_page(act_info))

        records = [enrich_record(r) for r in records]
        self.stats["records"] += len(records)
        logger.info("India Code: extracted %d sections", len(records))
        return records

    def _india_code_get_act_listing(self) -> List[Dict]:
        """Fetch the act listing from India Code search or alphabetical page."""
        acts = []
        # India Code has an alphabetical listing
        url = f"{self.INDIA_CODE_BASE}/listing/repealedActChronologicalList"
        soup = self._soup(url)
        if not soup:
            return acts

        for row in soup.select("table tbody tr"):
            cells = row.find_all("td")
            if len(cells) >= 3:
                link = cells[1].find("a")
                if link and link.get("href"):
                    href = link["href"]
                    full_url = href if href.startswith("http") else self.INDIA_CODE_BASE + href
                    acts.append({
                        "name": link.get_text(strip=True),
                        "url": full_url,
                        "year": cells[0].get_text(strip=True),
                    })
        return acts

    def _india_code_crawl_act(self, act_id: str) -> List[LegalRecord]:
        """Crawl a specific act by its India Code internal ID."""
        url = f"{self.INDIA_CODE_BASE}/show-data?actid={act_id}&type=act"
        return self._india_code_parse_act_page(url, act_id)

    def _india_code_crawl_act_page(self, act_info: Dict) -> List[LegalRecord]:
        """Crawl an act from its listing page URL."""
        return self._india_code_parse_act_page(act_info["url"], act_info.get("name", ""))

    def _india_code_parse_act_page(self, url: str, fallback_name: str) -> List[LegalRecord]:
        """
        Parse an India Code act detail page.

        Strategy:
        - India Code renders sections inside tables or div containers.
        - Each row/block typically has: section number, marginal heading, text.
        - We try multiple CSS selectors to handle layout variations.
        """
        records: List[LegalRecord] = []
        soup = self._soup(url)
        if not soup:
            return records

        # Extract act name from heading
        heading = soup.find("h3") or soup.find("h2") or soup.find("title")
        act_name = heading.get_text(strip=True) if heading else fallback_name
        act_name = re.sub(r"\s+", " ", act_name).strip()

        # Try various section container selectors
        containers = (
            soup.select(".section-content")
            or soup.select("div.orderCont")
            or soup.select("table.table tbody tr")
            or soup.select("div.akn-section")
        )

        for container in containers:
            rec = self._india_code_extract_section(container, act_name, url)
            if rec:
                records.append(rec)

        return records

    def _india_code_extract_section(
        self, el: Tag, act_name: str, source_url: str
    ) -> Optional[LegalRecord]:
        """Extract one section from a page element."""
        # Section number
        num_el = (
            el.select_one(".section-number")
            or el.select_one("td:first-child")
            or el.find("b")
        )
        if not num_el:
            return None
        raw_num = num_el.get_text(strip=True)
        sec_num = clean_section_number(raw_num)
        if not sec_num:
            return None

        # Title / marginal heading
        heading_el = (
            el.select_one(".section-heading")
            or el.select_one("td:nth-child(2)")
            or el.find("strong")
        )
        title = heading_el.get_text(strip=True) if heading_el else f"Section {sec_num}"

        # Full section text
        text_el = el.select_one(".section-text") or el
        section_text = text_el.get_text(separator=" ", strip=True)
        # Remove section number and title from the body to avoid repetition
        section_text = section_text.replace(raw_num, "", 1).replace(title, "", 1).strip()
        if len(section_text) < 10:
            section_text = title

        return LegalRecord(
            act_name=act_name,
            section_number=sec_num,
            title=title,
            section_text=section_text,
            source_url=source_url,
            law_type="act",
            jurisdiction="central",
        )

    # ══════════════════════════════════════════════════════════════════════
    #  2. CONSTITUTION CRAWLER
    # ══════════════════════════════════════════════════════════════════════

    CONSTITUTION_URL = "https://www.india.gov.in/my-government/constitution-india/constitution-india-full-text"

    def crawl_constitution(self) -> List[LegalRecord]:
        """
        Crawl the Constitution of India — Articles, Amendments, Schedules.
        Source: india.gov.in
        """
        logger.info("Starting Constitution crawl...")
        records: List[LegalRecord] = []

        soup = self._soup(self.CONSTITUTION_URL)
        if soup:
            records.extend(self._constitution_parse_articles(soup, self.CONSTITUTION_URL))

        # Also try part-wise pages
        records.extend(self._constitution_crawl_parts())

        records = [enrich_record(r) for r in records]
        self.stats["records"] += len(records)
        logger.info("Constitution: extracted %d articles/provisions", len(records))
        return records

    def _constitution_parse_articles(self, soup: BeautifulSoup, source_url: str) -> List[LegalRecord]:
        """Split full-text Constitution page into individual articles."""
        records: List[LegalRecord] = []

        # Remove nav/header/footer noise
        for tag in soup.find_all(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        content = soup.select_one(".field-items") or soup.select_one("main") or soup.find("body")
        if not content:
            return records

        full_text = content.get_text(separator="\n")
        # Split on "Article NNN" boundaries
        chunks = re.split(r"(?=Article\s+\d+[A-Za-z]*\.?\s)", full_text, flags=re.I)

        article_re = re.compile(r"Article\s+(\d+[A-Za-z]*)", re.I)

        for chunk in chunks:
            m = article_re.search(chunk)
            if not m:
                continue
            art_num = m.group(1)
            lines = chunk.strip().split("\n")
            # First line contains article number + title
            title_line = lines[0] if lines else ""
            title = re.sub(r"Article\s+\d+[A-Za-z]*\.?\s*", "", title_line).strip(" .:-")
            if not title:
                title = f"Article {art_num}"
            body = "\n".join(lines[1:]).strip() if len(lines) > 1 else title
            if len(body) < 5:
                continue

            records.append(LegalRecord(
                act_name="Constitution of India",
                section_number=f"Article {art_num}",
                title=title,
                section_text=body[:8000],
                source_url=source_url,
                category="constitutional",
                law_type="article",
                jurisdiction="central",
            ))

        return records

    def _constitution_crawl_parts(self) -> List[LegalRecord]:
        """Crawl Constitution part-by-part from index page."""
        records: List[LegalRecord] = []
        base = "https://www.india.gov.in"
        index_url = f"{base}/my-government/constitution-india"
        soup = self._soup(index_url)
        if not soup:
            return records

        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            text = link.get_text(strip=True)
            if "part-" in href.lower() or re.search(r"Part\s+[IVXLC]+", text, re.I):
                full_url = href if href.startswith("http") else base + href
                part_soup = self._soup(full_url)
                if part_soup:
                    records.extend(self._constitution_parse_articles(part_soup, full_url))

        return records

    # ══════════════════════════════════════════════════════════════════════
    #  3. SUPREME COURT CRAWLER
    # ══════════════════════════════════════════════════════════════════════

    SCI_BASE = "https://main.sci.gov.in"

    def crawl_supreme_court(self) -> List[LegalRecord]:
        """
        Crawl recent Supreme Court of India judgments.
        Source: main.sci.gov.in
        """
        logger.info("Starting Supreme Court crawl...")
        records: List[LegalRecord] = []

        judgment_infos = self._sci_get_judgment_list()
        for info in judgment_infos:
            recs = self._sci_parse_judgment(info)
            records.extend(recs)

        records = [enrich_record(r) for r in records]
        self.stats["records"] += len(records)
        logger.info("Supreme Court: extracted %d judgment records", len(records))
        return records

    def _sci_get_judgment_list(self) -> List[Dict]:
        """Fetch judgment listing from SCI website."""
        judgments = []
        soup = self._soup(f"{self.SCI_BASE}/judgments")
        if not soup:
            return judgments

        for row in soup.select("table tbody tr, .judgment-item, .list-group-item"):
            link = row.find("a", href=True)
            if not link:
                continue
            href = link["href"]
            full_url = href if href.startswith("http") else self.SCI_BASE + href
            judgments.append({
                "url": full_url,
                "case_name": link.get_text(strip=True),
            })

        logger.info("SCI: found %d judgments in listing", len(judgments))
        return judgments

    def _sci_parse_judgment(self, info: Dict) -> List[LegalRecord]:
        """Parse a single judgment page."""
        records: List[LegalRecord] = []
        soup = self._soup(info["url"])
        if not soup:
            return records

        content_el = (
            soup.select_one(".judgment-content")
            or soup.select_one(".order-content")
            or soup.select_one("pre")
            or soup.select_one("main")
        )
        if not content_el:
            return records

        text = content_el.get_text(separator="\n", strip=True)
        case_name = info.get("case_name", "Unknown")

        records.append(LegalRecord(
            act_name=f"Supreme Court Judgment: {case_name[:200]}",
            section_number="Judgment",
            title=case_name[:500],
            section_text=text[:8000],
            source_url=info["url"],
            law_type="judgment",
            jurisdiction="central",
        ))
        return records

    # ══════════════════════════════════════════════════════════════════════
    #  4. HIGH COURT CRAWLER
    # ══════════════════════════════════════════════════════════════════════

    def crawl_high_courts(self, court: Optional[str] = None) -> List[LegalRecord]:
        """
        Crawl High Court judgment listings.

        Args:
            court: Specific court name (e.g. "Delhi"). None → all courts.
        """
        logger.info("Starting High Court crawl...")
        records: List[LegalRecord] = []

        portals = (
            {court: HIGH_COURT_PORTALS[court]} if court and court in HIGH_COURT_PORTALS
            else HIGH_COURT_PORTALS
        )

        for name, base_url in portals.items():
            records.extend(self._hc_crawl_court(name, base_url))

        records = [enrich_record(r) for r in records]
        self.stats["records"] += len(records)
        logger.info("High Courts: extracted %d records", len(records))
        return records

    def _hc_crawl_court(self, court_name: str, base_url: str) -> List[LegalRecord]:
        """Crawl a single High Court portal."""
        records: List[LegalRecord] = []
        for path in ["/judgments", "/judgment", "/orders", "/causelist"]:
            soup = self._soup(base_url + path)
            if not soup:
                continue
            for link in soup.find_all("a", href=True):
                text = link.get_text(strip=True)
                href = link["href"]
                if len(text) > 20 and re.search(r"judgment|order", href, re.I):
                    full_url = href if href.startswith("http") else base_url + "/" + href.lstrip("/")
                    records.append(LegalRecord(
                        act_name=f"{court_name} High Court Judgment",
                        section_number="Judgment",
                        title=text[:500],
                        section_text=text[:5000],
                        source_url=full_url,
                        law_type="judgment",
                        jurisdiction="state",
                        state_name=court_name,
                    ))
            break  # Stop after first successful path
        return records

    # ══════════════════════════════════════════════════════════════════════
    #  5. eGAZETTE CRAWLER
    # ══════════════════════════════════════════════════════════════════════

    GAZETTE_BASE = "https://egazette.gov.in"

    def crawl_gazette(self) -> List[LegalRecord]:
        """
        Crawl government gazette notifications from egazette.gov.in.
        Extracts recently published notifications, rules, and amendments.
        """
        logger.info("Starting eGazette crawl...")
        records: List[LegalRecord] = []

        soup = self._soup(f"{self.GAZETTE_BASE}/Search.aspx")
        if not soup:
            return records

        for row in soup.select("table tr, .gazette-item, .list-group-item"):
            link = row.find("a", href=True)
            text = row.get_text(separator=" ", strip=True)
            if len(text) < 20:
                continue
            title = link.get_text(strip=True) if link else text[:200]
            source_url = ""
            if link:
                href = link["href"]
                source_url = href if href.startswith("http") else f"{self.GAZETTE_BASE}/{href}"

            records.append(LegalRecord(
                act_name="Government Gazette Notification",
                section_number=f"Notification-{len(records)+1}",
                title=title[:500],
                section_text=text[:5000],
                source_url=source_url,
                law_type="notification",
                jurisdiction="central",
            ))

        records = [enrich_record(r) for r in records]
        self.stats["records"] += len(records)
        logger.info("eGazette: extracted %d notifications", len(records))
        return records

    # ══════════════════════════════════════════════════════════════════════
    #  6. STATE LAW CRAWLER
    # ══════════════════════════════════════════════════════════════════════

    def crawl_state_laws(self, state: Optional[str] = None) -> List[LegalRecord]:
        """
        Crawl state legislation from official state law department portals.

        Args:
            state: Specific state name. None → all known state portals.
        """
        logger.info("Starting State Law crawl...")
        records: List[LegalRecord] = []

        portals = (
            {state: STATE_LAW_PORTALS[state]} if state and state in STATE_LAW_PORTALS
            else STATE_LAW_PORTALS
        )

        for state_name, portal_url in portals.items():
            recs = self._state_crawl_portal(state_name, portal_url)
            records.extend(recs)

        records = [enrich_record(r) for r in records]
        self.stats["records"] += len(records)
        logger.info("State Laws: extracted %d records", len(records))
        return records

    def _state_crawl_portal(self, state_name: str, portal_url: str) -> List[LegalRecord]:
        """Crawl a single state's law department portal."""
        records: List[LegalRecord] = []
        soup = self._soup(portal_url)
        if not soup:
            return records

        for link in soup.find_all("a", href=True):
            text = link.get_text(strip=True)
            href = link["href"]
            if re.search(r"act|rule|regulation|ordinance", text, re.I) and len(text) > 10:
                full_url = href if href.startswith("http") else portal_url.rstrip("/") + "/" + href.lstrip("/")
                records.append(LegalRecord(
                    act_name=text[:500],
                    section_number="Full Act",
                    title=text[:500],
                    section_text=f"State legislation of {state_name}: {text}",
                    source_url=full_url,
                    law_type="act",
                    jurisdiction="state",
                    state_name=state_name,
                ))

        logger.info("State %s: %d records", state_name, len(records))
        return records

    # ══════════════════════════════════════════════════════════════════════
    #  7. LEGISLATIVE DEPARTMENT CRAWLER
    # ══════════════════════════════════════════════════════════════════════

    LEGISLATIVE_BASE = "https://legislative.gov.in"

    def crawl_legislative_dept(self) -> List[LegalRecord]:
        """
        Crawl the Legislative Department website.
        Source of bills, recently enacted acts, and ordinances.
        """
        logger.info("Starting Legislative Department crawl...")
        records: List[LegalRecord] = []

        for path in ["/bill-and-act", "/newly-enacted-laws", "/ordinances"]:
            soup = self._soup(self.LEGISLATIVE_BASE + path)
            if not soup:
                continue
            for link in soup.find_all("a", href=True):
                text = link.get_text(strip=True)
                href = link["href"]
                if len(text) > 15 and re.search(r"act|bill|ordinance", text, re.I):
                    full_url = href if href.startswith("http") else self.LEGISLATIVE_BASE + href
                    records.append(LegalRecord(
                        act_name=text[:500],
                        section_number="Full Text",
                        title=text[:500],
                        section_text=f"Legislative publication: {text}",
                        source_url=full_url,
                        law_type="act",
                        jurisdiction="central",
                    ))

        records = [enrich_record(r) for r in records]
        self.stats["records"] += len(records)
        logger.info("Legislative Dept: extracted %d records", len(records))
        return records

    # ══════════════════════════════════════════════════════════════════════
    #  MASTER CRAWL
    # ══════════════════════════════════════════════════════════════════════

    def crawl_all(self) -> List[LegalRecord]:
        """Run all crawlers and merge results."""
        logger.info("=" * 60)
        logger.info("  YAMA AI — Full Legal Data Crawl")
        logger.info("=" * 60)

        all_records: List[LegalRecord] = []
        sources = [
            ("India Code",           self.crawl_india_code),
            ("Constitution",         self.crawl_constitution),
            ("Supreme Court",        self.crawl_supreme_court),
            ("High Courts",          self.crawl_high_courts),
            ("eGazette",             self.crawl_gazette),
            ("State Laws",           self.crawl_state_laws),
            ("Legislative Dept",     self.crawl_legislative_dept),
        ]

        for name, func in sources:
            try:
                recs = func()
                all_records.extend(recs)
                logger.info("✅ %s: %d records", name, len(recs))
            except Exception as exc:
                logger.error("❌ %s failed: %s", name, exc)

        # Deduplicate by content hash
        all_records = self.deduplicate(all_records)

        logger.info("=" * 60)
        logger.info("  Total unique records: %d", len(all_records))
        logger.info("  HTTP requests: %d", self.stats["requests"])
        logger.info("  Errors: %d", self.stats["errors"])
        logger.info("=" * 60)
        return all_records

    # ══════════════════════════════════════════════════════════════════════
    #  DEDUPLICATION
    # ══════════════════════════════════════════════════════════════════════

    @staticmethod
    def deduplicate(records: List[LegalRecord]) -> List[LegalRecord]:
        """Remove duplicates by content hash; keep first occurrence."""
        seen = set()
        unique = []
        for r in records:
            if r.content_hash not in seen:
                seen.add(r.content_hash)
                unique.append(r)
        removed = len(records) - len(unique)
        if removed:
            logger.info("Dedup: removed %d duplicates", removed)
        return unique

    # ══════════════════════════════════════════════════════════════════════
    #  DATABASE STORAGE
    # ══════════════════════════════════════════════════════════════════════

    def store_records(self, records: List[LegalRecord], source_name: str = "crawler") -> Dict:
        """
        Persist crawled records into SQLite/PostgreSQL + ChromaDB.

        Uses content_hash to skip unchanged records (upsert semantics).

        Returns:
            Dict with inserted, updated, skipped, vector_indexed counts.
        """
        from app.db.database import SessionLocal, engine
        from app.db.models import Base, LawSection, IngestionLog
        from app.services.retrieval_engine.vector_store import get_vector_store

        Base.metadata.create_all(bind=engine)
        db = SessionLocal()

        stats = {"inserted": 0, "updated": 0, "skipped": 0, "vector_indexed": 0}

        # Create ingestion log entry
        log = IngestionLog(
            source_name=source_name, run_type="incremental",
            status="running", records_found=len(records),
        )
        db.add(log)
        db.commit()

        try:
            for rec in records:
                d = rec.to_dict()
                existing = (
                    db.query(LawSection)
                    .filter_by(act_name=d["act_name"], section_number=d["section_number"])
                    .first()
                )
                if existing:
                    if existing.content_hash == d["content_hash"]:
                        stats["skipped"] += 1
                        continue
                    # Update changed record
                    for col in ("title", "description", "keywords", "category",
                                "punishment", "old_law_reference", "jurisdiction",
                                "state_name", "law_type", "source_url", "content_hash"):
                        setattr(existing, col, d.get(col, getattr(existing, col)))
                    stats["updated"] += 1
                else:
                    row = LawSection(
                        act_name=d["act_name"],
                        section_number=d["section_number"],
                        title=d["title"],
                        description=d["description"],
                        keywords=d.get("keywords", ""),
                        category=d.get("category", "general"),
                        punishment=d.get("punishment"),
                        old_law_reference=d.get("old_law_reference"),
                        jurisdiction=d.get("jurisdiction", "central"),
                        state_name=d.get("state_name"),
                        law_type=d.get("law_type", "act"),
                        source_url=d.get("source_url"),
                        content_hash=d.get("content_hash"),
                        is_active=True,
                    )
                    db.add(row)
                    stats["inserted"] += 1

            db.commit()

            # Index into ChromaDB
            try:
                vs = get_vector_store()
                sections = db.query(LawSection).filter_by(is_active=True).all()
                batch = []
                for s in sections:
                    text = f"{s.act_name} — Section {s.section_number}: {s.title}\n\n{s.description}"
                    meta = {
                        "act_name": s.act_name or "",
                        "section_number": s.section_number or "",
                        "title": s.title or "",
                        "category": s.category or "general",
                        "jurisdiction": s.jurisdiction or "central",
                        "law_type": s.law_type or "act",
                    }
                    if s.state_name:
                        meta["state_name"] = s.state_name
                    if s.punishment:
                        meta["punishment"] = s.punishment[:200]
                    batch.append({"id": str(s.id), "text": text, "metadata": meta})

                # Batch upsert (50 at a time)
                for i in range(0, len(batch), 50):
                    vs.add_laws_batch(batch[i:i+50])
                stats["vector_indexed"] = len(batch)
            except Exception as exc:
                logger.warning("ChromaDB indexing skipped: %s", exc)

            # Update log
            log.status = "completed"
            log.records_inserted = stats["inserted"]
            log.records_updated = stats["updated"]
            log.records_skipped = stats["skipped"]
            log.completed_at = datetime.utcnow()
            db.commit()

        except Exception as exc:
            db.rollback()
            log.status = "failed"
            log.error_message = str(exc)[:2000]
            db.commit()
            raise
        finally:
            db.close()

        logger.info(
            "Storage: %d inserted, %d updated, %d skipped, %d vectorized",
            stats["inserted"], stats["updated"], stats["skipped"], stats["vector_indexed"],
        )
        return stats

    # ══════════════════════════════════════════════════════════════════════
    #  EXPORT
    # ══════════════════════════════════════════════════════════════════════

    @staticmethod
    def export_json(records: List[LegalRecord], filepath: str):
        """Export records to a JSON file."""
        data = {
            "metadata": {
                "exported_at": datetime.utcnow().isoformat(),
                "total_records": len(records),
                "source": "YAMA AI Legal Crawler",
            },
            "laws": [r.to_dict() for r in records],
        }
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("Exported %d records → %s", len(records), filepath)

    @staticmethod
    def export_csv(records: List[LegalRecord], filepath: str):
        """Export records to a CSV file."""
        if not records:
            return
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        rows = [r.to_dict() for r in records]
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        logger.info("Exported %d records → %s", len(records), filepath)

    # ══════════════════════════════════════════════════════════════════════
    #  CLEANUP
    # ══════════════════════════════════════════════════════════════════════

    def close(self):
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# ═══════════════════════════════════════════════════════════════════════════
#  CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

SOURCE_MAP = {
    "india_code":     "crawl_india_code",
    "constitution":   "crawl_constitution",
    "supreme_court":  "crawl_supreme_court",
    "high_courts":    "crawl_high_courts",
    "gazette":        "crawl_gazette",
    "state_laws":     "crawl_state_laws",
    "legislative":    "crawl_legislative_dept",
    "all":            "crawl_all",
}


def main():
    import argparse

    parser = argparse.ArgumentParser(
        prog="python -m data_pipeline.crawler",
        description="YAMA AI — Legal Data Crawler for Indian Government Sources",
    )
    parser.add_argument(
        "--source", type=str, default="all",
        choices=list(SOURCE_MAP.keys()),
        help="Data source to crawl",
    )
    parser.add_argument("--export", type=str, choices=["json", "csv"], help="Export format")
    parser.add_argument("--output", type=str, default="data_pipeline/output", help="Output directory")
    parser.add_argument("--store", action="store_true", default=True, help="Store into DB + ChromaDB")
    parser.add_argument("--no-store", action="store_true", help="Skip database storage")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between HTTP requests (seconds)")

    args = parser.parse_args()

    print()
    print("═" * 60)
    print("  YAMA AI — Legal Data Crawler")
    print("═" * 60)
    print(f"  Source:  {args.source}")
    print(f"  Delay:   {args.delay}s between requests")
    print(f"  Store:   {'yes' if not args.no_store else 'no'}")
    print(f"  Export:  {args.export or 'none'}")
    print("═" * 60)
    print()

    with LegalCrawler(delay=args.delay) as crawler:
        method = getattr(crawler, SOURCE_MAP[args.source])
        records = method()

        print(f"\n✅ Crawled {len(records)} records")
        print(f"   HTTP requests: {crawler.stats['requests']}")
        print(f"   Errors: {crawler.stats['errors']}")

        # Deduplicate
        records = crawler.deduplicate(records)
        print(f"   After dedup: {len(records)} unique records")

        # Store
        if not args.no_store:
            print("\n💾 Storing into database + ChromaDB...")
            stats = crawler.store_records(records, source_name=args.source)
            print(f"   Inserted:  {stats['inserted']}")
            print(f"   Updated:   {stats['updated']}")
            print(f"   Skipped:   {stats['skipped']}")
            print(f"   Vectorized: {stats['vector_indexed']}")

        # Export
        if args.export:
            os.makedirs(args.output, exist_ok=True)
            ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            if args.export == "json":
                path = os.path.join(args.output, f"crawl_{args.source}_{ts}.json")
                crawler.export_json(records, path)
                print(f"\n📄 Exported → {path}")
            elif args.export == "csv":
                path = os.path.join(args.output, f"crawl_{args.source}_{ts}.csv")
                crawler.export_csv(records, path)
                print(f"\n📄 Exported → {path}")

    print("\n✅ Done!")


if __name__ == "__main__":
    main()
