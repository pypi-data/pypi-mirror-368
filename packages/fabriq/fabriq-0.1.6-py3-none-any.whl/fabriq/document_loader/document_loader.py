from markitdown import MarkItDown
import os
from pymupdf4llm import to_markdown
from langchain.schema import Document
from typing import List


class DocumentLoader:
    def __init__(self):
        self.md = MarkItDown(enable_plugins=False)

    def load_document(self, file_path: str, metadata={}) -> List[Document]:
        """Load the document in Markdown format."""
        self.file_path = file_path
        if os.path.basename(self.file_path).endswith((".pptx", ".xlsx", ".docx")):
            markdown_result = self.md.convert(self.file_path,keep_data_uris=True)

        elif os.path.basename(self.file_path).endswith((".pdf")):
            markdown_result = to_markdown(
                self.file_path,
                page_chunks=True,
                embed_images=True,
                image_size_limit=0,
                force_text=False,
            )

        result = [
            Document(
                page_content=doc["text"],
                metadata={
                    "source": self.file_path,
                    "file_name": os.path.basename(self.file_path),
                    "page_num": doc["metadata"].get("page") or "",
                    **metadata,
                },
            )
            for doc in markdown_result
        ]
        return result
