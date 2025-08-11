from fabriq.llm_model import LLMModel
from fabriq.retriever import VectorRetriever
from fabriq.reranking import Reranker
from typing import List, Dict, Any
from langchain.schema import Document


class RAGPipeline:
    def __init__(self,config):
        """Initialize the RAG pipeline with an LLM model, retriever, and prompt template."""
        self.config = config
        self.llm_model = LLMModel(self.config)
        self.retriever = VectorRetriever(self.config)
        self.reranker = Reranker(self.config)
        # self.prompt_template = "You are a helpful AI assistant. Based on the following context, answer the question. DO NOT MAKE UP YOUR OWN ANSWER, ANSWER USING THE GIVEN CONTEXT ONLY. \n\n{documents}\n\nQuestion: {query}\nAnswer:"
        self.prompt_template : str = self.config.get("prompts").get("params").get("rag_prompt", None)

    def is_query_relevant(self, query: str, documents: List[Document]) -> bool:
        """Check if the query is relevant to the retrieved documents."""
        self.llm_model.system_prompt = "Your task is to determine if the query is relevant to the provided documents. Respond with 'True' or 'False' strictly."
        prompt = self.llm_model.system_prompt + f"\n\nDocuments: {documents}\n\nQuery: {query}"
        response = self.llm_model.generate(prompt)
        return True if "true" in response.lower() else False

    def get_response(self, query: str, filter=None, rerank: bool = False) -> str:
        """Run the RAG pipeline to retrieve relevant documents and generate a response."""
        # Retrieve relevant documents
        top_k = self.config.get("retriever").get("params").get("top_k", 25)
        documents = self.retriever.retrieve(query, top_k=top_k, filter=filter)
        if rerank:
            documents = self.reranker.rerank(query, documents)
        documents = documents[:top_k]

        if not documents:
            return "No relevant documents found."

        # Format the retrieved documents for the prompt
        documents = "\n\n----------\n\n".join([doc.page_content for doc in documents])

        if not self.prompt_template:
            raise ValueError("Prompt is not set.")
        if not self.llm_model:
            raise ValueError("LLM model is not initialized.")
        
        # Check if the query is relevant to the retrieved documents
        if self.is_query_relevant(query, documents) is False:
            result = {
                "text": "I cannot find relevant information to answer your question. Please ask your question relevant to the documents or rephrase it.",
                "chunks": [],
                "metadata": []
            }

        else:
            # Prepare the prompt with retrieved documents
            prompt = self.prompt_template.format(query=query, context=documents)

            # Generate a response using the LLM model
            response = self.llm_model.generate(prompt)

            result = {
                "text": response if response else "No response generated",
                "chunks": documents,
                "metadata": (
                    [getattr(doc, "metadata", {}) for doc in documents] if response else []
                ),
            }
        return result
