"""
YAMA AI — Supreme Court & High Court Judgment Crawler
Fetches judgments from official court websites.

Sources:
    - Supreme Court of India: https://main.sci.gov.in
    - Various High Court portals

Note:
    Court websites often use dynamic rendering (JavaScript).
    For production, use Playwright for reliable extraction.
    This module provides both httpx (static) and Playwright (dynamic) modes.
"""

import re
import logging
from datetime import datetime
from typing import List, Optional
from bs4 import BeautifulSoup

from ingestion.crawlers.base_crawler import BaseCrawler, LegalRecord

logger = logging.getLogger("yama_ai.ingestion.courts")

# ── High Court domain registry ──
HIGH_COURT_PORTALS = {
    "Delhi": "https://delhihighcourt.nic.in",
    "Bombay": "https://bombayhighcourt.nic.in",
    "Madras": "https://www.mhc.tn.gov.in",
    "Calcutta": "https://calcuttahighcourt.gov.in",
    "Karnataka": "https://karnatakajudiciary.kar.nic.in",
    "Allahabad": "https://www.allahabadhighcourt.in",
    "Kerala": "https://highcourtofkerala.nic.in",
    "Gujarat": "https://gujarathighcourt.nic.in",
    "Punjab and Haryana": "https://phhc.gov.in",
    "Telangana": "https://tshc.gov.in",
}


class SupremeCourtCrawler(BaseCrawler):
    """
    Crawler for Supreme Court of India judgments.

    The Supreme Court website (main.sci.gov.in) provides:
    - Daily cause list
    - Judgments by date/case number
    - Free text search

    This crawler fetches recent judgments and extracts:
    - Case name, citation, date
    - Legal principles / ratio decidendi
    - Acts and sections cited
    """

    BASE_URL = "https://main.sci.gov.in"

    @property
    def source_name(self) -> str:
        return "supreme_court"

    def crawl(self, from_date: Optional[str] = None, to_date: Optional[str] = None) -> List[LegalRecord]:
        """
        Crawl Supreme Court judgments.

        Args:
            from_date: Start date (DD-MM-YYYY). Defaults to last 30 days.
            to_date: End date (DD-MM-YYYY). Defaults to today.
        """
        records: List[LegalRecord] = []

        if not from_date:
            from_date = datetime.now().strftime("%d-%m-%Y")
        if not to_date:
            to_date = datetime.now().strftime("%d-%m-%Y")

        # Fetch judgment listing page
        judgment_urls = self._get_judgment_list(from_date, to_date)

        for j_info in judgment_urls:
            j_records = self._parse_judgment(j_info)
            records.extend(j_records)

        self.stats["records_extracted"] = len(records)
        logger.info(f"[{self.source_name}] Extracted {len(records)} judgment records")
        return records

    def _get_judgment_list(self, from_date: str, to_date: str) -> List[dict]:
        """Fetch list of judgments from the SCI website."""
        judgments = []

        url = f"{self.BASE_URL}/judgments"
        resp = self.fetch(url)
        if not resp:
            return judgments

        soup = BeautifulSoup(resp.text, "html.parser")

        # SCI lists judgments in table rows or card elements
        for row in soup.select("table tbody tr, .judgment-item, .list-group-item"):
            link = row.find("a", href=True)
            if not link:
                continue

            href = link.get("href", "")
            if not href:
                continue

            full_url = href if href.startswith("http") else self.BASE_URL + href
            case_text = link.get_text(strip=True)

            judgments.append({
                "url": full_url,
                "case_name": case_text,
                "date": from_date,
            })

        logger.info(f"[{self.source_name}] Found {len(judgments)} judgments in listing")
        return judgments

    def _parse_judgment(self, j_info: dict) -> List[LegalRecord]:
        """Parse a single judgment page and extract legal records."""
        records: List[LegalRecord] = []

        resp = self.fetch(j_info["url"])
        if not resp:
            return records

        soup = BeautifulSoup(resp.text, "html.parser")

        # Extract judgment text
        content_el = (
            soup.select_one(".judgment-content")
            or soup.select_one(".order-content")
            or soup.select_one("pre")
            or soup.select_one("main")
        )

        if not content_el:
            return records

        text = content_el.get_text(separator="\n", strip=True)
        case_name = j_info.get("case_name", "Unknown Case")

        # Extract cited sections: "Section 302 of IPC", "Article 21", etc.
        cited_sections = self._extract_cited_provisions(text)

        # Create a record for the judgment itself
        records.append(LegalRecord(
            act_name=f"Supreme Court Judgment: {case_name[:200]}",
            section_number="Judgment",
            title=case_name[:500],
            description=text[:8000],
            keywords=self._extract_keywords(case_name, text),
            category=self._classify_judgment(text),
            jurisdiction="central",
            law_type="judgment",
            source_url=j_info["url"],
        ))

        return records

    def _extract_cited_provisions(self, text: str) -> List[str]:
        """Find all Acts/Sections cited in judgment text."""
        patterns = [
            r"Section\s+(\d+[A-Za-z]*)\s+of\s+([A-Z][A-Za-z\s,]+(?:Act|Code|Sanhita))",
            r"Article\s+(\d+[A-Za-z]*)\s+of\s+the\s+Constitution",
            r"under\s+Section\s+(\d+[A-Za-z]*)\s+([A-Z][A-Za-z\s]+)",
        ]
        cited = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for m in matches:
                cited.append(" ".join(m).strip())
        return list(set(cited))[:20]

    @staticmethod
    def _classify_judgment(text: str) -> str:
        """Classify judgment into legal category."""
        text_lower = text[:3000].lower()
        if any(w in text_lower for w in ["murder", "criminal", "accused", "fir", "bail"]):
            return "criminal"
        if any(w in text_lower for w in ["constitution", "fundamental", "article 14", "article 21"]):
            return "constitutional"
        if any(w in text_lower for w in ["property", "land", "tenant", "rent"]):
            return "property"
        if any(w in text_lower for w in ["consumer", "deficiency", "service"]):
            return "consumer"
        if any(w in text_lower for w in ["company", "director", "shareholder"]):
            return "corporate"
        return "civil"

    @staticmethod
    def _extract_keywords(title: str, text: str) -> str:
        combined = f"{title} {text[:1000]}".lower()
        stop_words = {"the", "of", "and", "in", "to", "a", "is", "or", "for", "be",
                      "an", "as", "by", "on", "at", "it", "that", "this", "with",
                      "any", "shall", "may", "such", "which", "who", "not", "from"}
        words = re.findall(r"[a-z]{3,}", combined)
        keywords = [w for w in dict.fromkeys(words) if w not in stop_words][:15]
        return ", ".join(keywords)


class HighCourtCrawler(BaseCrawler):
    """
    Crawler for High Court judgments.
    Can target specific High Courts from the registry.
    """

    @property
    def source_name(self) -> str:
        return "high_courts"

    def crawl(self, court_name: Optional[str] = None) -> List[LegalRecord]:
        """
        Crawl High Court judgments.

        Args:
            court_name: Specific court (e.g., 'Delhi'). If None, crawls all.
        """
        records: List[LegalRecord] = []

        courts = {court_name: HIGH_COURT_PORTALS[court_name]} if court_name else HIGH_COURT_PORTALS

        for name, base_url in courts.items():
            court_records = self._crawl_court(name, base_url)
            records.extend(court_records)

        self.stats["records_extracted"] = len(records)
        return records

    def _crawl_court(self, court_name: str, base_url: str) -> List[LegalRecord]:
        """Crawl a single High Court's judgment listing."""
        records: List[LegalRecord] = []

        # Try common judgment listing paths
        for path in ["/judgments", "/judgment", "/orders", "/causelist"]:
            resp = self.fetch(base_url + path)
            if resp:
                soup = BeautifulSoup(resp.text, "html.parser")
                for link in soup.find_all("a", href=True):
                    href = link.get("href", "")
                    text = link.get_text(strip=True)
                    if len(text) > 20 and ("judgment" in href.lower() or "order" in href.lower()):
                        full_url = href if href.startswith("http") else base_url + href
                        records.append(LegalRecord(
                            act_name=f"{court_name} High Court Judgment",
                            section_number="Judgment",
                            title=text[:500],
                            description=text[:5000],
                            keywords=f"high court, {court_name.lower()}, judgment",
                            category="civil",
                            jurisdiction="state",
                            state_name=court_name,
                            law_type="judgment",
                            source_url=full_url,
                        ))
                break

        logger.info(f"[{self.source_name}] {court_name} HC: {len(records)} records")
        return records
