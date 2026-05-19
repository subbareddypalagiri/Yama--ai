"""
YAMA AI — State Laws Crawler
=============================================================================
Crawls state legislation, rules, and notifications from official Indian state
government portals and the eGazette of India.

Covered Sources:
    • State legislative portals (law department websites)
    • eGazette of India (https://egazette.gov.in)
    • India Code state legislation section
    • State assembly / legislative assembly websites

State Portals Targeted:
    Maharashtra, Karnataka, Tamil Nadu, Kerala, Gujarat, Rajasthan,
    Uttar Pradesh, Delhi, West Bengal, Telangana, Punjab, Haryana,
    Andhra Pradesh, Madhya Pradesh, Bihar, Odisha

Extracts per provision:
    {
        "act_name":        "Maharashtra Rent Control Act, 1999",
        "section_number":  "7",
        "title":           "Standard rent",
        "description":     "The standard rent of any premises...",
        "keywords":        "rent, standard rent, premises, landlord",
        "jurisdiction":    "state",
        "state_name":      "Maharashtra",
        "source_url":      "https://...",
        "last_updated":    "2024-01-01T00:00:00+00:00"
    }

Usage:
    python -m data_pipeline.crawler_state_laws
    python -m data_pipeline.crawler_state_laws --states Maharashtra Karnataka
    python -m data_pipeline.crawler_state_laws --offline --export state_laws.json
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
logger = logging.getLogger("yama_ai.crawler.state_laws")


# ═══════════════════════════════════════════════════════════════════════════
#  DATA MODEL
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class StateLawRecord:
    """One provision from a State Act, Rule, or Notification."""
    act_name: str = ""
    section_number: str = ""
    title: str = ""
    description: str = ""
    keywords: str = ""
    jurisdiction: str = "state"
    state_name: str = ""
    law_type: str = "act"           # act / rule / notification / ordinance
    category: str = "general"
    source_url: str = ""
    content_hash: str = ""
    last_updated: str = ""

    def __post_init__(self):
        if not self.last_updated:
            self.last_updated = datetime.now(timezone.utc).isoformat()
        if not self.content_hash:
            raw = f"{self.state_name}|{self.act_name}|{self.section_number}|{self.description}"
            self.content_hash = hashlib.sha256(raw.encode()).hexdigest()

    def to_dict(self) -> Dict:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════════════════
#  STATE PORTAL REGISTRY
# ═══════════════════════════════════════════════════════════════════════════

STATE_PORTALS: Dict[str, Dict] = {
    "Maharashtra": {
        "law_dept": "https://bombayhighcourt.nic.in/stateacts.php",
        "legislature": "https://lj.maharashtra.gov.in",
        "gazette": "https://mahagov.maharashtra.gov.in",
    },
    "Karnataka": {
        "law_dept": "https://dpal.karnataka.gov.in",
        "legislature": "https://kla.kar.nic.in",
        "gazette": "https://dpal.karnataka.gov.in/publications",
    },
    "Tamil Nadu": {
        "law_dept": "https://www.tn.gov.in/laws",
        "legislature": "https://www.tnlegislature.gov.in",
        "gazette": "https://www.tn.gov.in/gazette",
    },
    "Kerala": {
        "law_dept": "https://www.kerala.gov.in/law-department",
        "legislature": "https://niyamasabha.org",
        "gazette": "https://www.kerala.gov.in/gazette",
    },
    "Gujarat": {
        "law_dept": "https://legal.gujarat.gov.in",
        "legislature": "https://gujaratassembly.gov.in",
        "gazette": "https://legal.gujarat.gov.in/gazette",
    },
    "Rajasthan": {
        "law_dept": "https://law.rajasthan.gov.in",
        "legislature": "https://rajassembly.nic.in",
        "gazette": "https://rajpatra.rajasthan.gov.in",
    },
    "Uttar Pradesh": {
        "law_dept": "https://updpadirector.up.nic.in",
        "legislature": "https://vidhanSabha.up.gov.in",
        "gazette": "https://upgazette.gov.in",
    },
    "Delhi": {
        "law_dept": "https://legislative.gov.in/state-legislation-delhi",
        "legislature": "https://delhiassembly.nic.in",
        "gazette": "https://delhi.gov.in/gazette",
    },
    "West Bengal": {
        "law_dept": "https://wbxpress.com/law-department",
        "legislature": "https://wbassembly.gov.in",
        "gazette": "https://wbxpress.com/gazette",
    },
    "Telangana": {
        "law_dept": "https://legislation.telangana.gov.in",
        "legislature": "https://tsassembly.gov.in",
        "gazette": "https://tggazette.cgg.gov.in",
    },
    "Andhra Pradesh": {
        "law_dept": "https://aplegislature.org",
        "legislature": "https://aplegislature.org",
        "gazette": "https://gazette.ap.gov.in",
    },
    "Madhya Pradesh": {
        "law_dept": "https://mplegisassembly.nic.in",
        "legislature": "https://mplegisassembly.nic.in",
        "gazette": "https://mpgazette.nic.in",
    },
    "Punjab": {
        "law_dept": "https://punjabassembly.nic.in",
        "legislature": "https://punjabassembly.nic.in",
        "gazette": "https://punjabgovt.gov.in/gazette",
    },
    "Haryana": {
        "law_dept": "https://legislative.nic.in/actsofparliament/haryana",
        "legislature": "https://haryana.gov.in",
        "gazette": "https://haryana.gov.in/gazette",
    },
}

# eGazette of India (central source for notifications)
EGAZETTE_BASE = "https://egazette.gov.in"
EGAZETTE_SEARCH = f"{EGAZETTE_BASE}/Search.aspx"


# ═══════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════

_CATEGORY_MAP: Dict[str, List[str]] = {
    "criminal": ["penal", "offence", "crime", "punishment", "ipc", "police", "bail"],
    "civil": ["civil", "contract", "suit", "property", "damages", "limitation"],
    "family": ["marriage", "divorce", "maintenance", "custody", "adoption", "dowry", "domestic"],
    "property": ["land", "land reform", "tenancy", "rent", "registration", "transfer", "leasehold", "mortgage"],
    "labour": ["labour", "labor", "worker", "employment", "wage", "factory", "shop", "establishment"],
    "municipal": ["municipality", "municipal", "panchayat", "local body", "village", "gram", "ward"],
    "education": ["education", "school", "university", "college", "student"],
    "tax": ["tax", "stamp duty", "registration fee", "value added tax", "state gst", "sgst"],
    "environment": ["pollution", "environment", "forest", "wildlife", "water", "sewage"],
    "consumer": ["consumer", "price control", "essential commodity", "public distribution"],
    "motor_vehicle": ["motor vehicle", "traffic", "road", "transport", "driving"],
}


def _classify(act_name: str, title: str, text: str) -> str:
    combined = f"{act_name} {title} {text[:400]}".lower()
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
    "state", "section", "act", "rule", "order", "provided", "government",
})


def _keywords(title: str, text: str, limit: int = 12) -> str:
    combined = f"{title} {text[:400]}".lower()
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


def _normalize_sec(raw: str) -> str:
    raw = re.sub(r"^(Section|Sec\.?|Rule|Regulation|Clause|Article)\s*", "", raw, flags=re.I)
    return raw.strip("()[]., ")


# ═══════════════════════════════════════════════════════════════════════════
#  STATE LAWS CRAWLER
# ═══════════════════════════════════════════════════════════════════════════

class StateLawsCrawler:
    """
    Crawls state legislation from official Indian state government portals.

    Strategy:
        1. For each target state, attempt its law department portal.
        2. Parse act listing → crawl individual act pages.
        3. Extract section number, title, and text.
        4. Also crawl eGazette for state-specific notifications/rules.
        5. Fall back to embedded seed data when portals are unreachable.

    Each state portal has different HTML structure — the crawler uses
    multiple selector strategies to handle layout variations.
    """

    USER_AGENT = "YAMA-AI-LegalCrawler/1.0 (Educational Legal Research)"

    def __init__(self, delay: float = 2.0, timeout: int = 30, max_retries: int = 3):
        self.delay = delay
        self.timeout = timeout
        self.max_retries = max_retries
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": self.USER_AGENT})
        self._last_request: float = 0
        self.stats = {"requests": 0, "records": 0, "errors": 0, "states_crawled": 0}

    # ── HTTP ──────────────────────────────────────────────────────────────

    def _get(self, url: str) -> Optional[requests.Response]:
        elapsed = time.time() - self._last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)

        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self._session.get(url, timeout=self.timeout, allow_redirects=True)
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
            except requests.RequestException as exc:
                logger.error("Request error %s: %s", url, exc)
                self.stats["errors"] += 1
                return None

        self.stats["errors"] += 1
        return None

    def _soup(self, url: str) -> Optional[BeautifulSoup]:
        resp = self._get(url)
        return BeautifulSoup(resp.text, "html.parser") if resp else None

    # ── State Portal Crawl ─────────────────────────────────────────────────

    def _crawl_state(self, state_name: str) -> List[StateLawRecord]:
        """Crawl all acts from a state's law department portal."""
        records: List[StateLawRecord] = []
        portals = STATE_PORTALS.get(state_name, {})

        for portal_type, url in portals.items():
            logger.info("  Trying %s portal: %s", portal_type, url)
            soup = self._soup(url)
            if not soup:
                continue

            # Find act links
            act_links = self._find_act_links(soup, url)
            logger.info("  Found %d act links on %s", len(act_links), url)

            for act_url, act_name_hint in act_links[:20]:  # cap per portal
                act_records = self._crawl_act_page(act_url, act_name_hint, state_name)
                records.extend(act_records)

            if records:
                break  # Stop after first successful portal

        return records

    def _find_act_links(self, soup: BeautifulSoup, base_url: str) -> List[Tuple[str, str]]:
        """Extract (url, name_hint) tuples from a portal listing page."""
        base_domain = "/".join(base_url.split("/")[:3])
        links: List[Tuple[str, str]] = []

        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)

            # Filter for act-like links
            if len(text) < 5 or len(text) > 300:
                continue
            if not any(kw in text.lower() for kw in ["act", "rule", "regulation", "law", "ordinance"]):
                continue

            full_url = href if href.startswith("http") else base_domain + ("" if href.startswith("/") else "/") + href
            if full_url.startswith("http"):
                links.append((full_url, text))

        return links

    def _crawl_act_page(self, url: str, act_name_hint: str, state_name: str) -> List[StateLawRecord]:
        """Parse an individual state act page and extract sections."""
        records: List[StateLawRecord] = []
        soup = self._soup(url)
        if not soup:
            return records

        # Resolve act name
        heading = soup.select_one("h1, h2, h3") or soup.find("title")
        act_name = _clean(heading.get_text()) if heading else act_name_hint
        if not act_name or len(act_name) < 5:
            act_name = act_name_hint

        # Parse sections
        # Strategy A: look for section divs / table rows
        section_blocks = (
            soup.select("div.section, div.section-content, div.provision")
            or soup.select("table tbody tr")
            or soup.select("li")
        )

        sec_re = re.compile(r"^(\d+[A-Za-z]?)\s*[\.\-\—]?\s+(.+)", re.MULTILINE)

        if not section_blocks:
            # Fallback: split full text on section boundaries
            full_text = _clean(soup.get_text(separator="\n"))
            for m in sec_re.finditer(full_text):
                sec_num = _normalize_sec(m.group(1))
                rest = m.group(2)[:5000]
                lines = [l.strip() for l in rest.split("\n") if l.strip()]
                title = lines[0][:300] if lines else f"Section {sec_num}"
                desc = " ".join(lines[1:])[:8000] if len(lines) > 1 else title

                records.append(StateLawRecord(
                    act_name=act_name,
                    section_number=sec_num,
                    title=title,
                    description=desc,
                    keywords=_keywords(title, desc),
                    state_name=state_name,
                    category=_classify(act_name, title, desc),
                    source_url=url,
                ))
        else:
            for el in section_blocks:
                cells = el.find_all("td") if el.name == "tr" else [el]
                if el.name == "tr" and len(cells) >= 2:
                    raw_num = cells[0].get_text(strip=True)
                    sec_num = _normalize_sec(raw_num)
                    title = _clean(cells[1].get_text()) if len(cells) > 1 else f"Section {sec_num}"
                    desc = _clean(cells[2].get_text()) if len(cells) > 2 else title
                else:
                    text = _clean(el.get_text(separator=" "))
                    m = re.match(r"(\d+[A-Za-z]?)[\.\-\—\s]+(.{5,300})", text)
                    if not m:
                        continue
                    sec_num = _normalize_sec(m.group(1))
                    title = m.group(2)[:300]
                    desc = text[m.end():][:8000] or title

                if sec_num and desc:
                    records.append(StateLawRecord(
                        act_name=act_name,
                        section_number=sec_num,
                        title=title,
                        description=desc,
                        keywords=_keywords(title, desc),
                        state_name=state_name,
                        category=_classify(act_name, title, desc),
                        source_url=url,
                    ))

        return records

    # ── eGazette Crawl ────────────────────────────────────────────────────

    def _crawl_egazette(self, state_name: Optional[str] = None) -> List[StateLawRecord]:
        """
        Crawl eGazette of India for state-specific notifications and rules.
        eGazette publishes GSR (General Statutory Rules) and SO (Statutory Orders).
        """
        records: List[StateLawRecord] = []
        params = "?type=state" if state_name else "?type=all"
        url = EGAZETTE_SEARCH + params

        soup = self._soup(url)
        if not soup:
            return records

        for row in soup.select("table tr, .gazette-item"):
            cells = row.find_all("td") if row.name == "tr" else [row]
            if len(cells) < 2:
                continue

            link = row.find("a", href=True)
            if not link:
                continue
            title = _clean(link.get_text())
            href = link["href"]
            full_url = href if href.startswith("http") else EGAZETTE_BASE + href

            # Extract metadata from table cells
            date_text = cells[-1].get_text(strip=True) if cells else ""
            department = cells[1].get_text(strip=True) if len(cells) > 1 else ""

            if len(title) < 10:
                continue

            records.append(StateLawRecord(
                act_name=title[:200],
                section_number="Notification",
                title=title[:500],
                description=f"{title}. Published on {date_text}. Department: {department}",
                keywords=_keywords(title, department),
                state_name=state_name or "Central",
                jurisdiction="state" if state_name else "central",
                law_type="notification",
                category=_classify(title, title, department),
                source_url=full_url,
            ))

        return records

    # ── Main Crawl ─────────────────────────────────────────────────────────

    def crawl(
        self,
        states: Optional[List[str]] = None,
        include_gazette: bool = True,
    ) -> List[StateLawRecord]:
        """
        Crawl state laws for specified states (or all configured states).

        Args:
            states:           List of state names. None = all configured states.
            include_gazette:  Also crawl eGazette for state notifications.

        Returns:
            List of StateLawRecord objects.
        """
        target_states = states or list(STATE_PORTALS.keys())
        all_records: List[StateLawRecord] = []

        for state in target_states:
            if state not in STATE_PORTALS:
                logger.warning("No portal configured for state: %s", state)
                continue

            logger.info("Crawling state: %s", state)
            records = self._crawl_state(state)

            if not records:
                logger.info("  No live records — using seed data for %s", state)
                records = [r for r in self._get_seed_data() if r.state_name == state]

            logger.info("  %d records for %s", len(records), state)
            all_records.extend(records)
            self.stats["states_crawled"] += 1

        if include_gazette:
            logger.info("Crawling eGazette for state notifications...")
            gazette_records = self._crawl_egazette()
            all_records.extend(gazette_records)

        # Fallback
        if not all_records:
            logger.warning("Live crawl returned nothing — using full seed dataset")
            all_records = self._get_seed_data()

        # Dedup
        seen: set = set()
        unique: List[StateLawRecord] = []
        for r in all_records:
            if r.content_hash not in seen:
                seen.add(r.content_hash)
                unique.append(r)

        self.stats["records"] = len(unique)
        logger.info("State laws crawl complete: %d records from %d states",
                    len(unique), self.stats["states_crawled"])
        return unique

    # ── Seed Data ─────────────────────────────────────────────────────────

    def _get_seed_data(self) -> List[StateLawRecord]:
        """
        Curated state law seed data covering major state acts.
        Used as offline fallback.
        """
        raw: List[Tuple] = [
            # ── Maharashtra ───────────────────────────────────────────────
            ("Maharashtra", "Maharashtra Rent Control Act, 1999", "7",
             "Standard rent",
             "The standard rent of any premises shall be the rent at which the premises were "
             "let on the 1st day of October 1987 or where the premises were not let on the "
             "said date, the rent at which they were last let before the said date; and where "
             "the premises were not let before the said date, the rent fixed by agreement "
             "between the landlord and tenant at the commencement of tenancy.",
             "property"),
            ("Maharashtra", "Maharashtra Shops and Establishments (Regulation of Employment and Conditions of Service) Act, 2017", "18",
             "Hours of work",
             "No employee shall be required or permitted to work in any establishment for more "
             "than nine hours in any day and forty-eight hours in any week. The employer shall "
             "not allow any employee to work for more than five hours consecutively without "
             "giving him a rest interval of at least half an hour.",
             "labour"),
            ("Maharashtra", "Maharashtra Prevention of Dangerous Activities Act, 1981", "3",
             "Power to detain persons",
             "The State Government may, if satisfied with respect to any person that with a "
             "view to preventing him from acting in any manner prejudicial to the maintenance "
             "of public order, it is necessary so to do, make an order directing that such "
             "person be detained.",
             "criminal"),
            ("Maharashtra", "Maharashtra Zamindar Abolition Act, 1950", "3",
             "Abolition of proprietary rights",
             "On and from the date of vesting, all rights, title and interests of the "
             "Zamindar in the estate and in the trees, standing crops, buildings, structures "
             "and other things attached to the land or permanently fastened to anything "
             "attached to the land, shall cease and be vested in the State Government.",
             "property"),

            # ── Karnataka ─────────────────────────────────────────────────
            ("Karnataka", "Karnataka Rent Act, 2001", "5",
             "Landlord cannot recover possession except on grounds",
             "No order or decree for the recovery of possession of any premises shall be "
             "made by any court in favour of the landlord against the tenant on any ground "
             "other than any of the grounds specified in section 27.",
             "property"),
            ("Karnataka", "Karnataka Shops and Commercial Establishments Act, 1961", "4",
             "Hours of work",
             "Subject to the provisions of this Act, no adult employee shall be required or "
             "permitted to work in any establishment for more than nine hours on any day and "
             "for more than forty-eight hours in any week.",
             "labour"),
            ("Karnataka", "Karnataka Land Reforms Act, 1961", "63",
             "Restriction on transfer",
             "Save as otherwise provided in this Act, no transfer of agricultural land held "
             "by a tenant shall be valid unless such transfer is made with the previous "
             "permission of the Deputy Commissioner.",
             "property"),
            ("Karnataka", "Karnataka Police Act, 1963", "29",
             "Powers of police to prevent commission of offences",
             "The police may take such measures as they deem fit to prevent the commission "
             "of any cognizable offence and for the maintenance of public order and tranquility "
             "in any area within their jurisdiction.",
             "criminal"),

            # ── Tamil Nadu ────────────────────────────────────────────────
            ("Tamil Nadu", "Tamil Nadu Shops and Establishments Act, 1947", "7",
             "Hours of work in establishments",
             "No person employed in an establishment shall be required or allowed to work "
             "therein for more than eight hours on any day and for more than forty-eight hours "
             "in any week: Provided that a person employed in an establishment may be required "
             "or allowed to work therein for more than eight hours in a day or forty-eight hours "
             "in a week if he is paid for the overtime work at twice the rate of his normal wages.",
             "labour"),
            ("Tamil Nadu", "Tamil Nadu Rent Control Act, 1960", "10",
             "Recovery of possession by landlord",
             "Notwithstanding anything contained in any law or contract, no order or decree "
             "for the recovery of possession of any building shall be made by any court in "
             "favour of the landlord against the tenant except on one or more of the following "
             "grounds, namely, that the tenant has not paid or tendered the rent due.",
             "property"),
            ("Tamil Nadu", "Tamil Nadu Anti-Social Activities (Prevention) Act, 2014", "3",
             "Power to detain persons",
             "The Government may, if satisfied with respect to any person that with a view to "
             "preventing him from acting in any manner prejudicial to the maintenance of public "
             "order or from smuggling or abetting the smuggling of any goods, it is necessary "
             "so to do, make an order directing that such person be detained.",
             "criminal"),

            # ── Kerala ────────────────────────────────────────────────────
            ("Kerala", "Kerala Buildings (Lease and Rent Control) Act, 1965", "11",
             "Eviction of tenants",
             "A landlord who seeks to recover possession of a building from the tenant shall "
             "apply to the Rent Control Court having jurisdiction over the area in which the "
             "building is situated and the Rent Control Court shall if it is satisfied that "
             "the claim of the landlord falls within any of the categories specified in "
             "sub-section (3), pass an order directing the tenant to put the landlord in "
             "possession of the building.",
             "property"),
            ("Kerala", "Kerala Police Act, 2011", "118",
             "Power to regulate traffic",
             "The District Police Chief may, by general or special order, regulate the "
             "movement of traffic in any public place. Such regulation may include prohibiting "
             "or restricting traffic or pedestrians and may be made to include public safety, "
             "health, convenience, free passage and the prevention of crime.",
             "motor_vehicle"),

            # ── Gujarat ───────────────────────────────────────────────────
            ("Gujarat", "Gujarat Tenancy and Agricultural Lands Act, 1948", "32",
             "Right of permanent tenure of tenant",
             "Every tenant in possession of land on or after the appointed day shall, subject "
             "to the provisions of this Act, be entitled to hold such land as a permanent "
             "tenant; and no landlord shall be entitled to recover possession of the land "
             "from such tenant.",
             "property"),
            ("Gujarat", "Gujarat Shops and Establishments (Regulation of Employment and Conditions of Service) Act, 2019", "16",
             "Restriction on working hours",
             "No employee shall be required or permitted to work in any establishment for more "
             "than nine hours in any day and forty-eight hours in any week. The State Government "
             "may, by notification, extend the hours of work in any establishment for specific "
             "occasions.",
             "labour"),

            # ── Uttar Pradesh ─────────────────────────────────────────────
            ("Uttar Pradesh", "Uttar Pradesh Zamindari Abolition and Land Reforms Act, 1950", "154",
             "Bhumidhari with non-transferable rights",
             "A person who is or is deemed to be a Bhumidhar with non-transferable rights, "
             "shall hold his holding subject to the condition that he shall not, so long as "
             "he holds such holding, transfer the same by sale, gift, mortgage with possession, "
             "exchange or otherwise.",
             "property"),
            ("Uttar Pradesh", "Uttar Pradesh Gangsters and Anti-Social Activities (Prevention) Act, 1986", "3",
             "Attachment of property",
             "Where the State Government is satisfied that a person is a gangster, it may "
             "direct the District Magistrate concerned to take steps for the attachment of "
             "the property, movable or immovable, acquired by such gangster from the proceeds "
             "of the gangster activities.",
             "criminal"),

            # ── Delhi ─────────────────────────────────────────────────────
            ("Delhi", "Delhi Rent Control Act, 1958", "14",
             "Protection of tenant against eviction",
             "Notwithstanding anything to the contrary contained in any other law or any "
             "contract, no order or decree for the recovery of possession of any premises "
             "shall be made by any court in favour of the landlord against a tenant except "
             "on one or more of the following grounds, namely, that the tenant has neither "
             "paid nor tendered the rent due.",
             "property"),
            ("Delhi", "Delhi Police Act, 1978", "34",
             "Power to issue prohibitory orders",
             "Whenever the Commissioner of Police considers it necessary so to do for the "
             "preservation of the public peace or public safety or for the prevention of "
             "riots or affrays, or for preventing obstruction to traffic, he may make an "
             "order in writing calling on any person or persons, or the public generally, "
             "to abstain from any act, or to take certain order with respect to certain "
             "matter or thing, for the period to be specified in the order.",
             "criminal"),

            # ── West Bengal ───────────────────────────────────────────────
            ("West Bengal", "West Bengal Premises Tenancy Act, 1997", "16",
             "Right of tenant to sub-let",
             "A tenant shall not sub-let the whole or any part of the premises let to him "
             "or transfer or assign his interest therein without the previous consent in "
             "writing of the landlord. The landlord shall not withhold his consent "
             "unreasonably.",
             "property"),
            ("West Bengal", "West Bengal Security of Land Tenure Act, 1955", "3",
             "Definition of bargadar",
             "In this Act, unless the context otherwise requires, 'bargadar' means a person "
             "who under the system generally known as adhi, barga or bhag cultivates the "
             "land of another person on condition of delivering a share of the produce of "
             "such land to that person.",
             "property"),

            # ── Telangana ─────────────────────────────────────────────────
            ("Telangana", "Telangana Shops and Establishments Act, 1988", "4",
             "Registration of establishment",
             "Every employer shall, before or within thirty days of the establishment "
             "becoming operative or coming into existence, as the case may be, make an "
             "application to the Inspector having jurisdiction for the registration of "
             "his establishment.",
             "labour"),
            ("Telangana", "Telangana Prohibition Act, 1994", "3",
             "Prohibition of import, etc. of intoxicating liquor",
             "No person shall import, export, transport, manufacture, sell, buy, possess, "
             "use or consume any intoxicating liquor or hemp in the State of Telangana "
             "except under and in conformity with the conditions of a licence, permit, pass "
             "or authorization granted under this Act.",
             "criminal"),

            # ── Rajasthan ─────────────────────────────────────────────────
            ("Rajasthan", "Rajasthan Tenancy Act, 1955", "42",
             "Rights of Khatedar tenant",
             "Subject to the provisions of this Act, a Khatedar tenant shall have a heritable "
             "and transferable right of occupancy in the land held by him and shall be entitled "
             "to use the land for any purpose other than non-agricultural purpose.",
             "property"),
        ]

        records = []
        for item in raw:
            state, act_name, sec_num, title, desc, category = item
            records.append(StateLawRecord(
                act_name=act_name,
                section_number=sec_num,
                title=title,
                description=desc,
                keywords=_keywords(title, desc),
                state_name=state,
                category=category,
                source_url=STATE_PORTALS.get(state, {}).get("law_dept", ""),
            ))

        return records

    # ── Export ─────────────────────────────────────────────────────────────

    def export_json(self, records: List[StateLawRecord], path: str) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        data = {
            "metadata": {
                "title": "YAMA AI — State Laws Dataset",
                "total_records": len(records),
                "states": sorted({r.state_name for r in records}),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "source": "State Law Department Portals / eGazette",
            },
            "records": [r.to_dict() for r in records],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("Exported %d records → %s", len(records), path)


# ═══════════════════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="YAMA AI — State Laws Crawler",
    )
    parser.add_argument("--states", nargs="*", help="States to crawl (e.g. Maharashtra Karnataka)")
    parser.add_argument("--export", metavar="FILE", default="", help="Export to JSON file")
    parser.add_argument("--offline", action="store_true", help="Use seed data only")
    parser.add_argument("--no-gazette", action="store_true", help="Skip eGazette crawl")
    parser.add_argument("--delay", type=float, default=2.0, help="Request delay seconds")
    args = parser.parse_args()

    crawler = StateLawsCrawler(delay=args.delay)

    if args.offline:
        records = crawler._get_seed_data()
        if args.states:
            states_lower = [s.lower() for s in args.states]
            records = [r for r in records if r.state_name.lower() in states_lower]
        logger.info("Offline mode: %d seed records", len(records))
    else:
        records = crawler.crawl(
            states=args.states,
            include_gazette=not args.no_gazette,
        )

    states_summary = sorted({r.state_name for r in records})
    print(f"\n{'-'*60}")
    print(f"  State laws crawl complete")
    print(f"  Records extracted : {len(records)}")
    print(f"  States covered    : {len(states_summary)}")
    print(f"  States            : {', '.join(states_summary)}")
    print(f"  HTTP requests     : {crawler.stats['requests']}")
    print(f"  Errors            : {crawler.stats['errors']}")
    print(f"{'-'*60}\n")

    if args.export:
        crawler.export_json(records, args.export)

    return records


if __name__ == "__main__":
    main()
