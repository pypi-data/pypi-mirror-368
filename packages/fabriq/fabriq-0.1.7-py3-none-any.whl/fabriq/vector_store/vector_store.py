from langchain_community.vectorstores import Chroma, FAISS
from fabriq.embeddings import EmbeddingModel


class VectorStore:
    def __init__(self, config):
        """Initialize the vector store with the specified type."""
        self.config = config
        vector_store_type = self.config.get("vector_store").get("type", "chromadb")
        self.collection_name = (
            self.config.get("vector_store")
            .get("params")
            .get("collection_name", "vector_store_collection")
        )
        self.embedding_model = EmbeddingModel(self.config)
        self.persist_directory = self.config.get("vector_store").get(
            "store_path", "assets/vector_store"
        )
        self.kwargs = self.config.get("vector_store").get("kwargs", {})

        if vector_store_type not in ["chromadb", "faiss"]:
            raise ValueError(f"Unsupported vector store type: {vector_store_type}")
        if self.embedding_model is None:
            raise ValueError("Embedding model must be provided.")

        if vector_store_type == "chromadb":
            self.store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embedding_model,
                persist_directory=self.persist_directory,
                **self.kwargs,
            )
        elif vector_store_type == "faiss":
            self.store = FAISS(embedding_function=self.embedding_model, **self.kwargs)
        else:
            raise ValueError(f"Unsupported vector store type: {vector_store_type}")

    def add_documents(self, documents):
        """Add documents to the vector store."""
        self.store.add_documents(documents)

    def retrieve(self, query, k=5, filter=None):
        """Search for similar documents in the vector store."""
        return self.store.similarity_search(query, k=k, filter=filter)

    def persist(self):
        """Persist the vector store to the specified directory."""
        if self.get_store() == "FAISS":
            self.store.save_local(self.persist_directory)
        elif self.get_store() == "Chroma":
            print("Already persisted")

    def load(self, persist_directory: str):
        """Load the vector store from the specified directory."""
        if isinstance(self.store, Chroma):
            self.store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embedding_model,
            )
        elif isinstance(self.store, FAISS):
            self.store = FAISS.load_local(persist_directory)
        else:
            raise ValueError("Unsupported vector store type for loading.")

    def get_store(self):
        """Get the underlying vector store instance."""
        return self.store.__class__.__name__
