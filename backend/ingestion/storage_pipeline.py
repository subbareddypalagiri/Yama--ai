"""
YAMA AI — Storage Pipeline
Stores cleaned legal records into both PostgreSQL/SQLite and ChromaDB.

Pipeline:
    LegalRecord dicts → Deduplicate → Upsert to SQL DB → Generate embeddings → Upsert to ChromaDB

Features:
    - Batch upserts for performance
    - Content-hash based change detection (skip unchanged records)
    - Transaction safety
    - Logging of inserted/updated/skipped counts
"""

import logging
from datetime import datetime
from typing import Dict, List, Tuple

from sqlalchemy.orm import Session

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db.database import SessionLocal, engine
from app.db.models import Base, LawSection, IngestionLog
from app.services.retrieval_engine.vector_store import get_vector_store
from ingestion.config import ingestion_settings

logger = logging.getLogger("yama_ai.ingestion.storage")


class StoragePipeline:
    """
    Stores legal records into SQL DB and ChromaDB vector store.
    Handles deduplication, upserts, and embedding generation.
    """

    def __init__(self):
        self.vector_store = None
        self._stats = {
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
            "vector_indexed": 0,
        }

    @property
    def stats(self) -> Dict:
        return self._stats.copy()

    def store(self, records: List[Dict], source_name: str = "manual") -> Dict:
        """
        Store a batch of cleaned, tagged legal records.

        Args:
            records: List of cleaned record dicts (from DataCleaner + MetadataTagger).
            source_name: Name of the data source for logging.

        Returns:
            Stats dict with counts of inserted, updated, skipped, vector_indexed.
        """
        self._stats = {"inserted": 0, "updated": 0, "skipped": 0, "vector_indexed": 0}

        # Ensure tables exist
        Base.metadata.create_all(bind=engine)

        db = SessionLocal()
        log_entry = IngestionLog(
            source_name=source_name,
            run_type="incremental",
            status="running",
            records_found=len(records),
        )

        try:
            db.add(log_entry)
            db.commit()

            # Process in batches
            batch_size = ingestion_settings.db_batch_size
            for i in range(0, len(records), batch_size):
                batch = records[i : i + batch_size]
                self._process_batch(db, batch)

            # Update log
            log_entry.status = "completed"
            log_entry.records_inserted = self._stats["inserted"]
            log_entry.records_updated = self._stats["updated"]
            log_entry.records_skipped = self._stats["skipped"]
            log_entry.completed_at = datetime.utcnow()
            db.commit()

            logger.info(
                f"[{source_name}] Storage complete: "
                f"{self._stats['inserted']} inserted, "
                f"{self._stats['updated']} updated, "
                f"{self._stats['skipped']} skipped"
            )

            # Index into ChromaDB
            self._index_to_vector_db(db)

        except Exception as e:
            db.rollback()
            log_entry.status = "failed"
            log_entry.error_message = str(e)[:2000]
            db.commit()
            logger.error(f"[{source_name}] Storage failed: {e}")
            raise
        finally:
            db.close()

        return self._stats

    def _process_batch(self, db: Session, batch: List[Dict]):
        """Process a single batch of records: upsert to SQL DB."""
        for record in batch:
            act_name = record.get("act_name", "")
            sec_num = record.get("section_number", "")
            content_hash = record.get("content_hash", "")

            # Check if record already exists
            existing = (
                db.query(LawSection)
                .filter_by(act_name=act_name, section_number=sec_num)
                .first()
            )

            if existing:
                # Compare content hash — skip if unchanged
                if existing.content_hash == content_hash:
                    self._stats["skipped"] += 1
                    continue

                # Update changed record
                existing.title = record.get("title", existing.title)
                existing.description = record.get("description", existing.description)
                existing.keywords = record.get("keywords", existing.keywords)
                existing.category = record.get("category", existing.category)
                existing.punishment = record.get("punishment", existing.punishment)
                existing.old_law_reference = record.get("old_law_reference", existing.old_law_reference)
                existing.jurisdiction = record.get("jurisdiction", existing.jurisdiction)
                existing.state_name = record.get("state_name", existing.state_name)
                existing.law_type = record.get("law_type", existing.law_type)
                existing.source_url = record.get("source_url", existing.source_url)
                existing.content_hash = content_hash
                self._stats["updated"] += 1

            else:
                # Insert new record
                new_record = LawSection(
                    act_name=act_name,
                    section_number=sec_num,
                    title=record.get("title", ""),
                    description=record.get("description", ""),
                    keywords=record.get("keywords", ""),
                    category=record.get("category", "general"),
                    punishment=record.get("punishment"),
                    old_law_reference=record.get("old_law_reference"),
                    jurisdiction=record.get("jurisdiction", "central"),
                    state_name=record.get("state_name"),
                    law_type=record.get("law_type", "act"),
                    source_url=record.get("source_url"),
                    content_hash=content_hash,
                    is_active=True,
                )
                db.add(new_record)
                self._stats["inserted"] += 1

        db.commit()

    def _index_to_vector_db(self, db: Session):
        """Index all law sections into ChromaDB for semantic search."""
        try:
            vs = get_vector_store()
        except Exception as e:
            logger.warning(f"ChromaDB not available: {e}")
            return

        # Fetch all active law sections
        sections = db.query(LawSection).filter_by(is_active=True).all()

        laws_for_vector = []
        for section in sections:
            text = (
                f"{section.act_name} — Section {section.section_number}: {section.title}\n\n"
                f"{section.description}"
            )
            metadata = {
                "act_name": section.act_name or "",
                "section_number": section.section_number or "",
                "title": section.title or "",
                "category": section.category or "general",
                "jurisdiction": section.jurisdiction or "central",
                "law_type": section.law_type or "act",
            }
            if section.state_name:
                metadata["state_name"] = section.state_name
            if section.punishment:
                metadata["punishment"] = section.punishment[:200]

            laws_for_vector.append({
                "id": str(section.id),
                "text": text,
                "metadata": metadata,
            })

        if laws_for_vector:
            # Batch upsert
            batch_size = ingestion_settings.vector_batch_size
            for i in range(0, len(laws_for_vector), batch_size):
                batch = laws_for_vector[i : i + batch_size]
                vs.add_laws_batch(batch)

            self._stats["vector_indexed"] = len(laws_for_vector)
            logger.info(f"Indexed {len(laws_for_vector)} sections into ChromaDB")


def run_storage_pipeline(records: List[Dict], source_name: str = "manual") -> Dict:
    """Convenience function to run the full storage pipeline."""
    pipeline = StoragePipeline()
    return pipeline.store(records, source_name)
