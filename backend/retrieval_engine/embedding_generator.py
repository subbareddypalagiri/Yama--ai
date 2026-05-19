"""
YAMA AI — Legal Embedding Pipeline
=============================================================================
Converts legal text into dense vector embeddings using sentence-transformers
and stores them in ChromaDB for high-quality semantic retrieval.

Models available (configurable via EMBEDDING_MODEL env var):
    • all-MiniLM-L6-v2        — 384-dim, fast, good quality (default)
    • all-mpnet-base-v2       — 768-dim, best quality, slower
    • paraphrase-MiniLM-L6-v2 — 384-dim, good for paraphrase tasks
    • legal-bert-base-uncased — 768-dim, legal domain (if available)

Architecture:
    LegalEmbeddingGenerator
        ├── load model (sentence-transformers)
        ├── build document text from DB records
        ├── encode in batches
        └── upsert into ChromaDB with metadata

    LegalVectorSearch
        ├── encode query with same model
        └── search ChromaDB collection
        └── return ranked results with scores

Usage:
    from retrieval_engine.embedding_generator import (
        LegalEmbeddingGenerator, LegalVectorSearch,
    )

    # Index all laws from database
    gen = LegalEmbeddingGenerator()
    stats = gen.index_from_database()

    # Semantic search
    searcher = LegalVectorSearch()
    results = searcher.search("someone stole my phone")

CLI:
    cd backend
    python -m retrieval_engine.embedding_generator index          # Index all laws
    python -m retrieval_engine.embedding_generator search "query" # Semantic search
    python -m retrieval_engine.embedding_generator stats          # Collection info
    python -m retrieval_engine.embedding_generator reindex        # Drop & re-index
    python -m retrieval_engine.embedding_generator benchmark      # Speed benchmark
=============================================================================
"""

import hashlib
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# ── Path setup ──
_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("yama_ai.embeddings")


# ═══════════════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# Model choices by quality/speed tradeoff
MODELS = {
    "fast": "all-MiniLM-L6-v2",          # 384-dim, ~14k sentences/sec
    "balanced": "all-MiniLM-L12-v2",      # 384-dim, ~7k sentences/sec
    "quality": "all-mpnet-base-v2",       # 768-dim, ~2.8k sentences/sec
    "legal": "nlpaueb/legal-bert-base-uncased",  # 768-dim, legal domain
}

DEFAULT_MODEL = os.environ.get("EMBEDDING_MODEL", MODELS["fast"])
COLLECTION_NAME = os.environ.get("CHROMA_COLLECTION", "yama_legal_embeddings")
CHROMA_DIR = os.environ.get("CHROMA_PERSIST_DIR", "./chroma_data")
BATCH_SIZE = int(os.environ.get("EMBEDDING_BATCH_SIZE", "64"))
MAX_TEXT_LENGTH = 8192  # Truncate very long sections


# ═══════════════════════════════════════════════════════════════════════════
#  CUSTOM EMBEDDING FUNCTION FOR CHROMADB
# ═══════════════════════════════════════════════════════════════════════════

class SentenceTransformerEmbeddingFunction:
    """
    ChromaDB-compatible embedding function using sentence-transformers.

    Implements the full ChromaDB EmbeddingFunction protocol:
        __call__, embed_query, name, build_from_config, get_config
    """

    def __init__(self, model_name: str = DEFAULT_MODEL):
        from sentence_transformers import SentenceTransformer
        logger.info("Loading embedding model: %s", model_name)
        t0 = time.time()
        self.model = SentenceTransformer(model_name)
        self._model_name = model_name
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(
            "Model loaded in %.1fs — dimension=%d",
            time.time() - t0, self.dimension,
        )

    # ── ChromaDB Protocol Methods ──

    @staticmethod
    def name() -> str:
        return "yama_sentence_transformer"

    def get_config(self) -> Dict[str, Any]:
        return {"model_name": self._model_name}

    @staticmethod
    def build_from_config(config: Dict[str, Any]) -> "SentenceTransformerEmbeddingFunction":
        model = config.get("model_name", DEFAULT_MODEL)
        return SentenceTransformerEmbeddingFunction(model)

    def __call__(self, input: List[str]) -> List[List[float]]:
        """Encode a list of texts into embeddings (used for documents)."""
        embeddings = self.model.encode(
            input,
            batch_size=BATCH_SIZE,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return embeddings.tolist()

    def embed_query(self, input: List[str]) -> List[List[float]]:
        """Encode query texts (ChromaDB calls this for searches)."""
        return self.__call__(input)

    # ── Direct encode (non-ChromaDB use) ──

    @property
    def model_name(self) -> str:
        return self._model_name

    def encode(
        self,
        texts: List[str],
        batch_size: int = BATCH_SIZE,
        show_progress: bool = False,
    ) -> List[List[float]]:
        """Encode texts directly (for non-ChromaDB use)."""
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=True,
        )
        return embeddings.tolist()


# Singleton embedding function
_embedding_fn: Optional[SentenceTransformerEmbeddingFunction] = None


def get_embedding_function(
    model_name: str = DEFAULT_MODEL,
) -> SentenceTransformerEmbeddingFunction:
    """Get or create the singleton embedding function."""
    global _embedding_fn
    if _embedding_fn is None or _embedding_fn.model_name != model_name:
        _embedding_fn = SentenceTransformerEmbeddingFunction(model_name)
    return _embedding_fn


# ═══════════════════════════════════════════════════════════════════════════
#  DOCUMENT BUILDER — creates searchable text from law records
# ═══════════════════════════════════════════════════════════════════════════

def build_document_text(record: Dict[str, Any]) -> str:
    """
    Build a single document string from a law record for embedding.

    Combines act name, section, title, keywords, and description into
    a rich text representation optimized for semantic search.
    """
    parts = []

    act = record.get("act_name", "")
    section = record.get("section_number", "")
    title = record.get("title", "")

    # Header line: "Bharatiya Nyaya Sanhita, 2023 — Section 103: Murder"
    header = f"{act} — Section {section}: {title}" if all([act, section, title]) else \
             f"{act} — Section {section}" if act and section else \
             act or title or ""
    if header:
        parts.append(header)

    # Keywords for additional context
    keywords = record.get("keywords", "")
    if keywords:
        parts.append(f"Keywords: {keywords}")

    # Full description
    desc = record.get("description", "")
    if desc:
        parts.append(desc)

    # Punishment info (if available)
    punishment = record.get("punishment", "")
    if punishment:
        parts.append(f"Punishment: {punishment}")

    # Old law reference (IPC → BNS mapping etc.)
    old_ref = record.get("old_law_reference", "")
    if old_ref:
        parts.append(f"Previously: {old_ref}")

    text = "\n\n".join(parts)

    # Truncate if too long
    if len(text) > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH] + "..."

    return text


def build_metadata(record: Dict[str, Any]) -> Dict[str, str]:
    """Extract ChromaDB-safe metadata (string values only) from a law record."""
    meta = {}
    str_fields = [
        "act_name", "section_number", "title", "category",
        "jurisdiction", "state_name", "law_type",
    ]
    for f in str_fields:
        val = record.get(f)
        if val:
            meta[f] = str(val)

    # Add computed fields
    if record.get("is_amended"):
        meta["is_amended"] = "true"
    if record.get("amendment_year"):
        meta["amendment_year"] = str(record["amendment_year"])
    if record.get("punishment"):
        meta["has_punishment"] = "true"
    if record.get("old_law_reference"):
        meta["old_law_reference"] = str(record["old_law_reference"])[:200]

    # Content hash for change detection
    if record.get("content_hash"):
        meta["content_hash"] = record["content_hash"]

    return meta


# ═══════════════════════════════════════════════════════════════════════════
#  LEGAL EMBEDDING GENERATOR
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class IndexStats:
    """Statistics from an indexing run."""
    total_records: int = 0
    indexed: int = 0
    skipped: int = 0
    errors: int = 0
    elapsed_seconds: float = 0.0
    collection_size: int = 0
    model_name: str = ""
    dimension: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_records": self.total_records,
            "indexed": self.indexed,
            "skipped": self.skipped,
            "errors": self.errors,
            "elapsed_seconds": round(self.elapsed_seconds, 2),
            "records_per_second": round(self.indexed / max(self.elapsed_seconds, 0.01), 1),
            "collection_size": self.collection_size,
            "model": self.model_name,
            "dimension": self.dimension,
        }


class LegalEmbeddingGenerator:
    """
    Generates embeddings for legal text and indexes them into ChromaDB.

    Uses sentence-transformers for encoding and ChromaDB for storage.
    The ChromaDB collection is created with the custom embedding function
    so that queries are also encoded with the same model automatically.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        collection_name: str = COLLECTION_NAME,
        chroma_dir: str = CHROMA_DIR,
    ):
        self.model_name = model_name
        self.collection_name = collection_name
        self.chroma_dir = chroma_dir

        # Initialize embedding function (loads model)
        self.embed_fn = get_embedding_function(model_name)

        # Initialize ChromaDB
        import chromadb
        os.makedirs(chroma_dir, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=chroma_dir)
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embed_fn,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            "ChromaDB collection '%s' — %d documents",
            collection_name, self.collection.count(),
        )

    # ── Index from dicts ──

    def index_records(
        self,
        records: List[Dict[str, Any]],
        id_prefix: str = "law",
    ) -> IndexStats:
        """
        Index a list of law records (dicts) into ChromaDB.

        Each record should have at minimum: act_name, section_number,
        title, description.

        Args:
            records: List of law dicts.
            id_prefix: Prefix for ChromaDB document IDs.

        Returns:
            IndexStats with counts and timing.
        """
        stats = IndexStats(
            total_records=len(records),
            model_name=self.model_name,
            dimension=self.embed_fn.dimension,
        )
        t0 = time.time()

        ids = []
        documents = []
        metadatas = []

        for rec in records:
            try:
                # Build unique ID
                rec_id = rec.get("id")
                if rec_id:
                    doc_id = f"{id_prefix}_{rec_id}"
                else:
                    # Generate from content hash
                    h = hashlib.md5(
                        f"{rec.get('act_name', '')}|{rec.get('section_number', '')}".encode()
                    ).hexdigest()[:12]
                    doc_id = f"{id_prefix}_{h}"

                # Build document text and metadata
                doc_text = build_document_text(rec)
                meta = build_metadata(rec)

                if not doc_text.strip():
                    stats.skipped += 1
                    continue

                ids.append(doc_id)
                documents.append(doc_text)
                metadatas.append(meta)

            except Exception as e:
                logger.warning("Error processing record: %s", e)
                stats.errors += 1

        # Upsert in batches
        if ids:
            for i in range(0, len(ids), BATCH_SIZE):
                end = min(i + BATCH_SIZE, len(ids))
                self.collection.upsert(
                    ids=ids[i:end],
                    documents=documents[i:end],
                    metadatas=metadatas[i:end],
                )
                logger.info(
                    "  Indexed batch %d–%d of %d",
                    i + 1, end, len(ids),
                )

        stats.indexed = len(ids)
        stats.elapsed_seconds = time.time() - t0
        stats.collection_size = self.collection.count()

        logger.info(
            "Indexing complete: %d indexed, %d skipped, %d errors in %.1fs",
            stats.indexed, stats.skipped, stats.errors, stats.elapsed_seconds,
        )
        return stats

    # ── Index from database ──

    def index_from_database(self, database_url: Optional[str] = None) -> IndexStats:
        """
        Load all active laws from the database and index them into ChromaDB.

        Uses the LegalStore from legal_database.store.
        """
        from legal_database.store import LegalStore

        store = LegalStore(database_url=database_url)
        store.init_db()

        # Export all active records
        db = store._session()
        try:
            from legal_database.store import Law
            laws = db.query(Law).filter(Law.is_active == True).all()
            records = [law.to_dict() for law in laws]
            logger.info("Loaded %d active laws from database", len(records))
        finally:
            db.close()

        if not records:
            logger.warning("No records found in database")
            return IndexStats()

        return self.index_records(records, id_prefix="law")

    # ── Index from JSON file ──

    def index_from_json(self, filepath: str) -> IndexStats:
        """Index records from a JSON file (list of law dicts)."""
        import json
        with open(filepath, "r", encoding="utf-8") as f:
            records = json.load(f)

        if isinstance(records, dict):
            records = [records]

        logger.info("Loaded %d records from %s", len(records), filepath)
        return self.index_records(records, id_prefix="json")

    # ── Embed single text ──

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single piece of text."""
        return self.embed_fn.encode([text])[0]

    # ── Embed multiple texts ──

    def embed_batch(
        self,
        texts: List[str],
        show_progress: bool = False,
    ) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        return self.embed_fn.encode(
            texts,
            batch_size=BATCH_SIZE,
            show_progress=show_progress,
        )

    # ── Collection management ──

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the ChromaDB collection."""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "model": self.model_name,
            "dimension": self.embed_fn.dimension,
            "chroma_dir": self.chroma_dir,
        }

    def reset_collection(self):
        """Delete and recreate the ChromaDB collection."""
        self.chroma_client.delete_collection(self.collection_name)
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embed_fn,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("Collection '%s' reset", self.collection_name)


# ═══════════════════════════════════════════════════════════════════════════
#  LEGAL VECTOR SEARCH — query interface
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SearchResult:
    """A single semantic search result."""
    id: str
    text: str
    metadata: Dict[str, str]
    score: float  # cosine similarity (1 - distance)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "metadata": self.metadata,
            "score": round(self.score, 4),
        }


class LegalVectorSearch:
    """
    Semantic search over the legal embedding collection.

    Uses the same sentence-transformer model as the generator so that
    query and document embeddings are in the same vector space.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        collection_name: str = COLLECTION_NAME,
        chroma_dir: str = CHROMA_DIR,
    ):
        self.embed_fn = get_embedding_function(model_name)

        import chromadb
        self.chroma_client = chromadb.PersistentClient(path=chroma_dir)
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embed_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def search(
        self,
        query: str,
        n_results: int = 10,
        category: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        act_name: Optional[str] = None,
        min_score: float = 0.0,
    ) -> List[SearchResult]:
        """
        Semantic search for legal provisions matching the query.

        Args:
            query: Natural language description of a situation or legal question.
            n_results: Max results to return.
            category: Filter by legal category (e.g. "criminal", "constitutional").
            jurisdiction: Filter by "central" or "state".
            act_name: Filter by specific act.
            min_score: Minimum cosine similarity score (0–1).

        Returns:
            List of SearchResult ordered by relevance.
        """
        # Build where filter
        where_clauses = []
        if category:
            where_clauses.append({"category": category})
        if jurisdiction:
            where_clauses.append({"jurisdiction": jurisdiction})
        if act_name:
            where_clauses.append({"act_name": act_name})

        where_filter = None
        if len(where_clauses) == 1:
            where_filter = where_clauses[0]
        elif len(where_clauses) > 1:
            where_filter = {"$and": where_clauses}

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        search_results = []
        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i]
                # ChromaDB cosine distance: 0 = identical, 2 = opposite
                # Convert to similarity score: 1 - (distance / 2)
                score = 1.0 - (distance / 2.0)

                if score < min_score:
                    continue

                search_results.append(SearchResult(
                    id=doc_id,
                    text=results["documents"][0][i],
                    metadata=results["metadatas"][0][i],
                    score=score,
                ))

        return search_results

    def search_with_context(
        self,
        query: str,
        n_results: int = 5,
        **filters,
    ) -> Dict[str, Any]:
        """
        Search and return results formatted for the AI reasoning engine.

        Returns a dict with query, results, and a combined context string
        ready for injection into an LLM prompt.
        """
        results = self.search(query, n_results=n_results, **filters)

        # Build context string for LLM
        context_parts = []
        for i, r in enumerate(results, 1):
            meta = r.metadata
            context_parts.append(
                f"[{i}] {meta.get('act_name', 'Unknown')} — "
                f"Section {meta.get('section_number', '?')}: "
                f"{meta.get('title', 'Untitled')}\n"
                f"(Relevance: {r.score:.0%})\n"
                f"{r.text}\n"
            )

        return {
            "query": query,
            "num_results": len(results),
            "results": [r.to_dict() for r in results],
            "context": "\n---\n".join(context_parts),
        }

    def get_count(self) -> int:
        """Return total number of documents in the collection."""
        return self.collection.count()


# ═══════════════════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════════════════

def _print_header(title: str):
    w = 70
    print("═" * w)
    print(f"  YAMA AI — {title}")
    print("═" * w)


def cli():
    """Command-line interface for the embedding pipeline."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="python -m retrieval_engine.embedding_generator",
        description="YAMA AI Legal Embedding Pipeline",
    )
    sub = parser.add_subparsers(dest="command", help="Command to run")

    # index
    p_index = sub.add_parser("index", help="Index all laws from database")
    p_index.add_argument("--model", default=DEFAULT_MODEL, help="Model name")
    p_index.add_argument("--file", help="Index from JSON file instead of DB")

    # search
    p_search = sub.add_parser("search", help="Semantic search")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("-n", "--num", type=int, default=5, help="Number of results")
    p_search.add_argument("--category", help="Filter by category")
    p_search.add_argument("--jurisdiction", help="Filter by jurisdiction")
    p_search.add_argument("--act", help="Filter by act name")
    p_search.add_argument("--model", default=DEFAULT_MODEL, help="Model name")

    # stats
    p_stats = sub.add_parser("stats", help="Collection statistics")
    p_stats.add_argument("--model", default=DEFAULT_MODEL, help="Model name")

    # reindex
    p_reindex = sub.add_parser("reindex", help="Drop & re-index all laws")
    p_reindex.add_argument("--model", default=DEFAULT_MODEL, help="Model name")

    # benchmark
    p_bench = sub.add_parser("benchmark", help="Embedding speed benchmark")
    p_bench.add_argument("--model", default=DEFAULT_MODEL, help="Model name")
    p_bench.add_argument("--samples", type=int, default=100, help="Sample count")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # ── index ──
    if args.command == "index":
        _print_header("Index Legal Embeddings")
        gen = LegalEmbeddingGenerator(model_name=args.model)
        if args.file:
            stats = gen.index_from_json(args.file)
        else:
            stats = gen.index_from_database()
        d = stats.to_dict()
        print(f"\n  Records processed: {d['total_records']}")
        print(f"  Indexed:           {d['indexed']}")
        print(f"  Skipped:           {d['skipped']}")
        print(f"  Errors:            {d['errors']}")
        print(f"  Time:              {d['elapsed_seconds']}s")
        print(f"  Speed:             {d['records_per_second']} rec/s")
        print(f"  Collection size:   {d['collection_size']}")
        print(f"  Model:             {d['model']}")
        print(f"  Dimension:         {d['dimension']}")

    # ── search ──
    elif args.command == "search":
        _print_header("Semantic Search")
        searcher = LegalVectorSearch(model_name=args.model)
        results = searcher.search(
            args.query,
            n_results=args.num,
            category=args.category,
            jurisdiction=args.jurisdiction,
            act_name=args.act,
        )
        print(f"\n  Query: \"{args.query}\"")
        print(f"  Results: {len(results)}\n")
        for i, r in enumerate(results, 1):
            m = r.metadata
            print(f"  [{i}] {m.get('act_name', '?')} — S.{m.get('section_number', '?')}")
            print(f"      {m.get('title', 'Untitled')}")
            print(f"      Score: {r.score:.4f}  Category: {m.get('category', '-')}")
            # Show first 150 chars of text
            snippet = r.text.replace("\n", " ")[:150]
            print(f"      {snippet}...")
            print()

    # ── stats ──
    elif args.command == "stats":
        _print_header("Collection Statistics")
        gen = LegalEmbeddingGenerator(model_name=args.model)
        s = gen.get_collection_stats()
        print(f"\n  Collection:  {s['collection_name']}")
        print(f"  Documents:   {s['document_count']}")
        print(f"  Model:       {s['model']}")
        print(f"  Dimension:   {s['dimension']}")
        print(f"  Storage:     {s['chroma_dir']}")

    # ── reindex ──
    elif args.command == "reindex":
        _print_header("Reindex (Drop + Index)")
        gen = LegalEmbeddingGenerator(model_name=args.model)
        print("  Dropping existing collection...")
        gen.reset_collection()
        print("  Re-indexing from database...")
        stats = gen.index_from_database()
        d = stats.to_dict()
        print(f"\n  Indexed: {d['indexed']} records in {d['elapsed_seconds']}s")
        print(f"  Collection size: {d['collection_size']}")

    # ── benchmark ──
    elif args.command == "benchmark":
        _print_header("Embedding Benchmark")
        embed_fn = get_embedding_function(args.model)
        print(f"\n  Model: {args.model}")
        print(f"  Dimension: {embed_fn.dimension}")
        print(f"  Samples: {args.samples}\n")

        # Generate test sentences
        test_texts = [
            f"Section {i} of the Indian Penal Code deals with criminal offenses "
            f"related to theft and dishonest misappropriation of property."
            for i in range(args.samples)
        ]

        t0 = time.time()
        _ = embed_fn.encode(test_texts, batch_size=BATCH_SIZE)
        elapsed = time.time() - t0

        print(f"  Time:    {elapsed:.2f}s")
        print(f"  Speed:   {args.samples / elapsed:.1f} texts/sec")
        print(f"  Avg:     {elapsed / args.samples * 1000:.1f} ms/text")


if __name__ == "__main__":
    cli()
