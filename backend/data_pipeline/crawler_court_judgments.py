"""
YAMA AI — Court Judgment Crawler
=============================================================================
Crawls Supreme Court and High Court judgments from official Indian judiciary
portals.

Primary Sources:
    • Supreme Court of India    — https://main.sci.gov.in
    • Delhi High Court          — https://delhihighcourt.nic.in
    • Bombay High Court         — https://bombayhighcourt.nic.in
    • Madras High Court         — https://www.mhc.tn.gov.in
    • Calcutta High Court       — https://calcuttahighcourt.gov.in
    • Karnataka High Court      — https://karnatakajudiciary.kar.nic.in
    • Allahabad High Court      — https://www.allahabadhighcourt.in
    • Kerala High Court         — https://highcourtofkerala.nic.in
    • eCourts Services          — https://services.ecourts.gov.in

Extracts per judgment:
    {
        "case_name":    "Maneka Gandhi v. Union of India",
        "court":        "Supreme Court of India",
        "date":         "1978-01-25",
        "legal_topic":  "constitutional, fundamental rights",
        "summary":      "The Supreme Court held that the right to life under...",
        "citation":     "AIR 1978 SC 597",
        "acts_cited":   ["Constitution of India, Article 21"],
        "source_url":   "https://main.sci.gov.in/..."
    }

Note on Playwright:
    Court websites often use JavaScript rendering. This module provides:
    - Static mode (requests + BeautifulSoup) for portals with static HTML
    - Dynamic mode (Playwright) for JavaScript-heavy portals
    Install Playwright: pip install playwright && playwright install chromium

Usage:
    python -m data_pipeline.crawler_court_judgments
    python -m data_pipeline.crawler_court_judgments --court supreme
    python -m data_pipeline.crawler_court_judgments --offline --export court_judgments.json
    python -m data_pipeline.crawler_court_judgments --dynamic  # uses Playwright
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
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
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
logger = logging.getLogger("yama_ai.crawler.court_judgments")


# ═══════════════════════════════════════════════════════════════════════════
#  DATA MODEL
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class JudgmentRecord:
    """
    One court judgment record.
    Stored in the laws table as law_type='judgment'.
    """
    # Primary judgment fields
    case_name: str = ""
    court: str = ""
    date: str = ""                  # ISO date: "1978-01-25"
    citation: str = ""              # "AIR 1978 SC 597"
    bench: str = ""                 # Judges who delivered judgment
    case_number: str = ""           # "Writ Petition 231 of 1977"

    # Legal analysis
    legal_topic: str = ""           # Comma-separated topics
    summary: str = ""               # Ratio decidendi / key holding
    acts_cited: List[str] = field(default_factory=list)
    sections_cited: List[str] = field(default_factory=list)
    legal_principles: List[str] = field(default_factory=list)

    # Metadata
    keywords: str = ""
    source_url: str = ""
    content_hash: str = ""
    last_updated: str = ""

    # Compatibility fields for the laws table
    act_name: str = ""              # Filled from case_name
    section_number: str = ""        # Filled from citation
    title: str = ""                 # Filled from case_name
    description: str = ""          # Filled from summary
    jurisdiction: str = "central"
    law_type: str = "judgment"

    def __post_init__(self):
        if not self.last_updated:
            self.last_updated = datetime.now(timezone.utc).isoformat()
        # Fill compatibility fields
        if not self.act_name:
            self.act_name = self.court or "Court Judgment"
        if not self.section_number:
            self.section_number = self.citation or self.case_number or self.date
        if not self.title:
            self.title = self.case_name
        if not self.description:
            self.description = self.summary
        if not self.content_hash:
            raw = f"{self.case_name}|{self.court}|{self.date}|{self.summary}"
            self.content_hash = hashlib.sha256(raw.encode()).hexdigest()

    def to_dict(self) -> Dict:
        d = asdict(self)
        return d


# ═══════════════════════════════════════════════════════════════════════════
#  COURT REGISTRY
# ═══════════════════════════════════════════════════════════════════════════

HIGH_COURTS: Dict[str, str] = {
    "Delhi":                "https://delhihighcourt.nic.in",
    "Bombay":               "https://bombayhighcourt.nic.in",
    "Madras":               "https://www.mhc.tn.gov.in",
    "Calcutta":             "https://calcuttahighcourt.gov.in",
    "Karnataka":            "https://karnatakajudiciary.kar.nic.in",
    "Allahabad":            "https://www.allahabadhighcourt.in",
    "Kerala":               "https://highcourtofkerala.nic.in",
    "Gujarat":              "https://gujarathighcourt.nic.in",
    "Punjab and Haryana":   "https://phhc.gov.in",
    "Telangana":            "https://tshc.gov.in",
    "Andhra Pradesh":       "https://hcap.nic.in",
    "Madhya Pradesh":       "https://mphc.gov.in",
    "Rajasthan":            "https://hcraj.nic.in",
    "Orissa":               "https://orissahighcourt.nic.in",
}

SCI_BASE = "https://main.sci.gov.in"
ECOURTS_BASE = "https://services.ecourts.gov.in"


# ═══════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════

_LEGAL_TOPICS: Dict[str, List[str]] = {
    "fundamental_rights": ["fundamental right", "article 21", "article 19", "article 14",
                           "article 32", "liberty", "equality", "life"],
    "criminal": ["bail", "arrest", "fir", "conviction", "acquittal", "murder", "rape",
                 "custodial death", "criminal", "ipc", "crpc", "bns", "bnss"],
    "constitutional": ["constitution", "article", "writ", "habeas corpus", "mandamus",
                       "certiorari", "quo warranto", "prohibition", "constitutional validity"],
    "civil": ["contract", "property", "suit", "damages", "decree", "execution",
              "injunction", "specific performance"],
    "family": ["marriage", "divorce", "maintenance", "custody", "adoption", "dowry"],
    "labour": ["employment", "worker", "service matter", "termination", "retrenchment",
               "provident fund", "gratuity"],
    "tax": ["income tax", "gst", "customs", "excise", "revenue", "tax evasion"],
    "corporate": ["company", "insolvency", "ibc", "nclt", "arbitration", "sebi"],
    "property": ["land", "title", "possession", "eviction", "tenancy", "mortgage"],
    "consumer": ["consumer", "deficiency", "service", "product liability"],
    "environment": ["environment", "pollution", "forest", "wildlife", "ngt"],
    "motor_vehicle": ["accident", "compensation", "motor vehicle", "motor accidents"],
}


def _classify_judgment(case_name: str, summary: str, acts: List[str]) -> str:
    combined = f"{case_name} {summary} {' '.join(acts)}".lower()
    best, top = "general", 0
    for topic, kws in _LEGAL_TOPICS.items():
        score = sum(1 for kw in kws if kw in combined)
        if score > top:
            best, top = topic, score
    return best


_STOP = frozenset({
    "the", "of", "and", "in", "to", "a", "is", "or", "for", "be", "an", "as",
    "by", "on", "at", "it", "that", "this", "with", "any", "shall", "may",
    "such", "which", "who", "not", "from", "under", "been", "has", "have",
    "his", "her", "its", "was", "were", "are", "being", "into", "than",
    "them", "then", "there", "court", "held", "case", "judgment", "appeal",
    "petitioner", "respondent", "plaintiff", "defendant", "vs", "versus",
    "hon", "honourable", "justice", "judge", "bench",
})


def _keywords(case_name: str, summary: str, limit: int = 12) -> str:
    combined = f"{case_name} {summary[:500]}".lower()
    words = re.findall(r"[a-z]{4,}", combined)
    freq: Dict[str, int] = {}
    for w in words:
        if w not in _STOP:
            freq[w] = freq.get(w, 0) + 1
    ranked = sorted(freq, key=lambda w: -freq[w])
    return ", ".join(ranked[:limit])


def _clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\u00a0", " ").replace("\u2019", "'")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_acts_cited(text: str) -> List[str]:
    """Extract acts/sections cited in a judgment text."""
    patterns = [
        r"((?:Indian Penal Code|IPC|Bharatiya Nyaya Sanhita|BNS|CrPC|BNSS|"
        r"Constitution of India|Article \d+[A-Z]?|Section \d+[A-Z]?|"
        r"(?:Information Technology|Consumer Protection|Motor Vehicles|"
        r"Evidence|Contract|Limitation|Arbitration) Act)[^,;\n]{0,50})",
    ]
    found = set()
    for p in patterns:
        for m in re.finditer(p, text, re.IGNORECASE):
            found.add(m.group(1).strip()[:150])
    return list(found)[:10]


def _extract_principles(text: str) -> List[str]:
    """Extract legal principles / holdings from judgment text."""
    patterns = [
        r"(?:held|observed|ruled|decided|opined)[:\s]+([^.]{30,200}\.)",
        r"(?:ratio decidendi|legal principle)[:\s]+([^.]{30,200}\.)",
        r"the (?:court|bench|tribunal) (?:held|observed)[:\s]+([^.]{30,200}\.)",
    ]
    principles = []
    for p in patterns:
        for m in re.finditer(p, text, re.IGNORECASE):
            principles.append(m.group(1).strip()[:300])
        if len(principles) >= 3:
            break
    return principles[:5]


# ═══════════════════════════════════════════════════════════════════════════
#  COURT JUDGMENT CRAWLER
# ═══════════════════════════════════════════════════════════════════════════

class CourtJudgmentCrawler:
    """
    Crawls court judgments from official Indian judiciary portals.

    Architecture:
        - Static mode: requests + BeautifulSoup (default)
        - Dynamic mode: Playwright for JS-rendered portals (optional)

    Strategy for Supreme Court:
        1. Fetch judgment listing from main.sci.gov.in/portal/
        2. Parse date-range result pages
        3. For each judgment: fetch full text, extract metadata

    Strategy for High Courts:
        1. Fetch judgment search page
        2. Parse results (each HC has unique HTML structure)
        3. Extract case name, date, bench, summary, acts cited

    Falls back to comprehensive seed data (landmark judgments) when
    live crawl fails.
    """

    USER_AGENT = (
        "YAMA-AI-LegalCrawler/1.0 "
        "(Educational Legal Research; court judgment indexing)"
    )

    def __init__(
        self,
        delay: float = 3.0,        # Slightly longer for court portals
        timeout: int = 45,
        max_retries: int = 3,
        use_playwright: bool = False,
    ):
        self.delay = delay
        self.timeout = timeout
        self.max_retries = max_retries
        self.use_playwright = use_playwright
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": self.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-IN,en;q=0.9",
        })
        self._last_request: float = 0
        self.stats = {"requests": 0, "records": 0, "errors": 0}
        self._playwright = None
        self._browser = None

    # ── HTTP ──────────────────────────────────────────────────────────────

    def _get(self, url: str) -> Optional[requests.Response]:
        elapsed = time.time() - self._last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)

        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self._session.get(
                    url, timeout=self.timeout,
                    allow_redirects=True,
                    verify=False,  # Some court portals use self-signed certs
                )
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
                logger.warning("Timeout attempt %d: %s", attempt, url)
                time.sleep(2 ** attempt)
            except Exception as exc:
                logger.error("Request error %s: %s", url, exc)
                self.stats["errors"] += 1
                return None

        self.stats["errors"] += 1
        return None

    def _soup(self, url: str) -> Optional[BeautifulSoup]:
        resp = self._get(url)
        return BeautifulSoup(resp.text, "html.parser") if resp else None

    # ── Playwright (Dynamic Pages) ─────────────────────────────────────────

    def _init_playwright(self):
        """Initialize Playwright browser for JS-rendered portals."""
        try:
            from playwright.sync_api import sync_playwright
            self._playwright_ctx = sync_playwright().__enter__()
            self._browser = self._playwright_ctx.chromium.launch(headless=True)
            logger.info("Playwright browser initialized")
        except ImportError:
            logger.warning(
                "Playwright not installed. Install with: pip install playwright && playwright install chromium\n"
                "Falling back to static crawl mode."
            )
            self.use_playwright = False

    def _get_dynamic(self, url: str) -> Optional[str]:
        """Fetch page HTML using Playwright for JS-rendered portals."""
        if not self._browser:
            self._init_playwright()
        if not self._browser:
            return None

        try:
            page = self._browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)
            time.sleep(2)  # Extra wait for dynamic content
            html = page.content()
            page.close()
            self.stats["requests"] += 1
            return html
        except Exception as exc:
            logger.error("Playwright error on %s: %s", url, exc)
            self.stats["errors"] += 1
            return None

    # ── Supreme Court ──────────────────────────────────────────────────────

    def crawl_supreme_court(
        self,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        max_judgments: int = 50,
    ) -> List[JudgmentRecord]:
        """
        Crawl Supreme Court judgments from main.sci.gov.in.

        Args:
            from_date:     Start date (DD-MM-YYYY). Default: 30 days ago.
            to_date:       End date (DD-MM-YYYY). Default: today.
            max_judgments: Maximum judgments to fetch (default: 50).

        Returns:
            List of JudgmentRecord objects.
        """
        logger.info("Crawling Supreme Court judgments...")
        records: List[JudgmentRecord] = []

        today = datetime.now()
        if not to_date:
            to_date = today.strftime("%d-%m-%Y")
        if not from_date:
            from_date = (today - timedelta(days=30)).strftime("%d-%m-%Y")

        # SCI judgment listing page
        listing_url = (
            f"{SCI_BASE}/portal/69.php?"
            f"frm_date={from_date}&to_date={to_date}&selparty=&selcourt=0"
        )

        html_source = None
        if self.use_playwright:
            html_source = self._get_dynamic(listing_url)
        if not html_source:
            resp = self._get(listing_url)
            if resp:
                html_source = resp.text

        if html_source:
            records.extend(self._parse_sci_listing(html_source, max_judgments))

        if not records:
            logger.info("SCI live crawl empty — trying alternate endpoint")
            # Try the public judgment search API
            alt_url = f"{SCI_BASE}/portal/liJudgments.php"
            resp = self._get(alt_url)
            if resp:
                records.extend(self._parse_sci_listing(resp.text, max_judgments))

        logger.info("Supreme Court: %d judgments extracted", len(records))
        return records

    def _parse_sci_listing(self, html: str, max_records: int) -> List[JudgmentRecord]:
        """Parse the SCI judgment listing page."""
        records: List[JudgmentRecord] = []
        soup = BeautifulSoup(html, "html.parser")

        # SCI typically renders a table with case info
        rows = (
            soup.select("table.result-table tr, table#resultTable tr")
            or soup.select("div.judgment-item")
            or soup.select("table tr")
        )

        for row in rows[:max_records]:
            cells = row.find_all("td")
            if len(cells) < 2:
                continue

            link = row.find("a", href=True)
            if not link:
                continue

            case_name = _clean(link.get_text())
            if len(case_name) < 5:
                continue

            href = link["href"]
            j_url = href if href.startswith("http") else SCI_BASE + href

            # Try to get more detail from judgment page
            rec = self._parse_judgment_page(j_url, case_name, "Supreme Court of India")
            if rec:
                records.append(rec)

        return records

    def _parse_judgment_page(
        self, url: str, case_name: str, court: str
    ) -> Optional[JudgmentRecord]:
        """Parse an individual judgment page."""
        soup = self._soup(url)
        if not soup:
            return None

        # Extract date
        date_el = soup.select_one(".judgment-date, .date, time, [class*='date']")
        date_str = ""
        if date_el:
            raw_date = _clean(date_el.get_text())
            date_str = _parse_date(raw_date)

        # Extract bench
        bench_el = soup.select_one(".bench, .judges, [class*='bench']")
        bench = _clean(bench_el.get_text())[:500] if bench_el else ""

        # Extract case number
        case_no_el = soup.select_one(".case-no, .case-number, [class*='case_no']")
        case_no = _clean(case_no_el.get_text())[:100] if case_no_el else ""

        # Extract full text
        content_el = (
            soup.select_one(".judgment-text, .content, article, main, .akn-doc")
            or soup.find("body")
        )
        full_text = _clean(content_el.get_text(separator=" "))[:20000] if content_el else ""

        if len(full_text) < 100:
            return None

        # Summary = first meaningful paragraph
        paragraphs = [p.strip() for p in full_text.split(".") if len(p.strip()) > 50]
        summary = ". ".join(paragraphs[:5]) if paragraphs else full_text[:1000]

        acts_cited = _extract_acts_cited(full_text)
        principles = _extract_principles(full_text)
        legal_topic = _classify_judgment(case_name, full_text[:2000], acts_cited)
        kw = _keywords(case_name, full_text)

        return JudgmentRecord(
            case_name=case_name,
            court=court,
            date=date_str,
            bench=bench,
            case_number=case_no,
            summary=summary[:3000],
            acts_cited=acts_cited,
            legal_principles=principles,
            legal_topic=legal_topic,
            keywords=kw,
            source_url=url,
        )

    # ── High Courts ────────────────────────────────────────────────────────

    def crawl_high_courts(
        self,
        courts: Optional[List[str]] = None,
        max_per_court: int = 20,
    ) -> List[JudgmentRecord]:
        """
        Crawl High Court judgments.

        Args:
            courts:        List of HC names (keys in HIGH_COURTS). None = all.
            max_per_court: Max judgments per High Court.

        Returns:
            List of JudgmentRecord objects.
        """
        target_courts = {k: v for k, v in HIGH_COURTS.items()
                         if not courts or k in courts}

        all_records: List[JudgmentRecord] = []

        for hc_name, hc_url in target_courts.items():
            logger.info("Crawling %s High Court: %s", hc_name, hc_url)
            records = self._crawl_high_court(hc_name, hc_url, max_per_court)
            logger.info("  %d judgments from %s HC", len(records), hc_name)
            all_records.extend(records)

        return all_records

    def _crawl_high_court(
        self, hc_name: str, hc_url: str, max_records: int
    ) -> List[JudgmentRecord]:
        """Crawl judgments from one High Court portal."""
        records: List[JudgmentRecord] = []

        # Common patterns for HC judgment listings
        search_paths = [
            "/judgments",
            "/judgment",
            "/dailyorders",
            "/judgment-search",
            "/cgi-bin/main.cgi",
        ]

        for path in search_paths:
            url = hc_url.rstrip("/") + path
            soup = self._soup(url)
            if not soup:
                continue

            # Look for judgment links
            judgment_links = self._find_judgment_links(soup, hc_url)
            if not judgment_links:
                continue

            court_name = f"{hc_name} High Court"
            for j_url, j_hint in judgment_links[:max_records]:
                rec = self._parse_judgment_page(j_url, j_hint, court_name)
                if rec:
                    records.append(rec)

            if records:
                break

        return records

    def _find_judgment_links(
        self, soup: BeautifulSoup, base_url: str
    ) -> List[Tuple[str, str]]:
        """Find judgment links on a court listing page."""
        base_domain = "/".join(base_url.split("/")[:3])
        links = []

        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = _clean(a.get_text())

            # Filter for judgment-like links
            if len(text) < 5:
                continue
            if not any(kw in href.lower() for kw in
                       ["judgment", "order", "judgment", "pdf", "file"]):
                if not any(kw in text.lower() for kw in
                           ["vs", "versus", "v.", "petition", "appeal"]):
                    continue

            full_url = href if href.startswith("http") else base_domain + href
            links.append((full_url, text[:300]))

        return links

    # ── Main Crawl ─────────────────────────────────────────────────────────

    def crawl(
        self,
        courts: Optional[List[str]] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        max_judgments: int = 100,
    ) -> List[JudgmentRecord]:
        """
        Full crawl of court judgments.

        Args:
            courts:        Subset of courts to crawl. None = all.
            from_date:     Start date for SC crawl.
            to_date:       End date for SC crawl.
            max_judgments: Total maximum records.

        Returns:
            List of JudgmentRecord objects.
        """
        if self.use_playwright:
            self._init_playwright()

        all_records: List[JudgmentRecord] = []

        # Supreme Court
        if not courts or "supreme" in [c.lower() for c in courts]:
            sc_records = self.crawl_supreme_court(from_date, to_date, max_judgments // 2)
            all_records.extend(sc_records)

        # High Courts
        hc_names = None
        if courts:
            hc_names = [c for c in courts if c.lower() != "supreme"]
        if hc_names is None or hc_names:
            hc_records = self.crawl_high_courts(hc_names, max_per_court=10)
            all_records.extend(hc_records)

        # Fallback to seed data
        if not all_records:
            logger.warning("Live crawl returned no judgments — using landmark seed data")
            all_records = self._get_seed_data()

        # Dedup
        seen: set = set()
        unique: List[JudgmentRecord] = []
        for r in all_records:
            if r.content_hash not in seen:
                seen.add(r.content_hash)
                unique.append(r)

        self.stats["records"] = len(unique)
        logger.info("Court judgment crawl complete: %d records", len(unique))
        return unique

    # ── Seed Data (Landmark Judgments) ─────────────────────────────────────

    def _get_seed_data(self) -> List[JudgmentRecord]:
        """
        Curated seed dataset of landmark Indian Supreme Court judgments.
        Covers the most important constitutional, criminal, and civil cases.
        """
        landmarks: List[Dict] = [
            {
                "case_name": "Maneka Gandhi v. Union of India",
                "court": "Supreme Court of India",
                "date": "1978-01-25",
                "citation": "AIR 1978 SC 597",
                "bench": "M.H. Beg CJ, Y.V. Chandrachud, V.R. Krishna Iyer, P.N. Bhagwati, N.L. Untwalia, S. Murtaza Fazal Ali, P.S. Kailasam JJ",
                "case_number": "Writ Petition 231 of 1977",
                "legal_topic": "fundamental_rights, constitutional",
                "summary": (
                    "The Supreme Court expanded the scope of Article 21 (right to life and personal liberty) "
                    "holding that 'procedure established by law' must be fair, just and reasonable and not "
                    "arbitrary or oppressive. The right to travel abroad is part of personal liberty under "
                    "Article 21. An order impounding Maneka Gandhi's passport without giving her an "
                    "opportunity to be heard violated Articles 14, 19 and 21. The Court established that "
                    "Articles 14, 19 and 21 are interlinked and must be read together — the golden triangle. "
                    "The Court overruled A.K. Gopalan v. State of Madras (1950) to the extent it held that "
                    "each Fundamental Right is a separate and independent right."
                ),
                "acts_cited": ["Constitution of India, Article 21", "Constitution of India, Article 14",
                               "Constitution of India, Article 19", "Passports Act, 1967"],
                "legal_principles": [
                    "Right to life includes right to live with human dignity",
                    "Procedure established by law must be fair, just and reasonable",
                    "Articles 14, 19 and 21 are interlinked and constitute a golden triangle",
                    "Passport authority must give reasonable opportunity before impounding passport",
                ],
            },
            {
                "case_name": "Kesavananda Bharati v. State of Kerala",
                "court": "Supreme Court of India",
                "date": "1973-04-24",
                "citation": "AIR 1973 SC 1461",
                "bench": "13-judge Constitution Bench",
                "case_number": "Writ Petition 135 of 1970",
                "legal_topic": "constitutional, fundamental_rights",
                "summary": (
                    "The Supreme Court in a 7-6 majority held that Parliament has the power to amend any "
                    "part of the Constitution including Fundamental Rights, but it cannot alter the 'basic "
                    "structure' of the Constitution. The basic structure doctrine was established — Parliament "
                    "cannot destroy the basic features of the Constitution through amendments. Elements of "
                    "basic structure include: supremacy of Constitution, republican and democratic form of "
                    "government, secular character, separation of powers, federal character. This judgment "
                    "effectively overruled Golak Nath v. State of Punjab (1967)."
                ),
                "acts_cited": ["Constitution of India, Article 368", "Kerala Land Reforms Act, 1963"],
                "legal_principles": [
                    "Parliament cannot alter the basic structure of the Constitution",
                    "Judicial review is part of the basic structure",
                    "Basic structure includes supremacy of Constitution, democracy, secularism, federalism",
                    "No amendment can destroy the Constitutional identity",
                ],
            },
            {
                "case_name": "Vishaka v. State of Rajasthan",
                "court": "Supreme Court of India",
                "date": "1997-08-13",
                "citation": "AIR 1997 SC 3011",
                "bench": "J.S. Verma CJ, Sujata V. Manohar, B.N. Kirpal JJ",
                "case_number": "Writ Petition 666 of 1992",
                "legal_topic": "fundamental_rights, labour",
                "summary": (
                    "The Supreme Court laid down guidelines (Vishaka Guidelines) for prevention of sexual "
                    "harassment at the workplace in the absence of enacted law. The Court held that sexual "
                    "harassment of working women amounts to violation of rights of gender equality and right "
                    "to life and liberty under Articles 14, 15 and 21. The guidelines included: employers "
                    "must prevent sexual harassment, set up complaints committee, and raise awareness. These "
                    "guidelines were given the force of law until Parliament enacted the Sexual Harassment "
                    "of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013."
                ),
                "acts_cited": ["Constitution of India, Article 14", "Constitution of India, Article 15",
                               "Constitution of India, Article 21", "Convention on Elimination of All Forms of Discrimination Against Women"],
                "legal_principles": [
                    "Sexual harassment at workplace violates fundamental rights",
                    "Employer has duty to prevent sexual harassment",
                    "Courts can issue guidelines having force of law when there is a legislative void",
                    "International conventions can be used to interpret fundamental rights",
                ],
            },
            {
                "case_name": "Shreya Singhal v. Union of India",
                "court": "Supreme Court of India",
                "date": "2015-03-24",
                "citation": "(2015) 5 SCC 1",
                "bench": "J. Chelameswar, Rohinton Fali Nariman JJ",
                "case_number": "Writ Petition 167 of 2012",
                "legal_topic": "fundamental_rights, cyber",
                "summary": (
                    "The Supreme Court struck down Section 66A of the Information Technology Act, 2000, "
                    "which punished sending 'grossly offensive' or 'menacing' messages online. The Court "
                    "held that Section 66A was unconstitutional as it violated the freedom of speech and "
                    "expression guaranteed under Article 19(1)(a). The expression 'grossly offensive' and "
                    "'menacing character' were vague and overbroad, creating a chilling effect on free speech. "
                    "The provision was not saved by Article 19(2) as it was not a reasonable restriction. "
                    "Section 79 read down: intermediaries not liable for third-party content unless they had "
                    "actual knowledge or had not acted expeditiously."
                ),
                "acts_cited": ["Information Technology Act, 2000, Section 66A",
                               "Constitution of India, Article 19", "Constitution of India, Article 19(2)"],
                "legal_principles": [
                    "Section 66A IT Act struck down for being unconstitutional",
                    "Vague laws that restrict free speech cannot be saved by Article 19(2)",
                    "Online speech has same protection as offline speech",
                    "Chilling effect on free speech renders law unconstitutional",
                ],
            },
            {
                "case_name": "D.K. Basu v. State of West Bengal",
                "court": "Supreme Court of India",
                "date": "1997-01-18",
                "citation": "AIR 1997 SC 610",
                "bench": "A.S. Anand, Kuldip Singh JJ",
                "case_number": "Writ Petition 539 of 1986",
                "legal_topic": "criminal, fundamental_rights",
                "summary": (
                    "The Supreme Court laid down guidelines to prevent custodial deaths and torture. The "
                    "Court held that custodial violence violates Article 21 (right to life). The guidelines "
                    "include: police must identify themselves in writing upon arrest; memo of arrest must be "
                    "prepared; arrestee must be informed of right to inform a relative; medical examination "
                    "at regular intervals; right to meet a lawyer; magistrate must be informed within 24 hours. "
                    "These guidelines were later incorporated into Section 41B of CrPC (now BNSS 2023). "
                    "Compensation must be paid to victims of custodial violence."
                ),
                "acts_cited": ["Constitution of India, Article 21", "Code of Criminal Procedure, 1973, Section 41",
                               "Constitution of India, Article 22"],
                "legal_principles": [
                    "Custodial torture violates Article 21",
                    "State is vicariously liable for acts of its officers",
                    "Arrested person must be produced before magistrate within 24 hours",
                    "Right to legal counsel must be communicated at time of arrest",
                ],
            },
            {
                "case_name": "Navtej Singh Johar v. Union of India",
                "court": "Supreme Court of India",
                "date": "2018-09-06",
                "citation": "(2018) 10 SCC 1",
                "bench": "Dipak Misra CJ, A.M. Khanwilkar, R.F. Nariman, D.Y. Chandrachud, Indu Malhotra JJ",
                "case_number": "Writ Petition 76 of 2016",
                "legal_topic": "fundamental_rights, constitutional",
                "summary": (
                    "The Supreme Court in a unanimous 5-judge Constitution Bench decriminalized consensual "
                    "same-sex relations between adults by reading down Section 377 of the Indian Penal Code. "
                    "The Court held that criminalizing consensual same-sex acts violates Articles 14, 15, 19 "
                    "and 21 of the Constitution. Sexual orientation is an essential attribute of identity. "
                    "LGBT persons have full constitutional rights. The Court overruled Suresh Kumar Koushal v. "
                    "Naz Foundation (2014). The right to privacy includes the right to sexual orientation."
                ),
                "acts_cited": ["Indian Penal Code, 1860, Section 377", "Constitution of India, Article 14",
                               "Constitution of India, Article 15", "Constitution of India, Article 21"],
                "legal_principles": [
                    "Section 377 IPC read down — consensual same-sex acts decriminalized",
                    "Sexual orientation is an essential attribute of identity protected under Article 21",
                    "Constitutional morality prevails over social morality",
                    "Right to privacy includes right to sexual orientation",
                ],
            },
            {
                "case_name": "Justice K.S. Puttaswamy v. Union of India",
                "court": "Supreme Court of India",
                "date": "2017-08-24",
                "citation": "(2017) 10 SCC 1",
                "bench": "9-judge Constitution Bench",
                "case_number": "Writ Petition 494 of 2012",
                "legal_topic": "fundamental_rights, constitutional",
                "summary": (
                    "A 9-judge Constitution Bench unanimously held that the right to privacy is a fundamental "
                    "right protected under Article 21 of the Constitution. Privacy is intrinsic to life and "
                    "liberty. The Bench overruled M.P. Sharma (1958) and Kharak Singh (1962) to the extent "
                    "they held otherwise. Privacy includes personal autonomy, bodily integrity, informational "
                    "privacy, and decisional autonomy. State can restrict privacy rights only on the touchstone "
                    "of legality, legitimate aim, and proportionality. The Aadhaar scheme was upheld partially "
                    "in a subsequent judgment."
                ),
                "acts_cited": ["Constitution of India, Article 21", "Constitution of India, Article 19"],
                "legal_principles": [
                    "Right to privacy is a fundamental right under Article 21",
                    "Privacy includes informational privacy, bodily integrity, and decisional autonomy",
                    "Any infringement of privacy must satisfy legality, legitimate aim, and proportionality",
                    "State surveillance must comply with Article 21 standards",
                ],
            },
            {
                "case_name": "M.C. Mehta v. Union of India (Oleum Gas Leak)",
                "court": "Supreme Court of India",
                "date": "1987-02-20",
                "citation": "AIR 1987 SC 1086",
                "bench": "P.N. Bhagwati CJ, Ranganath Misra, G.L. Oza, M.M. Dutt, K.N. Singh JJ",
                "case_number": "Writ Petition 12739 of 1985",
                "legal_topic": "environment, constitutional",
                "summary": (
                    "The Supreme Court evolved the principle of 'absolute liability' distinct from strict "
                    "liability in Rylands v. Fletcher. An enterprise engaged in a hazardous activity is "
                    "absolutely liable for harm resulting from such activity. No exceptions apply — an "
                    "enterprise cannot escape liability by showing the escape was due to an Act of God or "
                    "act of a stranger. The quantum of damages should be commensurate with the magnitude "
                    "and capacity of the enterprise. This case established the 'polluter pays' principle in "
                    "Indian law and formed the basis for environmental liability."
                ),
                "acts_cited": ["Constitution of India, Article 21", "Environment Protection Act, 1986"],
                "legal_principles": [
                    "Absolute liability for hazardous activities — no exceptions",
                    "Polluter pays principle established in Indian law",
                    "Enterprises must compensate all victims of hazardous industrial activity",
                    "Right to live in a clean environment is part of Article 21",
                ],
            },
            {
                "case_name": "Arnesh Kumar v. State of Bihar",
                "court": "Supreme Court of India",
                "date": "2014-07-02",
                "citation": "(2014) 8 SCC 273",
                "bench": "Chandramauli Kumar Prasad, Pinaki Chandra Ghose JJ",
                "case_number": "Criminal Appeal 1277 of 2014",
                "legal_topic": "criminal, fundamental_rights",
                "summary": (
                    "The Supreme Court issued guidelines to prevent arbitrary arrest in cases under Section "
                    "498A IPC (now Section 85 BNS) and the Dowry Prohibition Act. The Court held that "
                    "police must apply their mind and be satisfied that arrest is necessary before arresting "
                    "a person. A Magistrate shall not authorize detention unless police officer furnishes "
                    "reasons for arrest. The Court directed all State Governments to instruct Magistrates "
                    "not to authorize detention mechanically. The guidelines apply to all offences "
                    "punishable with imprisonment up to 7 years under Section 41 CrPC (now BNSS)."
                ),
                "acts_cited": ["Indian Penal Code, 1860, Section 498A",
                               "Code of Criminal Procedure, 1973, Section 41",
                               "Dowry Prohibition Act, 1961"],
                "legal_principles": [
                    "Arrest is not mandatory even for cognizable offences",
                    "Police must apply mind before effecting arrest",
                    "Section 41A CrPC notice must be served before arrest in 7-year offences",
                    "Magistrate must record reasons before authorizing detention",
                ],
            },
            {
                "case_name": "Indira Sawhney v. Union of India",
                "court": "Supreme Court of India",
                "date": "1992-11-16",
                "citation": "AIR 1993 SC 477",
                "bench": "9-judge Constitution Bench",
                "case_number": "Writ Petition 930 of 1990",
                "legal_topic": "constitutional, fundamental_rights",
                "summary": (
                    "The Supreme Court upheld the Mandal Commission's 27% reservation for Other Backward "
                    "Classes (OBCs) in central government jobs under Article 16(4). The Court held that "
                    "the 'creamy layer' among OBCs must be excluded from reservation benefits. The total "
                    "reservation cannot exceed 50% (the '50% ceiling rule'). Reservations in promotions "
                    "are not permitted. Backward classes under Article 16(4) need not be socially and "
                    "educationally backward — social backwardness alone suffices. Caste can be a determining "
                    "factor for backwardness."
                ),
                "acts_cited": ["Constitution of India, Article 16", "Constitution of India, Article 16(4)"],
                "legal_principles": [
                    "OBC reservation capped at 27% with creamy layer exclusion",
                    "Total reservation cannot exceed 50%",
                    "Reservations in promotions not permissible under Article 16(4)",
                    "Caste can be a determining factor for social backwardness",
                ],
            },
            {
                "case_name": "Olga Tellis v. Bombay Municipal Corporation",
                "court": "Supreme Court of India",
                "date": "1985-07-10",
                "citation": "AIR 1986 SC 180",
                "bench": "Y.V. Chandrachud CJ, V.D. Tulzapurkar, O. Chinnappa Reddy, V. Balakrishna Eradi, A. Varadarajan JJ",
                "case_number": "Writ Petition 4582 of 1985",
                "legal_topic": "fundamental_rights, civil",
                "summary": (
                    "The Supreme Court held that the right to livelihood is an intrinsic part of the right "
                    "to life under Article 21. Pavement dwellers have a right to their livelihood — "
                    "eviction from pavements without alternative shelter violates Article 21. The State "
                    "cannot evict the urban poor from their means of livelihood without providing "
                    "reasonable opportunity and alternative accommodation. The right to life includes the "
                    "right to live with basic human dignity. However, the eviction order was upheld with "
                    "directions to provide alternative sites."
                ),
                "acts_cited": ["Constitution of India, Article 21", "Bombay Municipal Corporation Act, 1888"],
                "legal_principles": [
                    "Right to livelihood is part of right to life under Article 21",
                    "Eviction of urban poor must comply with Article 21",
                    "State must provide reasonable opportunity before eviction",
                    "Right to life includes right to live with human dignity",
                ],
            },
            {
                "case_name": "Gian Kaur v. State of Punjab",
                "court": "Supreme Court of India",
                "date": "1996-03-21",
                "citation": "AIR 1996 SC 946",
                "bench": "J.S. Verma, G.N. Ray, N.P. Singh, Faizan Uddin, G.T. Nanavati JJ",
                "case_number": "Criminal Appeal 417 of 1994",
                "legal_topic": "criminal, fundamental_rights",
                "summary": (
                    "A 5-judge Constitution Bench upheld the validity of Section 309 IPC (attempt to commit "
                    "suicide) and Section 306 IPC (abetment of suicide). The Court held that the right to "
                    "die is not included in the right to life under Article 21 — the right to life does not "
                    "include the right to extinguish life. Overruling P. Rathinam v. Union of India, the "
                    "Court held that Article 21 cannot be interpreted to include the right to die. "
                    "However, the Court recognized 'passive euthanasia' in later cases."
                ),
                "acts_cited": ["Indian Penal Code, 1860, Section 306",
                               "Indian Penal Code, 1860, Section 309",
                               "Constitution of India, Article 21"],
                "legal_principles": [
                    "Right to life does not include right to die",
                    "Section 309 IPC (attempt to suicide) held constitutionally valid",
                    "Section 306 IPC (abetment of suicide) valid",
                    "Article 21 protects life, not its extinction",
                ],
            },
        ]

        records = []
        for j in landmarks:
            rec = JudgmentRecord(
                case_name=j["case_name"],
                court=j["court"],
                date=j["date"],
                citation=j.get("citation", ""),
                bench=j.get("bench", ""),
                case_number=j.get("case_number", ""),
                legal_topic=j.get("legal_topic", ""),
                summary=j["summary"],
                acts_cited=j.get("acts_cited", []),
                legal_principles=j.get("legal_principles", []),
                keywords=_keywords(j["case_name"], j["summary"]),
                source_url=SCI_BASE,
            )
            records.append(rec)

        return records

    # ── Export ─────────────────────────────────────────────────────────────

    def export_json(self, records: List[JudgmentRecord], path: str) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        data = {
            "metadata": {
                "title": "YAMA AI — Court Judgments Dataset",
                "total_records": len(records),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "source": "main.sci.gov.in / High Court portals",
            },
            "records": [r.to_dict() for r in records],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("Exported %d records → %s", len(records), path)


# ═══════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _parse_date(raw: str) -> str:
    """Try to parse a date string into ISO format YYYY-MM-DD."""
    formats = ["%d-%m-%Y", "%d/%m/%Y", "%B %d, %Y", "%d %B %Y",
               "%d %b %Y", "%Y-%m-%d", "%d.%m.%Y"]
    raw = raw.strip()
    for fmt in formats:
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            continue
    return raw[:10]


# Suppress insecure HTTPS warnings (many court portals use self-signed certs)
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    pass


# ═══════════════════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="YAMA AI — Court Judgment Crawler",
    )
    parser.add_argument("--court", nargs="*",
                        help="Courts to crawl: supreme, Delhi, Bombay, etc.")
    parser.add_argument("--from-date", help="Start date DD-MM-YYYY")
    parser.add_argument("--to-date", help="End date DD-MM-YYYY")
    parser.add_argument("--max", type=int, default=100, help="Max judgments to fetch")
    parser.add_argument("--export", metavar="FILE", default="", help="Export to JSON")
    parser.add_argument("--offline", action="store_true", help="Use seed data only")
    parser.add_argument("--dynamic", action="store_true", help="Use Playwright (JS rendering)")
    parser.add_argument("--delay", type=float, default=3.0, help="Request delay seconds")
    args = parser.parse_args()

    crawler = CourtJudgmentCrawler(
        delay=args.delay,
        use_playwright=args.dynamic,
    )

    if args.offline:
        records = crawler._get_seed_data()
        logger.info("Offline mode: %d landmark judgments", len(records))
    else:
        records = crawler.crawl(
            courts=args.court,
            from_date=args.from_date,
            to_date=args.to_date,
            max_judgments=args.max,
        )

    courts_covered = sorted({r.court for r in records})
    print(f"\n{'-'*60}")
    print(f"  Court judgment crawl complete")
    print(f"  Judgments extracted : {len(records)}")
    print(f"  Courts covered      : {len(courts_covered)}")
    for c in courts_covered:
        count = sum(1 for r in records if r.court == c)
        print(f"    {c}: {count}")
    print(f"  HTTP requests       : {crawler.stats['requests']}")
    print(f"  Errors              : {crawler.stats['errors']}")
    print(f"{'-'*60}\n")

    if args.export:
        crawler.export_json(records, args.export)

    return records


if __name__ == "__main__":
    main()
