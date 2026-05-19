"""
YAMA AI — Legal Database Store
=============================================================================
Python module for inserting, updating, querying, and managing legal records
in the 'laws' table. Works with both PostgreSQL and SQLite.

Features:
    • Single & batch insert with upsert (ON CONFLICT UPDATE)
    • Content-hash dedup — skips unchanged records automatically
    • Full-text search (PostgreSQL ts_vector / SQLite LIKE fallback)
    • Filter by category, jurisdiction, state, law_type, act_name
    • Amendment tracking (auto-flags amended records)
    • Bulk import from JSON, CSV, or LegalRecord objects
    • Statistics & summary queries
    • ChromaDB vector indexing after insert

Usage:
    from legal_database.store import LegalStore

    store = LegalStore()                        # auto-detects SQLite/PostgreSQL
    store.init_db()                             # create tables if needed

    # Insert single record
    store.insert({
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "section_number": "303",
        "title": "Theft",
        "description": "Whoever intending to take dishonestly...",
        "keywords": "theft, property, dishonest",
    })

    # Batch insert
    store.insert_batch(records)

    # Search
    results = store.search("theft of property")
    results = store.filter(category="criminal", jurisdiction="central")

    # Import from file
    stats = store.import_file("data.json")

CLI:
    cd backend
    python -m legal_database.store init                      # Create tables
    python -m legal_database.store import data.json          # Import from file
    python -m legal_database.store search "theft property"   # Full-text search
    python -m legal_database.store stats                     # Show DB statistics
=============================================================================
"""

import csv
import hashlib
import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

# Backend root for app.* imports
_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Index,
    create_engine, text, inspect, func,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("yama_ai.store")

Base = declarative_base()


# ═══════════════════════════════════════════════════════════════════════════
#  ORM MODEL — maps to the 'laws' table from schema.sql
# ═══════════════════════════════════════════════════════════════════════════

class Law(Base):
    """ORM model for the 'laws' table."""

    __tablename__ = "laws"

    id                = Column(Integer, primary_key=True, autoincrement=True)
    act_name          = Column(String(500), nullable=False, index=True)
    section_number    = Column(String(50), nullable=False)
    title             = Column(String(1000), nullable=False)
    description       = Column(Text, nullable=False)
    keywords          = Column(Text)
    category          = Column(String(100), nullable=False, default="general")
    jurisdiction      = Column(String(50), nullable=False, default="central")
    state_name        = Column(String(200))
    law_type          = Column(String(100), default="act")
    source_url        = Column(String(2000))
    content_hash      = Column(String(64), index=True)
    punishment        = Column(Text)
    old_law_reference = Column(String(500))
    is_amended        = Column(Boolean, default=False)
    amendment_notes   = Column(Text)
    amendment_year    = Column(Integer)
    is_active         = Column(Boolean, default=True)
    created_at        = Column(DateTime(timezone=True), server_default=func.now())
    last_updated      = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("uq_laws_act_section", "act_name", "section_number", unique=True),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "act_name": self.act_name,
            "section_number": self.section_number,
            "title": self.title,
            "description": self.description,
            "keywords": self.keywords,
            "category": self.category,
            "jurisdiction": self.jurisdiction,
            "state_name": self.state_name,
            "law_type": self.law_type,
            "source_url": self.source_url,
            "content_hash": self.content_hash,
            "punishment": self.punishment,
            "old_law_reference": self.old_law_reference,
            "is_amended": self.is_amended,
            "amendment_notes": self.amendment_notes,
            "amendment_year": self.amendment_year,
            "is_active": self.is_active,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }

    def __repr__(self):
        return f"<Law {self.act_name} — S.{self.section_number}>"


# ═══════════════════════════════════════════════════════════════════════════
#  LEGAL STORE
# ═══════════════════════════════════════════════════════════════════════════

class LegalStore:
    """
    High-level interface for the legal database.

    Handles connection, table creation, CRUD, search, import/export,
    and optional ChromaDB vector indexing.
    """

    def __init__(self, database_url: Optional[str] = None):
        """
        Args:
            database_url: SQLAlchemy connection string.
                          Defaults to settings.DATABASE_URL.
        """
        self.database_url = database_url or settings.DATABASE_URL
        self.is_sqlite = self.database_url.startswith("sqlite")

        connect_args = {}
        if self.is_sqlite:
            connect_args["check_same_thread"] = False

        self.engine = create_engine(
            self.database_url,
            pool_pre_ping=not self.is_sqlite,
            connect_args=connect_args,
        )
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)

        # Enable WAL for SQLite
        if self.is_sqlite:
            from sqlalchemy import event
            @event.listens_for(self.engine, "connect")
            def _wal(dbapi_conn, _):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA journal_mode=WAL;")
                cursor.close()

    # ── Session helper ──

    def _session(self) -> Session:
        return self.SessionLocal()

    # ══════════════════════════════════════════════════════════════════════
    #  INITIALIZATION
    # ══════════════════════════════════════════════════════════════════════

    def init_db(self):
        """Create all tables if they don't exist."""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database initialized (%s)", "SQLite" if self.is_sqlite else "PostgreSQL")

    def drop_all(self):
        """Drop all tables (use with caution)."""
        Base.metadata.drop_all(bind=self.engine)
        logger.warning("All tables dropped!")

    def run_schema_sql(self, sql_path: Optional[str] = None):
        """
        Execute the raw schema.sql against PostgreSQL.
        Only needed for PostgreSQL-specific features (triggers, views, extensions).
        """
        if self.is_sqlite:
            logger.info("Skipping schema.sql — SQLite mode (tables created via ORM)")
            return

        if not sql_path:
            sql_path = os.path.join(os.path.dirname(__file__), "schema.sql")

        if not os.path.exists(sql_path):
            logger.warning("schema.sql not found at %s", sql_path)
            return

        with open(sql_path, "r", encoding="utf-8") as f:
            sql = f.read()

        with self.engine.connect() as conn:
            # Split on semicolons and execute each statement
            for statement in sql.split(";"):
                statement = statement.strip()
                if statement and not statement.startswith("--"):
                    try:
                        conn.execute(text(statement))
                    except Exception as exc:
                        logger.warning("SQL statement skipped: %s", str(exc)[:200])
            conn.commit()

        logger.info("schema.sql executed successfully")

    # ══════════════════════════════════════════════════════════════════════
    #  INSERT / UPSERT
    # ══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _compute_hash(record: Dict[str, Any]) -> str:
        """Compute content hash for deduplication."""
        blob = (
            f"{record.get('act_name', '')}|"
            f"{record.get('section_number', '')}|"
            f"{record.get('title', '')}|"
            f"{record.get('description', '')}"
        )
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def insert(self, record: Dict[str, Any]) -> Dict[str, str]:
        """
        Insert or update a single law record.

        Uses act_name + section_number as the unique key.
        Skips if content_hash matches (no changes).

        Returns:
            {"status": "inserted" | "updated" | "skipped"}
        """
        db = self._session()
        try:
            content_hash = record.get("content_hash") or self._compute_hash(record)

            existing = (
                db.query(Law)
                .filter_by(
                    act_name=record["act_name"],
                    section_number=record["section_number"],
                )
                .first()
            )

            if existing:
                if existing.content_hash == content_hash:
                    return {"status": "skipped"}
                # Update
                for col in (
                    "title", "description", "keywords", "category", "jurisdiction",
                    "state_name", "law_type", "source_url", "punishment",
                    "old_law_reference", "is_amended", "amendment_notes",
                    "amendment_year", "is_active",
                ):
                    if col in record and record[col] is not None:
                        setattr(existing, col, record[col])
                existing.content_hash = content_hash
                existing.last_updated = datetime.now(timezone.utc)
                db.commit()
                return {"status": "updated"}

            # Insert new
            law = Law(
                act_name=record["act_name"],
                section_number=record["section_number"],
                title=record.get("title", f"Section {record['section_number']}"),
                description=record["description"],
                keywords=record.get("keywords", ""),
                category=record.get("category", "general"),
                jurisdiction=record.get("jurisdiction", "central"),
                state_name=record.get("state_name"),
                law_type=record.get("law_type", "act"),
                source_url=record.get("source_url"),
                content_hash=content_hash,
                punishment=record.get("punishment"),
                old_law_reference=record.get("old_law_reference"),
                is_amended=record.get("is_amended", False),
                amendment_notes=(
                    json.dumps(record["amendment_notes"])
                    if isinstance(record.get("amendment_notes"), list)
                    else record.get("amendment_notes")
                ),
                amendment_year=record.get("amendment_year"),
                is_active=record.get("is_active", True),
            )
            db.add(law)
            db.commit()
            return {"status": "inserted"}

        except Exception as exc:
            db.rollback()
            logger.error("Insert error: %s", exc)
            raise
        finally:
            db.close()

    def insert_batch(
        self,
        records: List[Dict[str, Any]],
        index_vectors: bool = True,
    ) -> Dict[str, int]:
        """
        Insert/update a batch of law records.

        Args:
            records: List of law dicts.
            index_vectors: If True, re-index ChromaDB after insert.

        Returns:
            {"inserted": N, "updated": N, "skipped": N, "errors": N}
        """
        stats = {"inserted": 0, "updated": 0, "skipped": 0, "errors": 0}

        for rec in records:
            try:
                result = self.insert(rec)
                stats[result["status"]] += 1
            except Exception as exc:
                stats["errors"] += 1
                logger.warning(
                    "Batch error on %s S.%s: %s",
                    rec.get("act_name", "?"), rec.get("section_number", "?"), exc,
                )

        logger.info(
            "Batch: %d inserted, %d updated, %d skipped, %d errors",
            stats["inserted"], stats["updated"], stats["skipped"], stats["errors"],
        )

        if index_vectors and (stats["inserted"] > 0 or stats["updated"] > 0):
            self.index_vectors()

        return stats

    # ══════════════════════════════════════════════════════════════════════
    #  QUERY / SEARCH
    # ══════════════════════════════════════════════════════════════════════

    def get_by_id(self, law_id: int) -> Optional[Dict[str, Any]]:
        """Get a single law by ID."""
        db = self._session()
        try:
            law = db.query(Law).filter_by(id=law_id, is_active=True).first()
            return law.to_dict() if law else None
        finally:
            db.close()

    def get_by_section(self, act_name: str, section_number: str) -> Optional[Dict[str, Any]]:
        """Get a specific section of an act."""
        db = self._session()
        try:
            law = (
                db.query(Law)
                .filter_by(act_name=act_name, section_number=section_number, is_active=True)
                .first()
            )
            return law.to_dict() if law else None
        finally:
            db.close()

    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Full-text search across title and description.

        PostgreSQL: uses ts_vector ranking.
        SQLite: falls back to LIKE matching.
        """
        db = self._session()
        try:
            if not self.is_sqlite:
                # PostgreSQL full-text search with ranking
                sql = text("""
                    SELECT *, ts_rank(
                        to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')),
                        plainto_tsquery('english', :query)
                    ) AS rank
                    FROM laws
                    WHERE is_active = TRUE
                      AND to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
                          @@ plainto_tsquery('english', :query)
                    ORDER BY rank DESC
                    LIMIT :limit
                """)
                rows = db.execute(sql, {"query": query, "limit": limit}).fetchall()
            else:
                # SQLite LIKE fallback
                terms = query.strip().split()
                q = db.query(Law).filter(Law.is_active == True)
                for term in terms:
                    pattern = f"%{term}%"
                    q = q.filter(
                        (Law.title.ilike(pattern)) |
                        (Law.description.ilike(pattern)) |
                        (Law.keywords.ilike(pattern))
                    )
                rows = q.limit(limit).all()
                return [r.to_dict() for r in rows]

            # Convert PostgreSQL rows to dicts
            results = []
            for row in rows:
                results.append({
                    "id": row.id,
                    "act_name": row.act_name,
                    "section_number": row.section_number,
                    "title": row.title,
                    "description": row.description,
                    "keywords": row.keywords,
                    "category": row.category,
                    "jurisdiction": row.jurisdiction,
                    "state_name": row.state_name,
                    "source_url": row.source_url,
                    "rank": float(row.rank) if hasattr(row, "rank") else 0,
                })
            return results

        finally:
            db.close()

    def filter(
        self,
        act_name: Optional[str] = None,
        category: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        state_name: Optional[str] = None,
        law_type: Optional[str] = None,
        is_amended: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Filter laws by any combination of fields.
        """
        db = self._session()
        try:
            q = db.query(Law).filter(Law.is_active == True)

            if act_name:
                q = q.filter(Law.act_name.ilike(f"%{act_name}%"))
            if category:
                q = q.filter(Law.category == category)
            if jurisdiction:
                q = q.filter(Law.jurisdiction == jurisdiction)
            if state_name:
                q = q.filter(Law.state_name.ilike(f"%{state_name}%"))
            if law_type:
                q = q.filter(Law.law_type == law_type)
            if is_amended is not None:
                q = q.filter(Law.is_amended == is_amended)

            q = q.order_by(Law.act_name, Law.section_number)
            rows = q.offset(offset).limit(limit).all()
            return [r.to_dict() for r in rows]

        finally:
            db.close()

    def list_acts(self) -> List[Dict[str, Any]]:
        """List all unique acts with section counts."""
        db = self._session()
        try:
            rows = (
                db.query(
                    Law.act_name,
                    Law.category,
                    Law.jurisdiction,
                    func.count(Law.id).label("section_count"),
                )
                .filter(Law.is_active == True)
                .group_by(Law.act_name, Law.category, Law.jurisdiction)
                .order_by(Law.act_name)
                .all()
            )
            return [
                {
                    "act_name": r.act_name,
                    "category": r.category,
                    "jurisdiction": r.jurisdiction,
                    "section_count": r.section_count,
                }
                for r in rows
            ]
        finally:
            db.close()

    # ══════════════════════════════════════════════════════════════════════
    #  STATISTICS
    # ══════════════════════════════════════════════════════════════════════

    def stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        db = self._session()
        try:
            total = db.query(func.count(Law.id)).filter(Law.is_active == True).scalar() or 0
            central = (
                db.query(func.count(Law.id))
                .filter(Law.is_active == True, Law.jurisdiction == "central")
                .scalar() or 0
            )
            state = (
                db.query(func.count(Law.id))
                .filter(Law.is_active == True, Law.jurisdiction == "state")
                .scalar() or 0
            )
            amended = (
                db.query(func.count(Law.id))
                .filter(Law.is_active == True, Law.is_amended == True)
                .scalar() or 0
            )
            acts = (
                db.query(func.count(func.distinct(Law.act_name)))
                .filter(Law.is_active == True)
                .scalar() or 0
            )

            # Category breakdown
            cat_rows = (
                db.query(Law.category, func.count(Law.id))
                .filter(Law.is_active == True)
                .group_by(Law.category)
                .all()
            )
            categories = {r[0]: r[1] for r in cat_rows}

            # Jurisdiction breakdown
            jur_rows = (
                db.query(Law.jurisdiction, func.count(Law.id))
                .filter(Law.is_active == True)
                .group_by(Law.jurisdiction)
                .all()
            )
            jurisdictions = {r[0] or "central": r[1] for r in jur_rows}

            return {
                "total_laws": total,
                "central_laws": central,
                "state_laws": state,
                "amended_laws": amended,
                "unique_acts": acts,
                "by_category": categories,
                "by_jurisdiction": jurisdictions,
            }

        finally:
            db.close()

    # ══════════════════════════════════════════════════════════════════════
    #  IMPORT FROM FILE
    # ══════════════════════════════════════════════════════════════════════

    def import_file(self, filepath: str, index_vectors: bool = True) -> Dict[str, int]:
        """
        Import records from a JSON or CSV file.

        JSON format: {"laws": [...]} or bare [...]
        CSV format: header row with field names.
        """
        ext = os.path.splitext(filepath)[1].lower()

        if ext == ".json":
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                records = data.get("laws") or data.get("records") or data.get("sections") or []
            else:
                records = []
        elif ext == ".csv":
            records = []
            with open(filepath, "r", encoding="utf-8", newline="") as f:
                for row in csv.DictReader(f):
                    records.append(dict(row))
        else:
            raise ValueError(f"Unsupported file format: {ext}")

        logger.info("Importing %d records from %s", len(records), filepath)
        return self.insert_batch(records, index_vectors=index_vectors)

    # ══════════════════════════════════════════════════════════════════════
    #  EXPORT
    # ══════════════════════════════════════════════════════════════════════

    def export_json(self, filepath: str, **filters) -> int:
        """Export filtered laws to a JSON file."""
        records = self.filter(**filters, limit=100000)
        output = {
            "metadata": {
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "total_records": len(records),
            },
            "laws": records,
        }
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2, default=str)
        logger.info("Exported %d records → %s", len(records), filepath)
        return len(records)

    # ══════════════════════════════════════════════════════════════════════
    #  VECTOR INDEXING (ChromaDB)
    # ══════════════════════════════════════════════════════════════════════

    def index_vectors(self):
        """Re-index all active laws into ChromaDB for semantic search."""
        try:
            from app.services.retrieval_engine.vector_store import get_vector_store
            vs = get_vector_store()
        except Exception as exc:
            logger.warning("ChromaDB not available: %s", exc)
            return

        db = self._session()
        try:
            laws = db.query(Law).filter(Law.is_active == True).all()
            batch = []
            for law in laws:
                doc_text = (
                    f"{law.act_name} — Section {law.section_number}: {law.title}\n\n"
                    f"{law.description}"
                )
                meta = {
                    "act_name": law.act_name or "",
                    "section_number": law.section_number or "",
                    "title": law.title or "",
                    "category": law.category or "general",
                    "jurisdiction": law.jurisdiction or "central",
                    "law_type": law.law_type or "act",
                }
                if law.state_name:
                    meta["state_name"] = law.state_name
                if law.punishment:
                    meta["punishment"] = law.punishment[:200]
                batch.append({"id": str(law.id), "text": doc_text, "metadata": meta})

            # Upsert in chunks
            for i in range(0, len(batch), 50):
                vs.add_laws_batch(batch[i:i + 50])

            logger.info("Indexed %d laws into ChromaDB", len(batch))
        finally:
            db.close()

    # ══════════════════════════════════════════════════════════════════════
    #  DELETE / SOFT DELETE
    # ══════════════════════════════════════════════════════════════════════

    def soft_delete(self, law_id: int) -> bool:
        """Soft-delete a law (set is_active = False)."""
        db = self._session()
        try:
            law = db.query(Law).filter_by(id=law_id).first()
            if law:
                law.is_active = False
                law.last_updated = datetime.now(timezone.utc)
                db.commit()
                return True
            return False
        finally:
            db.close()

    def hard_delete(self, law_id: int) -> bool:
        """Permanently delete a law record."""
        db = self._session()
        try:
            law = db.query(Law).filter_by(id=law_id).first()
            if law:
                db.delete(law)
                db.commit()
                return True
            return False
        finally:
            db.close()


# ═══════════════════════════════════════════════════════════════════════════
#  CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

def main():
    import argparse

    ap = argparse.ArgumentParser(
        prog="python -m legal_database.store",
        description="YAMA AI — Legal Database Store: Manage the laws table.",
    )
    sub = ap.add_subparsers(dest="command", required=True)

    # init
    sub.add_parser("init", help="Create database tables")

    # import
    p_import = sub.add_parser("import", help="Import records from JSON/CSV file")
    p_import.add_argument("file", help="Path to JSON or CSV file")
    p_import.add_argument("--no-vectors", action="store_true", help="Skip ChromaDB indexing")

    # search
    p_search = sub.add_parser("search", help="Full-text search")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--limit", type=int, default=10)

    # filter
    p_filter = sub.add_parser("filter", help="Filter laws")
    p_filter.add_argument("--act", default=None)
    p_filter.add_argument("--category", default=None)
    p_filter.add_argument("--jurisdiction", default=None)
    p_filter.add_argument("--state", default=None)
    p_filter.add_argument("--limit", type=int, default=20)

    # stats
    sub.add_parser("stats", help="Show database statistics")

    # export
    p_export = sub.add_parser("export", help="Export laws to JSON")
    p_export.add_argument("--output", "-o", default="legal_database/export/laws.json")
    p_export.add_argument("--category", default=None)
    p_export.add_argument("--jurisdiction", default=None)

    # acts
    sub.add_parser("acts", help="List all acts")

    args = ap.parse_args()
    store = LegalStore()

    if args.command == "init":
        store.init_db()
        if not store.is_sqlite:
            store.run_schema_sql()
        print("✅ Database initialized")

    elif args.command == "import":
        store.init_db()
        stats = store.import_file(args.file, index_vectors=not args.no_vectors)
        print(f"✅ Import complete: {stats}")

    elif args.command == "search":
        results = store.search(args.query, limit=args.limit)
        print(f"\n🔍 Found {len(results)} results for '{args.query}':\n")
        for r in results:
            print(f"  [{r['category']}] {r['act_name']} S.{r['section_number']}: {r['title']}")
            desc = r["description"][:120].replace("\n", " ")
            print(f"    {desc}...")
            print()

    elif args.command == "filter":
        results = store.filter(
            act_name=args.act, category=args.category,
            jurisdiction=args.jurisdiction, state_name=args.state,
            limit=args.limit,
        )
        print(f"\n📋 {len(results)} laws matching filters:\n")
        for r in results:
            print(f"  {r['act_name']} S.{r['section_number']}: {r['title']}")

    elif args.command == "stats":
        s = store.stats()
        print("\n" + "═" * 50)
        print("  YAMA AI — Database Statistics")
        print("═" * 50)
        print(f"  Total laws:      {s['total_laws']}")
        print(f"  Central:         {s['central_laws']}")
        print(f"  State:           {s['state_laws']}")
        print(f"  Amended:         {s['amended_laws']}")
        print(f"  Unique acts:     {s['unique_acts']}")
        print(f"\n  By category:")
        for cat, cnt in sorted(s["by_category"].items()):
            print(f"    {cat:20s} {cnt}")
        print("═" * 50)

    elif args.command == "export":
        store.init_db()
        kwargs = {}
        if args.category:
            kwargs["category"] = args.category
        if args.jurisdiction:
            kwargs["jurisdiction"] = args.jurisdiction
        count = store.export_json(args.output, **kwargs)
        print(f"✅ Exported {count} laws → {args.output}")

    elif args.command == "acts":
        acts = store.list_acts()
        print(f"\n📚 {len(acts)} acts in database:\n")
        for a in acts:
            print(f"  {a['act_name']:50s} [{a['category']:15s}] {a['section_count']} sections")


if __name__ == "__main__":
    main()
