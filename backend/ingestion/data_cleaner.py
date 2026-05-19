"""
YAMA AI — Data Cleaning Module
Cleans, normalizes, and validates legal data before storage.

Operations:
    - Remove HTML artifacts and encoding issues
    - Normalize section numbers (e.g., "302A" → "302A", "section 302" → "302")
    - Standardize act names
    - Remove duplicate records
    - Validate required fields
    - Clean unicode and special characters
"""

import re
import hashlib
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger("yama_ai.ingestion.cleaner")


# ── Act Name Standardization Map ──
ACT_NAME_ALIASES = {
    # BNS / IPC
    "bharatiya nyaya sanhita": "Bharatiya Nyaya Sanhita, 2023",
    "bns": "Bharatiya Nyaya Sanhita, 2023",
    "indian penal code": "Indian Penal Code, 1860",
    "ipc": "Indian Penal Code, 1860",
    # BNSS / CrPC
    "bharatiya nagarik suraksha sanhita": "Bharatiya Nagarik Suraksha Sanhita, 2023",
    "bnss": "Bharatiya Nagarik Suraksha Sanhita, 2023",
    "criminal procedure code": "Code of Criminal Procedure, 1973",
    "crpc": "Code of Criminal Procedure, 1973",
    # BSA / Indian Evidence Act
    "bharatiya sakshya adhiniyam": "Bharatiya Sakshya Adhiniyam, 2023",
    "bsa": "Bharatiya Sakshya Adhiniyam, 2023",
    "indian evidence act": "Indian Evidence Act, 1872",
    # IT Act
    "information technology act": "Information Technology Act, 2000",
    "it act": "Information Technology Act, 2000",
    # Consumer Protection
    "consumer protection act": "Consumer Protection Act, 2019",
    # Motor Vehicles
    "motor vehicles act": "Motor Vehicles Act, 1988",
    # Constitution
    "constitution of india": "Constitution of India",
    "constitution": "Constitution of India",
}


class DataCleaner:
    """
    Cleans and normalizes legal data records.
    Call `clean_record()` on each record before storage.
    """

    def clean_record(self, record: Dict) -> Optional[Dict]:
        """
        Clean a single legal data record.

        Returns:
            Cleaned record dict, or None if the record is invalid.
        """
        try:
            # 1. Clean text fields
            record["act_name"] = self._clean_act_name(record.get("act_name", ""))
            record["section_number"] = self._clean_section_number(record.get("section_number", ""))
            record["title"] = self._clean_text(record.get("title", ""))
            record["description"] = self._clean_description(record.get("description", ""))
            record["keywords"] = self._clean_keywords(record.get("keywords", ""))

            # 2. Standardize act name
            record["act_name"] = self._standardize_act_name(record["act_name"])

            # 3. Validate required fields
            if not self._validate(record):
                return None

            # 4. Recompute content hash
            record["content_hash"] = self._compute_hash(record)

            return record

        except Exception as e:
            logger.warning(f"Failed to clean record: {e}")
            return None

    def clean_batch(self, records: List[Dict]) -> Tuple[List[Dict], int]:
        """
        Clean a batch of records.

        Returns:
            Tuple of (cleaned_records, skipped_count)
        """
        cleaned = []
        skipped = 0

        for record in records:
            result = self.clean_record(record)
            if result:
                cleaned.append(result)
            else:
                skipped += 1

        logger.info(f"Cleaned {len(cleaned)} records, skipped {skipped}")
        return cleaned, skipped

    def deduplicate(self, records: List[Dict]) -> List[Dict]:
        """
        Remove duplicate records based on content hash.
        Keeps the first occurrence.
        """
        seen_hashes = set()
        unique = []

        for record in records:
            h = record.get("content_hash") or self._compute_hash(record)
            if h not in seen_hashes:
                seen_hashes.add(h)
                unique.append(record)

        removed = len(records) - len(unique)
        if removed:
            logger.info(f"Deduplication: removed {removed} duplicate records")
        return unique

    # ── Text Cleaning ──

    @staticmethod
    def _clean_text(text: str) -> str:
        """General text cleanup."""
        if not text:
            return ""
        # Remove HTML tags
        text = re.sub(r"<[^>]+>", " ", text)
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)
        # Remove control characters (keep newlines)
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
        # Fix common encoding issues
        text = text.replace("\u00a0", " ")  # non-breaking space
        text = text.replace("\u2018", "'").replace("\u2019", "'")
        text = text.replace("\u201c", '"').replace("\u201d", '"')
        text = text.replace("\u2014", "—").replace("\u2013", "–")
        return text.strip()

    @staticmethod
    def _clean_act_name(name: str) -> str:
        """Clean and normalize act name."""
        if not name:
            return ""
        name = re.sub(r"<[^>]+>", "", name)
        name = re.sub(r"\s+", " ", name).strip()
        # Remove common prefixes
        name = re.sub(r"^(The\s+)", "", name, flags=re.IGNORECASE)
        # Remove trailing punctuation
        name = name.rstrip(" .,;:")
        return name

    @staticmethod
    def _clean_section_number(sec_num: str) -> str:
        """Normalize section number format."""
        if not sec_num:
            return ""
        sec_num = sec_num.strip()
        # Remove "Section", "Article", "Rule" prefixes
        sec_num = re.sub(r"^(Section|Article|Rule|Sec\.?)\s*", "", sec_num, flags=re.IGNORECASE)
        # Remove surrounding brackets
        sec_num = sec_num.strip("()[]")
        return sec_num.strip()

    def _clean_description(self, desc: str) -> str:
        """Clean section description/body text."""
        if not desc:
            return ""
        desc = self._clean_text(desc)
        # Truncate extremely long descriptions
        if len(desc) > 10000:
            desc = desc[:10000] + "... [truncated]"
        return desc

    @staticmethod
    def _clean_keywords(keywords: str) -> str:
        """Normalize keywords: lowercase, deduplicate, trim."""
        if not keywords:
            return ""
        # Split by comma, clean each keyword
        kw_list = [kw.strip().lower() for kw in keywords.split(",")]
        # Remove empty and duplicates (preserve order)
        seen = set()
        unique = []
        for kw in kw_list:
            if kw and kw not in seen:
                seen.add(kw)
                unique.append(kw)
        return ", ".join(unique[:20])

    @staticmethod
    def _standardize_act_name(name: str) -> str:
        """Map common aliases to standard act names."""
        key = name.lower().strip()
        # Try exact match first
        if key in ACT_NAME_ALIASES:
            return ACT_NAME_ALIASES[key]
        # Try partial match
        for alias, standard in ACT_NAME_ALIASES.items():
            if alias in key:
                return standard
        return name

    # ── Validation ──

    @staticmethod
    def _validate(record: Dict) -> bool:
        """Validate that a record has all required fields."""
        required = ["act_name", "section_number", "title", "description"]
        for field in required:
            val = record.get(field, "")
            if not val or len(str(val).strip()) < 2:
                logger.debug(f"Validation failed: '{field}' is empty or too short")
                return False

        # Description should be meaningful
        if len(record.get("description", "")) < 10:
            logger.debug("Validation failed: description too short")
            return False

        return True

    @staticmethod
    def _compute_hash(record: Dict) -> str:
        """Compute SHA-256 content hash for change detection."""
        payload = (
            f"{record.get('act_name', '')}|"
            f"{record.get('section_number', '')}|"
            f"{record.get('title', '')}|"
            f"{record.get('description', '')}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
