"""
YAMA AI — Vector Store Indexer
Indexes legal provisions from PostgreSQL into ChromaDB.
Run: python -m app.services.retrieval_engine.indexer
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from app.db.database import SessionLocal
from app.db.models import LawSection
from app.services.retrieval_engine.vector_store import get_vector_store


def index_all_laws():
    """Index all law sections from PostgreSQL into ChromaDB."""
    print("📚 Indexing legal provisions into ChromaDB...")

    db = SessionLocal()
    vector_store = get_vector_store()

    try:
        laws = db.query(LawSection).filter_by(is_active=True).all()
        print(f"Found {len(laws)} active law sections to index.")

        batch = []
        for law in laws:
            text = (
                f"{law.act_name} — Section {law.section_number}: {law.title}\n"
                f"{law.description}\n"
                f"Keywords: {law.keywords or ''}\n"
                f"Punishment: {law.punishment or 'N/A'}\n"
                f"Old Law Reference: {law.old_law_reference or 'N/A'}"
            )

            batch.append({
                "id": str(law.id),
                "text": text,
                "metadata": {
                    "act_name": law.act_name,
                    "section_number": law.section_number,
                    "title": law.title,
                    "category": law.category,
                    "punishment": law.punishment or "",
                    "old_law_reference": law.old_law_reference or "",
                },
            })

        if batch:
            vector_store.add_laws_batch(batch)

        print(f"✅ Indexed {len(batch)} sections into ChromaDB.")
        print(f"   Total documents in vector store: {vector_store.get_count()}")

    finally:
        db.close()


if __name__ == "__main__":
    index_all_laws()
