"""
YAMA AI — India Code Crawler
Crawls https://www.indiacode.nic.in for central legislation.

India Code is the official digital repository maintained by the Legislative Department.
It contains all Central Acts (current and repealed), their sections, amendments, and metadata.

Strategy:
    1. Fetch the act listing or search results page.
    2. For each act, navigate to its sections index.
    3. Extract section number, title, and text.
    4. Tag with category, keywords, and jurisdiction.
"""

import re
import logging
from typing import List, Optional
from bs4 import BeautifulSoup

from ingestion.crawlers.base_crawler import BaseCrawler, LegalRecord
from ingestion.config import CATEGORY_KEYWORDS

logger = logging.getLogger("yama_ai.ingestion.india_code")


class IndiaCodeCrawler(BaseCrawler):
    """
    Crawler for India Code (https://www.indiacode.nic.in).
    Extracts central acts and their sections.
    """

    BASE_URL = "https://www.indiacode.nic.in"

    @property
    def source_name(self) -> str:
        return "india_code"

    def crawl(self, act_ids: Optional[List[str]] = None) -> List[LegalRecord]:
        """
        Main crawl entry point.

        Args:
            act_ids: Optional list of specific act IDs to crawl.
                     If None, crawls the index of all central acts.

        Returns:
            List of LegalRecord objects.
        """
        records: List[LegalRecord] = []

        if act_ids:
            for act_id in act_ids:
                act_records = self._crawl_act(act_id)
                records.extend(act_records)
        else:
            act_list = self._get_act_listing()
            for act_info in act_list:
                act_records = self._crawl_act_by_info(act_info)
                records.extend(act_records)

        self.stats["records_extracted"] = len(records)
        logger.info(f"[{self.source_name}] Crawled {len(records)} sections from India Code")
        return records

    def _get_act_listing(self) -> List[dict]:
        """
        Fetch the listing of all central acts from India Code.
        Returns list of dicts with act_name, act_url, year, etc.
        """
        acts = []
        url = f"{self.BASE_URL}/listing/repealedActChronologicalList"
        resp = self.fetch(url)
        if not resp:
            logger.error("Failed to fetch India Code act listing")
            return acts

        soup = BeautifulSoup(resp.text, "html.parser")

        # India Code uses table rows for act listings
        for row in soup.select("table tbody tr"):
            cells = row.find_all("td")
            if len(cells) >= 3:
                link = cells[1].find("a")
                if link:
                    acts.append({
                        "name": link.get_text(strip=True),
                        "url": self.BASE_URL + link.get("href", ""),
                        "year": cells[0].get_text(strip=True),
                    })

        logger.info(f"[{self.source_name}] Found {len(acts)} acts in listing")
        return acts

    def _crawl_act(self, act_id: str) -> List[LegalRecord]:
        """Crawl a specific act by its India Code act ID."""
        url = f"{self.BASE_URL}/show-data?actid={act_id}&type=act"
        return self._parse_act_page(url, act_id)

    def _crawl_act_by_info(self, act_info: dict) -> List[LegalRecord]:
        """Crawl an act using info from the listing page."""
        return self._parse_act_page(act_info["url"], act_info.get("name", "Unknown"))

    def _parse_act_page(self, url: str, act_identifier: str) -> List[LegalRecord]:
        """
        Parse an act detail page and extract all sections.

        India Code act pages typically have:
        - Act title and year in a heading
        - Section list in a table or accordion
        - Each section has: number, marginal heading, text
        """
        records: List[LegalRecord] = []

        resp = self.fetch(url)
        if not resp:
            logger.warning(f"Failed to fetch act page: {url}")
            return records

        soup = BeautifulSoup(resp.text, "html.parser")

        # Extract act name from page title
        title_el = soup.find("h3") or soup.find("h2") or soup.find("title")
        act_name = title_el.get_text(strip=True) if title_el else str(act_identifier)
        act_name = self._clean_act_name(act_name)

        # Find section containers — India Code uses various structures
        section_containers = (
            soup.select(".section-content")
            or soup.select("div.orderCont")
            or soup.select("table.table tbody tr")
        )

        for idx, container in enumerate(section_containers, 1):
            record = self._extract_section(container, act_name, url)
            if record:
                records.append(record)

        logger.info(f"[{self.source_name}] Extracted {len(records)} sections from '{act_name}'")
        return records

    def _extract_section(
        self, element: "BeautifulSoup", act_name: str, source_url: str
    ) -> Optional[LegalRecord]:
        """Extract a single section from a page element."""

        # Try different selectors for section number and heading
        sec_num_el = (
            element.select_one(".section-number")
            or element.select_one("td:first-child")
            or element.find("b")
        )
        heading_el = (
            element.select_one(".section-heading")
            or element.select_one("td:nth-child(2)")
            or element.find("strong")
        )

        if not sec_num_el:
            return None

        raw_num = sec_num_el.get_text(strip=True)
        section_number = self._clean_section_number(raw_num)
        if not section_number:
            return None

        title = heading_el.get_text(strip=True) if heading_el else f"Section {section_number}"

        # Description: rest of the text content
        desc_el = element.select_one(".section-text") or element
        description = desc_el.get_text(separator=" ", strip=True)
        # Remove the section number/title from the description
        description = description.replace(raw_num, "").replace(title, "").strip()
        if len(description) < 10:
            description = title  # Fallback

        category = self._classify_category(act_name, title, description)
        keywords = self._extract_keywords(title, description)

        return LegalRecord(
            act_name=act_name,
            section_number=section_number,
            title=title,
            description=description,
            keywords=keywords,
            category=category,
            jurisdiction="central",
            law_type="act",
            source_url=source_url,
        )

    # ── Helpers ──

    @staticmethod
    def _clean_act_name(name: str) -> str:
        """Normalize act name."""
        name = re.sub(r"\s+", " ", name).strip()
        name = re.sub(r"\[.*?\]", "", name).strip()
        return name

    @staticmethod
    def _clean_section_number(raw: str) -> str:
        """Extract clean section number from raw text."""
        match = re.search(r"(?:Section\s*)?(\d+[A-Za-z]*)", raw, re.IGNORECASE)
        return match.group(1) if match else ""

    @staticmethod
    def _classify_category(act_name: str, title: str, description: str) -> str:
        """Auto-classify into a legal category based on content keywords."""
        combined = f"{act_name} {title} {description}".lower()
        best_category = "general"
        best_score = 0

        for category, keywords in CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in combined)
            if score > best_score:
                best_score = score
                best_category = category

        return best_category

    @staticmethod
    def _extract_keywords(title: str, description: str) -> str:
        """Generate comma-separated keywords from title and description."""
        combined = f"{title} {description}".lower()
        # Remove common stop words
        stop_words = {"the", "of", "and", "in", "to", "a", "is", "or", "for", "be",
                      "an", "as", "by", "on", "at", "it", "that", "this", "with",
                      "any", "shall", "may", "such", "which", "who", "not", "from",
                      "under", "been", "has", "have", "his", "her", "its", "was"}
        words = re.findall(r"[a-z]{3,}", combined)
        keywords = [w for w in dict.fromkeys(words) if w not in stop_words][:15]
        return ", ".join(keywords)
