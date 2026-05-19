"""
YAMA AI — Constitution of India Crawler
=============================================================================
Dedicated crawler for the Constitution of India from official government
sources. Structured as a standalone, runnable module.

Extracts:
    • Articles (1–395+) with full text
    • Constitutional Parts (I–XXII)
    • Schedules (First–Twelfth)
    • Constitutional Amendments (1st–106th)

Sources (official only):
    • https://www.india.gov.in  (full text)
    • https://legislative.gov.in (amendments and schedule)
    • https://indiacode.nic.in (Constitution as Central Act)

Output schema (each record):
    {
        "act_name":        "Constitution of India",
        "section_number":  "Article 21",
        "title":           "Protection of life and personal liberty",
        "description":     "No person shall be deprived of his life...",
        "keywords":        "life, liberty, due process, article 21",
        "jurisdiction":    "central",
        "state_name":      null,
        "source_url":      "https://...",
        "last_updated":    "2024-01-01T00:00:00"
    }

Usage:
    python -m data_pipeline.crawler_constitution
    python -m data_pipeline.crawler_constitution --export constitution.json
    python -m data_pipeline.crawler_constitution --export constitution.json --offline
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

# ── Ensure backend root is on sys.path ──
_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("yama_ai.crawler.constitution")


# ═══════════════════════════════════════════════════════════════════════════
#  DATA MODEL
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ConstitutionRecord:
    """
    One constitutional provision — article, schedule entry, or amendment.
    """
    act_name: str = "Constitution of India"
    section_number: str = ""        # "Article 21", "Schedule 1", "Amendment 44"
    title: str = ""                 # "Protection of life and personal liberty"
    description: str = ""          # Full provision text
    keywords: str = ""             # Auto-extracted
    jurisdiction: str = "central"
    state_name: Optional[str] = None
    law_type: str = "article"      # article / schedule / amendment
    part: str = ""                 # "Part III — Fundamental Rights"
    source_url: str = ""
    content_hash: str = ""
    last_updated: str = ""

    def __post_init__(self):
        if not self.last_updated:
            self.last_updated = datetime.now(timezone.utc).isoformat()
        if not self.content_hash:
            raw = f"{self.section_number}|{self.title}|{self.description}"
            self.content_hash = hashlib.sha256(raw.encode()).hexdigest()

    def to_dict(self) -> Dict:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════════════════
#  CONSTITUTIONAL METADATA
# ═══════════════════════════════════════════════════════════════════════════

CONSTITUTION_PARTS = {
    "I":     "The Union and Its Territory",
    "II":    "Citizenship",
    "III":   "Fundamental Rights",
    "IV":    "Directive Principles of State Policy",
    "IVA":   "Fundamental Duties",
    "V":     "The Union",
    "VI":    "The States",
    "VII":   "The States in Part B of the First Schedule",
    "VIII":  "The Union Territories",
    "IX":    "The Panchayats",
    "IXA":   "The Municipalities",
    "IXB":   "The Co-operative Societies",
    "X":     "The Scheduled and Tribal Areas",
    "XI":    "Relations Between the Union and the States",
    "XII":   "Finance, Property, Contracts and Suits",
    "XIII":  "Trade, Commerce and Intercourse Within India",
    "XIV":   "Services Under the Union and the States",
    "XIVA":  "Tribunals",
    "XV":    "Elections",
    "XVI":   "Special Provisions Relating to Certain Classes",
    "XVII":  "Official Language",
    "XVIII": "Emergency Provisions",
    "XIX":   "Miscellaneous",
    "XX":    "Amendment of the Constitution",
    "XXI":   "Temporary, Transitional and Special Provisions",
    "XXII":  "Short Title, Commencement, Authoritative Text in Hindi and Repeals",
}

ARTICLE_TO_PART: Dict[str, str] = {
    # Part I
    **{str(a): "I" for a in range(1, 5)},
    # Part II
    **{str(a): "II" for a in range(5, 12)},
    # Part III — Fundamental Rights (Articles 12–35)
    **{str(a): "III" for a in range(12, 36)},
    # Part IV — Directive Principles (36–51)
    **{str(a): "IV" for a in range(36, 52)},
    "51A": "IVA",
    # Part V — The Union (52–151)
    **{str(a): "V" for a in range(52, 152)},
    # Part VI — The States (152–237)
    **{str(a): "VI" for a in range(152, 238)},
    # Part VIII — Union Territories (239–242)
    **{str(a): "VIII" for a in range(239, 243)},
    # Part IX — Panchayats (243–243O)
    **{str(a): "IX" for a in range(243, 244)},
    # Part XI — Union-State Relations (245–263)
    **{str(a): "XI" for a in range(245, 264)},
    # Part XII — Finance (264–300A)
    **{str(a): "XII" for a in range(264, 302)},
    # Part XV — Elections (324–329A)
    **{str(a): "XV" for a in range(324, 330)},
    # Part XVIII — Emergency (352–360)
    **{str(a): "XVIII" for a in range(352, 361)},
    # Part XX — Amendment (368)
    "368": "XX",
}


def _get_part_for_article(article_num: str) -> Tuple[str, str]:
    """Return (part_roman, part_title) for a given article number."""
    # Strip alphabetic suffix for lookup
    base = re.sub(r"[A-Za-z]+$", "", article_num)
    roman = ARTICLE_TO_PART.get(article_num) or ARTICLE_TO_PART.get(base, "")
    title = CONSTITUTION_PARTS.get(roman, "")
    return roman, title


# ═══════════════════════════════════════════════════════════════════════════
#  KEYWORD EXTRACTOR
# ═══════════════════════════════════════════════════════════════════════════

_STOP = frozenset({
    "the", "of", "and", "in", "to", "a", "is", "or", "for", "be", "an",
    "as", "by", "on", "at", "it", "that", "this", "with", "any", "shall",
    "may", "such", "which", "who", "not", "from", "under", "been", "has",
    "have", "his", "her", "its", "was", "were", "are", "being", "into",
    "than", "them", "then", "there", "these", "they", "upon", "where",
    "whether", "whom", "will", "would", "every", "person", "article",
    "state", "union", "india", "provided", "right", "law",
})


def _extract_keywords(title: str, text: str, limit: int = 12) -> str:
    combined = f"{title} {text[:400]}".lower()
    words = re.findall(r"[a-z]{4,}", combined)
    seen: dict = {}
    for w in words:
        if w not in _STOP:
            seen[w] = seen.get(w, 0) + 1
    ranked = sorted(seen, key=lambda w: -seen[w])
    return ", ".join(ranked[:limit])


def _clean(text: str) -> str:
    """Strip HTML noise and normalize whitespace."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\u00a0", " ").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ═══════════════════════════════════════════════════════════════════════════
#  CONSTITUTION CRAWLER
# ═══════════════════════════════════════════════════════════════════════════

class ConstitutionCrawler:
    """
    Crawls the Constitution of India from official government portals.

    Strategy:
        1. Fetch full-text page from india.gov.in
        2. Split on "Article N" boundaries using regex
        3. For each article: extract number, title, body text
        4. Separately crawl Schedules and Amendments
        5. Fall back to embedded seed data when network is unavailable

    Respects rate limits with configurable delays.
    """

    INDIA_GOV_FULL_TEXT = (
        "https://www.india.gov.in/my-government/constitution-india"
        "/constitution-india-full-text"
    )
    INDIA_GOV_INDEX = "https://www.india.gov.in/my-government/constitution-india"
    LEGISLATIVE_CONSTITUTION = (
        "https://legislative.gov.in/constitution-of-india/"
    )
    INDIA_CODE_CONSTITUTION = (
        "https://www.indiacode.nic.in/handle/123456789/1353"
    )

    USER_AGENT = (
        "YAMA-AI-LegalCrawler/1.0 "
        "(Educational Legal Research; constitutional provisions)"
    )

    def __init__(self, delay: float = 2.0, timeout: int = 30, max_retries: int = 3):
        self.delay = delay
        self.timeout = timeout
        self.max_retries = max_retries
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": self.USER_AGENT})
        self._last_request: float = 0
        self.stats = {"requests": 0, "records": 0, "errors": 0}

    # ── HTTP ──────────────────────────────────────────────────────────────

    def _get(self, url: str) -> Optional[requests.Response]:
        """Polite GET with retry and exponential back-off."""
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
                    logger.warning("HTTP %d — retry in %ds: %s", resp.status_code, wait, url)
                    time.sleep(wait)
                    continue
                logger.warning("HTTP %d: %s", resp.status_code, url)
                return None

            except requests.Timeout:
                logger.warning("Timeout (attempt %d/%d): %s", attempt, self.max_retries, url)
                time.sleep(2 ** attempt)
            except requests.RequestException as exc:
                logger.error("Request error: %s", exc)
                self.stats["errors"] += 1
                return None

        self.stats["errors"] += 1
        return None

    def _soup(self, url: str) -> Optional[BeautifulSoup]:
        resp = self._get(url)
        if not resp:
            return None
        return BeautifulSoup(resp.text, "html.parser")

    # ── Article Parsing ───────────────────────────────────────────────────

    def _parse_full_text_page(self, html: str, source_url: str) -> List[ConstitutionRecord]:
        """
        Parse full-text Constitution HTML page into per-article records.
        Handles:
            "Article 21.—Protection of life..."
            "21. Protection of life..."
        """
        records: List[ConstitutionRecord] = []
        soup = BeautifulSoup(html, "html.parser")

        # Remove nav noise
        for tag in soup.find_all(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        content_el = (
            soup.select_one(".field-items")
            or soup.select_one("article")
            or soup.select_one("main")
            or soup.find("body")
        )
        if not content_el:
            return records

        full_text = content_el.get_text(separator="\n")
        full_text = _clean(full_text)

        # Split on article boundaries
        chunks = re.split(
            r"(?=\bArticle\s+\d+[A-Za-z]*\.?\s)",
            full_text,
            flags=re.IGNORECASE,
        )

        art_re = re.compile(r"Article\s+(\d+[A-Za-z]*)", re.IGNORECASE)

        for chunk in chunks:
            chunk = chunk.strip()
            m = art_re.match(chunk)
            if not m:
                continue
            art_num = m.group(1)

            # Strip the "Article N" prefix to get the rest
            rest = chunk[m.end():].lstrip(".—: \n")
            lines = [ln.strip() for ln in rest.split("\n") if ln.strip()]

            # First non-empty line is usually the title/heading
            title = lines[0] if lines else f"Article {art_num}"
            body = " ".join(lines[1:]) if len(lines) > 1 else title

            if len(body) < 10 and len(title) < 10:
                continue

            part_roman, part_title = _get_part_for_article(art_num)
            part_label = f"Part {part_roman} — {part_title}" if part_roman else ""

            rec = ConstitutionRecord(
                section_number=f"Article {art_num}",
                title=title[:500],
                description=body[:10000],
                keywords=_extract_keywords(title, body),
                law_type="article",
                part=part_label,
                source_url=source_url,
            )
            records.append(rec)

        return records

    # ── Schedule Parsing ──────────────────────────────────────────────────

    def _parse_schedules(self, html: str, source_url: str) -> List[ConstitutionRecord]:
        """Extract Schedules (First–Twelfth) from Constitution text."""
        records: List[ConstitutionRecord] = []
        soup = BeautifulSoup(html, "html.parser")
        full_text = soup.get_text(separator="\n")

        schedule_re = re.compile(
            r"(FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH|"
            r"ELEVENTH|TWELFTH)\s+SCHEDULE",
            re.IGNORECASE,
        )
        ordinal_map = {
            "first": "1", "second": "2", "third": "3", "fourth": "4",
            "fifth": "5", "sixth": "6", "seventh": "7", "eighth": "8",
            "ninth": "9", "tenth": "10", "eleventh": "11", "twelfth": "12",
        }

        chunks = schedule_re.split(full_text)
        matches = schedule_re.findall(full_text)

        for i, ordinal in enumerate(matches):
            if i + 1 < len(chunks):
                body = chunks[i + 1].strip()[:5000]
                num = ordinal_map.get(ordinal.lower(), ordinal)
                records.append(ConstitutionRecord(
                    section_number=f"Schedule {num}",
                    title=f"{ordinal.title()} Schedule",
                    description=body,
                    keywords=_extract_keywords(f"Schedule {ordinal}", body),
                    law_type="schedule",
                    source_url=source_url,
                ))

        return records

    # ── Amendment Parsing ─────────────────────────────────────────────────

    def _parse_amendments(self, html: str, source_url: str) -> List[ConstitutionRecord]:
        """
        Extract Constitutional Amendments.
        Amendment pages typically list: No., Year, Short Title, Act No.
        """
        records: List[ConstitutionRecord] = []
        soup = BeautifulSoup(html, "html.parser")

        # Look for a table of amendments
        for row in soup.select("table tr"):
            cells = row.find_all("td")
            if len(cells) < 3:
                continue
            raw_num = cells[0].get_text(strip=True)
            if not re.match(r"^\d+", raw_num):
                continue
            num = raw_num.strip(".")
            year = cells[1].get_text(strip=True) if len(cells) > 1 else ""
            title = cells[2].get_text(strip=True) if len(cells) > 2 else f"Amendment {num}"
            body = f"The {_ordinal(int(num))} Constitutional Amendment ({year}). {title}"
            records.append(ConstitutionRecord(
                section_number=f"Amendment {num}",
                title=title,
                description=body,
                keywords=_extract_keywords(title, body),
                law_type="amendment",
                source_url=source_url,
            ))

        return records

    # ── Main Crawl ────────────────────────────────────────────────────────

    def crawl(self) -> List[ConstitutionRecord]:
        """
        Full crawl of the Constitution of India.

        Returns:
            List of ConstitutionRecord objects (articles + schedules + amendments).
        """
        records: List[ConstitutionRecord] = []

        logger.info("Fetching Constitution full-text from india.gov.in...")
        resp = self._get(self.INDIA_GOV_FULL_TEXT)
        if resp:
            records.extend(self._parse_full_text_page(resp.text, self.INDIA_GOV_FULL_TEXT))
            records.extend(self._parse_schedules(resp.text, self.INDIA_GOV_FULL_TEXT))
        else:
            logger.warning("india.gov.in unavailable — trying legislative.gov.in")
            resp2 = self._get(self.LEGISLATIVE_CONSTITUTION)
            if resp2:
                records.extend(self._parse_full_text_page(resp2.text, self.LEGISLATIVE_CONSTITUTION))

        # Crawl index for part-by-part pages
        records.extend(self._crawl_parts())

        # Remove duplicates by section_number
        seen: set = set()
        unique: List[ConstitutionRecord] = []
        for r in records:
            if r.section_number not in seen and r.section_number:
                seen.add(r.section_number)
                unique.append(r)

        # If live crawl returned nothing, fall back to seed data
        if not unique:
            logger.warning("Live crawl returned no records — using embedded seed data")
            unique = self._get_seed_data()

        self.stats["records"] = len(unique)
        logger.info("Constitution crawl complete: %d records", len(unique))
        return unique

    def _crawl_parts(self) -> List[ConstitutionRecord]:
        """Crawl individual Part pages linked from the index page."""
        records: List[ConstitutionRecord] = []
        soup = self._soup(self.INDIA_GOV_INDEX)
        if not soup:
            return records

        for link in soup.find_all("a", href=True):
            href = link["href"]
            text = link.get_text(strip=True)
            if re.search(r"part[\-_/]", href, re.I) or re.search(r"Part\s+[IVXLC]+", text):
                full_url = href if href.startswith("http") else "https://www.india.gov.in" + href
                part_resp = self._get(full_url)
                if part_resp:
                    records.extend(self._parse_full_text_page(part_resp.text, full_url))

        return records

    # ── Seed Data (offline fallback) ──────────────────────────────────────

    def _get_seed_data(self) -> List[ConstitutionRecord]:
        """
        Curated seed data covering key articles. Used as fallback
        when official portals are unreachable (e.g., development / CI).
        """
        provisions = [
            ("Article 12",  "III",  "Definition of State",
             "In this Part, unless the context otherwise requires, 'the State' includes the "
             "Government and Parliament of India and the Government and the Legislature of each "
             "of the States and all local or other authorities within the territory of India or "
             "under the control of the Government of India."),
            ("Article 13",  "III",  "Laws inconsistent with or in derogation of the fundamental rights",
             "All laws in force in the territory of India immediately before the commencement of "
             "this Constitution, in so far as they are inconsistent with the provisions of this "
             "Part, shall, to the extent of such inconsistency, be void."),
            ("Article 14",  "III",  "Equality before law",
             "The State shall not deny to any person equality before the law or the equal "
             "protection of the laws within the territory of India."),
            ("Article 15",  "III",  "Prohibition of discrimination on grounds of religion, race, caste, sex or place of birth",
             "The State shall not discriminate against any citizen on grounds only of religion, "
             "race, caste, sex, place of birth or any of them."),
            ("Article 16",  "III",  "Equality of opportunity in matters of public employment",
             "There shall be equality of opportunity for all citizens in matters relating to "
             "employment or appointment to any office under the State."),
            ("Article 17",  "III",  "Abolition of Untouchability",
             "Untouchability is abolished and its practice in any form is forbidden. The "
             "enforcement of any disability arising out of Untouchability shall be an offence "
             "punishable in accordance with law."),
            ("Article 18",  "III",  "Abolition of titles",
             "No title, not being a military or academic distinction, shall be conferred by the State."),
            ("Article 19",  "III",  "Protection of certain rights regarding freedom of speech",
             "All citizens shall have the right to freedom of speech and expression; to assemble "
             "peaceably and without arms; to form associations or unions; to move freely throughout "
             "the territory of India; to reside and settle in any part of the territory of India; "
             "and to practise any profession, or to carry on any occupation, trade or business."),
            ("Article 20",  "III",  "Protection in respect of conviction for offences",
             "No person shall be convicted of any offence except for violation of a law in force "
             "at the time of the commission of the act charged as an offence, nor be subjected to "
             "a penalty greater than that which might have been inflicted under the law in force "
             "at the time of the commission of the offence."),
            ("Article 21",  "III",  "Protection of life and personal liberty",
             "No person shall be deprived of his life or personal liberty except according to "
             "procedure established by law."),
            ("Article 21A", "III",  "Right to Education",
             "The State shall provide free and compulsory education to all children of the age "
             "of six to fourteen years in such manner as the State may, by law, determine."),
            ("Article 22",  "III",  "Protection against arrest and detention in certain cases",
             "No person who is arrested shall be detained in custody without being informed, as "
             "soon as may be, of the grounds for such arrest nor shall he be denied the right to "
             "consult, and to be defended by, a legal practitioner of his choice."),
            ("Article 23",  "III",  "Prohibition of traffic in human beings and forced labour",
             "Traffic in human beings and begar and other similar forms of forced labour are "
             "prohibited and any contravention of this provision shall be an offence punishable "
             "in accordance with law."),
            ("Article 24",  "III",  "Prohibition of employment of children in factories",
             "No child below the age of fourteen years shall be employed to work in any factory "
             "or mine or engaged in any other hazardous employment."),
            ("Article 25",  "III",  "Freedom of conscience and free profession, practice and propagation of religion",
             "Subject to public order, morality and health and to the other provisions of this "
             "Part, all persons are equally entitled to freedom of conscience and the right freely "
             "to profess, practise and propagate religion."),
            ("Article 32",  "III",  "Remedies for enforcement of rights conferred by this Part",
             "The right to move the Supreme Court by appropriate proceedings for the enforcement "
             "of the rights conferred by this Part is guaranteed."),
            ("Article 37",  "IV",  "Application of the principles contained in this Part",
             "The provisions contained in this Part shall not be enforceable by any court, but "
             "the principles therein laid down are nevertheless fundamental in the governance of "
             "the country and it shall be the duty of the State to apply these principles in "
             "making laws."),
            ("Article 39A", "IV",  "Equal justice and free legal aid",
             "The State shall secure that the operation of the legal system promotes justice, on "
             "a basis of equal opportunity, and shall, in particular, provide free legal aid, by "
             "suitable legislation or schemes or in any other way, to ensure that opportunities "
             "for securing justice are not denied to any citizen by reason of economic or other "
             "disabilities."),
            ("Article 51A", "IVA", "Fundamental Duties",
             "It shall be the duty of every citizen of India to abide by the Constitution and "
             "respect its ideals and institutions, the National Flag and the National Anthem; to "
             "cherish and follow the noble ideals which inspired our national struggle for freedom; "
             "to uphold and protect the sovereignty, unity and integrity of India; to defend the "
             "country and render national service when called upon to do so."),
            ("Article 72",  "V",   "Power of President to grant pardons",
             "The President shall have the power to grant pardons, reprieves, respites or "
             "remissions of punishment or to suspend, remit or commute the sentence of any person "
             "convicted of any offence."),
            ("Article 124", "V",   "Establishment and constitution of Supreme Court",
             "There shall be a Supreme Court of India consisting of a Chief Justice of India and, "
             "until Parliament by law prescribes a larger number, of not more than thirty-three "
             "other Judges."),
            ("Article 136", "V",   "Special leave to appeal by the Supreme Court",
             "Notwithstanding anything in this Chapter, the Supreme Court may, in its discretion, "
             "grant special leave to appeal from any judgment, decree, determination, sentence or "
             "order in any cause or matter passed or made by any court or tribunal in the territory "
             "of India."),
            ("Article 141", "V",   "Law declared by Supreme Court to be binding on all courts",
             "The law declared by the Supreme Court shall be binding on all courts within the "
             "territory of India."),
            ("Article 142", "V",   "Enforcement of decrees and orders of Supreme Court",
             "The Supreme Court in the exercise of its jurisdiction may pass such decree or make "
             "such order as is necessary for doing complete justice in any cause or matter pending "
             "before it."),
            ("Article 226", "VI",  "Power of High Courts to issue certain writs",
             "Notwithstanding anything in article 32, every High Court shall have power, throughout "
             "the territories in relation to which it exercises jurisdiction, to issue to any person "
             "or authority, including in appropriate cases, any Government, within those territories "
             "directions, orders or writs, including writs in the nature of habeas corpus, mandamus, "
             "prohibition, quo warranto and certiorari."),
            ("Article 300A", "XII", "Persons not to be deprived of property save by authority of law",
             "No person shall be deprived of his property save by authority of law."),
            ("Article 324", "XV",  "Superintendence, direction and control of elections",
             "The superintendence, direction and control of the preparation of the electoral rolls "
             "for, and the conduct of, all elections to Parliament and to the Legislature of every "
             "State and of elections to the offices of President and Vice-President shall be vested "
             "in the Election Commission."),
            ("Article 352", "XVIII", "Proclamation of Emergency",
             "If the President is satisfied that a grave emergency exists whereby the security of "
             "India or of any part of the territory thereof is threatened, whether by war or "
             "external aggression or armed rebellion, he may, by Proclamation, make a declaration "
             "to that effect in respect of the whole of India or of such part of the territory "
             "thereof as may be specified in the Proclamation."),
            ("Article 356", "XVIII", "Provisions in case of failure of constitutional machinery in States",
             "If the President, on receipt of report from the Governor of the State or otherwise, "
             "is satisfied that the government of the State cannot be carried on in accordance with "
             "the provisions of this Constitution, the President may by Proclamation assume to "
             "himself all or any of the functions of the Government of the State."),
            ("Article 368", "XX",  "Power of Parliament to amend the Constitution and procedure therefor",
             "Notwithstanding anything in this Constitution, Parliament may in exercise of its "
             "constituent power amend by way of addition, variation or repeal any provision of "
             "this Constitution in accordance with the procedure laid down in this article."),
        ]

        records = []
        for art_num, part_roman, title, body in provisions:
            part_title = CONSTITUTION_PARTS.get(part_roman, "")
            part_label = f"Part {part_roman} — {part_title}" if part_roman else ""
            num = art_num.replace("Article ", "")
            records.append(ConstitutionRecord(
                section_number=art_num,
                title=title,
                description=body,
                keywords=_extract_keywords(title, body),
                law_type="article",
                part=part_label,
                source_url=self.INDIA_GOV_FULL_TEXT,
            ))

        # Add key Constitutional Amendments as records
        amendments = [
            ("1",  "1951", "First Amendment",
             "Added restrictions on freedom of speech and expression in Article 19, added the "
             "Ninth Schedule protecting certain land reform laws from judicial review."),
            ("42", "1976", "Forty-second Amendment (Mini-Constitution)",
             "Added 'socialist', 'secular', and 'integrity' to the Preamble. Added Fundamental "
             "Duties (Article 51A). Made Directive Principles supersede Fundamental Rights."),
            ("44", "1978", "Forty-fourth Amendment",
             "Removed the right to property from Fundamental Rights (Article 19(1)(f) deleted). "
             "Added Article 300A — property can only be taken by authority of law."),
            ("73", "1992", "Seventy-third Amendment — Panchayati Raj",
             "Added Part IX and the Eleventh Schedule to give constitutional status to Panchayati "
             "Raj institutions and provide for reservation of seats for SC/ST and women."),
            ("86", "2002", "Eighty-sixth Amendment — Right to Education",
             "Inserted Article 21A making education a fundamental right for children aged 6–14. "
             "Amended Article 45 and Article 51A(k) accordingly."),
            ("101", "2016", "Hundred and First Amendment — GST",
             "Introduced Goods and Services Tax (GST) replacing multiple indirect taxes. "
             "Amended Articles 246A, 269A, 279A and inserted the new GST Council."),
            ("103", "2019", "Hundred and Third Amendment — EWS Reservation",
             "Provided for 10% reservation in educational institutions and public employment "
             "for Economically Weaker Sections (EWS) not covered by existing reservations."),
            ("106", "2023", "Hundred and Sixth Amendment — Women's Reservation",
             "Reserved one-third of seats in the House of the People and State Assemblies "
             "for women (Articles 330A and 332A inserted)."),
        ]
        for num, year, title, body in amendments:
            records.append(ConstitutionRecord(
                section_number=f"Amendment {num}",
                title=f"{title} ({year})",
                description=body,
                keywords=_extract_keywords(title, body),
                law_type="amendment",
                source_url=self.INDIA_GOV_FULL_TEXT,
            ))

        return records

    # ── Export ────────────────────────────────────────────────────────────

    def export_json(self, records: List[ConstitutionRecord], path: str) -> None:
        """Write records to a JSON file."""
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        data = {
            "metadata": {
                "title": "YAMA AI — Constitution of India Dataset",
                "total_records": len(records),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "source": "india.gov.in / legislative.gov.in",
            },
            "records": [r.to_dict() for r in records],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("Exported %d records → %s", len(records), path)


# ═══════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _ordinal(n: int) -> str:
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10 if n % 100 not in (11, 12, 13) else 0, "th")
    return f"{n}{suffix}"


# ═══════════════════════════════════════════════════════════════════════════
#  CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="YAMA AI — Constitution of India Crawler",
    )
    parser.add_argument(
        "--export",
        metavar="FILE",
        default="",
        help="Export results to JSON file (e.g. constitution.json)",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Use embedded seed data only (no network requests)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Seconds between HTTP requests (default: 2.0)",
    )
    args = parser.parse_args()

    crawler = ConstitutionCrawler(delay=args.delay)

    if args.offline:
        records = crawler._get_seed_data()
        logger.info("Offline mode: loaded %d seed records", len(records))
    else:
        records = crawler.crawl()

    print(f"\n{'-'*60}")
    print(f"  Constitution crawl complete")
    print(f"  Records extracted : {len(records)}")
    print(f"  HTTP requests     : {crawler.stats['requests']}")
    print(f"  Errors            : {crawler.stats['errors']}")
    print(f"{'-'*60}\n")

    if args.export:
        crawler.export_json(records, args.export)

    return records


if __name__ == "__main__":
    main()
