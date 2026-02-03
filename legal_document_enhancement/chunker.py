"""
Legal Document Chunker

This module provides enhanced chunking capabilities for legal documents
that work alongside GPT Researcher's existing chunking without modifying
the core system.
"""

import logging
from typing import List, Dict, Any, Optional
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Optional imports with fallback handling
try:
    import numpy as np
    from sentence_transformers import SentenceTransformer, util
    SEMANTIC_CHUNKING_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Semantic chunking dependencies not available: {e}")
    SEMANTIC_CHUNKING_AVAILABLE = False
    np = None
    SentenceTransformer = None
    util = None

logger = logging.getLogger(__name__)

class LegalChunker:
    """
    Enhanced chunker for legal documents that provides semantic chunking
    capabilities alongside GPT Researcher's existing chunking.
    """
    
    def __init__(self,
                 model_name: str = "BAAI/bge-large-en-v1.5",
                 similarity_threshold: float = 0.75,
                 min_chunk_size: int = 200,
                 max_chunk_size: int = 1000,
                 chunk_overlap: int = 100):
        """
        Initialize the legal chunker.
        
        Args:
            model_name: Name of the sentence transformer model
            similarity_threshold: Threshold for semantic similarity
            min_chunk_size: Minimum chunk size in characters
            max_chunk_size: Maximum chunk size in characters
            chunk_overlap: Overlap between chunks
        """
        self.model_name = model_name
        self.similarity_threshold = similarity_threshold
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize the embedding model
        self._initialize_model()
        
        # Fallback to GPT Researcher's chunker
        self.fallback_chunker = RecursiveCharacterTextSplitter(
            chunk_size=max_chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    def _initialize_model(self):
        """Initialize the sentence transformer model."""
        if not SEMANTIC_CHUNKING_AVAILABLE:
            logger.info("Semantic chunking not available, using fallback mode")
            self.model = None
            return
            
        try:
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load sentence transformer model: {e}")
            logger.info("Falling back to basic chunking")
            self.model = None
    
    def chunk_document(self, document: Document) -> List[Document]:
        """
        Chunk a document using enhanced semantic chunking.
        
        Args:
            document: LangChain Document to chunk
            
        Returns:
            List of chunked documents
        """
        if not self.model:
            logger.info("Using fallback chunking")
            return self.fallback_chunker.split_documents([document])
        
        try:
            return self._semantic_chunk(document)
        except Exception as e:
            logger.warning(f"Semantic chunking failed: {e}")
            logger.info("Falling back to GPT Researcher's chunking")
            return self.fallback_chunker.split_documents([document])
    
    def chunk_document_semantic(self, document: Document) -> List[Document]:
        """
        Use your original semantic chunking approach - MUCH better quality!
        This preserves the AI-guided semantic chunking from your RAG stack.
        """
        if not self.model:
            logger.info("Semantic model not available, using fallback")
            return self.fallback_chunker.split_documents([document])
        
        try:
            return self._semantic_chunk_original(document)
        except Exception as e:
            logger.warning(f"Original semantic chunking failed: {e}")
            return self.fallback_chunker.split_documents([document])
    
    def _semantic_chunk(self, document: Document) -> List[Document]:
        """Perform semantic chunking on the document."""
        text = document.page_content
        metadata = document.metadata.copy()
        
        # Split text into sentences
        sentences = self._split_into_sentences(text)
        
        if len(sentences) < 2:
            # If too few sentences, return as single chunk
            return [Document(page_content=text, metadata=metadata)]
        
        # Generate embeddings for sentences
        embeddings = self.model.encode(sentences)
        
        # Group sentences into semantic chunks
        chunks = self._group_sentences_semantically(sentences, embeddings)
        
        # Convert chunks to Document objects
        chunked_docs = []
        for i, chunk_text in enumerate(chunks):
            if len(chunk_text.strip()) >= self.min_chunk_size:
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    "chunk_index": i,
                    "chunking_method": "semantic",
                    "total_chunks": len(chunks)
                })
                chunked_docs.append(Document(page_content=chunk_text, metadata=chunk_metadata))
        
        return chunked_docs
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        import re
        
        # Simple sentence splitting (can be enhanced with more sophisticated methods)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def _group_sentences_semantically(self, sentences: List[str], embeddings) -> List[str]:
        """Group sentences into semantic chunks based on similarity."""
        chunks = []
        current_chunk = []
        current_chunk_embeddings = []
        
        for i, (sentence, embedding) in enumerate(zip(sentences, embeddings)):
            if not current_chunk:
                # Start new chunk
                current_chunk.append(sentence)
                current_chunk_embeddings.append(embedding)
            else:
                # Calculate similarity with current chunk
                current_chunk_embedding = np.mean(current_chunk_embeddings, axis=0)
                similarity = util.cos_sim(embedding, current_chunk_embedding).item()
                
                # Check if we should start a new chunk
                should_start_new = (
                    similarity < self.similarity_threshold or
                    len(" ".join(current_chunk)) > self.max_chunk_size
                )
                
                if should_start_new and current_chunk:
                    # Finalize current chunk
                    chunks.append(" ".join(current_chunk))
                    current_chunk = [sentence]
                    current_chunk_embeddings = [embedding]
                else:
                    # Add to current chunk
                    current_chunk.append(sentence)
                    current_chunk_embeddings.append(embedding)
        
        # Add final chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def _semantic_chunk_original(self, document: Document) -> List[Document]:
        """
        Your original semantic chunking approach - preserves the quality!
        This is the AI-guided chunking from your RAG stack.
        """
        text = document.page_content
        metadata = document.metadata.copy()
        
        # Split text into sentences (your original approach)
        sentences = self._split_into_sentences(text)
        
        if len(sentences) < 2:
            return [Document(page_content=text, metadata=metadata)]
        
        # Generate embeddings for all sentences
        embeddings = self.model.encode(sentences)
        
        # Your original semantic grouping logic
        chunks = []
        current_chunk = []
        current_chunk_embeddings = []
        
        for i, (sentence, embedding) in enumerate(zip(sentences, embeddings)):
            if not current_chunk:
                # Start new chunk
                current_chunk.append(sentence)
                current_chunk_embeddings.append(embedding)
            else:
                # Calculate similarity with current chunk (your original logic)
                current_chunk_embedding = np.mean(current_chunk_embeddings, axis=0)
                similarity = util.cos_sim(embedding, current_chunk_embedding).item()
                
                # Check if we should start a new chunk (your original threshold logic)
                should_start_new = (
                    similarity < self.similarity_threshold or
                    len(" ".join(current_chunk)) > self.max_chunk_size
                )
                
                if should_start_new and current_chunk:
                    # Finalize current chunk
                    chunks.append(" ".join(current_chunk))
                    current_chunk = [sentence]
                    current_chunk_embeddings = [embedding]
                else:
                    # Add to current chunk
                    current_chunk.append(sentence)
                    current_chunk_embeddings.append(embedding)
        
        # Add final chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        # Convert to LangChain Documents (only change needed)
        chunked_docs = []
        for i, chunk_text in enumerate(chunks):
            if len(chunk_text.strip()) >= self.min_chunk_size:
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    "chunk_index": i,
                    "chunking_method": "semantic_original",  # Mark as original method
                    "total_chunks": len(chunks),
                    "similarity_threshold": self.similarity_threshold
                })
                chunked_docs.append(Document(page_content=chunk_text, metadata=chunk_metadata))
        
        return chunked_docs
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Chunk multiple documents."""
        all_chunks = []
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
        return all_chunks
    
    def chunk_legal_document(self, document: Document, 
                           legal_entities: Optional[List[str]] = None) -> List[Document]:
        """
        Chunk a legal document with special consideration for legal entities.
        
        Args:
            document: Document to chunk
            legal_entities: List of legal entities to preserve in chunks
            
        Returns:
            List of chunked documents
        """
        # First, do semantic chunking
        chunks = self.chunk_document(document)
        
        # If legal entities are provided, try to keep them together
        if legal_entities:
            chunks = self._preserve_legal_entities(chunks, legal_entities)
        
        return chunks
    
    def _preserve_legal_entities(self, chunks: List[Document], 
                                legal_entities: List[str]) -> List[Document]:
        """Ensure legal entities are preserved within chunks."""
        # This is a simplified implementation
        # In practice, you might want to use NER to identify legal entities
        # and ensure they don't get split across chunks
        
        preserved_chunks = []
        for chunk in chunks:
            # Check if any legal entities are split across chunk boundaries
            # For now, we'll just return the chunks as-is
            # This could be enhanced with more sophisticated logic
            preserved_chunks.append(chunk)
        
        return preserved_chunks