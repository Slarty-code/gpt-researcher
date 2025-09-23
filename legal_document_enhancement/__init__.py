"""
Legal Document Enhancement Module

This module adds advanced document processing capabilities to GPT Researcher
without modifying the core system. It includes:

- PaddleOCR for complex PDFs with layout analysis
- LayoutLMv3 for document structure recognition
- Camelot for table extraction
- Enhanced error handling for legal documents
"""

from .document_processor import LegalDocumentProcessor
from .chunker import LegalChunker

__all__ = ["LegalDocumentProcessor", "LegalChunker"]