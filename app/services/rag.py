from app.models.document import Document


class RagService:
    """Placeholder in-memory store with keyword search.

    Swap the internals for embeddings + a vector store later; the routes only
    depend on ingest / list_documents / search.
    """

    def __init__(self) -> None:
        self._documents: dict[str, Document] = {}

    def ingest(self, documents: list[Document]) -> int:
        for doc in documents:
            self._documents[doc.id] = doc  # upsert, so re-ingesting is safe
        return len(documents)

    def list_documents(self) -> list[Document]:
        return list(self._documents.values())

    def search(self, question: str, top_k: int = 3) -> list[Document]:
        words = set(question.lower().split())
        scored = [
            (len(words & set(doc.content.lower().split())), doc)
            for doc in self._documents.values()
        ]
        hits = sorted((s for s in scored if s[0] > 0), key=lambda s: s[0], reverse=True)
        return [doc for _, doc in hits[:top_k]]
