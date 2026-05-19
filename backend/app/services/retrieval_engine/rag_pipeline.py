"""
YAMA AI — RAG (Retrieval Augmented Generation) Pipeline
=============================================================================
Orchestrates the full retrieval → reasoning workflow:

    User query
        ↓
    Semantic vector search  (sentence-transformers + ChromaDB)
        ↓
    SQL keyword search      (law_sections + laws tables)
        ↓
    Merge & rank results
        ↓
    IRAC reasoning engine
        ↓
    Structured legal analysis

Uses the sentence-transformer embedding pipeline from
`retrieval_engine.embedding_generator` for high-quality semantic search,
with fallback to ChromaDB default embeddings if unavailable.
=============================================================================
"""

import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.models import LawSection
from app.services.ai_engine.reasoning import get_reasoning_engine

logger = logging.getLogger("yama_ai.rag")


# ═══════════════════════════════════════════════════════════════════════════
#  VECTOR SEARCH — sentence-transformers preferred, fallback to default
# ═══════════════════════════════════════════════════════════════════════════

_vector_searcher = None


def _get_vector_searcher():
    """
    Get the best available vector search backend.
    Prefers sentence-transformer LegalVectorSearch; falls back to old vector_store.
    """
    global _vector_searcher
    if _vector_searcher is not None:
        return _vector_searcher

    try:
        from retrieval_engine.embedding_generator import LegalVectorSearch
        searcher = LegalVectorSearch()
        if searcher.get_count() > 0:
            _vector_searcher = ("st", searcher)
            logger.info(
                "RAG: Using sentence-transformer vector search (%d documents)",
                searcher.get_count(),
            )
            return _vector_searcher
        logger.warning("RAG: Sentence-transformer collection is empty, trying fallback")
    except Exception as e:
        logger.warning("RAG: sentence-transformers unavailable (%s), using fallback", e)

    try:
        from app.services.retrieval_engine.vector_store import get_vector_store
        vs = get_vector_store()
        _vector_searcher = ("default", vs)
        logger.info("RAG: Using default ChromaDB vector search (%d documents)", vs.get_count())
    except Exception as e:
        logger.warning("RAG: No vector search available (%s)", e)
        _vector_searcher = ("none", None)

    return _vector_searcher


def reset_vector_searcher():
    """Reset cached searcher (e.g. after reindexing)."""
    global _vector_searcher
    _vector_searcher = None


# ═══════════════════════════════════════════════════════════════════════════
#  RAG PIPELINE
# ═══════════════════════════════════════════════════════════════════════════

class RAGPipeline:
    """
    Orchestrates the full RAG pipeline:
    1. Semantic search via sentence-transformers + ChromaDB
    2. SQL keyword search across law tables
    3. Merge and rank results
    4. Feed to IRAC reasoning engine
    5. Return structured analysis
    """

    def __init__(self, db: Session):
        self.db = db

    # ── Retrieval ──

    def retrieve_relevant_laws(
        self, query: str, category: Optional[str] = None, limit: int = 10
    ) -> List[Dict]:
        """
        Retrieve relevant laws using both vector search and keyword search.
        Merges results for comprehensive coverage.
        """
        # 1. Vector (semantic) search
        vector_results = self._vector_search(query, category, limit)

        # 2. Keyword search in SQL
        sql_results = self._keyword_search(query, category, limit)

        # 3. Merge and deduplicate
        merged = self._merge_results(vector_results, sql_results)

        return merged[:limit]

    def _vector_search(
        self, query: str, category: Optional[str], limit: int,
    ) -> List[Dict]:
        """Semantic search via the best available vector backend."""
        backend_type, backend = _get_vector_searcher()

        if backend_type == "none" or backend is None:
            return []

        try:
            if backend_type == "st":
                # sentence-transformer LegalVectorSearch
                results = backend.search(
                    query,
                    n_results=limit,
                    category=category,
                )
                return [
                    {
                        "id": r.id,
                        "text": r.text,
                        "metadata": r.metadata,
                        "score": r.score,
                        "source": "vector_st",
                    }
                    for r in results
                ]
            else:
                # Default ChromaDB vector store
                results = backend.search(query, n_results=limit, category=category)
                return [
                    {
                        "id": r["id"],
                        "text": r["text"],
                        "metadata": r["metadata"],
                        "score": 1.0 - (r.get("distance", 0) / 2.0),
                        "source": "vector_default",
                    }
                    for r in results
                ]
        except Exception as e:
            logger.error("Vector search failed: %s", e)
            return []

    def _keyword_search(
        self, query: str, category: Optional[str], limit: int,
    ) -> List[Dict]:
        """
        Search SQL database using keyword matching.
        Queries both law_sections table and laws table (if available),
        then deduplicates by act_name + section_number.
        """
        results = []
        seen_keys = set()

        # ── Search law_sections table (original) ──
        terms = query.lower().split()
        filters = []
        for term in terms:
            if len(term) > 2:
                filters.append(LawSection.keywords.ilike(f"%{term}%"))
                filters.append(LawSection.title.ilike(f"%{term}%"))
                filters.append(LawSection.description.ilike(f"%{term}%"))

        q = self.db.query(LawSection).filter(or_(*filters)) if filters else self.db.query(LawSection)
        if category:
            q = q.filter(LawSection.category == category)

        for r in q.limit(limit).all():
            key = f"{r.act_name}|{r.section_number}"
            if key in seen_keys:
                continue
            seen_keys.add(key)
            results.append({
                "id": f"ls_{r.id}",
                "text": (
                    f"{r.act_name} — Section {r.section_number}: {r.title}\n\n"
                    f"{r.description}"
                ),
                "metadata": {
                    "act_name": r.act_name,
                    "section_number": r.section_number,
                    "title": r.title,
                    "category": r.category,
                    "punishment": r.punishment or "",
                    "old_law_reference": r.old_law_reference or "",
                },
                "score": 0.5,  # Baseline score for keyword matches
                "source": "sql",
                "db_record": r,
            })

        # ── Search laws table (legal_database.store) if available ──
        try:
            from legal_database.store import Law, LegalStore
            store = LegalStore()
            db2 = store._session()
            try:
                filters2 = []
                for term in terms:
                    if len(term) > 2:
                        filters2.append(Law.keywords.ilike(f"%{term}%"))
                        filters2.append(Law.title.ilike(f"%{term}%"))
                        filters2.append(Law.description.ilike(f"%{term}%"))

                q2 = db2.query(Law).filter(Law.is_active == True)
                if filters2:
                    q2 = q2.filter(or_(*filters2))
                if category:
                    q2 = q2.filter(Law.category == category)

                for r in q2.limit(limit).all():
                    key = f"{r.act_name}|{r.section_number}"
                    if key in seen_keys:
                        continue
                    seen_keys.add(key)
                    results.append({
                        "id": f"law_{r.id}",
                        "text": (
                            f"{r.act_name} — Section {r.section_number}: {r.title}\n\n"
                            f"{r.description}"
                        ),
                        "metadata": {
                            "act_name": r.act_name,
                            "section_number": r.section_number,
                            "title": r.title,
                            "category": r.category or "general",
                            "punishment": r.punishment or "",
                            "old_law_reference": r.old_law_reference or "",
                        },
                        "score": 0.5,
                        "source": "sql_laws",
                    })
            finally:
                db2.close()
        except Exception as e:
            logger.debug("laws table not available: %s", e)

        return results

    def _merge_results(
        self, vector_results: List[Dict], sql_results: List[Dict],
    ) -> List[Dict]:
        """
        Merge and deduplicate results from vector and SQL searches.
        Vector results come first (higher semantic relevance).
        Deduplicates by act_name + section_number.
        """
        seen_keys = set()
        merged = []

        # Vector results first (better semantic match, already scored)
        for r in sorted(vector_results, key=lambda x: x.get("score", 0), reverse=True):
            meta = r.get("metadata", {})
            key = f"{meta.get('act_name', '')}|{meta.get('section_number', '')}"
            if key not in seen_keys:
                seen_keys.add(key)
                merged.append(r)

        # Add SQL results that aren't duplicates
        for r in sql_results:
            meta = r.get("metadata", {})
            key = f"{meta.get('act_name', '')}|{meta.get('section_number', '')}"
            if key not in seen_keys:
                seen_keys.add(key)
                merged.append(r)

        return merged

    # ── Format for reasoning ──

    def format_laws_for_prompt(self, laws: List[Dict]) -> str:
        """Format retrieved laws into a readable string for the reasoning engine."""
        if not laws:
            return "No specific legal provisions were found in the database for this query."

        parts = []
        for i, law in enumerate(laws, 1):
            meta = law.get("metadata", {})
            score = law.get("score", 0)
            source = law.get("source", "unknown")

            part = f"""\
{i}. {meta.get('act_name', 'Unknown Act')} — Section {meta.get('section_number', 'N/A')}
   Title: {meta.get('title', 'N/A')}
   Content: {law.get('text', 'N/A')}
   Punishment: {meta.get('punishment', 'N/A')}
   Old Law Reference: {meta.get('old_law_reference', 'N/A')}
   Relevance: {score:.0%} ({source})"""
            parts.append(part)

        return "\n\n".join(parts)

    # ── Full pipeline ──

    def analyze_situation(
        self, situation: str, category: Optional[str] = None,
    ) -> Dict:
        """
        Full RAG pipeline: retrieve laws → reason → return analysis.

        Returns:
            {
                "analysis": str,           # Full IRAC markdown
                "relevant_laws": [...],    # ORM records for API response
                "retrieved_count": int,
            }
        """
        # Step 1: Retrieve relevant laws
        relevant_laws = self.retrieve_relevant_laws(situation, category)

        # Step 2: Format laws for the reasoning engine
        laws_text = self.format_laws_for_prompt(relevant_laws)

        # Step 3: Run IRAC reasoning engine
        engine = get_reasoning_engine()
        analysis = engine.analyze(situation, laws_text)

        # Step 4: Resolve DB records for API response
        law_records = self._resolve_db_records(relevant_laws)

        return {
            "analysis": analysis,
            "relevant_laws": law_records,
            "retrieved_count": len(relevant_laws),
        }

    def _resolve_db_records(self, laws: List[Dict]) -> List:
        """
        Convert retrieval results back to LawSection ORM records
        for the API response serializer.
        """
        records = []
        seen = set()

        for law in laws:
            # If we already have the DB record attached
            if "db_record" in law:
                rec = law["db_record"]
                if rec.id not in seen:
                    seen.add(rec.id)
                    records.append(rec)
                continue

            # Try to find by act_name + section_number in law_sections
            meta = law.get("metadata", {})
            act = meta.get("act_name", "")
            section = meta.get("section_number", "")
            if not act or not section:
                continue

            try:
                rec = (
                    self.db.query(LawSection)
                    .filter_by(act_name=act, section_number=section)
                    .first()
                )
                if rec and rec.id not in seen:
                    seen.add(rec.id)
                    records.append(rec)
            except Exception:
                pass

        return records

    # ── Standalone search ──

    def search_laws(
        self, query: str, category: Optional[str] = None, limit: int = 10,
    ) -> List[LawSection]:
        """Search laws and return LawSection DB records."""
        results = self.retrieve_relevant_laws(query, category, limit)
        return self._resolve_db_records(results)
