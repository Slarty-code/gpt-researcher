# 📋 Stack Options Quick Reference

## **🚀 Available Stacks**

| Stack | File | Services | Ports | RAM | CPU | Use Case |
|-------|------|----------|-------|-----|-----|----------|
| **Basic** | `docker-compose.basic.yml` | GPT Researcher | 8000 | 2GB | 1 | Simple research |
| **Enhanced** | `docker-compose.enhanced.yml` | GPT Researcher + Legal Enhancement | 8000, 8001 | 4GB | 2 | Legal document processing |
| **OWUI Bridge** | `docker-compose.owui-bridge.yml` | GPT Researcher + Legal Enhancement + OWUI Bridge | 8000, 8001, 8002 | 4GB | 2 | API-only multi-shot/chain-of-thought |
| **OWUI Complete** | `docker-compose.owui-complete.yml` | All services + OWUI + ChromaDB + Redis | 8000, 8001, 8002, 3000, 8003, 6379 | 8GB | 4 | Complete web interface |
| **Full Stack** | `docker-compose.full-stack.yml` | All services | 8000, 8001, 8002, 3000, 8003, 6379 | 8GB | 4 | Full production setup |

## **🔧 Portainer Deployment**

### **Repository Details:**
- **Repository URL:** `https://github.com/assafelovic/gpt-researcher.git`
- **Reference:** `refs/heads/master`
- **Compose path:** `docker-compose.[stack-name].yml`

### **Environment Variables:**
```yaml
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
RESEARCH_TYPE=research_report
MAX_ITERATIONS=3
USE_ENHANCED_PROCESSING=true
USE_SEMANTIC_CHUNKING=true
EMBED_MODEL_NAME=BAAI/bge-large-en-v1.5
SIMILARITY_THRESHOLD=0.75
WEBUI_SECRET_KEY=your-secret-key-here
```

## **📊 Feature Comparison**

| Feature | Basic | Enhanced | OWUI Bridge | OWUI Complete | Full Stack |
|---------|-------|----------|-------------|---------------|------------|
| **Web Research** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Report Generation** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Email Processing** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Archive Processing** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Semantic Chunking** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Multi-shot Research** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Chain-of-thought** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **OWUI Frontend** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Vector Database** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Caching** | ❌ | ❌ | ❌ | ✅ | ✅ |

## **🎯 Quick Start Commands**

### **Local Development:**
```bash
# Basic stack
docker-compose -f docker-compose.basic.yml up -d

# Enhanced stack
docker-compose -f docker-compose.enhanced.yml up -d

# OWUI Bridge stack
docker-compose -f docker-compose.owui-bridge.yml up -d

# OWUI Complete stack
docker-compose -f docker-compose.owui-complete.yml up -d

# Full stack
docker-compose -f docker-compose.full-stack.yml up -d
```

### **Portainer Deployment:**
1. Go to **Portainer → Stacks → Add Stack**
2. Choose **Repository**
3. Set **Repository URL:** `https://github.com/assafelovic/gpt-researcher.git`
4. Set **Reference:** `refs/heads/master`
5. Set **Compose path:** `docker-compose.[stack-name].yml`
6. Set **Environment variables**
7. Click **Deploy**

## **🔄 Stack Switching**

### **Stop Current Stack:**
```bash
# In Portainer: Stacks → [Your Stack] → Stop
# Or via CLI:
docker-compose -f docker-compose.current.yml down
```

### **Start New Stack:**
```bash
# In Portainer: Stacks → [Your Stack] → Start
# Or via CLI:
docker-compose -f docker-compose.new.yml up -d
```

## **💡 Recommendations**

### **For Your Legal Corpus (7500 pages + 2GB PST):**

**Recommended Stack:** **OWUI Complete** or **Full Stack**

**Why:**
- ✅ **Email processing** for PST files
- ✅ **Archive processing** for compressed files
- ✅ **Semantic chunking** for better retrieval
- ✅ **Multi-shot research** for context learning
- ✅ **Chain-of-thought** for complex analysis
- ✅ **Web interface** for easy interaction

### **For Simple Research:**
**Recommended Stack:** **Basic**

### **For Legal Document Processing:**
**Recommended Stack:** **Enhanced**

### **For API Integration:**
**Recommended Stack:** **OWUI Bridge**

## **✅ Ready to Deploy!**

Choose your stack and deploy in Portainer:

1. **Basic** - Simple research tasks
2. **Enhanced** - Legal document processing
3. **OWUI Bridge** - API-only multi-shot/chain-of-thought
4. **OWUI Complete** - Full web interface
5. **Full Stack** - Complete production setup

**All stacks use the same repository and can be easily switched!** :-)