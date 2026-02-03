# 🚀 Portainer Deployment with Ollama

## **📋 Quick Setup Guide**

### **1. Create Stack in Portainer**

1. **Go to Portainer** → **Stacks** → **Add Stack**
2. **Name:** `gpt-researcher-basic-ollama`
3. **Build method:** `Repository`
4. **Repository URL:** `https://github.com/Slarty-code/gpt-researcher.git`
5. **Reference:** `master`
6. **Compose path:** `portainer-stack-basic-ollama.yml`

### **2. Environment Variables (Optional)**

You can add these in the **Environment variables** section:

```bash
LANGCHAIN_API_KEY=your_langchain_key_here
TAVILY_API_KEY=your_tavily_key_here
RESEARCH_TYPE=research_report
MAX_ITERATIONS=3
```

### **3. Deploy the Stack**

1. Click **Deploy the stack**
2. Wait for both containers to start:
   - `ollama-basic` (Ollama service)
   - `gpt-researcher-basic` (GPT Researcher)

### **4. Pull Ollama Models**

After deployment, you'll need to pull a model for Ollama:

```bash
# SSH into your server or use Portainer's console
docker exec -it ollama-basic ollama pull llama3.2:3b
# or
docker exec -it ollama-basic ollama pull mistral:7b
# or
docker exec -it ollama-basic ollama pull qwen2.5:7b
```

### **5. Test the Setup**

```bash
# Health check
curl http://localhost:8067/health

# Test research
curl -X POST http://localhost:8067/research \
  -H "Content-Type: application/json" \
  -d '{"query": "What is artificial intelligence?", "report_type": "research_report"}'
```

## **🔧 Configuration Details**

### **Ports:**
- **GPT Researcher:** `8067` (original GPT Researcher port)
- **Ollama:** `11434` (standard Ollama port)

### **Volumes:**
- **Ollama models:** `ollama_data` (persistent storage for models)
- **GPT Researcher data:** `./data` (local data directory)
- **GPT Researcher logs:** `./logs` (local logs directory)

### **Networks:**
- **gpt-researcher-basic:** Internal network for communication

## **📊 Resource Requirements**

### **Minimum:**
- **CPU:** 2 cores
- **RAM:** 4GB
- **Storage:** 10GB

### **Recommended:**
- **CPU:** 4 cores
- **RAM:** 8GB
- **Storage:** 20GB

## **🔄 Model Management**

### **List Available Models:**
```bash
docker exec -it ollama-basic ollama list
```

### **Pull New Models:**
```bash
# Small, fast models (good for testing)
docker exec -it ollama-basic ollama pull llama3.2:3b
docker exec -it ollama-basic ollama pull qwen2.5:3b

# Medium models (good balance)
docker exec -it ollama-basic ollama pull llama3.2:7b
docker exec -it ollama-basic ollama pull mistral:7b
docker exec -it ollama-basic ollama pull qwen2.5:7b

# Large models (best quality, slower)
docker exec -it ollama-basic ollama pull llama3.2:70b
docker exec -it ollama-basic ollama pull qwen2.5:72b
```

### **Remove Models:**
```bash
docker exec -it ollama-basic ollama rm model_name
```

## **🐛 Troubleshooting**

### **Common Issues:**

1. **"No models available"**
   - Pull a model: `docker exec -it ollama-basic ollama pull llama3.2:3b`

2. **"Connection refused"**
   - Check if Ollama is running: `docker ps`
   - Check logs: `docker logs ollama-basic`

3. **"Out of memory"**
   - Use a smaller model (3b instead of 7b)
   - Increase server RAM

4. **"Build failed"**
   - Check if you have enough disk space
   - Check Portainer logs for specific errors

### **Logs:**
```bash
# GPT Researcher logs
docker logs gpt-researcher-basic

# Ollama logs
docker logs ollama-basic
```

## **✅ Success Indicators**

When everything is working:

1. **Both containers are running:**
   ```bash
   docker ps | grep -E "(ollama-basic|gpt-researcher-basic)"
   ```

2. **Health check passes:**
   ```bash
   curl http://localhost:8067/health
   ```

3. **Research request works:**
   ```bash
   curl -X POST http://localhost:8067/research \
     -H "Content-Type: application/json" \
     -d '{"query": "Test query", "report_type": "research_report"}'
   ```

## **🎯 Next Steps**

Once the basic stack is working:

1. **Test with different models** to find your preferred one
2. **Try the enhanced stack** (ports 8068-8069) for legal document processing
3. **Try the OWUI Bridge stack** (ports 8070-8072) for web interface
4. **Try the OWUI Complete stack** (ports 8080-8085) for full features

**Ready to deploy!** 🚀