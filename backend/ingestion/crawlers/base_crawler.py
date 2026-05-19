"""
YAMA AI — Base Crawler Framework
Abstract base class for all legal data crawlers.
Provides: HTTP session, retry logic, rate limiting, logging, and error handling.
"""

import hashlib
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional

import httpx

from ingestion.config import ingestion_settings

logger = logging.getLogger("yama_ai.ingestion")


class LegalRecord:
    """
    Standardized container for a single legal data record.
    Every crawler must produce a list of these.
    """

    def __init__(
        self,
        act_name: str,
        section_number: str,
        title: str,
        description: str,
        keywords: str = "",
        category: str = "general",
        punishment: Optional[str] = None,
        old_law_reference: Optional[str] = None,
        jurisdiction: str = "central",
        state_name: Optional[str] = None,
        law_type: str = "act",
        source_url: Optional[str] = None,
    ):
        self.act_name = act_name
        self.section_number = section_number
        self.title = title
        self.description = description
        self.keywords = keywords
        self.category = category
        self.punishment = punishment
        self.old_law_reference = old_law_reference
        self.jurisdiction = jurisdiction
        self.state_name = state_name
        self.law_type = law_type
        self.source_url = source_url
        self.content_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """SHA-256 of the core content for change detection."""
        payload = f"{self.act_name}|{self.section_number}|{self.title}|{self.description}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict:
        return {
            "act_name": self.act_name,
            "section_number": self.section_number,
            "title": self.title,
            "description": self.description,
            "keywords": self.keywords,
            "category": self.category,
            "punishment": self.punishment,
            "old_law_reference": self.old_law_reference,
            "jurisdiction": self.jurisdiction,
            "state_name": self.state_name,
            "law_type": self.law_type,
            "source_url": self.source_url,
            "content_hash": self.content_hash,
        }


class BaseCrawler(ABC):
    """
    Abstract base for all legal data crawlers.

    Subclasses implement:
        - `crawl()` → list of LegalRecord
        - `source_name` property

    The base class provides:
        - HTTP client with retries and rate limiting
        - Polite request delays
        - Consistent error handling
    """

    def __init__(self):
        self._client: Optional[httpx.Client] = None
        self._last_request_time: float = 0
        self.stats = {
            "requests_made": 0,
            "records_extracted": 0,
            "errors": 0,
        }

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Identifier for this data source, e.g. 'india_code'."""
        ...

    @abstractmethod
    def crawl(self) -> List[LegalRecord]:
        """Execute the crawl and return extracted legal records."""
        ...

    # ── HTTP helpers ──

    def _get_client(self) -> httpx.Client:
        if self._client is None or self._client.is_closed:
            self._client = httpx.Client(
                timeout=ingestion_settings.request_timeout,
                headers={"User-Agent": ingestion_settings.user_agent},
                follow_redirects=True,
            )
        return self._client

    def fetch(self, url: str, retries: int = 0) -> Optional[httpx.Response]:
        """
        Fetch a URL with polite delay and retry logic.
        Returns None on permanent failure.
        """
        # Rate-limit: wait between requests
        elapsed = time.time() - self._last_request_time
        if elapsed < ingestion_settings.request_delay:
            time.sleep(ingestion_settings.request_delay - elapsed)

        max_tries = retries or ingestion_settings.max_retries
        for attempt in range(1, max_tries + 1):
            try:
                client = self._get_client()
                logger.debug(f"[{self.source_name}] GET {url} (attempt {attempt})")
                resp = client.get(url)
                self._last_request_time = time.time()
                self.stats["requests_made"] += 1

                if resp.status_code == 200:
                    return resp

                if resp.status_code in (429, 503):
                    wait = min(2 ** attempt, 30)
                    logger.warning(f"[{self.source_name}] {resp.status_code} — retrying in {wait}s")
                    time.sleep(wait)
                    continue

                logger.warning(f"[{self.source_name}] HTTP {resp.status_code} for {url}")
                return None

            except httpx.TimeoutException:
                logger.warning(f"[{self.source_name}] Timeout for {url} (attempt {attempt})")
                time.sleep(2 ** attempt)
            except httpx.HTTPError as e:
                logger.error(f"[{self.source_name}] HTTP error: {e}")
                self.stats["errors"] += 1
                return None

        logger.error(f"[{self.source_name}] Failed after {max_tries} attempts: {url}")
        self.stats["errors"] += 1
        return None

    def close(self):
        if self._client and not self._client.is_closed:
            self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
