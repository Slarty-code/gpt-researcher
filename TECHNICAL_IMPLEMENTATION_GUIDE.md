# Technical Implementation Guide: Legal RAG Enhancement

## 🏗️ Architecture Overview

### Current GPT Researcher Architecture
```
Frontend (Next.js) → Backend (FastAPI) → GPT Researcher Core → LLM Providers
```

### Enhanced Architecture for Legal Documents
```
Frontend (Next.js) → Backend (FastAPI) → Enhanced RAG Pipeline → Legal Document Processing → Multi-Modal Retrieval → LLM Providers
```

## 🔧 Implementation Phases

### Phase 1: Enhanced Chunking System

#### 1.1 Semantic Chunking Implementation
```python
# File: gpt_researcher/chunking/semantic_chunker.py
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict, Any
import numpy as np

class LegalSemanticChunker:
    def __init__(self, 
                 model_name: str = "all-MiniLM-L6-v2",
                 similarity_threshold: float = 0.85,
                 min_chunk_size: int = 200,
                 max_chunk_size: int = 1000):
        self.model = SentenceTransformer(model_name)
        self.similarity_threshold = similarity_threshold
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
    
    def chunk_document(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Chunk document using semantic similarity"""
        sentences = self._split_into_sentences(text)
        embeddings = self.model.encode(sentences, convert_to_tensor=True)
        
        chunks = []
        current_chunk = [sentences[0]]
        
        for i in range(1, len(sentences)):
            similarity = util.pytorch_cos_sim(embeddings[i-1], embeddings[i]).item()
            
            if similarity > self.similarity_threshold and len(' '.join(current_chunk)) < self.max_chunk_size:
                current_chunk.append(sentences[i])
            else:
                if len(' '.join(current_chunk)) >= self.min_chunk_size:
                    chunks.append(self._create_chunk(current_chunk, metadata))
                current_chunk = [sentences[i]]
        
        if current_chunk:
            chunks.append(self._create_chunk(current_chunk, metadata))
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using legal-aware tokenization"""
        # Implement legal document sentence splitting
        pass
    
    def _create_chunk(self, sentences: List[str], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create chunk with legal-specific metadata"""
        content = ' '.join(sentences)
        return {
            'content': content,
            'metadata': {
                **metadata,
                'chunk_type': 'semantic',
                'sentence_count': len(sentences),
                'legal_entities': self._extract_legal_entities(content)
            }
        }
    
    def _extract_legal_entities(self, text: str) -> List[str]:
        """Extract legal entities from text"""
        # Implement legal entity extraction
        pass
```

#### 1.2 Legal-Specific Recursive Chunking
```python
# File: gpt_researcher/chunking/legal_recursive_chunker.py
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Any
import re

class LegalRecursiveChunker:
    def __init__(self, 
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.legal_separators = [
            "\n\nArticle ",  # Legal articles
            "\n\nSection ",  # Legal sections
            "\n\nClause ",   # Legal clauses
            "\n\n",          # Paragraph breaks
            "\n",            # Line breaks
            ". ",            # Sentence endings
            " ",             # Word boundaries
            ""               # Character level
        ]
    
    def chunk_document(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Chunk document using legal-aware recursive splitting"""
        splitter = RecursiveCharacterTextSplitter(
            separators=self.legal_separators,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len
        )
        
        chunks = splitter.split_text(text)
        legal_chunks = []
        
        for i, chunk in enumerate(chunks):
            legal_chunks.append(self._create_legal_chunk(chunk, i, metadata))
        
        return legal_chunks
    
    def _create_legal_chunk(self, content: str, index: int, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create chunk with legal-specific metadata"""
        return {
            'content': content,
            'metadata': {
                **metadata,
                'chunk_type': 'recursive_legal',
                'chunk_index': index,
                'legal_structure': self._identify_legal_structure(content),
                'article_references': self._extract_article_references(content)
            }
        }
    
    def _identify_legal_structure(self, content: str) -> str:
        """Identify legal document structure (article, section, clause, etc.)"""
        if re.search(r'Article \d+', content):
            return 'article'
        elif re.search(r'Section \d+', content):
            return 'section'
        elif re.search(r'Clause \d+', content):
            return 'clause'
        else:
            return 'paragraph'
    
    def _extract_article_references(self, content: str) -> List[str]:
        """Extract article references from content"""
        return re.findall(r'Article \d+', content)
```

### Phase 2: Document Processing Enhancement

#### 2.1 Legal Document Parser
```python
# File: gpt_researcher/document/legal_document_parser.py
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.docx import partition_docx
from typing import List, Dict, Any
import re

class LegalDocumentParser:
    def __init__(self):
        self.legal_patterns = {
            'article': r'Article \d+',
            'section': r'Section \d+',
            'clause': r'Clause \d+',
            'party': r'(?:Party|Parties?)\s+[A-Z][a-zA-Z\s]+',
            'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            'amount': r'\$[\d,]+(?:\.\d{2})?'
        }
    
    def parse_document(self, file_path: str) -> Dict[str, Any]:
        """Parse legal document and extract structured information"""
        if file_path.endswith('.pdf'):
            elements = partition_pdf(file_path)
        elif file_path.endswith('.docx'):
            elements = partition_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
        
        parsed_doc = {
            'file_path': file_path,
            'elements': elements,
            'legal_structure': self._extract_legal_structure(elements),
            'metadata': self._extract_metadata(elements)
        }
        
        return parsed_doc
    
    def _extract_legal_structure(self, elements: List[Any]) -> Dict[str, Any]:
        """Extract legal document structure"""
        structure = {
            'articles': [],
            'sections': [],
            'clauses': [],
            'parties': [],
            'dates': [],
            'amounts': []
        }
        
        for element in elements:
            text = element.text if hasattr(element, 'text') else str(element)
            
            for pattern_type, pattern in self.legal_patterns.items():
                matches = re.findall(pattern, text)
                if matches:
                    structure[pattern_type + 's'].extend(matches)
        
        return structure
    
    def _extract_metadata(self, elements: List[Any]) -> Dict[str, Any]:
        """Extract document metadata"""
        metadata = {
            'document_type': 'legal',
            'total_elements': len(elements),
            'has_tables': any('table' in str(type(elem)).lower() for elem in elements),
            'has_images': any('image' in str(type(elem)).lower() for elem in elements)
        }
        
        return metadata
```

#### 2.2 Legal Entity Extraction
```python
# File: gpt_researcher/document/legal_entity_extractor.py
import spacy
from typing import List, Dict, Any
import re

class LegalEntityExtractor:
    def __init__(self, model_name: str = "en_core_web_sm"):
        self.nlp = spacy.load(model_name)
        self.legal_entities = {
            'PARTY': r'(?:Party|Parties?)\s+[A-Z][a-zA-Z\s]+',
            'DATE': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            'AMOUNT': r'\$[\d,]+(?:\.\d{2})?',
            'ARTICLE': r'Article \d+',
            'SECTION': r'Section \d+',
            'CLAUSE': r'Clause \d+'
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract legal entities from text"""
        entities = {}
        
        # Use spaCy for general NER
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG', 'DATE', 'MONEY']:
                if ent.label_ not in entities:
                    entities[ent.label_] = []
                entities[ent.label_].append(ent.text)
        
        # Use regex for legal-specific entities
        for entity_type, pattern in self.legal_entities.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches
        
        return entities
```

### Phase 3: Enhanced Retrieval System

#### 3.1 Hybrid Retrieval Implementation
```python
# File: gpt_researcher/retrieval/hybrid_retriever.py
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
import re

class HybridLegalRetriever:
    def __init__(self, 
                 vector_store,
                 embedding_model: str = "all-MiniLM-L6-v2"):
        self.vector_store = vector_store
        self.embedding_model = SentenceTransformer(embedding_model)
        self.legal_keywords = self._load_legal_keywords()
    
    def retrieve(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Hybrid retrieval combining semantic and keyword search"""
        # Semantic retrieval
        semantic_results = self._semantic_retrieve(query, top_k)
        
        # Keyword retrieval
        keyword_results = self._keyword_retrieve(query, top_k)
        
        # Combine and rerank results
        combined_results = self._combine_results(semantic_results, keyword_results)
        reranked_results = self._rerank_results(query, combined_results)
        
        return reranked_results[:top_k]
    
    def _semantic_retrieve(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Semantic similarity retrieval"""
        query_embedding = self.embedding_model.encode([query])
        results = self.vector_store.similarity_search_by_vector(
            query_embedding[0], 
            k=top_k
        )
        return results
    
    def _keyword_retrieve(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Keyword-based retrieval for legal terms"""
        legal_terms = self._extract_legal_terms(query)
        results = []
        
        for term in legal_terms:
            term_results = self.vector_store.similarity_search(term, k=top_k//len(legal_terms))
            results.extend(term_results)
        
        return results
    
    def _extract_legal_terms(self, query: str) -> List[str]:
        """Extract legal terms from query"""
        legal_terms = []
        query_lower = query.lower()
        
        for keyword in self.legal_keywords:
            if keyword.lower() in query_lower:
                legal_terms.append(keyword)
        
        return legal_terms
    
    def _combine_results(self, semantic_results: List, keyword_results: List) -> List[Dict[str, Any]]:
        """Combine semantic and keyword results"""
        # Implement result combination logic
        pass
    
    def _rerank_results(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rerank results based on legal relevance"""
        # Implement legal-specific reranking
        pass
    
    def _load_legal_keywords(self) -> List[str]:
        """Load legal domain keywords"""
        return [
            'contract', 'agreement', 'clause', 'article', 'section',
            'party', 'parties', 'obligation', 'liability', 'indemnity',
            'warranty', 'representation', 'covenant', 'condition'
        ]
```

### Phase 4: Integration with GPT Researcher

#### 4.1 Enhanced Document Processing Pipeline
```python
# File: gpt_researcher/document/enhanced_document_processor.py
from typing import List, Dict, Any
import asyncio

class EnhancedDocumentProcessor:
    def __init__(self):
        self.parser = LegalDocumentParser()
        self.semantic_chunker = LegalSemanticChunker()
        self.recursive_chunker = LegalRecursiveChunker()
        self.entity_extractor = LegalEntityExtractor()
    
    async def process_legal_document(self, file_path: str) -> List[Dict[str, Any]]:
        """Process legal document with enhanced pipeline"""
        # Parse document
        parsed_doc = self.parser.parse_document(file_path)
        
        # Extract text and metadata
        text = self._extract_text(parsed_doc['elements'])
        metadata = parsed_doc['metadata']
        
        # Create chunks using multiple strategies
        semantic_chunks = self.semantic_chunker.chunk_document(text, metadata)
        recursive_chunks = self.recursive_chunker.chunk_document(text, metadata)
        
        # Combine and deduplicate chunks
        combined_chunks = self._combine_chunks(semantic_chunks, recursive_chunks)
        
        # Extract legal entities for each chunk
        for chunk in combined_chunks:
            chunk['metadata']['legal_entities'] = self.entity_extractor.extract_entities(
                chunk['content']
            )
        
        return combined_chunks
    
    def _extract_text(self, elements: List[Any]) -> str:
        """Extract text from document elements"""
        text_parts = []
        for element in elements:
            if hasattr(element, 'text'):
                text_parts.append(element.text)
        return '\n\n'.join(text_parts)
    
    def _combine_chunks(self, semantic_chunks: List, recursive_chunks: List) -> List[Dict[str, Any]]:
        """Combine and deduplicate chunks from different strategies"""
        # Implement chunk combination logic
        pass
```

## 🧪 Testing Framework

### 4.1 Legal Document Test Suite
```python
# File: tests/test_legal_rag.py
import pytest
from gpt_researcher.chunking.semantic_chunker import LegalSemanticChunker
from gpt_researcher.document.legal_document_parser import LegalDocumentParser

class TestLegalRAG:
    def test_semantic_chunking(self):
        """Test semantic chunking for legal documents"""
        chunker = LegalSemanticChunker()
        test_text = "Article 1. This agreement shall be governed by the laws of the State of California. Article 2. The parties agree to resolve disputes through arbitration."
        
        chunks = chunker.chunk_document(test_text)
        
        assert len(chunks) > 0
        assert all('content' in chunk for chunk in chunks)
        assert all('metadata' in chunk for chunk in chunks)
    
    def test_legal_entity_extraction(self):
        """Test legal entity extraction"""
        parser = LegalDocumentParser()
        test_text = "Party A agrees to pay Party B $10,000 on January 1, 2024."
        
        entities = parser._extract_legal_structure([test_text])
        
        assert 'parties' in entities
        assert 'amounts' in entities
        assert 'dates' in entities
    
    def test_hybrid_retrieval(self):
        """Test hybrid retrieval system"""
        # Implement hybrid retrieval tests
        pass
```

## 📊 Performance Monitoring

### 5.1 Metrics Collection
```python
# File: gpt_researcher/monitoring/performance_monitor.py
import time
from typing import Dict, Any
import logging

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        self.logger = logging.getLogger(__name__)
    
    def track_chunking_performance(self, document_size: int, chunking_time: float, chunk_count: int):
        """Track chunking performance metrics"""
        self.metrics['chunking'] = {
            'document_size': document_size,
            'chunking_time': chunking_time,
            'chunk_count': chunk_count,
            'chunks_per_second': chunk_count / chunking_time
        }
    
    def track_retrieval_performance(self, query: str, retrieval_time: float, result_count: int):
        """Track retrieval performance metrics"""
        self.metrics['retrieval'] = {
            'query_length': len(query),
            'retrieval_time': retrieval_time,
            'result_count': result_count
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return self.metrics
```

## 🚀 Deployment Configuration

### 6.1 Docker Configuration
```dockerfile
# File: Dockerfile.legal-rag
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements-legal.txt .
RUN pip install -r requirements-legal.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . /app
WORKDIR /app

# Run application
CMD ["python", "-m", "uvicorn", "backend.server.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 6.2 Requirements File
```txt
# File: requirements-legal.txt
# Existing GPT Researcher requirements
# ... (include all existing requirements)

# Legal RAG specific requirements
sentence-transformers>=2.2.0
spacy>=3.4.0
unstructured[pdf,docx]>=0.8.0
cohere>=4.0.0
flashrank>=0.1.0
voyageai>=0.1.0
```

## 📈 Success Metrics

### Technical Metrics:
- **Chunking Quality**: 15-25% improvement in chunk relevance
- **Retrieval Accuracy**: 90%+ relevant results in top 5
- **Processing Speed**: < 2 hours for full corpus ingestion
- **Query Response Time**: < 3 seconds for complex queries

### Business Metrics:
- **User Satisfaction**: 4.5+ stars from legal users
- **Query Success Rate**: 85%+ queries answered satisfactorily
- **Time Savings**: 50%+ reduction in document search time
- **Accuracy**: 95%+ accuracy on legal fact extraction

## 🔄 Next Steps

1. **Week 1**: Set up development environment and begin Phase 1
2. **Week 2**: Complete architecture design and start chunking implementation
3. **Week 3**: Implement semantic and recursive chunking
4. **Week 4**: Complete chunking system and begin document processing
5. **Week 5-6**: Implement document processing and entity extraction
6. **Week 7-8**: Build hybrid retrieval and reranking systems
7. **Week 9-10**: Comprehensive testing and validation
8. **Week 11-12**: Deployment and optimization