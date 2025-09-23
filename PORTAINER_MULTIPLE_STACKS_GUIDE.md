# 🐳 Portainer Multiple Stacks Guide

## **🎯 Overview**

This guide shows you how to create multiple GPT Researcher stacks in Portainer from the same repository, allowing you to switch between different configurations easily.

## **📁 Available Stack Files**

| Stack File | Description | Services | Ports | Use Case |
|------------|-------------|----------|-------|----------|
| `docker-compose.basic.yml` | Basic GPT Researcher | GPT Researcher | 8000 | Simple research |
| `docker-compose.enhanced.yml` | GPT Researcher + Legal Enhancement | GPT Researcher + Legal Enhancement | 8000, 8001 | Legal document processing |
| `docker-compose.owui-bridge.yml` | GPT Researcher + Legal Enhancement + OWUI Bridge | GPT Researcher + Legal Enhancement + OWUI Bridge | 8000, 8001, 8002 | API-only multi-shot/chain-of-thought |
| `docker-compose.owui-complete.yml` | Full Stack with OWUI Frontend | All services + OWUI + ChromaDB + Redis | 8000, 8001, 8002, 3000, 8003, 6379 | Complete web interface |
| `docker-compose.full-stack.yml` | Complete Full Stack | All services | 8000, 8001, 8002, 3000, 8003, 6379 | Full production setup |

## **🚀 Creating Multiple Stacks in Portainer**

### **Step 1: Create Stack 1 - Basic GPT Researcher**

1. **Go to Portainer → Stacks → Add Stack**
2. **Name:** `gpt-researcher-basic`
3. **Build method:** `Repository`
4. **Repository URL:** `https://github.com/assafelovic/gpt-researcher.git`
5. **Reference:** `refs/heads/master`
6. **Compose path:** `docker-compose.basic.yml`
7. **Environment variables:**
   ```yaml
   OPENAI_API_KEY=your_openai_api_key_here
   RESEARCH_TYPE=research_report
   MAX_ITERATIONS=3
   ```
8. **Click Deploy**

### **Step 2: Create Stack 2 - Enhanced GPT Researcher**

1. **Go to Portainer → Stacks → Add Stack**
2. **Name:** `gpt-researcher-enhanced`
3. **Build method:** `Repository`
4. **Repository URL:** `https://github.com/assafelovic/gpt-researcher.git`
5. **Reference:** `refs/heads/master`
6. **Compose path:** `docker-compose.enhanced.yml`
7. **Environment variables:**
   ```yaml
   OPENAI_API_KEY=your_openai_api_key_here
   RESEARCH_TYPE=research_report
   MAX_ITERATIONS=3
   USE_ENHANCED_PROCESSING=true
   USE_SEMANTIC_CHUNKING=true
   EMBED_MODEL_NAME=BAAI/bge-large-en-v1.5
   SIMILARITY_THRESHOLD=0.75
   ```
8. **Click Deploy**

### **Step 3: Create Stack 3 - OWUI Bridge**

1. **Go to Portainer → Stacks → Add Stack**
2. **Name:** `gpt-researcher-owui-bridge`
3. **Build method:** `Repository`
4. **Repository URL:** `https://github.com/assafelovic/gpt-researcher.git`
5. **Reference:** `refs/heads/master`
6. **Compose path:** `docker-compose.owui-bridge.yml`
7. **Environment variables:**
   ```yaml
   OPENAI_API_KEY=your_openai_api_key_here
   RESEARCH_TYPE=research_report
   MAX_ITERATIONS=3
   USE_ENHANCED_PROCESSING=true
   USE_SEMANTIC_CHUNKING=true
   EMBED_MODEL_NAME=BAAI/bge-large-en-v1.5
   SIMILARITY_THRESHOLD=0.75
   ```
8. **Click Deploy**

### **Step 4: Create Stack 4 - OWUI Complete**

1. **Go to Portainer → Stacks → Add Stack**
2. **Name:** `gpt-researcher-owui-complete`
3. **Build method:** `Repository`
4. **Repository URL:** `https://github.com/assafelovic/gpt-researcher.git`
5. **Reference:** `refs/heads/master`
6. **Compose path:** `docker-compose.owui-complete.yml`
7. **Environment variables:**
   ```yaml
   OPENAI_API_KEY=your_openai_api_key_here
   RESEARCH_TYPE=research_report
   MAX_ITERATIONS=3
   USE_ENHANCED_PROCESSING=true
   USE_SEMANTIC_CHUNKING=true
   EMBED_MODEL_NAME=BAAI/bge-large-en-v1.5
   SIMILARITY_THRESHOLD=0.75
   WEBUI_SECRET_KEY=your-secret-key-here
   ```
8. **Click Deploy**

## **🔄 Switching Between Stacks**

### **Method 1: Stop One, Start Another**

1. **Stop current stack:**
   - Go to Portainer → Stacks
   - Find your current stack
   - Click **Stop**

2. **Start new stack:**
   - Go to Portainer → Stacks
   - Find the stack you want to start
   - Click **Start**

### **Method 2: Use Different Ports (Run Simultaneously)**

If you want to run multiple stacks at the same time, modify the ports:

```yaml
# Stack 1: Basic (ports 8000-8009)
services:
  gpt-researcher:
    ports:
      - "8000:8000"

# Stack 2: Enhanced (ports 8010-8019)
services:
  gpt-researcher:
    ports:
      - "8010:8000"
  legal-enhancement:
    ports:
      - "8011:8001"

# Stack 3: OWUI Bridge (ports 8020-8029)
services:
  gpt-researcher:
    ports:
      - "8020:8000"
  legal-enhancement:
    ports:
      - "8021:8001"
  owui-bridge:
    ports:
      - "8022:8002"
```

## **📊 Stack Comparison**

### **Basic Stack (docker-compose.basic.yml)**
- **Services:** GPT Researcher only
- **Ports:** 8000
- **Use Case:** Simple research tasks
- **Resources:** Low (2GB RAM, 1 CPU)
- **Features:** Basic web research, report generation

### **Enhanced Stack (docker-compose.enhanced.yml)**
- **Services:** GPT Researcher + Legal Enhancement
- **Ports:** 8000, 8001
- **Use Case:** Legal document processing
- **Resources:** Medium (4GB RAM, 2 CPU)
- **Features:** Email processing, archive support, semantic chunking

### **OWUI Bridge Stack (docker-compose.owui-bridge.yml)**
- **Services:** GPT Researcher + Legal Enhancement + OWUI Bridge
- **Ports:** 8000, 8001, 8002
- **Use Case:** API-only multi-shot/chain-of-thought
- **Resources:** Medium (4GB RAM, 2 CPU)
- **Features:** Multi-shot research, chain-of-thought prompting

### **OWUI Complete Stack (docker-compose.owui-complete.yml)**
- **Services:** All services + OWUI Frontend + ChromaDB + Redis
- **Ports:** 8000, 8001, 8002, 3000, 8003, 6379
- **Use Case:** Complete web interface
- **Resources:** High (8GB RAM, 4 CPU)
- **Features:** Full web interface, vector database, caching

## **🔧 Portainer Stack Management**

### **Creating a New Stack:**

1. **Go to Portainer → Stacks**
2. **Click "Add Stack"**
3. **Choose "Repository"**
4. **Enter repository details:**
   - **Repository URL:** `https://github.com/assafelovic/gpt-researcher.git`
   - **Reference:** `refs/heads/master`
   - **Compose path:** `docker-compose.[stack-name].yml`
5. **Set environment variables**
6. **Click "Deploy"**

### **Managing Existing Stacks:**

| Action | Description |
|--------|-------------|
| **Start** | Start a stopped stack |
| **Stop** | Stop a running stack |
| **Restart** | Restart a running stack |
| **Update** | Update stack from repository |
| **Delete** | Delete stack and all containers |
| **Duplicate** | Create a copy of the stack |

### **Environment Variables:**

```yaml
# Required for all stacks
OPENAI_API_KEY=your_openai_api_key_here

# Optional for all stacks
RESEARCH_TYPE=research_report
MAX_ITERATIONS=3

# Required for enhanced stacks
USE_ENHANCED_PROCESSING=true
USE_SEMANTIC_CHUNKING=true
EMBED_MODEL_NAME=BAAI/bge-large-en-v1.5
SIMILARITY_THRESHOLD=0.75

# Required for OWUI stacks
WEBUI_SECRET_KEY=your-secret-key-here
```

## **💡 Best Practices**

### **1. Stack Naming:**
- Use descriptive names: `gpt-researcher-basic`, `gpt-researcher-enhanced`
- Include version numbers: `gpt-researcher-v1.0`, `gpt-researcher-v2.0`
- Use environment prefixes: `dev-gpt-researcher`, `prod-gpt-researcher`

### **2. Resource Management:**
- Monitor resource usage in Portainer
- Stop unused stacks to free resources
- Use appropriate stack for your needs

### **3. Data Persistence:**
- All stacks use the same `./data` volume
- Data persists when switching stacks
- Backup data regularly

### **4. Port Management:**
- Each stack uses the same ports (8000, 8001, etc.)
- Only one stack can run at a time with default ports
- Use different ports for simultaneous stacks

## **🎯 Recommended Workflow**

### **For Development:**
1. Start with **Basic Stack** for simple testing
2. Upgrade to **Enhanced Stack** for legal document processing
3. Use **OWUI Bridge Stack** for API testing
4. Deploy **OWUI Complete Stack** for full testing

### **For Production:**
1. Use **OWUI Complete Stack** for full production
2. Keep **Enhanced Stack** as backup
3. Monitor resource usage
4. Regular backups of data

## **✅ Success!**

You now have multiple GPT Researcher stacks ready to deploy in Portainer:

- ✅ **Basic Stack** - Simple research
- ✅ **Enhanced Stack** - Legal document processing
- ✅ **OWUI Bridge Stack** - API-only multi-shot/chain-of-thought
- ✅ **OWUI Complete Stack** - Full web interface
- ✅ **Easy switching** between stacks
- ✅ **Same repository** for all stacks
- ✅ **Portainer ready** for deployment

**Ready to deploy your preferred stack configuration!** :-)