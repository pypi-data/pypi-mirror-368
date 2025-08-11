import re
from fabriq.llm_model import LLMModel
from typing import Any
from langchain_core.documents import Document

class Reranker:
    def __init__(self, config):
        """Initialize the reranking model based on the specified type."""
        self.config = config
        model_name = (
            self.config.get("reranker")
            .get("params")
            .get("model_name", "BAAI/bge-reranker-base")
        )
        self.model_type = self.config.get("reranker").get("type", "cross_encoder")
        top_k = self.config.get("retriever").get("params").get("top_k", 25)
        device = self.config.get("reranker").get("params").get("device", "cpu")
        kwargs = self.config.get("reranker").get("kwargs", {})
        self.top_k = top_k
        dtype = kwargs.pop("torch_dtype", "float16")

        if self.model_type == "cross_encoder":
            from sentence_transformers import CrossEncoder
            self.reranker = CrossEncoder(
                model_name,
                device=device,
                automodel_args={"torch_dtype": dtype},
                **kwargs,
            )
        elif self.model_type == "llm":
            self.reranker = LLMModel(self.config)
        else:
            raise ValueError(f"Unsupported embedding model type: {self.model_type}")

    def get_reranking_model(self):
        """Return the initialized reranking model."""
        return self.reranker

    def llm_rerank(self, query, documents, llm):
        ranked_results = []
        for doc in documents:
            prompt = f"""
            Query: {query}
            Document: {doc}
            
            On a scale of 0-10, how relevant is this document to the query?
            Provide your score in the following format:
            Score: <score>
            """
            score_response = llm.generate(prompt)
            score_pattern = r"Score:\s*(\d+(?:\.\d+)?)"
            match = re.search(score_pattern, score_response)
            if match:
                score = float(match.group(1))
            else:
                score = 0.0
            ranked_results.append((score, doc))
        sorted_results = sorted(ranked_results, key=lambda x: x[0], reverse=True)
        sorted_results = sorted_results[: self.top_k]
        return [
            Document(
                page_content=doc.page_content,
                metadata=doc.metadata if hasattr(doc, "metadata") else {},
            )
            for _, doc in sorted_results
        ]

    def cross_encoder_rerank(self, query, documents, reranker):
        """Rerank a list of documents using a cross-encoder."""
        reranked_docs = []
        model_inputs = [[query, doc.page_content] for doc in documents]
        scores = reranker.predict(model_inputs)

        # Sort the scores in decreasing order
        results = [
            {"input": inp, "score": score} for inp, score in zip(model_inputs, scores)
        ]
        results = sorted(results, key=lambda x: x["score"], reverse=True)

        for hit in results[: self.top_k]:
            # Find the original document by matching page_content
            matched_doc = next(
                (doc for doc in documents if doc.page_content == hit["input"][1]), None
            )
            if matched_doc:
                reranked_docs.append(
                    Document(
                        page_content=matched_doc.page_content,
                        metadata=getattr(matched_doc, "metadata", {}),
                    )
                )
        return reranked_docs

    def rerank(self, query, documents):
        """Rerank a list of documents."""
        if self.model_type == "cross_encoder":
            return self.cross_encoder_rerank(query, documents, self.reranker)
        elif self.model_type == "llm":
            return self.llm_rerank(query, documents, self.reranker)
        else:
            raise ValueError("Unsupported reranking model type.")
