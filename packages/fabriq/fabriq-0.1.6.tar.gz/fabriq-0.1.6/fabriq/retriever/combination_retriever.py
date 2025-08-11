from langchain.retrievers import EnsembleRetriever
from fabriq.retriever import VectorRetriever
from fabriq.vector_store.bm25_store import BM25
from langchain.schema import Document
from typing import List


class CombinationRetriever:
    def __init__(self, config):
        self.config = config
        retriever_names = (
            self.config.get("retriever").get("params").get("ensemble_retrievers", [])
        )
        weights = self.config.get("retriever").get("kwargs").get("weights", [0.5, 0.5])
        retrievers = []
        if not retriever_names:
            if "vector" in retriever_names:
                retrievers.append(VectorRetriever(self.config))
            if "bm25" in retriever_names:
                retrievers.append(BM25(self.config))
            if len(retrievers) > 1:
                self.ensemble_retriever = EnsembleRetriever(
                    retrievers=retrievers, weights=weights
                )
        else:
            self.ensemble_retriever = EnsembleRetriever(
                retrievers=[VectorRetriever(self.config), BM25(self.config)],
                weights=[0.5, 0.5],
            )

    def retrieve(self, query: str) -> List[Document]:
        documents = self.ensemble_retriever.invoke(query)
        return documents
