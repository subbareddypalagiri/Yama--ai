"""
YAMA AI — Legal Text Extractor
Extracts structured legal text from raw HTML/PDF content.

Handles:
    - HTML act pages (tables, lists, nested divs)
    - Section splitting (numbered sections, articles)
    - Amendment detection
    - Cross-reference linking
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup

logger = logging.getLogger("yama_ai.ingestion.extractor")


class LegalTextExtractor:
    """
    Parses raw legal HTML/text into structured section-level records.
    Specialized for Indian legislative document formatting.
    """

    # Common patterns in Indian legal text
    SECTION_PATTERNS = [
        # "1. Short title and commencement.—"
        re.compile(r"^(\d+[A-Za-z]?)\.?\s*(.+?)(?:\.—|—|\.\s*$)", re.MULTILINE),
        # "Section 302. Punishment for murder."
        re.compile(r"Section\s+(\d+[A-Za-z]?)\.?\s*(.+?)(?:\.\s*$|—)", re.MULTILINE | re.IGNORECASE),
        # "Article 14. Equality before law"
        re.compile(r"Article\s+(\d+[A-Za-z]?)\.?\s*(.+?)(?:\.\s*$|—)", re.MULTILINE | re.IGNORECASE),
        # "Rule 3. Definitions"
        re.compile(r"Rule\s+(\d+[A-Za-z]?)\.?\s*(.+?)(?:\.\s*$|—)", re.MULTILINE | re.IGNORECASE),
    ]

    AMENDMENT_PATTERN = re.compile(
        r"\[(?:Ins|Subs|Omitted|Added|Deleted)\.?\s+by\s+Act\s+(\d+)\s+of\s+(\d{4})",
        re.IGNORECASE,
    )

    PROVISO_PATTERN = re.compile(r"Provided\s+that", re.IGNORECASE)
    EXPLANATION_PATTERN = re.compile(r"Explanation\.?\s*[-—]?", re.IGNORECASE)

    def extract_from_html(self, html: str, act_name: str = "") -> List[Dict]:
        """
        Extract sections from an HTML page of an Indian act.

        Returns:
            List of dicts with: section_number, title, text, amendments, provisos
        """
        soup = BeautifulSoup(html, "html.parser")

        # Remove script/style elements
        for tag in soup.find_all(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        return self.extract_from_text(text, act_name)

    def extract_from_text(self, text: str, act_name: str = "") -> List[Dict]:
        """
        Extract sections from plain text of an Indian act.

        Strategy:
        1. Split by section boundaries.
        2. Parse each section's number, title, body.
        3. Detect amendments, provisos, explanations.
        """
        sections: List[Dict] = []

        # Try each section pattern
        for pattern in self.SECTION_PATTERNS:
            matches = list(pattern.finditer(text))
            if len(matches) >= 3:  # Need at least 3 matches to be confident
                sections = self._split_by_matches(text, matches, act_name)
                break

        # Fallback: simple numbered splitting
        if not sections:
            sections = self._fallback_split(text, act_name)

        logger.info(f"Extracted {len(sections)} sections from '{act_name or 'unknown'}'")
        return sections

    def _split_by_matches(self, text: str, matches: list, act_name: str) -> List[Dict]:
        """Split text into sections using regex match positions."""
        sections: List[Dict] = []

        for i, match in enumerate(matches):
            sec_num = match.group(1)
            sec_title = match.group(2).strip(" .:-—")

            # Body extends from end of this match to start of next match (or end of text)
            body_start = match.end()
            body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[body_start:body_end].strip()

            # Detect amendments within this section
            amendments = self._find_amendments(body)

            # Count provisos and explanations
            provisos = len(self.PROVISO_PATTERN.findall(body))
            explanations = len(self.EXPLANATION_PATTERN.findall(body))

            sections.append({
                "section_number": sec_num,
                "title": sec_title[:500],
                "text": body[:10000],
                "amendments": amendments,
                "has_proviso": provisos > 0,
                "proviso_count": provisos,
                "has_explanation": explanations > 0,
                "act_name": act_name,
            })

        return sections

    def _fallback_split(self, text: str, act_name: str) -> List[Dict]:
        """Fallback: split text by paragraph with numbering heuristics."""
        sections: List[Dict] = []
        paragraphs = text.split("\n\n")
        sec_counter = 0

        for para in paragraphs:
            para = para.strip()
            if len(para) < 30:
                continue

            # Check if paragraph starts with a number
            num_match = re.match(r"^(\d+[A-Za-z]?)[\.\)\s](.+)", para)
            if num_match:
                sec_counter = 0
                sec_num = num_match.group(1)
                rest = num_match.group(2).strip()
                # First sentence is title
                sentences = rest.split(".")
                title = sentences[0].strip() if sentences else f"Section {sec_num}"
                body = ".".join(sentences[1:]).strip() if len(sentences) > 1 else rest
            else:
                sec_counter += 1
                sec_num = f"para-{sec_counter}"
                title = para[:100]
                body = para

            sections.append({
                "section_number": sec_num,
                "title": title[:500],
                "text": body[:10000],
                "amendments": self._find_amendments(body),
                "has_proviso": bool(self.PROVISO_PATTERN.search(body)),
                "proviso_count": len(self.PROVISO_PATTERN.findall(body)),
                "has_explanation": bool(self.EXPLANATION_PATTERN.search(body)),
                "act_name": act_name,
            })

        return sections

    def _find_amendments(self, text: str) -> List[Dict]:
        """Find all amendment references in a section's text."""
        amendments = []
        for match in self.AMENDMENT_PATTERN.finditer(text):
            amendments.append({
                "act_number": match.group(1),
                "year": match.group(2),
                "context": text[max(0, match.start()-50):match.end()+50].strip(),
            })
        return amendments

    def extract_cross_references(self, text: str) -> List[Dict]:
        """Find all cross-references to other acts/sections in the text."""
        refs = []

        # "Section X of the Y Act"
        for match in re.finditer(
            r"[Ss]ection\s+(\d+[A-Za-z]*)\s+of\s+(?:the\s+)?(.+?(?:Act|Code|Sanhita)\s*,?\s*\d*)",
            text
        ):
            refs.append({
                "type": "section",
                "number": match.group(1),
                "act": match.group(2).strip(),
            })

        # "Article X of the Constitution"
        for match in re.finditer(r"[Aa]rticle\s+(\d+[A-Za-z]*)\s+of\s+the\s+Constitution", text):
            refs.append({
                "type": "article",
                "number": match.group(1),
                "act": "Constitution of India",
            })

        return refs
