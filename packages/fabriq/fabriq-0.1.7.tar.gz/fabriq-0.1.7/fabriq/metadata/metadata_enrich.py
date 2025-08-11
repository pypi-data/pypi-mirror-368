import json
from fabriq.llm_model import LLMModel
from langchain.schema import Document
from typing import List
from pydantic import BaseModel, Field


class EnrichSchema(BaseModel):
    """Schema for metadata enrichment"""

    document_id: str = Field(..., description="Unique identifier for the document")
    title: str = Field(..., description="Title of the document")
    summary: str = Field(..., description="Summary of the document")
    keywords: List[str] = Field(
        ..., description="Keywords associated with the document"
    )
    rephrased_content: str = Field(..., description="Rephrased content of the document")
    questions: List[str] = Field(
        ..., description="Questions that the document chunk can answer"
    )


class DenseMetadataEnricher:
    """Class for enriching metadata of documents"""

    def __init__(self, config, llm_model: LLMModel):
        self.config = config
        self.llm_model = llm_model

    def enrich_metadata(self, document) -> Document:
        """Enrich metadata of documents using LLM"""
        # Extract content from the document
        content = document.page_content
        doc_id = document.id

        enriched_metadata = self.llm_model.generate(
            """Generate
            - title, 
            - summary, 
            - keywords_list (List of keywords separated by commas), 
            - rephrased_content, 
            - 5 questions (list of 5 questions that the content can answer)

            based on the content provided. Use the following json schema for output STRICTLY, DO NOT WRITE ANYTHING ELSE EXCEPT THE JSON:
            {{
                "title": "<title>",
                "summary": "<summary>",
                "keywords_list": ["<keyword1>", "<keyword2>, ..."],
                "rephrased_content": "<rephrased_content>",
                "questions": ["<question1>", "<question2>, ... , <question5>"]
            }}
            
            for the following content:\n"""+ content,
            # response_format=EnrichSchema
        )
        enriched_metadata = json.loads(enriched_metadata)

        return Document(
            id=doc_id,
            page_content=content,
            metadata={
                "title": enriched_metadata.get("title", ""),
                "summary": enriched_metadata.get("summary", ""),
                "keywords_list": enriched_metadata.get("keywords", []),
                "rephrased_content": enriched_metadata.get("rephrased_content", ""),
                "questions": enriched_metadata.get("questions", []),
            },
        )
