# Enhanced RAG Architecture Design for Legal Documents

## 🏗️ Current vs Enhanced Architecture

### Current GPT Researcher Architecture
```
Frontend (Next.js) → Backend (FastAPI) → GPT Researcher Core → LLM Providers
                                    ↓
                            Vector Store (Chroma/Pinecone)
                                    ↓
                            Basic Chunking (1000 chars, 200 overlap)
                                    ↓
                            Simple Retrieval (similarity search)
```

### Enhanced RAG Architecture for Legal Documents
```
Frontend (Next.js) → Backend (FastAPI) → Enhanced RAG Pipeline → Legal Document Processing → Multi-Modal Retrieval → LLM Providers
                                    ↓
                            Legal Document Parser (Unstructured.io)
                                    ↓
                            Advanced Chunking System
                                    ↓
                            Legal Entity Extraction
                                    ↓
                            Hybrid Vector Store (Chroma + Legal Metadata)
                                    ↓
                            Hybrid Retrieval (Semantic + Keyword + Legal)
                                    ↓
                            Legal Reranking (Cohere/FlashRank)
                                    ↓
                            Citation Tracking & Legal References
```

## 🔧 Implementation Strategy (One-Person Team)

### Phase 1: Enhanced Document Processing (Week 1-2)
**Goal**: Upgrade document processing for legal documents

#### 1.1 Legal Document Parser Enhancement
```python
# File: gpt_researcher/document/legal_document_parser.py
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.docx import partition_docx
import re
from typing import List, Dict, Any

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
        """Parse legal document with structure recognition"""
        if file_path.endswith('.pdf'):
            elements = partition_pdf(file_path, strategy="hi_res")
        elif file_path.endswith('.docx'):
            elements = partition_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
        
        return {
            'file_path': file_path,
            'elements': elements,
            'legal_structure': self._extract_legal_structure(elements),
            'metadata': self._extract_metadata(elements)
        }
    
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
```

#### 1.2 Enhanced Chunking System
```python
# File: gpt_researcher/chunking/legal_chunker.py
from sentence_transformers import SentenceTransformer, util
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Any
import numpy as np

class LegalChunker:
    def __init__(self, 
                 model_name: str = "all-MiniLM-L6-v2",
                 similarity_threshold: float = 0.85):
        self.model = SentenceTransformer(model_name)
        self.similarity_threshold = similarity_threshold
        self.recursive_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\nArticle ", "\n\nSection ", "\n\nClause ", "\n\n", "\n", ". ", " "],
            chunk_size=1000,
            chunk_overlap=200
        )
    
    def chunk_document(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Hybrid chunking: semantic + recursive for legal documents"""
        # First, try semantic chunking
        semantic_chunks = self._semantic_chunk(text, metadata)
        
        # Then, apply recursive chunking for structure preservation
        final_chunks = []
        for chunk in semantic_chunks:
            if len(chunk['content']) > 1500:  # If too large, split recursively
                recursive_chunks = self.recursive_splitter.split_text(chunk['content'])
                for i, rec_chunk in enumerate(recursive_chunks):
                    final_chunks.append({
                        'content': rec_chunk,
                        'metadata': {
                            **chunk['metadata'],
                            'chunk_type': 'hybrid',
                            'chunk_index': i,
                            'legal_entities': self._extract_legal_entities(rec_chunk)
                        }
                    })
            else:
                final_chunks.append(chunk)
        
        return final_chunks
    
    def _semantic_chunk(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Semantic chunking for legal documents"""
        sentences = text.split('. ')
        if len(sentences) < 2:
            return [{'content': text, 'metadata': metadata}]
        
        embeddings = self.model.encode(sentences)
        chunks = []
        current_chunk = [sentences[0]]
        
        for i in range(1, len(sentences)):
            similarity = util.pytorch_cos_sim(embeddings[i-1], embeddings[i]).item()
            
            if similarity > self.similarity_threshold:
                current_chunk.append(sentences[i])
            else:
                chunks.append({
                    'content': '. '.join(current_chunk),
                    'metadata': {
                        **metadata,
                        'chunk_type': 'semantic',
                        'legal_entities': self._extract_legal_entities('. '.join(current_chunk))
                    }
                })
                current_chunk = [sentences[i]]
        
        if current_chunk:
            chunks.append({
                'content': '. '.join(current_chunk),
                'metadata': {
                    **metadata,
                    'chunk_type': 'semantic',
                    'legal_entities': self._extract_legal_entities('. '.join(current_chunk))
                }
            })
        
        return chunks
    
    def _extract_legal_entities(self, text: str) -> List[str]:
        """Extract legal entities from text"""
        legal_entities = []
        for pattern_type, pattern in self.legal_patterns.items():
            matches = re.findall(pattern, text)
            legal_entities.extend(matches)
        return legal_entities
```

### Phase 2: Enhanced Retrieval System (Week 3-4)
**Goal**: Implement hybrid retrieval with legal-specific optimizations

#### 2.1 Hybrid Legal Retriever
```python
# File: gpt_researcher/retrieval/legal_retriever.py
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
import re

class LegalRetriever:
    def __init__(self, vector_store, embedding_model: str = "all-MiniLM-L6-v2"):
        self.vector_store = vector_store
        self.embedding_model = SentenceTransformer(embedding_model)
        self.legal_keywords = self._load_legal_keywords()
    
    def retrieve(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Hybrid retrieval: semantic + keyword + legal-specific"""
        # 1. Semantic retrieval
        semantic_results = self._semantic_retrieve(query, top_k)
        
        # 2. Keyword retrieval for legal terms
        keyword_results = self._keyword_retrieve(query, top_k)
        
        # 3. Legal entity retrieval
        entity_results = self._entity_retrieve(query, top_k)
        
        # 4. Combine and rerank
        combined_results = self._combine_results(semantic_results, keyword_results, entity_results)
        reranked_results = self._rerank_legal_results(query, combined_results)
        
        return reranked_results[:top_k]
    
    def _semantic_retrieve(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Semantic similarity retrieval"""
        query_embedding = self.embedding_model.encode([query])
        results = self.vector_store.similarity_search_by_vector(
            query_embedding[0], 
            k=top_k
        )
        return [{'content': doc.page_content, 'metadata': doc.metadata, 'score': 1.0} for doc in results]
    
    def _keyword_retrieve(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Keyword-based retrieval for legal terms"""
        legal_terms = self._extract_legal_terms(query)
        results = []
        
        for term in legal_terms:
            term_results = self.vector_store.similarity_search(term, k=top_k//len(legal_terms))
            results.extend([{'content': doc.page_content, 'metadata': doc.metadata, 'score': 0.8} for doc in term_results])
        
        return results
    
    def _entity_retrieve(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Retrieve based on legal entities in query"""
        entities = self._extract_legal_entities(query)
        results = []
        
        for entity in entities:
            entity_results = self.vector_store.similarity_search(entity, k=top_k//len(entities))
            results.extend([{'content': doc.page_content, 'metadata': doc.metadata, 'score': 0.9} for doc in entity_results])
        
        return results
    
    def _combine_results(self, semantic_results: List, keyword_results: List, entity_results: List) -> List[Dict[str, Any]]:
        """Combine results from different retrieval methods"""
        all_results = {}
        
        for result in semantic_results + keyword_results + entity_results:
            content = result['content']
            if content not in all_results:
                all_results[content] = result
            else:
                # Boost score if found in multiple methods
                all_results[content]['score'] = max(all_results[content]['score'], result['score']) + 0.1
        
        return list(all_results.values())
    
    def _rerank_legal_results(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rerank results based on legal relevance"""
        # Simple reranking based on legal entity matches
        for result in results:
            legal_entities = result['metadata'].get('legal_entities', [])
            query_entities = self._extract_legal_entities(query)
            
            # Boost score for legal entity matches
            entity_matches = len(set(legal_entities) & set(query_entities))
            result['score'] += entity_matches * 0.2
        
        return sorted(results, key=lambda x: x['score'], reverse=True)
    
    def _extract_legal_terms(self, query: str) -> List[str]:
        """Extract legal terms from query"""
        legal_terms = []
        query_lower = query.lower()
        
        for keyword in self.legal_keywords:
            if keyword.lower() in query_lower:
                legal_terms.append(keyword)
        
        return legal_terms
    
    def _extract_legal_entities(self, text: str) -> List[str]:
        """Extract legal entities from text"""
        legal_entities = []
        patterns = {
            'article': r'Article \d+',
            'section': r'Section \d+',
            'clause': r'Clause \d+',
            'party': r'(?:Party|Parties?)\s+[A-Z][a-zA-Z\s]+',
            'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            'amount': r'\$[\d,]+(?:\.\d{2})?'
        }
        
        for pattern_type, pattern in patterns.items():
            matches = re.findall(pattern, text)
            legal_entities.extend(matches)
        
        return legal_entities
    
    def _load_legal_keywords(self) -> List[str]:
        """Load legal domain keywords"""
        return [
            'contract', 'agreement', 'clause', 'article', 'section',
            'party', 'parties', 'obligation', 'liability', 'indemnity',
            'warranty', 'representation', 'covenant', 'condition',
            'breach', 'remedy', 'damages', 'termination', 'renewal'
        ]
```

### Phase 3: Integration with GPT Researcher (Week 5-6)
**Goal**: Integrate enhanced RAG with existing GPT Researcher pipeline

#### 3.1 Enhanced Document Loader
```python
# File: gpt_researcher/document/enhanced_document_loader.py
from .legal_document_parser import LegalDocumentParser
from .legal_chunker import LegalChunker
from typing import List, Dict, Any
import asyncio

class EnhancedDocumentLoader:
    def __init__(self):
        self.parser = LegalDocumentParser()
        self.chunker = LegalChunker()
    
    async def load_legal_documents(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Load and process legal documents with enhanced pipeline"""
        documents = []
        
        for file_path in file_paths:
            try:
                # Parse document
                parsed_doc = self.parser.parse_document(file_path)
                
                # Extract text
                text = self._extract_text(parsed_doc['elements'])
                
                # Create chunks
                chunks = self.chunker.chunk_document(text, {
                    'source': file_path,
                    'legal_structure': parsed_doc['legal_structure'],
                    'metadata': parsed_doc['metadata']
                })
                
                documents.extend(chunks)
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        return documents
    
    def _extract_text(self, elements: List[Any]) -> str:
        """Extract text from document elements"""
        text_parts = []
        for element in elements:
            if hasattr(element, 'text'):
                text_parts.append(element.text)
        return '\n\n'.join(text_parts)
```

#### 3.2 Enhanced Vector Store Integration
```python
# File: gpt_researcher/vector_store/enhanced_vector_store.py
from .vector_store import VectorStoreWrapper
from typing import List, Dict, Any

class EnhancedVectorStore(VectorStoreWrapper):
    def __init__(self, vector_store):
        super().__init__(vector_store)
        self.legal_metadata_fields = [
            'legal_entities', 'article_references', 'section_references',
            'party_names', 'dates', 'amounts', 'chunk_type'
        ]
    
    def load_legal_documents(self, documents: List[Dict[str, Any]]):
        """Load legal documents with enhanced metadata"""
        # Convert to LangChain documents with legal metadata
        langchain_documents = self._create_legal_langchain_documents(documents)
        
        # Split documents (already chunked, but may need further splitting)
        splitted_documents = self._split_legal_documents(langchain_documents)
        
        # Add to vector store
        self.vector_store.add_documents(splitted_documents)
    
    def _create_legal_langchain_documents(self, documents: List[Dict[str, Any]]) -> List[Document]:
        """Convert legal documents to LangChain format with enhanced metadata"""
        langchain_docs = []
        
        for doc in documents:
            metadata = {
                'source': doc['metadata'].get('source', ''),
                'chunk_type': doc['metadata'].get('chunk_type', 'unknown'),
                'legal_entities': doc['metadata'].get('legal_entities', []),
                'article_references': doc['metadata'].get('article_references', []),
                'section_references': doc['metadata'].get('section_references', []),
                'party_names': doc['metadata'].get('party_names', []),
                'dates': doc['metadata'].get('dates', []),
                'amounts': doc['metadata'].get('amounts', [])
            }
            
            langchain_docs.append(Document(
                page_content=doc['content'],
                metadata=metadata
            ))
        
        return langchain_docs
    
    def _split_legal_documents(self, documents: List[Document]) -> List[Document]:
        """Split legal documents if needed (most are already chunked)"""
        # For legal documents, we usually want to keep chunks as-is
        # Only split if they're too large
        final_documents = []
        
        for doc in documents:
            if len(doc.page_content) > 2000:  # If too large, split further
                from langchain.text_splitter import RecursiveCharacterTextSplitter
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200,
                    separators=["\n\n", "\n", ". ", " "]
                )
                split_docs = splitter.split_documents([doc])
                final_documents.extend(split_docs)
            else:
                final_documents.append(doc)
        
        return final_documents
```

## 🚀 Implementation Plan (One-Person Team)

### Week 1: Foundation
- [ ] **Day 1-2**: Set up legal document parser
- [ ] **Day 3-4**: Implement enhanced chunking system
- [ ] **Day 5**: Test with sample legal documents

### Week 2: Retrieval Enhancement
- [ ] **Day 1-2**: Implement hybrid legal retriever
- [ ] **Day 3-4**: Add legal entity extraction
- [ ] **Day 5**: Test retrieval with legal queries

### Week 3: Integration
- [ ] **Day 1-2**: Integrate with existing GPT Researcher
- [ ] **Day 3-4**: Test end-to-end pipeline
- [ ] **Day 5**: Optimize performance

### Week 4: Testing & Deployment
- [ ] **Day 1-2**: Comprehensive testing
- [ ] **Day 3-4**: Performance optimization
- [ ] **Day 5**: Deploy and monitor

## 📊 Success Metrics

### Technical Metrics
- **Chunking Quality**: 15-25% improvement in chunk relevance
- **Retrieval Accuracy**: 90%+ relevant results in top 5
- **Processing Speed**: < 2 hours for full corpus ingestion
- **Query Response Time**: < 3 seconds for complex queries

### Business Metrics
- **User Satisfaction**: 4.5+ stars from legal users
- **Query Success Rate**: 85%+ queries answered satisfactorily
- **Time Savings**: 50%+ reduction in document search time
- **Accuracy**: 95%+ accuracy on legal fact extraction

## 🔧 Key Implementation Notes

### 1. **Incremental Implementation**
- Start with basic legal document parsing
- Add semantic chunking gradually
- Implement hybrid retrieval step by step
- Test each component thoroughly

### 2. **Backward Compatibility**
- Maintain existing GPT Researcher functionality
- Add legal features as optional enhancements
- Use feature flags for gradual rollout

### 3. **Performance Optimization**
- Use caching for frequently accessed documents
- Implement async processing for large document sets
- Monitor and optimize memory usage

### 4. **Legal Domain Expertise**
- Involve legal experts in testing
- Validate legal entity extraction accuracy
- Ensure compliance with legal document handling

This architecture builds on your existing GPT Researcher foundation while adding the advanced RAG capabilities needed for your 7500-page legal document corpus! :-)