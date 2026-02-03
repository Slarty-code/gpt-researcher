# 🚀 GPT Researcher Full Stack Deployment Guide

## **🎯 Overview**

This guide shows you how to deploy the complete GPT Researcher stack with all enhancements in a single Docker Compose setup.

## **🏗️ Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   OWUI Frontend │    │   OWUI Bridge    │    │ GPT Researcher  │
│   (Port 3000)   │◄──►│   (Port 8002)    │◄──►│   (Port 8000)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │ Legal Enhancement│    │    ChromaDB     │
                       │   (Port 8001)    │    │   (Port 8003)   │
                       └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │      Redis       │
                       │   (Port 6379)    │
                       └──────────────────┘
```

## **📋 Prerequisites**

- Docker and Docker Compose installed
- OpenAI API key
- At least 8GB RAM (16GB recommended)
- 20GB free disk space

## **🚀 Quick Start**

### **Step 1: Clone and Setup**

```bash
# Clone the repository (if not already done)
git clone https://github.com/assafelovic/gpt-researcher.git
cd gpt-researcher

# Make startup script executable
chmod +x start-full-stack.sh
```

### **Step 2: Configure Environment**

```bash
# Copy environment template
cp env.full-stack env.full-stack.local

# Edit environment file
nano env.full-stack.local
```

**Required Configuration:**
```bash
# Set your OpenAI API key
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Optional: Set other configurations
RESEARCH_TYPE=research_report
USE_ENHANCED_PROCESSING=true
USE_SEMANTIC_CHUNKING=true
```

### **Step 3: Start the Full Stack**

```bash
# Start all services
./start-full-stack.sh

# Or manually with docker-compose
docker-compose -f docker-compose.full-stack.yml up --build -d
```

### **Step 4: Verify Services**

```bash
# Check all services
curl http://localhost:8000/health  # GPT Researcher
curl http://localhost:8001/health  # Legal Enhancement
curl http://localhost:8002/health  # OWUI Bridge
curl http://localhost:3000         # OWUI Frontend
```

## **🔧 Service Details**

### **GPT Researcher Core (Port 8000)**
- **Purpose:** Main research engine
- **Features:** Web research, report generation, multi-agent system
- **Health Check:** `http://localhost:8000/health`

### **Legal Enhancement (Port 8001)**
- **Purpose:** Advanced document processing
- **Features:** Email processing, archive support, semantic chunking
- **Health Check:** `http://localhost:8001/health`

### **OWUI Bridge (Port 8002)**
- **Purpose:** Bridge between OWUI and GPT Researcher
- **Features:** Multi-shot research, chain-of-thought prompting
- **Health Check:** `http://localhost:8002/health`

### **OWUI Frontend (Port 3000)**
- **Purpose:** Web interface for GPT Researcher
- **Features:** Chat interface, document upload, research management
- **URL:** `http://localhost:3000`

### **ChromaDB (Port 8003)**
- **Purpose:** Vector database for embeddings
- **Features:** Semantic search, document storage
- **Health Check:** `http://localhost:8003`

### **Redis (Port 6379)**
- **Purpose:** Caching and session storage
- **Features:** Performance optimization, session management

## **📊 API Endpoints**

### **GPT Researcher API:**
```bash
# Health check
GET http://localhost:8000/health

# Research endpoint
POST http://localhost:8000/research
{
  "query": "What are the key legal issues?",
  "research_type": "research_report"
}
```

### **Legal Enhancement API:**
```bash
# Health check
GET http://localhost:8001/health

# Process document
POST http://localhost:8001/process-document
{
  "file_path": "/app/data/contract.pdf",
  "use_enhanced_processing": true
}

# Process email
POST http://localhost:8001/process-email-file
{
  "file_path": "/app/data/emails.pst"
}

# Process archive
POST http://localhost:8001/process-archive-file
{
  "file_path": "/app/data/case_files.zip"
}
```

### **OWUI Bridge API:**
```bash
# Health check
GET http://localhost:8002/health

# Multi-shot research
POST http://localhost:8002/multi-shot-research
{
  "query": "What are the key legal issues?",
  "context_documents": ["/app/data/contract1.pdf"],
  "research_type": "research_report",
  "num_shots": 3
}

# Chain-of-thought research
POST http://localhost:8002/chain-of-thought-research
{
  "query": "Analyze the legal implications",
  "steps": ["Identify parties", "Analyze terms", "Assess risks"],
  "context_documents": ["/app/data/merger.pdf"]
}
```

## **📁 Directory Structure**

```
gpt-researcher/
├── docker-compose.full-stack.yml    # Full stack configuration
├── Dockerfile.gpt-researcher        # GPT Researcher container
├── Dockerfile.legal-enhancement     # Legal enhancement container
├── Dockerfile.owui-bridge          # OWUI bridge container
├── start-full-stack.sh             # Startup script
├── env.full-stack                  # Environment template
├── data/                           # Document storage
│   ├── contracts/
│   ├── emails/
│   └── archives/
├── logs/                           # Log files
└── legal_document_enhancement/     # Legal enhancement module
```

## **🔧 Configuration Options**

### **Environment Variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | Required | OpenAI API key |
| `RESEARCH_TYPE` | `research_report` | Type of research to perform |
| `MAX_ITERATIONS` | `3` | Maximum research iterations |
| `USE_ENHANCED_PROCESSING` | `true` | Enable enhanced document processing |
| `USE_SEMANTIC_CHUNKING` | `true` | Enable semantic chunking |
| `EMBED_MODEL_NAME` | `BAAI/bge-large-en-v1.5` | Embedding model |
| `SIMILARITY_THRESHOLD` | `0.75` | Similarity threshold for chunking |

### **Docker Compose Configuration:**

```yaml
# Customize resource limits
services:
  gpt-researcher:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'
```

## **📈 Performance Tuning**

### **Memory Requirements:**
- **Minimum:** 8GB RAM
- **Recommended:** 16GB RAM
- **For large corpora:** 32GB+ RAM

### **Storage Requirements:**
- **Base installation:** 5GB
- **Per 1000 documents:** 1GB
- **Vector database:** 2-4GB
- **Logs:** 1GB per month

### **CPU Requirements:**
- **Minimum:** 2 CPU cores
- **Recommended:** 4+ CPU cores
- **For large corpora:** 8+ CPU cores

## **🚨 Troubleshooting**

### **Common Issues:**

1. **Services not starting:**
   ```bash
   # Check logs
   docker-compose -f docker-compose.full-stack.yml logs
   
   # Restart services
   docker-compose -f docker-compose.full-stack.yml restart
   ```

2. **Out of memory:**
   ```bash
   # Check memory usage
   docker stats
   
   # Increase memory limits in docker-compose.yml
   ```

3. **API connection errors:**
   ```bash
   # Check service health
   curl http://localhost:8000/health
   curl http://localhost:8001/health
   curl http://localhost:8002/health
   ```

4. **Document processing failures:**
   ```bash
   # Check document paths
   ls -la ./data/
   
   # Check legal enhancement logs
   docker logs legal-enhancement
   ```

### **Debug Mode:**

```bash
# Run in debug mode
docker-compose -f docker-compose.full-stack.yml up --build

# Check specific service logs
docker-compose -f docker-compose.full-stack.yml logs -f gpt-researcher
docker-compose -f docker-compose.full-stack.yml logs -f legal-enhancement
docker-compose -f docker-compose.full-stack.yml logs -f owui-bridge
```

## **🔄 Maintenance**

### **Regular Tasks:**

1. **Update services:**
   ```bash
   docker-compose -f docker-compose.full-stack.yml pull
   docker-compose -f docker-compose.full-stack.yml up --build -d
   ```

2. **Clean up logs:**
   ```bash
   # Clean old logs
   find ./logs -name "*.log" -mtime +30 -delete
   ```

3. **Backup data:**
   ```bash
   # Backup data directory
   tar -czf backup-$(date +%Y%m%d).tar.gz ./data
   ```

### **Monitoring:**

```bash
# Check service status
docker-compose -f docker-compose.full-stack.yml ps

# Check resource usage
docker stats

# Check disk usage
du -sh ./data ./logs
```

## **🎯 Usage Examples**

### **1. Process Legal Documents:**

```bash
# Upload documents to ./data/
cp your_legal_docs.pdf ./data/
cp your_emails.pst ./data/
cp your_archives.zip ./data/

# Access OWUI at http://localhost:3000
# Use multi-shot research with your documents
```

### **2. API Usage:**

```bash
# Process a document
curl -X POST http://localhost:8001/process-document \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/app/data/contract.pdf", "use_enhanced_processing": true}'

# Perform multi-shot research
curl -X POST http://localhost:8002/multi-shot-research \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the key legal issues?", "context_documents": ["/app/data/contract.pdf"]}'
```

### **3. Chain-of-Thought Analysis:**

```bash
# Perform chain-of-thought analysis
curl -X POST http://localhost:8002/chain-of-thought-research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze the legal implications of this merger",
    "steps": [
      "Identify the key parties",
      "Analyze the financial terms",
      "Review regulatory compliance",
      "Assess legal risks",
      "Provide recommendations"
    ],
    "context_documents": ["/app/data/merger.pdf"]
  }'
```

## **🎉 Success!**

Your GPT Researcher full stack is now running with:

- ✅ **GPT Researcher Core** - Main research engine
- ✅ **Legal Enhancement** - Advanced document processing
- ✅ **OWUI Bridge** - Multi-shot and chain-of-thought prompting
- ✅ **OWUI Frontend** - Web interface
- ✅ **ChromaDB** - Vector database
- ✅ **Redis** - Caching layer

**Ready to process your 7500-page + 2GB PST legal corpus!** :-)