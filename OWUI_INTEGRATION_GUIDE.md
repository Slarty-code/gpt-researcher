# 🔗 OWUI + GPT Researcher Integration Guide

## **🎯 Overview**

This guide shows you how to integrate GPT Researcher with OWUI (Open WebUI) for multi-shot and chain-of-thought prompting, bypassing the MCP limitations.

## **🏗️ Architecture**

```
OWUI → OWUI Bridge → GPT Researcher → Legal Enhancement
  ↓         ↓              ↓              ↓
Web UI   Multi-shot    Research API    Document Processing
         Chain-of-     Semantic        Email/Archive
         Thought       Chunking        Support
```

## **📋 Prerequisites**

- GPT Researcher running (port 8000)
- Legal Enhancement running (port 8001)
- OWUI running (port 3000)
- Docker and Docker Compose

## **🚀 Quick Start**

### **Step 1: Start the Services**

```bash
# Start GPT Researcher + Legal Enhancement + OWUI Bridge
docker-compose -f docker-compose.owui-bridge.yml up -d

# Check services are running
curl http://localhost:8000/health  # GPT Researcher
curl http://localhost:8001/health  # Legal Enhancement
curl http://localhost:8002/health  # OWUI Bridge
```

### **Step 2: Configure OWUI**

In OWUI, add the bridge as a custom API:

1. **Go to Settings → API Keys**
2. **Add Custom API:**
   - **Name:** GPT Researcher Bridge
   - **Base URL:** `http://localhost:8002`
   - **API Key:** (leave empty if no auth required)

### **Step 3: Test Integration**

```bash
# Test multi-shot research
curl -X POST http://localhost:8002/multi-shot-research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key legal issues in this contract?",
    "context_documents": ["/app/data/contract1.pdf", "/app/data/contract2.pdf"],
    "research_type": "research_report",
    "num_shots": 3
  }'

# Test chain-of-thought research
curl -X POST http://localhost:8002/chain-of-thought-research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze the legal implications of this merger agreement",
    "steps": [
      "Identify the key parties and their roles",
      "Analyze the financial terms and conditions",
      "Review regulatory compliance requirements",
      "Assess potential legal risks and liabilities",
      "Provide recommendations for risk mitigation"
    ],
    "context_documents": ["/app/data/merger_agreement.pdf"]
  }'
```

## **🔧 API Endpoints**

### **Multi-Shot Research**

**Endpoint:** `POST /multi-shot-research`

**Request:**
```json
{
  "query": "What are the key legal issues in this contract?",
  "context_documents": ["/path/to/contract1.pdf", "/path/to/contract2.pdf"],
  "research_type": "research_report",
  "num_shots": 3,
  "use_legal_enhancement": true
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "query": "What are the key legal issues in this contract?",
    "research_type": "research_report",
    "num_shots": 3,
    "context_documents": 2,
    "research_result": {
      "research_type": "research_report",
      "result": "Research completed...",
      "sources": [],
      "citations": []
    },
    "prompt_used": "MULTI-SHOT LEGAL RESEARCH PROMPT..."
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### **Chain-of-Thought Research**

**Endpoint:** `POST /chain-of-thought-research`

**Request:**
```json
{
  "query": "Analyze the legal implications of this merger agreement",
  "steps": [
    "Identify the key parties and their roles",
    "Analyze the financial terms and conditions",
    "Review regulatory compliance requirements",
    "Assess potential legal risks and liabilities",
    "Provide recommendations for risk mitigation"
  ],
  "context_documents": ["/path/to/merger_agreement.pdf"],
  "use_legal_enhancement": true
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "query": "Analyze the legal implications of this merger agreement",
    "steps": ["Identify the key parties...", "Analyze the financial terms..."],
    "research_steps": [
      {
        "step_number": 1,
        "total_steps": 5,
        "step_description": "Identify the key parties and their roles",
        "result": "Step 1 completed...",
        "timestamp": "2024-01-15T10:30:00Z"
      }
    ],
    "final_result": {
      "query": "Analyze the legal implications...",
      "synthesis": "Chain-of-thought analysis completed...",
      "steps_completed": 5,
      "context_used": 1,
      "timestamp": "2024-01-15T10:30:00Z"
    },
    "prompt_used": "CHAIN-OF-THOUGHT LEGAL RESEARCH..."
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## **🎨 OWUI Integration Examples**

### **Example 1: Multi-Shot Legal Research**

```python
# In OWUI, create a custom function
def multi_shot_legal_research(query, context_docs):
    import requests
    
    response = requests.post(
        "http://localhost:8002/multi-shot-research",
        json={
            "query": query,
            "context_documents": context_docs,
            "research_type": "research_report",
            "num_shots": 3,
            "use_legal_enhancement": True
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        if result["success"]:
            return result["result"]["research_result"]["result"]
        else:
            return f"Error: {result['error']}"
    else:
        return f"API Error: {response.status_code}"

# Usage in OWUI
result = multi_shot_legal_research(
    "What are the key legal issues in this contract?",
    ["/app/data/contract1.pdf", "/app/data/contract2.pdf"]
)
```

### **Example 2: Chain-of-Thought Analysis**

```python
# In OWUI, create a custom function
def chain_of_thought_analysis(query, steps, context_docs):
    import requests
    
    response = requests.post(
        "http://localhost:8002/chain-of-thought-research",
        json={
            "query": query,
            "steps": steps,
            "context_documents": context_docs,
            "use_legal_enhancement": True
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        if result["success"]:
            return result["result"]["final_result"]["synthesis"]
        else:
            return f"Error: {result['error']}"
    else:
        return f"API Error: {response.status_code}"

# Usage in OWUI
result = chain_of_thought_analysis(
    "Analyze the legal implications of this merger agreement",
    [
        "Identify the key parties and their roles",
        "Analyze the financial terms and conditions",
        "Review regulatory compliance requirements",
        "Assess potential legal risks and liabilities",
        "Provide recommendations for risk mitigation"
    ],
    ["/app/data/merger_agreement.pdf"]
)
```

## **🔧 Configuration Options**

### **Environment Variables**

```bash
# OWUI Bridge Configuration
GPT_RESEARCHER_URL=http://gpt-researcher:8000
LEGAL_ENHANCEMENT_URL=http://legal-enhancement:8001
BRIDGE_PORT=8002

# GPT Researcher Configuration
OPENAI_API_KEY=your_openai_api_key
RESEARCH_TYPE=research_report

# Legal Enhancement Configuration
USE_ENHANCED_PROCESSING=true
USE_SEMANTIC_CHUNKING=true
```

### **Docker Compose Configuration**

```yaml
# docker-compose.owui-bridge.yml
services:
  owui-gpt-researcher-bridge:
    environment:
      - GPT_RESEARCHER_URL=http://gpt-researcher:8000
      - LEGAL_ENHANCEMENT_URL=http://legal-enhancement:8001
      - BRIDGE_PORT=8002
    volumes:
      - ./data:/app/data  # Mount your documents here
```

## **📊 Supported Features**

### **Multi-Shot Research:**
- ✅ **Context document processing** - Uses legal enhancement
- ✅ **Example extraction** - Extracts examples from context
- ✅ **Pattern recognition** - Learns from provided examples
- ✅ **Structured output** - Follows example patterns
- ✅ **Legal optimization** - Specialized for legal work

### **Chain-of-Thought Research:**
- ✅ **Step-by-step reasoning** - Systematic analysis
- ✅ **Context integration** - Uses provided documents
- ✅ **Logical progression** - Builds upon previous steps
- ✅ **Synthesis** - Combines all steps into final result
- ✅ **Legal accuracy** - Ensures legal compliance

### **Document Processing:**
- ✅ **Email support** - MSG, EML, PST files
- ✅ **Archive support** - ZIP, RAR, TAR files
- ✅ **Enhanced OCR** - PaddleOCR + LayoutLMv3
- ✅ **Table extraction** - Camelot for complex tables
- ✅ **Semantic chunking** - AI-guided chunking

## **🚨 Troubleshooting**

### **Common Issues:**

1. **Services not starting:**
   ```bash
   # Check logs
   docker-compose -f docker-compose.owui-bridge.yml logs
   
   # Restart services
   docker-compose -f docker-compose.owui-bridge.yml restart
   ```

2. **API connection errors:**
   ```bash
   # Check service health
   curl http://localhost:8000/health  # GPT Researcher
   curl http://localhost:8001/health  # Legal Enhancement
   curl http://localhost:8002/health  # OWUI Bridge
   ```

3. **Document processing failures:**
   ```bash
   # Check document paths
   ls -la /app/data/
   
   # Check legal enhancement logs
   docker logs legal-enhancement
   ```

### **Debug Mode:**

```bash
# Run bridge in debug mode
docker run -it --rm \
  -p 8002:8002 \
  -v $(pwd)/owui_gpt_researcher_bridge.py:/app/owui_gpt_researcher_bridge.py \
  -v $(pwd)/data:/app/data \
  python:3.11-slim \
  bash -c "pip install fastapi uvicorn requests && python owui_gpt_researcher_bridge.py"
```

## **🎯 Best Practices**

### **1. Document Organization:**
```
data/
├── contracts/
│   ├── contract1.pdf
│   ├── contract2.pdf
│   └── legal_opinion.docx
├── emails/
│   ├── communications.pst
│   └── important_emails.msg
└── archives/
    ├── case_files.zip
    └── evidence.rar
```

### **2. Prompt Engineering:**
- **Be specific** with research queries
- **Provide relevant context** documents
- **Use clear reasoning steps** for chain-of-thought
- **Include legal terminology** for better results

### **3. Performance Optimization:**
- **Batch process** multiple documents
- **Use appropriate research types** for your needs
- **Monitor resource usage** during processing
- **Cache results** when possible

## **🎉 Success!**

You now have GPT Researcher integrated with OWUI for multi-shot and chain-of-thought prompting! 

**Key Benefits:**
- ✅ **Multi-shot learning** from context documents
- ✅ **Chain-of-thought reasoning** for complex analysis
- ✅ **Legal document processing** with email/archive support
- ✅ **Semantic chunking** for better retrieval
- ✅ **OWUI integration** without MCP limitations

**Ready to process your 7500-page + 2GB PST legal corpus!** :-)