# 🔌 Port Assignments for Concurrent Stacks

## **📊 Port Ranges by Stack**

| Stack | Port Range | Services | Ports |
|-------|------------|----------|-------|
| **Basic** | 8067 | GPT Researcher | 8067 |
| **Enhanced** | 8068-8069 | GPT Researcher + Legal Enhancement | 8068, 8069 |
| **OWUI Bridge** | 8070-8072 | GPT Researcher + Legal Enhancement + OWUI Bridge | 8070, 8071, 8072 |
| **OWUI Complete** | 8080-8085 | All services + OWUI + ChromaDB + Redis | 8080, 8081, 8082, 8083, 8084, 8085 |
| **Full Stack** | 8000-8039 | All services (uses standard ports) | 8000, 8001, 8002, 3000, 8003, 6379 |

## **🎯 Quick Reference**

### **Basic Stack (docker-compose.basic.yml)**
- **GPT Researcher:** `http://localhost:8067`
- **Health Check:** `http://localhost:8067/health`

### **Enhanced Stack (docker-compose.enhanced.yml)**
- **GPT Researcher:** `http://localhost:8068`
- **Legal Enhancement:** `http://localhost:8069`
- **Health Checks:** 
  - `http://localhost:8068/health`
  - `http://localhost:8069/health`

### **OWUI Bridge Stack (docker-compose.owui-bridge.yml)**
- **GPT Researcher:** `http://localhost:8070`
- **Legal Enhancement:** `http://localhost:8071`
- **OWUI Bridge:** `http://localhost:8072`
- **Health Checks:**
  - `http://localhost:8070/health`
  - `http://localhost:8071/health`
  - `http://localhost:8072/health`

### **OWUI Complete Stack (docker-compose.owui-complete.yml)**
- **GPT Researcher:** `http://localhost:8080`
- **Legal Enhancement:** `http://localhost:8081`
- **OWUI Bridge:** `http://localhost:8082`
- **OWUI Frontend:** `http://localhost:8083`
- **ChromaDB:** `http://localhost:8084`
- **Redis:** `localhost:8085`
- **Health Checks:**
  - `http://localhost:8080/health`
  - `http://localhost:8081/health`
  - `http://localhost:8082/health`
  - `http://localhost:8083`

## **🚀 Running Multiple Stacks**

### **Command Line:**
```bash
# Start Basic stack
docker-compose -f docker-compose.basic.yml up -d

# Start Enhanced stack (different ports)
docker-compose -f docker-compose.enhanced.yml up -d

# Start OWUI Bridge stack (different ports)
docker-compose -f docker-compose.owui-bridge.yml up -d

# Start OWUI Complete stack (different ports)
docker-compose -f docker-compose.owui-complete.yml up -d
```

### **Portainer:**
1. **Create 4 separate stacks** in Portainer
2. **Use the respective compose files**
3. **All stacks can run simultaneously** (different ports)

## **🔍 Testing Concurrent Stacks**

### **Health Check All Stacks:**
```bash
# Basic stack
curl http://localhost:8067/health

# Enhanced stack
curl http://localhost:8068/health
curl http://localhost:8069/health

# OWUI Bridge stack
curl http://localhost:8070/health
curl http://localhost:8071/health
curl http://localhost:8072/health

# OWUI Complete stack
curl http://localhost:8080/health
curl http://localhost:8081/health
curl http://localhost:8082/health
curl http://localhost:8083
```

### **API Testing:**
```bash
# Test Basic stack
curl -X POST http://localhost:8067/research \
  -H "Content-Type: application/json" \
  -d '{"query": "What is AI?", "report_type": "research_report"}'

# Test Enhanced stack
curl -X POST http://localhost:8069/process-document \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/app/data/contract.pdf", "use_enhanced_processing": true}'

# Test OWUI Bridge stack
curl -X POST http://localhost:8072/multi-shot-research \
  -H "Content-Type: application/json" \
  -d '{"query": "What are legal issues?", "context_documents": ["/app/data/contract.pdf"]}'
```

## **💡 Benefits of Different Ports**

### **✅ Advantages:**
- **No port conflicts** - Each stack uses different ports
- **Run simultaneously** - All stacks can run at the same time
- **Easy testing** - Compare different configurations
- **A/B testing** - Test different approaches
- **Development** - Work on multiple versions

### **⚠️ Considerations:**
- **Resource usage** - Each stack uses significant resources
- **Memory requirements** - 2-8GB per stack
- **CPU requirements** - 1-4 cores per stack
- **Storage requirements** - 5-20GB per stack

## **🎯 Recommended Usage**

### **For Development:**
1. **Start with Basic** - Test core functionality
2. **Add Enhanced** - Test legal document processing
3. **Add OWUI Bridge** - Test API integration
4. **Add OWUI Complete** - Test full web interface

### **For Production:**
1. **Choose one stack** - Deploy only what you need
2. **Use standard ports** - Use the full-stack version
3. **Monitor resources** - Keep an eye on usage
4. **Scale as needed** - Add more instances if needed

## **✅ Ready to Run Concurrently!**

Now you can run multiple stacks simultaneously:

- ✅ **Basic Stack** - Port 8067 (original GPT Researcher port)
- ✅ **Enhanced Stack** - Ports 8068-8069
- ✅ **OWUI Bridge Stack** - Ports 8070-8072
- ✅ **OWUI Complete Stack** - Ports 8080-8085

**All stacks can run at the same time with no port conflicts!** :-)