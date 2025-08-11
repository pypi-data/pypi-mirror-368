import os
import logging
from pathlib import Path
from typing import Dict, Any
import magic

from fabriq.document_loader.doc_utils import (
    BaseLoader, PyMuPDF4LLMLoader, UnstructuredLoader,
    MarkItDownLoader, WhisperLoader, PandasLoader, OpenPyXLLoader,
    #PythonDocxLoader, 
    PPTXLoader, SimpleTextLoader
)
from fabriq.document_loader.document_analyzer import (
    ContentAnalyzer,
    DocumentContent,
    LoaderType,
    BaseLoader,
    DocumentType
)

class SmartDocumentLoader:
    """Smart document loader that selects optimal loader based on content analysis"""

    def __init__(self):
        self.content_analyzer = ContentAnalyzer()
        self.loaders = self._initialize_loaders()
        self.logger = logging.getLogger(__name__)

    def _initialize_loaders(self) -> Dict[LoaderType, BaseLoader]:
        """Initialize all available loaders"""
        return {
            LoaderType.PYMUPDF4LLM: PyMuPDF4LLMLoader(),
            # LoaderType.DOCLING: DoclingLoader(),
            LoaderType.UNSTRUCTURED: UnstructuredLoader(),
            LoaderType.MARKITDOWN: MarkItDownLoader(),
            LoaderType.WHISPER: WhisperLoader(),
            LoaderType.PANDAS: PandasLoader(),
            LoaderType.OPENPYXL: OpenPyXLLoader(),
            # LoaderType.PYTHON_DOCX: PythonDocxLoader(),
            LoaderType.PPTX: PPTXLoader(),
            LoaderType.SIMPLE_TEXT: SimpleTextLoader(),
        }

    def detect_document_type(self, file_path: str) -> DocumentType:
        """Detect document type from file"""
        # Get file extension
        ext = Path(file_path).suffix.lower().lstrip(".")

        # Use magic library for more accurate detection
        try:
            mime_type = magic.from_file(file_path, mime=True)

            # Map MIME types to document types
            mime_mapping = {
                "application/pdf": DocumentType.PDF,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": DocumentType.DOCX,
                "application/msword": DocumentType.DOC,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": DocumentType.XLSX,
                "application/vnd.ms-excel": DocumentType.XLS,
                "application/vnd.openxmlformats-officedocument.presentationml.presentation": DocumentType.PPTX,
                "application/vnd.ms-powerpoint": DocumentType.PPT,
                "text/plain": DocumentType.TXT,
                "text/html": DocumentType.HTML,
                "text/csv": DocumentType.CSV,
                "application/json": DocumentType.JSON,
                "video/mp4": DocumentType.MP4,
                "audio/mpeg": DocumentType.MP3,
                "audio/wav": DocumentType.WAV,
                "image/png": DocumentType.PNG,
                "image/jpeg": DocumentType.JPG,
            }

            if mime_type in mime_mapping:
                return mime_mapping[mime_type]

        except Exception as e:
            self.logger.warning(f"Could not detect MIME type for {file_path}: {e}")

        # Fallback to extension-based detection
        try:
            return DocumentType(ext)
        except ValueError:
            self.logger.warning(f"Unknown file extension: {ext}")
            return DocumentType.TXT  # Default fallback

    def analyze_content(
        self, file_path: str, doc_type: DocumentType
    ) -> DocumentContent:
        """Analyze document content based on type"""
        if doc_type == DocumentType.PDF:
            return self.content_analyzer.analyze_pdf(file_path)
        elif doc_type == DocumentType.DOCX:
            return self.content_analyzer.analyze_docx(file_path)
        elif doc_type in [DocumentType.XLSX, DocumentType.XLS]:
            return self.content_analyzer.analyze_excel(file_path)
        elif doc_type == DocumentType.PPTX:
            return self.content_analyzer.analyze_pptx(file_path)
        else:
            return DocumentContent()

    def select_optimal_loader(
        self, doc_type: DocumentType, content: DocumentContent
    ) -> LoaderType:
        """Select the best loader based on document type and content analysis"""

        # Media files
        if doc_type in [
            DocumentType.MP4,
            DocumentType.AVI,
            DocumentType.MKV,
            DocumentType.MOV,
            DocumentType.MP3,
            DocumentType.WAV,
            DocumentType.M4A,
        ]:
            return LoaderType.WHISPER

        # PDF files - complex decision tree
        if doc_type == DocumentType.PDF:
            return self._select_pdf_loader(content)

        # Office documents
        if doc_type == DocumentType.DOCX:
            return self._select_docx_loader(content)

        if doc_type in [DocumentType.XLSX, DocumentType.XLS]:
            return self._select_excel_loader(content)

        if doc_type == DocumentType.PPTX:
            return LoaderType.MARKITDOWN

        # Structured data
        if doc_type == DocumentType.CSV:
            return LoaderType.PANDAS

        if doc_type == DocumentType.JSON:
            return LoaderType.SIMPLE_TEXT

        # Images
        if doc_type in [
            DocumentType.PNG,
            DocumentType.JPG,
            DocumentType.JPEG,
            DocumentType.GIF,
            DocumentType.BMP,
            DocumentType.TIFF,
        ]:
            return LoaderType.MULTIMODAL_LLM

        # Default fallback
        return LoaderType.MARKITDOWN

    def _select_pdf_loader(self, content: DocumentContent) -> LoaderType:
        """Select optimal PDF loader based on content analysis"""

        # Scanned documents or image-heavy PDFs
        if content.is_scanned or (content.has_images and content.image_count > 5):
            return LoaderType.UNSTRUCTURED

        # Complex layouts with diagrams and charts
        if content.has_diagrams or content.has_charts or content.has_complex_layout:
            return LoaderType.UNSTRUCTURED

        # Table-heavy documents
        if content.has_tables and content.table_count > 3:
            return LoaderType.UNSTRUCTURED

        # Forms
        if content.has_forms:
            return LoaderType.UNSTRUCTURED

        # Simple text-based PDFs
        if content.has_text and content.text_density > 0.5:
            return LoaderType.PYMUPDF4LLM

        # Default for PDFs
        return LoaderType.PYMUPDF4LLM

    def _select_docx_loader(self, content: DocumentContent) -> LoaderType:
        """Select optimal DOCX loader"""

        # Complex documents with many tables and images
        if content.has_tables and content.table_count > 2 and content.has_images:
            return LoaderType.MARKITDOWN

        # Simple text documents
        if content.has_text and not content.has_tables and not content.has_images:
            return LoaderType.MARKITDOWN

        # Default
        return LoaderType.MARKITDOWN

    def _select_excel_loader(self, content: DocumentContent) -> LoaderType:
        """Select optimal Excel loader"""

        # Charts and complex formatting
        if content.has_charts or content.has_images:
            return LoaderType.MARKITDOWN

        # Simple data tables
        return LoaderType.PANDAS

    def load_document(self, file_path: str) -> Dict[str, Any]:
        """Main method to load any document intelligently"""

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Step 1: Detect document type
        doc_type = self.detect_document_type(file_path)
        self.logger.info(f"Detected document type: {doc_type}")

        # Step 2: Analyze content
        content = self.analyze_content(file_path, doc_type)
        self.logger.info(f"Content analysis: {content}")

        # Step 3: Select optimal loader
        loader_type = self.select_optimal_loader(doc_type, content)
        self.logger.info(f"Selected loader: {loader_type}")

        # Step 4: Load document
        loader = self.loaders[loader_type]
        result = loader.load(file_path)

        # # Add metadata
        # result['metadata'].update({
        #         "source": file_path,
        #         "file_name": os.path.basename(file_path),
        #     }
        # )
        return result
