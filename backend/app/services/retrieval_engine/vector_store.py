"""
YAMA AI — ChromaDB Vector Store for Legal Text Retrieval
Implements semantic search using ChromaDB embeddings.
"""

import chromadb
from typing import List, Dict, Optional
from app.core.config import settings


class LegalVectorStore:
    """
    Manages ChromaDB vector store for semantic search of legal provisions.
    Uses ChromaDB's built-in default embedding function.
    """

    def __init__(self):
        persist_dir = settings.CHROMA_PERSIST_DIR
        try:
            # ChromaDB >= 0.4.x uses PersistentClient
            self.client = chromadb.PersistentClient(path=persist_dir)
        except (TypeError, AttributeError):
            # Fallback for older chromadb or in-memory when persistence fails
            self.client = chromadb.Client()

        self.collection = self.client.get_or_create_collection(
            name="indian_laws",
            metadata={"hnsw:space": "cosine"},
        )

    def add_law(self, law_id: str, text: str, metadata: Dict):
        """Add a single law section to the vector store."""
        self.collection.add(
            ids=[law_id],
            documents=[text],
            metadatas=[metadata],
        )

    def add_laws_batch(self, laws: List[Dict]):
        """
        Add multiple law sections to the vector store.
        Each law dict should have: id, text, metadata
        """
        if not laws:
            return

        ids = [str(law["id"]) for law in laws]
        documents = [law["text"] for law in laws]
        metadatas = [law["metadata"] for law in laws]

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

    def search(self, query: str, n_results: int = 10, category: Optional[str] = None) -> List[Dict]:
        """
        Semantic search for relevant legal provisions.

        Args:
            query: User's situation or search query.
            n_results: Number of results to return.
            category: Optional category filter.

        Returns:
            List of matching legal provisions with scores.
        """
        where_filter = {"category": category} if category else None

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        formatted = []
        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                formatted.append({
                    "id": doc_id,
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                })

        return formatted

    def get_count(self) -> int:
        """Return total number of documents in the collection."""
        return self.collection.count()


# Singleton instance
_vector_store = None


def get_vector_store() -> LegalVectorStore:
    """Get or create the vector store singleton."""
    global _vector_store
    if _vector_store is None:
        _vector_store = LegalVectorStore()
    return _vector_store
