"""
YAMA AI — Legal Text Parser
=============================================================================
Production-grade parser that takes raw legal text (scraped HTML, plain text,
or PDF-extracted text) and converts it into clean, structured JSON records
compatible with the YAMA AI pipeline.

Capabilities:
    1. CLEANING     — Strip HTML, fix encoding, normalize whitespace/punctuation
    2. DETECTION    — Identify sections, articles, rules, clauses, sub-clauses,
                      provisos, explanations, schedules, amendments, definitions
    3. STRUCTURING  — Build a hierarchical tree (Act → Part → Chapter → Section
                      → Sub-section → Clause → Proviso → Explanation)
    4. OUTPUT       — Emit structured JSON (flat list or hierarchical tree)

Handles Indian legal drafting conventions:
    - "Section 302.—" / "302." / "Section 302A"
    - "Article 21" / "Art. 21"
    - "(1)", "(2)", "(a)", "(b)" sub-sections/clauses
    - "Provided that..." provisos
    - "Explanation.—" / "Explanation I.—"
    - "CHAPTER III — OF OFFENCES"
    - "PART IV" / "SCHEDULE I"
    - Amendment notes: "[Substituted by Act 25 of 2023]"
    - Definition sections: "\"theft\" means..."

Usage:
    from data_pipeline.parser import LegalTextParser

    parser = LegalTextParser()

    # Parse raw text of an act
    result = parser.parse(raw_text, act_name="Bharatiya Nyaya Sanhita, 2023")

    # result.sections        — list of ParsedSection objects
    # result.to_json()       — full JSON string
    # result.to_records()    — list of LegalRecord (for crawler pipeline)

    # Parse and export
    parser.parse_file("bns_2023.txt", act_name="BNS 2023", output="parsed_bns.json")

CLI:
    cd backend
    python -m data_pipeline.parser --input raw_text.txt --act "BNS 2023" --output parsed.json
    python -m data_pipeline.parser --input raw_text.html --format tree --output parsed.json
=============================================================================
"""

import hashlib
import json
import logging
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("yama_ai.parser")

# Ensure backend root on sys.path for LegalRecord import
_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)


# ═══════════════════════════════════════════════════════════════════════════
#  ENUMS & DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════

class NodeType(str, Enum):
    """Types of structural nodes in an Indian statute."""
    ACT = "act"
    PART = "part"
    CHAPTER = "chapter"
    SCHEDULE = "schedule"
    SECTION = "section"
    ARTICLE = "article"
    RULE = "rule"
    SUBSECTION = "sub_section"
    CLAUSE = "clause"
    SUBCLAUSE = "sub_clause"
    PROVISO = "proviso"
    EXPLANATION = "explanation"
    DEFINITION = "definition"
    AMENDMENT_NOTE = "amendment_note"
    PREAMBLE = "preamble"
    HEADING = "heading"
    MISCELLANEOUS = "miscellaneous"


@dataclass
class ParsedNode:
    """
    A single structural node from a parsed legal document.
    Can represent anything from a full Part down to a proviso.
    """
    node_type: NodeType
    number: str                                # "302", "21", "(1)", "(a)", ""
    heading: str                               # Marginal heading / title
    text: str                                  # Full text content of this node
    children: List["ParsedNode"] = field(default_factory=list)

    # Metadata
    amendment_notes: List[str] = field(default_factory=list)
    is_definition: bool = False
    defined_term: Optional[str] = None         # If this is a definition section

    def to_dict(self) -> Dict[str, Any]:
        """Recursive dict representation."""
        d: Dict[str, Any] = {
            "type": self.node_type.value,
            "number": self.number,
            "heading": self.heading,
            "text": self.text,
        }
        if self.children:
            d["children"] = [c.to_dict() for c in self.children]
        if self.amendment_notes:
            d["amendment_notes"] = self.amendment_notes
        if self.is_definition:
            d["is_definition"] = True
            if self.defined_term:
                d["defined_term"] = self.defined_term
        return d


@dataclass
class ParsedSection:
    """
    A flattened, pipeline-ready representation of a single section/article.
    This is the primary output unit used downstream.
    """
    act_name: str
    section_number: str
    title: str
    full_text: str
    sub_sections: List[Dict[str, str]] = field(default_factory=list)
    provisos: List[str] = field(default_factory=list)
    explanations: List[str] = field(default_factory=list)
    amendment_notes: List[str] = field(default_factory=list)
    definitions: List[Dict[str, str]] = field(default_factory=list)
    chapter: str = ""
    part: str = ""
    content_hash: str = ""

    def __post_init__(self):
        if not self.content_hash:
            blob = f"{self.act_name}|{self.section_number}|{self.title}|{self.full_text}"
            self.content_hash = hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "act_name": self.act_name,
            "section_number": self.section_number,
            "title": self.title,
            "full_text": self.full_text,
            "sub_sections": self.sub_sections,
            "provisos": self.provisos,
            "explanations": self.explanations,
            "amendment_notes": self.amendment_notes,
            "definitions": self.definitions,
            "chapter": self.chapter,
            "part": self.part,
            "content_hash": self.content_hash,
        }


@dataclass
class ParseResult:
    """Complete result of parsing a legal document."""
    act_name: str
    source: str                                # File path or URL
    sections: List[ParsedSection] = field(default_factory=list)
    tree: Optional[ParsedNode] = None          # Hierarchical tree (optional)
    stats: Dict[str, int] = field(default_factory=dict)

    def to_json(self, indent: int = 2) -> str:
        """Serialize full result to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "metadata": {
                "act_name": self.act_name,
                "source": self.source,
                "total_sections": len(self.sections),
                "stats": self.stats,
            },
            "sections": [s.to_dict() for s in self.sections],
        }
        if self.tree:
            d["tree"] = self.tree.to_dict()
        return d

    def to_records(self) -> list:
        """
        Convert to a list of LegalRecord objects compatible with
        data_pipeline.crawler for storage pipeline integration.
        """
        from data_pipeline.crawler import LegalRecord, enrich_record

        records = []
        for sec in self.sections:
            rec = LegalRecord(
                act_name=sec.act_name,
                section_number=sec.section_number,
                title=sec.title,
                section_text=sec.full_text,
                source_url=self.source,
            )
            rec = enrich_record(rec)
            records.append(rec)
        return records


# ═══════════════════════════════════════════════════════════════════════════
#  TEXT CLEANING ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class TextCleaner:
    """
    Cleans raw legal text from HTML, PDF extraction, or OCR output.
    Preserves legal structure markers (section numbers, clause numbering).
    """

    # HTML tag pattern
    _HTML_TAG = re.compile(r"<[^>]+>")
    # HTML entities
    _HTML_ENTITY = re.compile(r"&(?:#\d+|#x[\da-fA-F]+|[a-zA-Z]+);")
    # Control characters (keep \n, \t)
    _CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
    # Multiple blank lines → single blank line
    _MULTI_BLANK = re.compile(r"\n{3,}")
    # Multiple spaces (not newlines)
    _MULTI_SPACE = re.compile(r"[^\S\n]+")
    # Page number artifacts from PDF
    _PAGE_NUM = re.compile(r"\n\s*-?\s*\d{1,4}\s*-?\s*\n")
    # Header/footer repeats from PDF
    _PDF_HEADER = re.compile(
        r"(?:THE GAZETTE OF INDIA|EXTRAORDINARY|PART II|Section \d+|"
        r"MINISTRY OF LAW|PUBLISHED BY AUTHORITY|(?:Page|Pg\.?)\s*\d+)"
        r"\s*\n",
        re.I,
    )
    # OCR noise
    _OCR_NOISE = re.compile(r"[|}{~`^\\]")

    # Unicode normalization map
    _UNICODE_MAP = {
        "\u00a0": " ",   # NBSP
        "\u2018": "'",   # Left single quote
        "\u2019": "'",   # Right single quote
        "\u201c": '"',   # Left double quote
        "\u201d": '"',   # Right double quote
        "\u2014": " — ", # Em dash
        "\u2013": " – ", # En dash
        "\u2026": "...", # Ellipsis
        "\u200b": "",    # Zero-width space
        "\u200c": "",    # Zero-width non-joiner
        "\u200d": "",    # Zero-width joiner
        "\ufeff": "",    # BOM
        "\u00b7": ".",   # Middle dot
    }

    # HTML entity decode table (common ones)
    _ENTITY_MAP = {
        "&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"',
        "&apos;": "'", "&nbsp;": " ", "&mdash;": " — ", "&ndash;": " – ",
        "&lsquo;": "'", "&rsquo;": "'", "&ldquo;": '"', "&rdquo;": '"',
        "&hellip;": "...", "&sect;": "§",
    }

    @classmethod
    def clean(cls, text: str, strip_html: bool = True, strip_pdf_artifacts: bool = True) -> str:
        """
        Full cleaning pipeline.

        Args:
            text: Raw input text (HTML, plain text, or PDF-extracted).
            strip_html: Remove HTML tags and decode entities.
            strip_pdf_artifacts: Remove page numbers, headers, footers.

        Returns:
            Cleaned text with legal structure preserved.
        """
        if not text:
            return ""

        # 1. Unicode normalization
        for old, new in cls._UNICODE_MAP.items():
            text = text.replace(old, new)

        # 2. HTML handling
        if strip_html:
            # Decode entities first
            for entity, char in cls._ENTITY_MAP.items():
                text = text.replace(entity, char)
            text = cls._HTML_ENTITY.sub("", text)
            # Replace block-level tags with newlines
            text = re.sub(r"<(?:br|p|div|tr|li|h[1-6])[^>]*>", "\n", text, flags=re.I)
            text = cls._HTML_TAG.sub("", text)

        # 3. Control characters
        text = cls._CONTROL.sub("", text)

        # 4. PDF artifacts
        if strip_pdf_artifacts:
            text = cls._PAGE_NUM.sub("\n", text)
            text = cls._PDF_HEADER.sub("", text)

        # 5. OCR noise
        text = cls._OCR_NOISE.sub("", text)

        # 6. Whitespace normalization
        text = cls._MULTI_SPACE.sub(" ", text)
        text = cls._MULTI_BLANK.sub("\n\n", text)

        # 7. Strip each line
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)

        return text.strip()

    @classmethod
    def clean_section_text(cls, text: str) -> str:
        """Clean text that is already identified as a section body."""
        text = cls.clean(text)
        # Collapse single newlines within paragraphs (preserve double newlines)
        text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
        return text.strip()


# ═══════════════════════════════════════════════════════════════════════════
#  STRUCTURAL DETECTION PATTERNS
# ═══════════════════════════════════════════════════════════════════════════

class LegalPatterns:
    """
    Compiled regex patterns for detecting Indian legal text structures.
    All patterns are designed for re.MULTILINE usage.
    """

    # ── Top-level structural markers ──

    # PART I, PART II, Part IV-A, etc.
    PART = re.compile(
        r"^(?:PART|Part)\s+([IVXLC]+-?[A-Z]?)\b[.\s—:–-]*(.*)$",
        re.MULTILINE,
    )

    # CHAPTER I, CHAPTER IV, Chapter XIIA
    CHAPTER = re.compile(
        r"^(?:CHAPTER|Chapter)\s+([IVXLC]+[A-Z]?|\d+[A-Z]?)\b[.\s—:–-]*(.*)$",
        re.MULTILINE,
    )

    # SCHEDULE I, First Schedule, THE FIRST SCHEDULE
    SCHEDULE = re.compile(
        r"^(?:THE\s+)?(?:SCHEDULE|Schedule)\s*([IVXLC]*|\d*|FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH|ELEVENTH|TWELFTH)?\b[.\s—:–-]*(.*)$",
        re.MULTILINE | re.I,
    )

    # ── Section / Article / Rule headers ──

    # "Section 302." / "302." / "Section 302A.—" / "Sec. 5"
    SECTION = re.compile(
        r"^(?:Section|Sec\.?)\s*(\d+[A-Za-z]*)\s*[.—:–-]+\s*(.*)$"
        r"|"
        r"^(\d+[A-Za-z]*)\.\s*[—–-]?\s*(.+)$",
        re.MULTILINE,
    )

    # "Article 21." / "Article 14A" / "Art. 21"
    ARTICLE = re.compile(
        r"^(?:Article|Art\.?)\s*(\d+[A-Za-z]*)\s*[.—:–-]*\s*(.*)$",
        re.MULTILINE,
    )

    # "Rule 5." / "Rule 12A"
    RULE = re.compile(
        r"^(?:Rule)\s*(\d+[A-Za-z]*)\s*[.—:–-]*\s*(.*)$",
        re.MULTILINE,
    )

    # ── Sub-structural markers ──

    # Sub-section: "(1)", "(2)", "(2A)"
    SUBSECTION = re.compile(
        r"^\((\d+[A-Za-z]?)\)\s*(.*)",
        re.MULTILINE,
    )

    # Clause: "(a)", "(b)", "(ii)", "(iv)"
    CLAUSE = re.compile(
        r"^\(([a-z]{1,3}|[ivxlc]+)\)\s*(.*)",
        re.MULTILINE,
    )

    # Sub-clause: "(i)", "(ii)" when nested inside a clause
    SUBCLAUSE = re.compile(
        r"^\(([ivxlc]+|[A-Z])\)\s*(.*)",
        re.MULTILINE,
    )

    # ── Special markers ──

    # "Provided that..." / "Provided further that..."
    PROVISO = re.compile(
        r"^(?:Provided|Proviso)\s+(?:further\s+)?that\b[:\s—–-]*(.*)",
        re.MULTILINE | re.I,
    )

    # "Explanation.—" / "Explanation I.—" / "Explanation 1.—"
    EXPLANATION = re.compile(
        r"^Explanation\s*([IVXLC\d]*)\s*[.—:–-]+(.*)",
        re.MULTILINE | re.I,
    )

    # Amendment notes: "[Ins. by Act 25 of 2020]" / "[Substituted...]"
    AMENDMENT = re.compile(
        r"\[(?:Ins(?:erted)?|Subs(?:tituted)?|Omitted|Added|Amended|Rep(?:ealed)?)"
        r"[^\]]{3,200}\]",
        re.I,
    )

    # Definitions: "\"theft\" means" / "'theft' means"
    DEFINITION = re.compile(
        r"""[""'']([A-Za-z][A-Za-z\s-]{1,60})[""'']\s+means\b""",
        re.I,
    )

    # Short title / Preamble: "An Act to..." / "This Act may be called..."
    SHORT_TITLE = re.compile(
        r"(?:An Act to\b|This Act may be called\b|Short title)",
        re.I,
    )

    # Punishment: "shall be punished with" / "punishable with"
    PUNISHMENT = re.compile(
        r"(?:shall be punish(?:ed|able)|punish(?:ed|able))\s+with\s+(.+?)(?:\.|$)",
        re.I | re.DOTALL,
    )


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION SPLITTER
# ═══════════════════════════════════════════════════════════════════════════

class SectionSplitter:
    """
    Splits a cleaned legal document into individual sections/articles
    based on structural markers.
    """

    @staticmethod
    def detect_document_type(text: str) -> str:
        """
        Detect whether the document uses Section, Article, or Rule numbering.
        Returns: "section", "article", or "rule"
        """
        sec_count = len(LegalPatterns.SECTION.findall(text))
        art_count = len(LegalPatterns.ARTICLE.findall(text))
        rule_count = len(LegalPatterns.RULE.findall(text))

        if art_count > sec_count and art_count > rule_count:
            return "article"
        if rule_count > sec_count and rule_count > art_count:
            return "rule"
        return "section"

    @staticmethod
    def split_into_sections(text: str, doc_type: str = "section") -> List[Tuple[str, str, str]]:
        """
        Split text into (number, heading, body) tuples at section/article/rule
        boundaries.

        Returns:
            List of (number, heading, body_text) tuples.
        """
        if doc_type == "article":
            pattern = LegalPatterns.ARTICLE
        elif doc_type == "rule":
            pattern = LegalPatterns.RULE
        else:
            pattern = LegalPatterns.SECTION

        matches = list(pattern.finditer(text))
        if not matches:
            return []

        results: List[Tuple[str, str, str]] = []

        for i, m in enumerate(matches):
            # Extract number and heading from matched groups
            groups = m.groups()
            # SECTION pattern has alternation with 4 groups
            if len(groups) == 4:
                number = groups[0] or groups[2] or ""
                heading = (groups[1] or groups[3] or "").strip()
            else:
                number = groups[0] or ""
                heading = groups[1].strip() if len(groups) > 1 and groups[1] else ""

            # Body extends from end of this match to start of next match
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start:end].strip()

            results.append((number.strip(), heading, body))

        return results

    @staticmethod
    def find_parts_and_chapters(text: str) -> List[Tuple[str, str, str, int]]:
        """
        Find PART and CHAPTER markers with their positions.

        Returns:
            List of (type, number, heading, position) tuples.
        """
        markers: List[Tuple[str, str, str, int]] = []

        for m in LegalPatterns.PART.finditer(text):
            markers.append(("part", m.group(1), m.group(2).strip(), m.start()))

        for m in LegalPatterns.CHAPTER.finditer(text):
            markers.append(("chapter", m.group(1), m.group(2).strip(), m.start()))

        for m in LegalPatterns.SCHEDULE.finditer(text):
            num = m.group(1) or ""
            markers.append(("schedule", num.strip(), m.group(2).strip(), m.start()))

        markers.sort(key=lambda x: x[3])
        return markers


# ═══════════════════════════════════════════════════════════════════════════
#  SECTION DETAIL PARSER
# ═══════════════════════════════════════════════════════════════════════════

class SectionDetailParser:
    """
    Parses the internal structure of a single section body:
    sub-sections, clauses, provisos, explanations, definitions,
    amendment notes, and punishment clauses.
    """

    @staticmethod
    def parse_subsections(body: str) -> List[Dict[str, str]]:
        """Extract numbered sub-sections: (1), (2), (2A), etc."""
        subs: List[Dict[str, str]] = []
        matches = list(LegalPatterns.SUBSECTION.finditer(body))
        for i, m in enumerate(matches):
            num = m.group(1)
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
            text = (m.group(2) + " " + body[start:end]).strip()
            # Stop at next sub-section boundary
            text = re.split(r"\n\(\d+[A-Za-z]?\)", text)[0].strip()
            subs.append({"number": num, "text": text})
        return subs

    @staticmethod
    def parse_clauses(body: str) -> List[Dict[str, str]]:
        """Extract lettered clauses: (a), (b), etc."""
        clauses: List[Dict[str, str]] = []
        matches = list(LegalPatterns.CLAUSE.finditer(body))
        for i, m in enumerate(matches):
            letter = m.group(1)
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
            text = (m.group(2) + " " + body[start:end]).strip()
            text = re.split(r"\n\([a-z]{1,3}\)", text)[0].strip()
            clauses.append({"letter": letter, "text": text})
        return clauses

    @staticmethod
    def parse_provisos(body: str) -> List[str]:
        """Extract proviso clauses."""
        provisos: List[str] = []
        for m in LegalPatterns.PROVISO.finditer(body):
            text = m.group(1).strip()
            if text:
                provisos.append(text)
        return provisos

    @staticmethod
    def parse_explanations(body: str) -> List[str]:
        """Extract explanation notes."""
        explanations: List[str] = []
        for m in LegalPatterns.EXPLANATION.finditer(body):
            num = m.group(1).strip()
            text = m.group(2).strip()
            prefix = f"Explanation {num}: " if num else ""
            explanations.append(f"{prefix}{text}")
        return explanations

    @staticmethod
    def parse_amendment_notes(body: str) -> List[str]:
        """Extract amendment bracket notes."""
        return [m.group(0) for m in LegalPatterns.AMENDMENT.finditer(body)]

    @staticmethod
    def parse_definitions(body: str) -> List[Dict[str, str]]:
        """Extract definition terms and their text."""
        defs: List[Dict[str, str]] = []
        for m in LegalPatterns.DEFINITION.finditer(body):
            term = m.group(1).strip()
            # Get the rest of the sentence after "means"
            start = m.end()
            rest = body[start:start + 1000]
            # End at period or semicolon
            end_match = re.search(r"[.;]", rest)
            definition_text = rest[:end_match.start()].strip() if end_match else rest.strip()
            defs.append({"term": term, "definition": definition_text})
        return defs

    @staticmethod
    def extract_punishment(body: str) -> Optional[str]:
        """Extract punishment clause if present."""
        m = LegalPatterns.PUNISHMENT.search(body)
        if m:
            return m.group(1).strip()[:500]
        return None


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN PARSER
# ═══════════════════════════════════════════════════════════════════════════

class LegalTextParser:
    """
    Complete legal text parser.

    Takes raw text of an Indian statute, Constitution part, or rules,
    and produces structured JSON output.

    Example:
        parser = LegalTextParser()
        result = parser.parse(raw_text, act_name="BNS 2023")
        print(result.to_json())
    """

    def __init__(self):
        self.cleaner = TextCleaner()
        self.splitter = SectionSplitter()
        self.detail_parser = SectionDetailParser()

    def parse(
        self,
        raw_text: str,
        act_name: str = "Unknown Act",
        source: str = "",
        build_tree: bool = False,
    ) -> ParseResult:
        """
        Parse raw legal text into structured output.

        Args:
            raw_text: Raw text (HTML, plain, or PDF-extracted).
            act_name: Name of the act/statute.
            source: Source URL or file path.
            build_tree: If True, also build hierarchical tree.

        Returns:
            ParseResult with sections, optional tree, and stats.
        """
        logger.info("Parsing '%s' (%d chars)...", act_name, len(raw_text))

        # Step 1: Clean
        cleaned = self.cleaner.clean(raw_text)
        logger.info("Cleaned: %d → %d chars", len(raw_text), len(cleaned))

        # Step 2: Detect document type
        doc_type = self.splitter.detect_document_type(cleaned)
        logger.info("Document type: %s", doc_type)

        # Step 3: Find structural markers (parts, chapters)
        markers = self.splitter.find_parts_and_chapters(cleaned)

        # Step 4: Split into sections
        raw_sections = self.splitter.split_into_sections(cleaned, doc_type)
        logger.info("Found %d sections/articles", len(raw_sections))

        # Step 5: Build context map (which part/chapter each section belongs to)
        context_map = self._build_context_map(markers, raw_sections, cleaned, doc_type)

        # Step 6: Parse each section in detail
        sections: List[ParsedSection] = []
        stats = {
            "total_sections": 0,
            "sections_with_subsections": 0,
            "sections_with_provisos": 0,
            "sections_with_explanations": 0,
            "sections_with_definitions": 0,
            "sections_with_amendments": 0,
            "sections_with_punishment": 0,
        }

        for idx, (number, heading, body) in enumerate(raw_sections):
            # Clean section body
            clean_body = self.cleaner.clean_section_text(body)

            # Parse internal structure
            subsections = self.detail_parser.parse_subsections(clean_body)
            clauses = self.detail_parser.parse_clauses(clean_body)
            provisos = self.detail_parser.parse_provisos(clean_body)
            explanations = self.detail_parser.parse_explanations(clean_body)
            amendments = self.detail_parser.parse_amendment_notes(clean_body)
            definitions = self.detail_parser.parse_definitions(clean_body)
            punishment = self.detail_parser.extract_punishment(clean_body)

            # Determine section number label
            if doc_type == "article":
                sec_num = f"Article {number}" if number else f"Article-{idx+1}"
            elif doc_type == "rule":
                sec_num = f"Rule {number}" if number else f"Rule-{idx+1}"
            else:
                sec_num = number or str(idx + 1)

            # Determine title
            title = heading or f"Section {sec_num}"
            if not heading and subsections:
                # Use first few words of body as title
                first_line = clean_body.split("\n")[0][:100]
                title = first_line.rstrip(".,;: ")

            # Build full text (main body without sub-structural noise for storage)
            full_text = clean_body
            if punishment:
                full_text += f"\n\nPunishment: {punishment}"

            ctx = context_map.get(idx, {})

            section = ParsedSection(
                act_name=act_name,
                section_number=sec_num,
                title=title,
                full_text=full_text,
                sub_sections=subsections + clauses,
                provisos=provisos,
                explanations=explanations,
                amendment_notes=amendments,
                definitions=definitions,
                chapter=ctx.get("chapter", ""),
                part=ctx.get("part", ""),
            )
            sections.append(section)

            # Update stats
            stats["total_sections"] += 1
            if subsections or clauses:
                stats["sections_with_subsections"] += 1
            if provisos:
                stats["sections_with_provisos"] += 1
            if explanations:
                stats["sections_with_explanations"] += 1
            if definitions:
                stats["sections_with_definitions"] += 1
            if amendments:
                stats["sections_with_amendments"] += 1
            if punishment:
                stats["sections_with_punishment"] += 1

        result = ParseResult(
            act_name=act_name,
            source=source,
            sections=sections,
            stats=stats,
        )

        # Step 7: Build tree if requested
        if build_tree:
            result.tree = self._build_tree(act_name, markers, sections, cleaned, doc_type)

        logger.info(
            "Parse complete: %d sections, %d with subs, %d provisos, %d definitions",
            stats["total_sections"],
            stats["sections_with_subsections"],
            stats["sections_with_provisos"],
            stats["sections_with_definitions"],
        )
        return result

    def parse_file(
        self,
        filepath: str,
        act_name: str = "",
        output: Optional[str] = None,
        build_tree: bool = False,
    ) -> ParseResult:
        """
        Parse a file containing raw legal text.

        Supports: .txt, .html, .htm files.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            raw_text = f.read()

        if not act_name:
            act_name = os.path.splitext(os.path.basename(filepath))[0]

        result = self.parse(
            raw_text,
            act_name=act_name,
            source=filepath,
            build_tree=build_tree,
        )

        if output:
            os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
            with open(output, "w", encoding="utf-8") as f:
                f.write(result.to_json())
            logger.info("Written → %s", output)

        return result

    # ── Internal helpers ──

    def _build_context_map(
        self,
        markers: List[Tuple[str, str, str, int]],
        raw_sections: List[Tuple[str, str, str]],
        full_text: str,
        doc_type: str,
    ) -> Dict[int, Dict[str, str]]:
        """
        Map each section index to its containing Part and Chapter.
        Uses positional information from markers.
        """
        if not markers:
            return {}

        # Find positions of each section in the full text
        if doc_type == "article":
            pattern = LegalPatterns.ARTICLE
        elif doc_type == "rule":
            pattern = LegalPatterns.RULE
        else:
            pattern = LegalPatterns.SECTION

        section_positions = [m.start() for m in pattern.finditer(full_text)]

        context_map: Dict[int, Dict[str, str]] = {}
        current_part = ""
        current_chapter = ""

        for idx, pos in enumerate(section_positions):
            # Find the most recent part and chapter before this position
            for m_type, m_num, m_heading, m_pos in markers:
                if m_pos > pos:
                    break
                label = f"{m_num} — {m_heading}" if m_heading else m_num
                if m_type == "part":
                    current_part = label
                elif m_type == "chapter":
                    current_chapter = label

            context_map[idx] = {
                "part": current_part,
                "chapter": current_chapter,
            }

        return context_map

    def _build_tree(
        self,
        act_name: str,
        markers: List[Tuple[str, str, str, int]],
        sections: List[ParsedSection],
        full_text: str,
        doc_type: str,
    ) -> ParsedNode:
        """Build a hierarchical tree of the act."""
        root = ParsedNode(
            node_type=NodeType.ACT,
            number="",
            heading=act_name,
            text="",
        )

        # Group sections by part/chapter
        current_part_node: Optional[ParsedNode] = None
        current_chapter_node: Optional[ParsedNode] = None

        for sec in sections:
            # Create section node
            sec_type = NodeType.ARTICLE if doc_type == "article" else (
                NodeType.RULE if doc_type == "rule" else NodeType.SECTION
            )
            sec_node = ParsedNode(
                node_type=sec_type,
                number=sec.section_number,
                heading=sec.title,
                text=sec.full_text,
                amendment_notes=sec.amendment_notes,
                is_definition=bool(sec.definitions),
                defined_term=sec.definitions[0]["term"] if sec.definitions else None,
            )

            # Add sub-section children
            for sub in sec.sub_sections:
                child_type = NodeType.SUBSECTION if "number" in sub else NodeType.CLAUSE
                child_num = sub.get("number", sub.get("letter", ""))
                sec_node.children.append(ParsedNode(
                    node_type=child_type,
                    number=child_num,
                    heading="",
                    text=sub["text"],
                ))

            # Add proviso children
            for prov in sec.provisos:
                sec_node.children.append(ParsedNode(
                    node_type=NodeType.PROVISO,
                    number="",
                    heading="Proviso",
                    text=prov,
                ))

            # Add explanation children
            for expl in sec.explanations:
                sec_node.children.append(ParsedNode(
                    node_type=NodeType.EXPLANATION,
                    number="",
                    heading="Explanation",
                    text=expl,
                ))

            # Determine parent
            if sec.part and (not current_part_node or current_part_node.heading != sec.part):
                current_part_node = ParsedNode(
                    node_type=NodeType.PART,
                    number=sec.part.split(" — ")[0] if " — " in sec.part else sec.part,
                    heading=sec.part,
                    text="",
                )
                root.children.append(current_part_node)
                current_chapter_node = None

            if sec.chapter and (not current_chapter_node or current_chapter_node.heading != sec.chapter):
                current_chapter_node = ParsedNode(
                    node_type=NodeType.CHAPTER,
                    number=sec.chapter.split(" — ")[0] if " — " in sec.chapter else sec.chapter,
                    heading=sec.chapter,
                    text="",
                )
                parent = current_part_node or root
                parent.children.append(current_chapter_node)

            # Attach section to innermost container
            parent = current_chapter_node or current_part_node or root
            parent.children.append(sec_node)

        return root


# ═══════════════════════════════════════════════════════════════════════════
#  CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

def main():
    import argparse

    ap = argparse.ArgumentParser(
        prog="python -m data_pipeline.parser",
        description="YAMA AI — Legal Text Parser: Clean, detect, and structure Indian legal text.",
    )
    ap.add_argument("--input", "-i", required=True, help="Input file path (txt, html)")
    ap.add_argument("--act", "-a", default="", help="Act name (auto-detected from filename if omitted)")
    ap.add_argument("--output", "-o", default=None, help="Output JSON file path")
    ap.add_argument(
        "--format", "-f", choices=["flat", "tree", "records"],
        default="flat",
        help="Output format: flat sections, hierarchical tree, or crawler-compatible records",
    )
    ap.add_argument("--stats", action="store_true", help="Print parsing statistics")
    ap.add_argument("--store", action="store_true", help="Store parsed records into DB + ChromaDB")
    args = ap.parse_args()

    print()
    print("═" * 60)
    print("  YAMA AI — Legal Text Parser")
    print("═" * 60)
    print(f"  Input:   {args.input}")
    print(f"  Act:     {args.act or '(auto-detect)'}")
    print(f"  Format:  {args.format}")
    print(f"  Output:  {args.output or '(stdout)'}")
    print("═" * 60)
    print()

    parser = LegalTextParser()
    result = parser.parse_file(
        args.input,
        act_name=args.act,
        build_tree=(args.format == "tree"),
    )

    print(f"✅ Parsed {result.stats.get('total_sections', 0)} sections from '{result.act_name}'")

    if args.stats:
        print("\n📊 Statistics:")
        for k, v in result.stats.items():
            print(f"   {k}: {v}")

    # Generate output
    if args.format == "records":
        records = result.to_records()
        output_data = {
            "metadata": {
                "act_name": result.act_name,
                "source": result.source,
                "total_records": len(records),
            },
            "records": [r.to_dict() for r in records],
        }
        json_str = json.dumps(output_data, ensure_ascii=False, indent=2)
    elif args.format == "tree":
        json_str = result.to_json()
    else:
        json_str = result.to_json()

    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json_str)
        print(f"\n📄 Written → {args.output}")
    else:
        print("\n" + json_str[:2000])
        if len(json_str) > 2000:
            print(f"\n... ({len(json_str)} total chars, use --output to save)")

    # Store into DB
    if args.store:
        print("\n💾 Storing into database + ChromaDB...")
        from data_pipeline.crawler import LegalCrawler
        records = result.to_records()
        with LegalCrawler() as crawler:
            stats = crawler.store_records(records, source_name="parser")
        print(f"   Inserted: {stats['inserted']}, Updated: {stats['updated']}, Skipped: {stats['skipped']}")

    print("\n✅ Done!")


if __name__ == "__main__":
    main()
