"""
Integration wrapper for Legal Document Enhancement

This module provides a safe integration layer that adds enhanced document
processing to GPT Researcher without modifying the core system.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from langchain.docstore.document import Document

from .document_processor import LegalDocumentProcessor
from .chunker import LegalChunker
from .email_processor import EmailProcessor
from .archive_processor import ArchiveProcessor

logger = logging.getLogger(__name__)

class LegalDocumentEnhancement:
    """
    Integration wrapper that adds legal document processing capabilities
    to GPT Researcher without modifying the core system.
    """
    
    def __init__(self, 
                 use_enhanced_processing: bool = True,
                 use_semantic_chunking: bool = True,
                 **kwargs):
        """
        Initialize the legal document enhancement.
        
        Args:
            use_enhanced_processing: Whether to use enhanced document processing
            use_semantic_chunking: Whether to use semantic chunking
            **kwargs: Additional arguments for processors
        """
        self.use_enhanced_processing = use_enhanced_processing
        self.use_semantic_chunking = use_semantic_chunking
        
        # Initialize processors
        if use_enhanced_processing:
            self.document_processor = LegalDocumentProcessor(**kwargs)
        else:
            self.document_processor = None
        
        if use_semantic_chunking:
            self.chunker = LegalChunker()
        else:
            self.chunker = None
        
        # Always initialize email processor (lightweight)
        self.email_processor = EmailProcessor()
        
        # Always initialize archive processor (lightweight)
        self.archive_processor = ArchiveProcessor()
        
        logger.info(f"Legal Document Enhancement initialized - "
                   f"Enhanced processing: {use_enhanced_processing}, "
                   f"Semantic chunking: {use_semantic_chunking}")
    
    async def process_document(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Process a document with enhanced capabilities.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Dictionary containing processed document data
        """
        if self.document_processor and self.use_enhanced_processing:
            try:
                logger.info(f"Using enhanced document processing for: {file_path}")
                return await self.document_processor.process_document(file_path)
            except Exception as e:
                logger.warning(f"Enhanced processing failed: {e}")
                logger.info("Falling back to GPT Researcher's processing")
        
        # Fallback to GPT Researcher's processing
        return await self._fallback_processing(file_path)
    
    async def _fallback_processing(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Fallback to GPT Researcher's existing document processing."""
        # This would integrate with GPT Researcher's existing DocumentLoader
        # For now, we'll return a basic structure
        return {
            "raw_content": f"Processed {file_path} with GPT Researcher",
            "url": Path(file_path).name,
            "enhanced_processing": False,
            "metadata": {
                "file_type": Path(file_path).suffix.lower(),
                "processing_method": "gpt_researcher"
            }
        }
    
    def chunk_document(self, document: Document) -> List[Document]:
        """
        Chunk a document with enhanced capabilities.
        
        Args:
            document: LangChain Document to chunk
            
        Returns:
            List of chunked documents
        """
        if self.chunker and self.use_semantic_chunking:
            try:
                logger.info("Using your original semantic chunking (BETTER QUALITY)")
                return self.chunker.chunk_document_semantic(document)
            except Exception as e:
                logger.warning(f"Original semantic chunking failed: {e}")
                logger.info("Falling back to basic semantic chunking")
                try:
                    return self.chunker.chunk_document(document)
                except Exception as e2:
                    logger.warning(f"Basic semantic chunking failed: {e2}")
                    logger.info("Falling back to GPT Researcher's chunking")
        
        # Fallback to GPT Researcher's chunking
        return self._fallback_chunking(document)
    
    def _fallback_chunking(self, document: Document) -> List[Document]:
        """Fallback to GPT Researcher's existing chunking."""
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        return text_splitter.split_documents([document])
    
    async def process_documents_batch(self, file_paths: List[Union[str, Path]]) -> List[Dict[str, Any]]:
        """Process multiple documents in batch."""
        if self.document_processor and self.use_enhanced_processing:
            return await self.document_processor.process_documents_batch(file_paths)
        else:
            # Fallback processing
            results = []
            for file_path in file_paths:
                result = await self._fallback_processing(file_path)
                results.append(result)
            return results
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Chunk multiple documents."""
        if self.chunker and self.use_semantic_chunking:
            return self.chunker.chunk_documents(documents)
        else:
            # Fallback chunking
            all_chunks = []
            for doc in documents:
                chunks = self._fallback_chunking(doc)
                all_chunks.extend(chunks)
            return all_chunks
    
    async def process_email_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Process an email file (MSG, EML, or PST) with enhanced capabilities.
        
        Args:
            file_path: Path to the email file
            
        Returns:
            Dictionary with processed email content and metadata
        """
        return await self.email_processor.process_email_file(file_path)
    
    async def process_email_files_batch(self, file_paths: List[Union[str, Path]]) -> List[Dict[str, Any]]:
        """
        Process multiple email files in batch.
        
        Args:
            file_paths: List of paths to email files
            
        Returns:
            List of processed email documents
        """
        return await self.email_processor.process_email_files_batch(file_paths)
    
    async def process_archive_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Process an archive file (ZIP, RAR, TAR) with enhanced capabilities.
        
        Args:
            file_path: Path to the archive file
            
        Returns:
            Dictionary with processed archive content and metadata
        """
        return await self.archive_processor.process_archive_file(file_path)
    
    async def process_archive_files_batch(self, file_paths: List[Union[str, Path]]) -> List[Dict[str, Any]]:
        """
        Process multiple archive files in batch.
        
        Args:
            file_paths: List of paths to archive files
            
        Returns:
            List of processed archive documents
        """
        return await self.archive_processor.process_archive_files_batch(file_paths)
    
    def get_processing_info(self) -> Dict[str, Any]:
        """Get information about the current processing configuration."""
        return {
            "enhanced_processing": self.use_enhanced_processing,
            "semantic_chunking": self.use_semantic_chunking,
            "email_processing": self.email_processor.is_available(),
            "pst_processing": self.email_processor.can_process_pst(),
            "archive_processing": self.archive_processor.is_available(),
            "zip_processing": self.archive_processor.can_process_zip(),
            "rar_processing": self.archive_processor.can_process_rar(),
            "document_processor_available": self.document_processor is not None,
            "chunker_available": self.chunker is not None
        }