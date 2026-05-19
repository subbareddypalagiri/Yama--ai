"""
YAMA AI — eGazette & State Law Crawler
Crawls government gazette notifications and state legislation.

Sources:
    - eGazette of India: https://egazette.gov.in
    - State legislative assembly websites
    - State law department portals

Extracts: Notifications, rules, state acts, and ordinances.
"""

import re
import logging
from typing import List, Optional
from bs4 import BeautifulSoup

from ingestion.crawlers.base_crawler import BaseCrawler, LegalRecord
from ingestion.config import INDIAN_STATES, CATEGORY_KEYWORDS

logger = logging.getLogger("yama_ai.ingestion.gazette")

# State law department portals (official sources)
STATE_LAW_PORTALS = {
    "Maharashtra": "https://bombayhighcourt.nic.in/stateacts.php",
    "Karnataka": "https://dpal.karnataka.gov.in",
    "Tamil Nadu": "https://www.tn.gov.in/laws",
    "Kerala": "https://www.keralalegislature.org",
    "Gujarat": "https://legal.gujarat.gov.in",
    "Rajasthan": "https://law.rajasthan.gov.in",
    "Uttar Pradesh": "https://updpadirector.up.nic.in",
    "Delhi": "https://legislative.gov.in/state-legislation-delhi",
    "West Bengal": "https://wbgov.org",
    "Telangana": "https://legislation.telangana.gov.in",
}


class GazetteCrawler(BaseCrawler):
    """
    Crawler for the eGazette of India.
    Government gazette publishes notifications, rules, and amendments.
    """

    BASE_URL = "https://egazette.gov.in"

    @property
    def source_name(self) -> str:
        return "gazette"

    def crawl(self, gazette_type: str = "all") -> List[LegalRecord]:
        """
        Crawl gazette notifications.

        Args:
            gazette_type: "extraordinary", "ordinary", or "all"
        """
        records: List[LegalRecord] = []

        # Gazette homepage lists recent publications
        url = f"{self.BASE_URL}/Search.aspx"
        resp = self.fetch(url)

        if resp:
            records.extend(self._parse_gazette_listing(resp.text))

        self.stats["records_extracted"] = len(records)
        logger.info(f"[{self.source_name}] Extracted {len(records)} gazette notifications")
        return records

    def _parse_gazette_listing(self, html: str) -> List[LegalRecord]:
        """Parse gazette search results page."""
        records: List[LegalRecord] = []
        soup = BeautifulSoup(html, "html.parser")

        for row in soup.select("table tr, .gazette-item, .list-group-item"):
            cells = row.find_all("td") if row.name == "tr" else [row]
            if len(cells) < 2:
                continue

            link = row.find("a", href=True)
            text = row.get_text(separator=" ", strip=True)

            if len(text) < 20:
                continue

            # Extract notification details
            title = link.get_text(strip=True) if link else text[:200]
            source_url = ""
            if link:
                href = link.get("href", "")
                source_url = href if href.startswith("http") else self.BASE_URL + "/" + href

            records.append(LegalRecord(
                act_name="Government Gazette Notification",
                section_number=f"Notification-{len(records)+1}",
                title=title[:500],
                description=text[:5000],
                keywords=self._extract_keywords(title),
                category=self._classify_notification(text),
                jurisdiction="central",
                law_type="notification",
                source_url=source_url,
            ))

        return records

    @staticmethod
    def _classify_notification(text: str) -> str:
        text_lower = text.lower()
        for category, kws in CATEGORY_KEYWORDS.items():
            if any(kw in text_lower for kw in kws):
                return category
        return "general"

    @staticmethod
    def _extract_keywords(title: str) -> str:
        stop_words = {"the", "of", "and", "in", "to", "a", "is", "or", "for"}
        words = re.findall(r"[a-z]{3,}", title.lower())
        return ", ".join([w for w in dict.fromkeys(words) if w not in stop_words][:10])


class StateLawCrawler(BaseCrawler):
    """
    Crawler for state legislation.
    Each state has its own law department portal.
    """

    @property
    def source_name(self) -> str:
        return "state_laws"

    def crawl(self, state: Optional[str] = None) -> List[LegalRecord]:
        """
        Crawl state legislation.

        Args:
            state: Specific state name. If None, crawls all known portals.
        """
        records: List[LegalRecord] = []

        portals = {state: STATE_LAW_PORTALS[state]} if state and state in STATE_LAW_PORTALS else STATE_LAW_PORTALS

        for state_name, portal_url in portals.items():
            state_records = self._crawl_state_portal(state_name, portal_url)
            records.extend(state_records)

        self.stats["records_extracted"] = len(records)
        logger.info(f"[{self.source_name}] Extracted {len(records)} state law records")
        return records

    def _crawl_state_portal(self, state_name: str, portal_url: str) -> List[LegalRecord]:
        """Crawl a single state's law department portal."""
        records: List[LegalRecord] = []

        resp = self.fetch(portal_url)
        if not resp:
            logger.warning(f"[{self.source_name}] Cannot reach {state_name} portal: {portal_url}")
            return records

        soup = BeautifulSoup(resp.text, "html.parser")

        # Look for links to individual acts
        for link in soup.find_all("a", href=True):
            text = link.get_text(strip=True)
            href = link.get("href", "")

            # Match links that look like act names
            if re.search(r"act|rule|regulation|ordinance", text, re.IGNORECASE) and len(text) > 10:
                full_url = href if href.startswith("http") else portal_url.rstrip("/") + "/" + href.lstrip("/")

                records.append(LegalRecord(
                    act_name=text[:500],
                    section_number="Full Act",
                    title=text[:500],
                    description=f"State legislation of {state_name}: {text}",
                    keywords=f"{state_name.lower()}, state law, {text[:50].lower()}",
                    category="general",
                    jurisdiction="state",
                    state_name=state_name,
                    law_type="act",
                    source_url=full_url,
                ))

        logger.info(f"[{self.source_name}] {state_name}: {len(records)} entries found")
        return records
