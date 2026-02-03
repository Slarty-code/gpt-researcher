# 🛡️ Dependency-Safe Integration Strategies

## **🚨 Problem: Major Package Conflicts**

### **Critical Conflicts Detected:**
- **sentence-transformers**: GPT Researcher `>=2.2.2` vs RAG Stack `4.1.0`
- **huggingface-hub**: GPT Researcher `>=0.32.0` vs RAG Stack `0.22.2`
- **langchain**: GPT Researcher `>=0.3.17` vs RAG Stack `0.0.267`
- **numpy**: GPT Researcher `>=2.2.6` vs RAG Stack `1.26.4`

## **🛡️ Strategy 1: Docker Microservices (RECOMMENDED)**

### **Architecture:**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GPT Researcher│    │  Legal RAG      │    │  Document       │
│   Container     │◄──►│  Enhancement    │◄──►│  Processing     │
│                 │    │  Container      │    │  Container      │
│ - LangChain 0.3+│    │ - LangChain 0.0+│    │ - PaddleOCR     │
│ - Transformers  │    │ - Transformers  │    │ - LayoutLMv3    │
│ - SentenceTrans │    │ - SentenceTrans │    │ - Camelot       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Benefits:**
- ✅ **Zero dependency conflicts** - each service has its own environment
- ✅ **Easy rollback** - just stop the enhancement container
- ✅ **Independent scaling** - scale each service separately
- ✅ **Technology isolation** - use best tool for each job

### **Implementation:**

#### **1. GPT Researcher Container (Unchanged)**
```dockerfile
# Dockerfile.gpt-researcher
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY gpt_researcher/ /app/gpt_researcher/
CMD ["python", "-m", "gpt_researcher"]
```

#### **2. Legal RAG Enhancement Container**
```dockerfile
# Dockerfile.legal-rag
FROM python:3.11-slim
COPY legal_rag_requirements.txt .
RUN pip install -r legal_rag_requirements.txt
COPY legal_rag_enhancement/ /app/legal_rag_enhancement/
CMD ["python", "-m", "legal_rag_enhancement"]
```

#### **3. Document Processing Container**
```dockerfile
# Dockerfile.document-processing
FROM python:3.11-slim
COPY document_processing_requirements.txt .
RUN pip install -r document_processing_requirements.txt
COPY document_processing/ /app/document_processing/
CMD ["python", "-m", "document_processing"]
```

#### **4. Docker Compose**
```yaml
# docker-compose.yml
version: '3.8'
services:
  gpt-researcher:
    build: .
    dockerfile: Dockerfile.gpt-researcher
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
  
  legal-rag:
    build: .
    dockerfile: Dockerfile.legal-rag
    ports:
      - "8001:8001"
    environment:
      - GPT_RESEARCHER_URL=http://gpt-researcher:8000
  
  document-processing:
    build: .
    dockerfile: Dockerfile.document-processing
    ports:
      - "8002:8002"
    volumes:
      - ./documents:/app/documents
```

## **🛡️ Strategy 2: API-Based Integration**

### **Architecture:**
```
┌─────────────────┐    HTTP API    ┌─────────────────┐
│   GPT Researcher│◄──────────────►│  Legal RAG      │
│   (Unchanged)   │                │  Enhancement    │
│                 │                │  Service        │
└─────────────────┘                └─────────────────┘
```

### **Implementation:**

#### **1. Legal RAG Enhancement Service**
```python
# legal_rag_service.py
from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

class DocumentRequest(BaseModel):
    file_path: str
    query: str

class DocumentResponse(BaseModel):
    enhanced_chunks: list
    legal_entities: list
    citations: list

@app.post("/process_document")
async def process_document(request: DocumentRequest):
    # Use your RAG stack's advanced processing
    enhanced_chunks = process_with_paddleocr(request.file_path)
    legal_entities = extract_legal_entities(enhanced_chunks)
    citations = extract_citations(enhanced_chunks)
    
    return DocumentResponse(
        enhanced_chunks=enhanced_chunks,
        legal_entities=legal_entities,
        citations=citations
    )

@app.post("/enhance_retrieval")
async def enhance_retrieval(query: str, chunks: list):
    # Use your RAG stack's reranking
    reranked_chunks = rerank_with_cross_encoder(query, chunks)
    return {"enhanced_chunks": reranked_chunks}
```

#### **2. GPT Researcher Integration**
```python
# gpt_researcher_enhanced.py
import requests
from gpt_researcher import GPTResearcher

class LegalGPTResearcher:
    def __init__(self, *args, **kwargs):
        self.gpt_researcher = GPTResearcher(*args, **kwargs)
        self.legal_rag_url = "http://localhost:8001"
    
    async def conduct_legal_research(self, query):
        # 1. Get GPT Researcher's results
        gpt_results = await self.gpt_researcher.conduct_research()
        
        # 2. Enhance with Legal RAG service
        enhanced_chunks = requests.post(
            f"{self.legal_rag_url}/enhance_retrieval",
            json={"query": query, "chunks": gpt_results}
        ).json()
        
        # 3. Return enhanced results
        return enhanced_chunks
```

## **🛡️ Strategy 3: Virtual Environment Isolation**

### **Implementation:**
```bash
# Create separate virtual environments
python -m venv venv_gpt_researcher
python -m venv venv_legal_rag
python -m venv venv_document_processing

# Install dependencies in each
source venv_gpt_researcher/bin/activate
pip install -r gpt_researcher_requirements.txt

source venv_legal_rag/bin/activate
pip install -r legal_rag_requirements.txt

source venv_document_processing/bin/activate
pip install -r document_processing_requirements.txt
```

### **Integration Script:**
```python
# integration_script.py
import subprocess
import sys
import os

def run_gpt_researcher(query):
    """Run GPT Researcher in its own environment"""
    cmd = [
        "venv_gpt_researcher/bin/python",
        "-m", "gpt_researcher",
        "--query", query
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def run_legal_rag_enhancement(query, documents):
    """Run Legal RAG enhancement in its own environment"""
    cmd = [
        "venv_legal_rag/bin/python",
        "-m", "legal_rag_enhancement",
        "--query", query,
        "--documents", documents
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def run_document_processing(file_path):
    """Run document processing in its own environment"""
    cmd = [
        "venv_document_processing/bin/python",
        "-m", "document_processing",
        "--file", file_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout
```

## **🛡️ Strategy 4: Conda Environment Isolation**

### **Implementation:**
```bash
# Create conda environments
conda create -n gpt_researcher python=3.11
conda create -n legal_rag python=3.11
conda create -n document_processing python=3.11

# Install dependencies
conda activate gpt_researcher
pip install -r gpt_researcher_requirements.txt

conda activate legal_rag
pip install -r legal_rag_requirements.txt

conda activate document_processing
pip install -r document_processing_requirements.txt
```

## **🎯 Recommended Approach: Docker Microservices**

### **Why Docker is Best:**
1. **Complete isolation** - no dependency conflicts possible
2. **Easy deployment** - works anywhere Docker runs
3. **Independent scaling** - scale each service as needed
4. **Easy rollback** - just stop the enhancement container
5. **Technology freedom** - use best tool for each job

### **Quick Start:**
```bash
# 1. Create the containers
docker-compose build

# 2. Start all services
docker-compose up -d

# 3. Test integration
curl -X POST "http://localhost:8001/process_document" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/documents/contract.pdf", "query": "What are the termination clauses?"}'

# 4. If something goes wrong, just stop the enhancement
docker-compose stop legal-rag document-processing
```

## **📋 Implementation Checklist:**

### **Week 1: Docker Setup**
- [ ] Create Dockerfile for each service
- [ ] Set up docker-compose.yml
- [ ] Test each service independently

### **Week 2: API Integration**
- [ ] Create Legal RAG API service
- [ ] Create Document Processing API service
- [ ] Test API communication

### **Week 3: GPT Researcher Integration**
- [ ] Create integration wrapper
- [ ] Test end-to-end workflow
- [ ] Performance testing

### **Week 4: Production Deployment**
- [ ] Add monitoring and logging
- [ ] Set up health checks
- [ ] Deploy to production

This approach gives you **zero dependency conflicts** while keeping **all the benefits** of both systems! :-)