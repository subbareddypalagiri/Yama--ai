"""
YAMA AI — Data Exporter
Exports legal data from the database into multiple formats:
    - JSON (for API consumption)
    - CSV (for analysis and spreadsheets)
    - SQL INSERT statements (for database import)
    - Embedding-ready JSONL (for vector DB bulk loading)

Usage:
    from ingestion.exporter import DataExporter
    exporter = DataExporter()
    exporter.export_json("output/laws.json")
    exporter.export_csv("output/laws.csv")
    exporter.export_sql("output/laws.sql")
    exporter.export_embeddings("output/laws.jsonl")
"""

import csv
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db.database import SessionLocal, engine
from app.db.models import Base, LawSection
from ingestion.config import ingestion_settings

logger = logging.getLogger("yama_ai.ingestion.exporter")


class DataExporter:
    """
    Exports legal records from the SQL database into various file formats.
    """

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or ingestion_settings.export_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _fetch_records(self, category: Optional[str] = None,
                       jurisdiction: Optional[str] = None) -> List[Dict]:
        """Fetch records from DB as list of dicts."""
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            query = db.query(LawSection).filter_by(is_active=True)
            if category:
                query = query.filter_by(category=category)
            if jurisdiction:
                query = query.filter_by(jurisdiction=jurisdiction)

            records = []
            for row in query.order_by(LawSection.act_name, LawSection.section_number).all():
                records.append({
                    "id": row.id,
                    "act_name": row.act_name,
                    "section_number": row.section_number,
                    "title": row.title,
                    "description": row.description,
                    "keywords": row.keywords or "",
                    "category": row.category,
                    "punishment": row.punishment or "",
                    "old_law_reference": row.old_law_reference or "",
                    "jurisdiction": row.jurisdiction or "central",
                    "state_name": row.state_name or "",
                    "law_type": row.law_type or "act",
                    "source_url": row.source_url or "",
                    "content_hash": row.content_hash or "",
                    "created_at": str(row.created_at) if row.created_at else "",
                    "updated_at": str(row.updated_at) if row.updated_at else "",
                })
            return records
        finally:
            db.close()

    # ── JSON Export ──

    def export_json(self, filename: str = "laws.json", **filters) -> str:
        """
        Export all law sections as a structured JSON file.

        Returns:
            Path to the generated file.
        """
        records = self._fetch_records(**filters)
        filepath = os.path.join(self.output_dir, filename)

        output = {
            "metadata": {
                "exported_at": datetime.utcnow().isoformat(),
                "total_records": len(records),
                "source": "YAMA AI Legal Database",
                "version": "1.0",
            },
            "laws": records,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        logger.info(f"Exported {len(records)} records to JSON: {filepath}")
        return filepath

    # ── CSV Export ──

    def export_csv(self, filename: str = "laws.csv", **filters) -> str:
        """
        Export all law sections as a CSV file.

        Returns:
            Path to the generated file.
        """
        records = self._fetch_records(**filters)
        filepath = os.path.join(self.output_dir, filename)

        if not records:
            logger.warning("No records to export to CSV")
            return filepath

        fieldnames = list(records[0].keys())

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

        logger.info(f"Exported {len(records)} records to CSV: {filepath}")
        return filepath

    # ── SQL Export ──

    def export_sql(self, filename: str = "laws.sql", **filters) -> str:
        """
        Export as SQL INSERT statements for PostgreSQL/SQLite import.

        Returns:
            Path to the generated file.
        """
        records = self._fetch_records(**filters)
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("-- YAMA AI Legal Database Export\n")
            f.write(f"-- Generated: {datetime.utcnow().isoformat()}\n")
            f.write(f"-- Records: {len(records)}\n\n")

            # Table creation DDL
            f.write("""CREATE TABLE IF NOT EXISTS law_sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    act_name VARCHAR(500) NOT NULL,
    section_number VARCHAR(50) NOT NULL,
    title VARCHAR(1000) NOT NULL,
    description TEXT NOT NULL,
    keywords TEXT,
    category VARCHAR(100) NOT NULL DEFAULT 'general',
    punishment TEXT,
    old_law_reference VARCHAR(500),
    jurisdiction VARCHAR(50) DEFAULT 'central',
    state_name VARCHAR(200),
    law_type VARCHAR(100) DEFAULT 'act',
    source_url VARCHAR(2000),
    content_hash VARCHAR(64),
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);\n\n""")

            for rec in records:
                values = (
                    self._sql_escape(rec["act_name"]),
                    self._sql_escape(rec["section_number"]),
                    self._sql_escape(rec["title"]),
                    self._sql_escape(rec["description"]),
                    self._sql_escape(rec["keywords"]),
                    self._sql_escape(rec["category"]),
                    self._sql_escape(rec["punishment"]),
                    self._sql_escape(rec["old_law_reference"]),
                    self._sql_escape(rec["jurisdiction"]),
                    self._sql_escape(rec["state_name"]),
                    self._sql_escape(rec["law_type"]),
                    self._sql_escape(rec["source_url"]),
                    self._sql_escape(rec["content_hash"]),
                )
                f.write(
                    "INSERT INTO law_sections "
                    "(act_name, section_number, title, description, keywords, "
                    "category, punishment, old_law_reference, jurisdiction, "
                    "state_name, law_type, source_url, content_hash) VALUES\n"
                    f"({', '.join(values)});\n"
                )

        logger.info(f"Exported {len(records)} records to SQL: {filepath}")
        return filepath

    # ── Embeddings Export (JSONL for ChromaDB bulk load) ──

    def export_embeddings(self, filename: str = "laws_embeddings.jsonl", **filters) -> str:
        """
        Export as JSONL where each line is a document ready for embedding.

        Format per line:
        {"id": "...", "text": "...", "metadata": {...}}

        Returns:
            Path to the generated file.
        """
        records = self._fetch_records(**filters)
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            for rec in records:
                text = (
                    f"{rec['act_name']} — Section {rec['section_number']}: {rec['title']}\n\n"
                    f"{rec['description']}"
                )
                doc = {
                    "id": str(rec["id"]),
                    "text": text,
                    "metadata": {
                        "act_name": rec["act_name"],
                        "section_number": rec["section_number"],
                        "title": rec["title"],
                        "category": rec["category"],
                        "jurisdiction": rec["jurisdiction"],
                        "law_type": rec["law_type"],
                    },
                }
                f.write(json.dumps(doc, ensure_ascii=False) + "\n")

        logger.info(f"Exported {len(records)} embedding docs to JSONL: {filepath}")
        return filepath

    # ── Export All Formats ──

    def export_all(self, prefix: str = "yama_ai_laws", **filters) -> Dict[str, str]:
        """Export in all formats at once."""
        return {
            "json": self.export_json(f"{prefix}.json", **filters),
            "csv": self.export_csv(f"{prefix}.csv", **filters),
            "sql": self.export_sql(f"{prefix}.sql", **filters),
            "embeddings": self.export_embeddings(f"{prefix}_embeddings.jsonl", **filters),
        }

    @staticmethod
    def _sql_escape(value) -> str:
        """Escape a value for SQL INSERT."""
        if value is None or value == "":
            return "NULL"
        s = str(value).replace("'", "''")
        return f"'{s}'"
