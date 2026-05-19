"""
YAMA AI — Constitution of India Crawler
Crawls the Constitution of India text from official government sources.

Sources:
    - india.gov.in/my-government/constitution-india
    - legislative.gov.in

Extracts: Parts, Articles, Amendments, Schedules.
"""

import re
import logging
from typing import List, Optional
from bs4 import BeautifulSoup

from ingestion.crawlers.base_crawler import BaseCrawler, LegalRecord
from ingestion.config import CATEGORY_KEYWORDS

logger = logging.getLogger("yama_ai.ingestion.constitution")


class ConstitutionCrawler(BaseCrawler):
    """
    Crawler for the Constitution of India.
    Extracts articles, amendments, and schedules.
    """

    BASE_URL = "https://www.india.gov.in"
    CONSTITUTION_INDEX = "/my-government/constitution-india/constitution-india-full-text"

    @property
    def source_name(self) -> str:
        return "constitution"

    def crawl(self) -> List[LegalRecord]:
        """Crawl the full Constitution of India."""
        records: List[LegalRecord] = []

        # Attempt to fetch the full text page
        url = self.BASE_URL + self.CONSTITUTION_INDEX
        resp = self.fetch(url)

        if resp:
            records.extend(self._parse_constitution_page(resp.text, url))

        # Also try part-wise pages (india.gov.in has separate part pages)
        part_records = self._crawl_parts()
        records.extend(part_records)

        self.stats["records_extracted"] = len(records)
        logger.info(f"[{self.source_name}] Extracted {len(records)} constitutional provisions")
        return records

    def _parse_constitution_page(self, html: str, source_url: str) -> List[LegalRecord]:
        """Parse the full Constitution text page and extract articles."""
        records: List[LegalRecord] = []
        soup = BeautifulSoup(html, "html.parser")

        # Look for article headings: "Article 14", "Article 19", etc.
        article_pattern = re.compile(r"Article\s+(\d+[A-Za-z]*)", re.IGNORECASE)

        # Find elements that contain article numbers
        content = soup.select_one(".field-items") or soup.select_one("main") or soup.find("body")
        if not content:
            return records

        # Split text by article boundaries
        full_text = content.get_text(separator="\n")
        article_splits = re.split(r"(?=Article\s+\d+[A-Za-z]*\.?\s)", full_text, flags=re.IGNORECASE)

        for chunk in article_splits:
            match = article_pattern.search(chunk)
            if not match:
                continue

            article_num = match.group(1)
            # Extract title (first line after article number)
            lines = chunk.strip().split("\n")
            title_line = lines[0] if lines else f"Article {article_num}"
            # Clean title
            title = re.sub(r"Article\s+\d+[A-Za-z]*\.?\s*", "", title_line).strip(" .:-")
            if not title:
                title = f"Article {article_num}"

            # Description is the rest
            description = "\n".join(lines[1:]).strip() if len(lines) > 1 else title

            if len(description) < 5:
                continue

            records.append(LegalRecord(
                act_name="Constitution of India",
                section_number=f"Article {article_num}",
                title=title,
                description=description[:5000],
                keywords=self._extract_keywords(title, description),
                category="constitutional",
                jurisdiction="central",
                law_type="article",
                source_url=source_url,
            ))

        return records

    def _crawl_parts(self) -> List[LegalRecord]:
        """
        Crawl Constitution parts individually.
        india.gov.in has separate pages for each part.
        """
        records: List[LegalRecord] = []
        parts_url = f"{self.BASE_URL}/my-government/constitution-india"
        resp = self.fetch(parts_url)
        if not resp:
            return records

        soup = BeautifulSoup(resp.text, "html.parser")

        # Find links to individual parts
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            text = link.get_text(strip=True)
            if "part-" in href.lower() or re.search(r"Part\s+[IVXLC]+", text, re.IGNORECASE):
                full_url = href if href.startswith("http") else self.BASE_URL + href
                part_resp = self.fetch(full_url)
                if part_resp:
                    part_records = self._parse_constitution_page(part_resp.text, full_url)
                    records.extend(part_records)

        return records

    @staticmethod
    def _extract_keywords(title: str, description: str) -> str:
        combined = f"{title} {description}".lower()
        stop_words = {"the", "of", "and", "in", "to", "a", "is", "or", "for", "be",
                      "an", "as", "by", "on", "at", "it", "that", "this", "with",
                      "any", "shall", "may", "such", "which", "who", "not", "from",
                      "under", "been", "has", "have", "his", "her", "its", "state"}
        words = re.findall(r"[a-z]{3,}", combined)
        keywords = [w for w in dict.fromkeys(words) if w not in stop_words][:15]
        return ", ".join(keywords)
