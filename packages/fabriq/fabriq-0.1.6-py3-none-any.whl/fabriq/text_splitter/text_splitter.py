from unstructured.partition.text import partition_text
from unstructured.chunking.basic import chunk_elements
from unstructured.chunking.title import chunk_by_title
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List


class TextSplitter:
    def __init__(self, config):
        """
        Initializes the TextSplitter with the specified parameters.

        Args:
            splitter_type (str): The type of text splitter to use (default is "markdown").
            chunking_strategy (str): The strategy for chunking text (default is "by_title").
            chunk_size (int): The maximum size of each text chunk (default is 1000).
            chunk_overlap (int): The number of overlapping characters between chunks (default is 200).
        """
        self.config = config
        self.splitter_type = self.config.get("text_splitter").get(
            "type", "unstructured"
        )
        self.chunking_strategy = (
            self.config.get("text_splitter")
            .get("params")
            .get("chunking_strategy", "by_title")
        )
        self.chunk_size = (
            self.config.get("text_splitter").get("params").get("chunk_size", 1000)
        )
        self.chunk_overlap = (
            self.config.get("text_splitter").get("params").get("chunk_overlap", 200)
        )
        if self.splitter_type not in ["recursive", "unstructured"]:
            raise ValueError(
                f"Unsupported splitter type: {self.splitter_type}. "
                "Supported types are 'recursive' and 'unstructured'."
            )

    def split_text(self, documents: List[Document]) -> List[Document]:
        """
        Splits the input text into smaller chunks based on the specified splitting strategy.

        Args:
            text (str): The text to be split.

        Returns:
            List[Document]: A list of Document objects containing the split text chunks.
        """
        if self.splitter_type == "recursive":
            chunks = RecursiveCharacterTextSplitter(
                chunk_size=100,
                chunk_overlap=20,
            ).split_documents(documents)
            return chunks

        elif self.splitter_type == "unstructured":
            elements = []
            metadatas = []
            for text in documents:
                element = partition_text(text=text.page_content)
                elements.extend(element)
                metadatas.append(
                    {
                        "page_number": text.metadata.get("page_num", ""),
                        "filename": text.metadata.get("file_name", ""),
                    }
                )
            if self.chunking_strategy == "by_title":
                chunks = chunk_by_title(
                    elements,
                    multipage_sections=True,
                    overlap=self.chunk_overlap,
                    max_characters=self.chunk_size,
                )
            else:
                chunks = chunk_elements(
                    elements, overlap=self.chunk_overlap, max_characters=self.chunk_size
                )

            return [
                Document(
                    page_content=chunk.text,
                    metadata=metadata,
                )
                for chunk, metadata in zip(chunks, metadatas)
            ]
