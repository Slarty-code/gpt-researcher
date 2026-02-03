"""
Enhanced Document Processor for Legal Documents

This module provides advanced document processing capabilities that work alongside
GPT Researcher's existing document processing without modifying the core system.
"""

import os
import tempfile
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Document processing imports (with fallback handling)
try:
    import torch
    from pdf2image import convert_from_path
    from transformers import LayoutLMv3Processor, LayoutLMv3ForSequenceClassification
    from paddleocr import PaddleOCR
    import pytesseract
    from PIL import Image
    import camelot
    import numpy as np
    import pandas as pd
    ADVANCED_PROCESSING_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Advanced processing dependencies not available: {e}")
    ADVANCED_PROCESSING_AVAILABLE = False
    # Create mock objects for basic functionality
    torch = None
    convert_from_path = None
    LayoutLMv3Processor = None
    LayoutLMv3ForSequenceClassification = None
    PaddleOCR = None
    pytesseract = None
    # Create a mock Image class
    class MockImage:
        @staticmethod
        def open(path):
            return None
        class Image:
            pass
    Image = MockImage
    camelot = None
    # Create a mock numpy
    class MockNumpy:
        def array(self, data):
            return data
        def mean(self, data):
            return 0.0
    np = MockNumpy()
    pd = None

# GPT Researcher imports (unchanged)
from langchain_community.document_loaders import (
    PyMuPDFLoader,
    TextLoader,
    UnstructuredCSVLoader,
    UnstructuredExcelLoader,
    UnstructuredMarkdownLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader
)

logger = logging.getLogger(__name__)

class LegalDocumentProcessor:
    """
    Enhanced document processor that adds advanced capabilities to GPT Researcher
    without modifying the core system.
    """
    
    def __init__(self, 
                 use_gpu: bool = True,
                 ocr_lang: str = 'en',
                 default_dpi: int = 300,
                 max_workers: int = 4):
        """
        Initialize the enhanced document processor.
        
        Args:
            use_gpu: Whether to use GPU for processing
            ocr_lang: Language for OCR processing
            default_dpi: Default DPI for PDF conversion
            max_workers: Maximum number of worker threads
        """
        self.device = 'cuda' if torch and torch.cuda.is_available() and use_gpu else 'cpu'
        self.ocr_lang = ocr_lang
        self.default_dpi = default_dpi
        self.max_workers = max_workers
        
        # Initialize models
        self._initialize_models()
        
        # Supported file types
        self.image_exts = {
            '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif',
            '.webp', '.svg', '.eps', '.raw', '.cr2', '.nef',
            '.orf', '.sr2', '.gif'
        }
        
        self.native_loaders = {
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', 
            '.pptx', '.txt', '.rtf', '.odt', '.ods', '.odp',
            '.epub', '.mobi', '.azw', '.prc', '.fb2'
        } | self.image_exts
    
    def _initialize_models(self):
        """Initialize the ML models for document processing."""
        if not ADVANCED_PROCESSING_AVAILABLE:
            logger.info("Advanced processing not available, using fallback mode")
            self.layout_processor = None
            self.layout_model = None
            self.ocr_engine = None
            return
            
        try:
            if self.device == 'cuda' and torch and torch.cuda.is_available():
                logger.info("Initializing models on GPU...")
                self.layout_processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base")
                self.layout_model = LayoutLMv3ForSequenceClassification.from_pretrained(
                    "microsoft/layoutlmv3-base"
                ).to(self.device)
                self.ocr_engine = PaddleOCR(use_angle_cls=True, lang=self.ocr_lang, use_gpu=True)
            else:
                logger.info("Initializing models on CPU...")
                self.layout_processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base")
                self.layout_model = LayoutLMv3ForSequenceClassification.from_pretrained(
                    "microsoft/layoutlmv3-base"
                )
                self.ocr_engine = PaddleOCR(use_angle_cls=True, lang=self.ocr_lang, use_gpu=False)
            
            logger.info("Models initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize advanced models: {e}")
            logger.info("Falling back to basic processing")
            self.layout_processor = None
            self.layout_model = None
            self.ocr_engine = None
    
    async def process_document(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Process a document with enhanced capabilities.
        
        Args:
            file_path: Path to the document to process
            
        Returns:
            Dictionary containing processed document data
        """
        file_path = Path(file_path)
        file_extension = file_path.suffix.lower()
        
        logger.info(f"Processing document: {file_path}")
        
        # Try enhanced processing first
        if file_extension == '.pdf':
            return await self._process_pdf_enhanced(file_path)
        elif file_extension in self.image_exts:
            return await self._process_image_enhanced(file_path)
        else:
            # Fall back to GPT Researcher's existing processing
            return await self._process_with_gpt_researcher(file_path)
    
    async def _process_pdf_enhanced(self, file_path: Path) -> Dict[str, Any]:
        """Enhanced PDF processing with OCR and layout analysis."""
        try:
            # Convert PDF to images
            images = convert_from_path(str(file_path), dpi=self.default_dpi)
            
            # Process each page
            pages_data = []
            for page_num, image in enumerate(images):
                page_data = await self._process_page_enhanced(image, page_num)
                pages_data.append(page_data)
            
            # Combine all pages
            combined_content = self._combine_pages(pages_data)
            
            return {
                "raw_content": combined_content,
                "url": file_path.name,
                "enhanced_processing": True,
                "pages": pages_data,
                "metadata": {
                    "file_type": "pdf",
                    "total_pages": len(images),
                    "processing_method": "enhanced"
                }
            }
            
        except Exception as e:
            logger.warning(f"Enhanced PDF processing failed: {e}")
            logger.info("Falling back to GPT Researcher's PDF processing")
            return await self._process_with_gpt_researcher(file_path)
    
    async def _process_image_enhanced(self, file_path: Path) -> Dict[str, Any]:
        """Enhanced image processing with OCR."""
        try:
            image = Image.open(file_path)
            page_data = await self._process_page_enhanced(image, 0)
            
            return {
                "raw_content": page_data["content"],
                "url": file_path.name,
                "enhanced_processing": True,
                "pages": [page_data],
                "metadata": {
                    "file_type": "image",
                    "total_pages": 1,
                    "processing_method": "enhanced"
                }
            }
            
        except Exception as e:
            logger.warning(f"Enhanced image processing failed: {e}")
            logger.info("Falling back to GPT Researcher's image processing")
            return await self._process_with_gpt_researcher(file_path)
    
    async def _process_page_enhanced(self, image: Image.Image, page_num: int) -> Dict[str, Any]:
        """Process a single page with enhanced capabilities."""
        page_data = {
            "page_number": page_num,
            "content": "",
            "tables": [],
            "layout_info": {},
            "ocr_confidence": 0.0
        }
        
        try:
            # OCR processing
            if self.ocr_engine:
                ocr_results = self.ocr_engine.ocr(np.array(image))
                if ocr_results and ocr_results[0]:
                    text_parts = []
                    confidences = []
                    for line in ocr_results[0]:
                        if line and len(line) >= 2:
                            text_parts.append(line[1][0])
                            confidences.append(line[1][1])
                    
                    page_data["content"] = "\n".join(text_parts)
                    page_data["ocr_confidence"] = np.mean(confidences) if confidences else 0.0
                else:
                    # Fallback to pytesseract
                    page_data["content"] = pytesseract.image_to_string(image)
            else:
                # Fallback to pytesseract
                page_data["content"] = pytesseract.image_to_string(image)
            
            # Layout analysis
            if self.layout_processor and self.layout_model:
                try:
                    layout_info = await self._analyze_layout(image)
                    page_data["layout_info"] = layout_info
                except Exception as e:
                    logger.warning(f"Layout analysis failed: {e}")
            
            # Table extraction (if it's a PDF page)
            try:
                tables = await self._extract_tables(image, page_num)
                page_data["tables"] = tables
            except Exception as e:
                logger.warning(f"Table extraction failed: {e}")
            
        except Exception as e:
            logger.error(f"Error processing page {page_num}: {e}")
            # Fallback to basic text extraction
            page_data["content"] = pytesseract.image_to_string(image)
        
        return page_data
    
    async def _analyze_layout(self, image: Image.Image) -> Dict[str, Any]:
        """Analyze document layout using LayoutLMv3."""
        try:
            # Convert image to format expected by LayoutLMv3
            inputs = self.layout_processor(image, return_tensors="pt")
            
            # Move to device
            if self.device == 'cuda':
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get predictions
            with torch.no_grad():
                outputs = self.layout_model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Extract layout information
            layout_info = {
                "has_text": True,  # Assume text is present
                "confidence": float(torch.max(predictions).item()),
                "layout_type": "document"
            }
            
            return layout_info
            
        except Exception as e:
            logger.warning(f"Layout analysis failed: {e}")
            return {"has_text": True, "confidence": 0.0, "layout_type": "unknown"}
    
    async def _extract_tables(self, image: Image.Image, page_num: int) -> List[Dict[str, Any]]:
        """Extract tables from the page."""
        try:
            # Save image temporarily for table extraction
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                image.save(tmp_file.name)
                
                # Extract tables using camelot
                tables = camelot.read_pdf(tmp_file.name, pages=str(page_num + 1))
                
                # Clean up
                os.unlink(tmp_file.name)
                
                # Convert tables to dictionaries
                table_data = []
                for i, table in enumerate(tables):
                    table_data.append({
                        "table_number": i + 1,
                        "data": table.df.to_dict('records'),
                        "accuracy": table.accuracy,
                        "page_number": page_num + 1
                    })
                
                return table_data
                
        except Exception as e:
            logger.warning(f"Table extraction failed: {e}")
            return []
    
    def _combine_pages(self, pages_data: List[Dict[str, Any]]) -> str:
        """Combine content from all pages."""
        combined_content = []
        
        for page in pages_data:
            if page["content"]:
                combined_content.append(f"--- Page {page['page_number']} ---")
                combined_content.append(page["content"])
                
                # Add table data if present
                for table in page["tables"]:
                    combined_content.append(f"\n--- Table {table['table_number']} ---")
                    # Convert table to text
                    if table["data"]:
                        df = pd.DataFrame(table["data"])
                        combined_content.append(df.to_string(index=False))
        
        return "\n\n".join(combined_content)
    
    async def _process_with_gpt_researcher(self, file_path: Path) -> Dict[str, Any]:
        """Fallback to GPT Researcher's existing document processing."""
        try:
            file_extension = file_path.suffix.lower().strip('.')
            
            # Use GPT Researcher's existing loaders
            loader_dict = {
                "pdf": PyMuPDFLoader(str(file_path)),
                "txt": TextLoader(str(file_path)),
                "doc": UnstructuredWordDocumentLoader(str(file_path)),
                "docx": UnstructuredWordDocumentLoader(str(file_path)),
                "pptx": UnstructuredPowerPointLoader(str(file_path)),
                "csv": UnstructuredCSVLoader(str(file_path), mode="elements"),
                "xls": UnstructuredExcelLoader(str(file_path), mode="elements"),
                "xlsx": UnstructuredExcelLoader(str(file_path), mode="elements"),
                "md": UnstructuredMarkdownLoader(str(file_path)),
            }
            
            loader = loader_dict.get(file_extension)
            if loader:
                pages = loader.load()
                content = "\n".join([page.page_content for page in pages if page.page_content])
                
                return {
                    "raw_content": content,
                    "url": file_path.name,
                    "enhanced_processing": False,
                    "metadata": {
                        "file_type": file_extension,
                        "processing_method": "gpt_researcher"
                    }
                }
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
                
        except Exception as e:
            logger.error(f"GPT Researcher processing failed: {e}")
            raise
    
    async def process_documents_batch(self, file_paths: List[Union[str, Path]]) -> List[Dict[str, Any]]:
        """Process multiple documents in parallel."""
        tasks = [self.process_document(file_path) for file_path in file_paths]
        return await asyncio.gather(*tasks, return_exceptions=True)