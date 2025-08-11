from fabriq.vector_store import VectorStore
from fabriq.embeddings import EmbeddingModel
from fabriq.document_loader import SmartDocumentLoader
from fabriq.text_splitter import TextSplitter
from typing import List
import pandas as pd

class DocumentIndexer:
    def __init__(self, config):
        """Initialize the document indexer with a specified vector store type."""
        self.config = config
        self.embedding_model = EmbeddingModel(self.config)
        self.vector_store = VectorStore(self.config)
    def index_document(self, file_path: str):
        """Load a document and add it to the vector store."""
        loader = SmartDocumentLoader()
        splitter = TextSplitter(self.config)
        document = loader.load_document(file_path)
        chunks = splitter.split_text(document)
        self.vector_store.add_documents(chunks)

    def index_documents(self, file_paths: List[str]):
        """Index multiple documents."""
        error_files = pd.DataFrame(columns=["file_path", "error"])
        for file_path in file_paths:
            try:
                self.index_document(file_path)
            except Exception as e:
                print(f"Error indexing document {file_path}: {e}")
                error_files = pd.concat([error_files, pd.DataFrame({"file_path": [file_path], "error": [str(e)]})], ignore_index=True)
                error_files.to_excel("error_files.xlsx", index=False)