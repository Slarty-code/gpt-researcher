# 🚀 Portainer Deployment Guide for Legal Enhancement

## **Overview**
This guide shows you how to deploy the Legal Document Enhancement alongside your existing GPT Researcher in Portainer.

## **Prerequisites**
- ✅ Portainer running
- ✅ GPT Researcher already deployed
- ✅ Docker and Docker Compose available
- ✅ OpenAI API key

## **Step 1: Prepare the Files**

### **1.1 Upload Files to Portainer**
Upload these files to your Portainer host:
```
/mnt/data/gpt-researcher/
├── docker-compose.legal-enhancement.yml
├── Dockerfile.legal-enhancement
├── start_legal_enhancement.sh
├── legal_api_server.py
├── legal-enhancement.env
├── legal_document_enhancement/
│   ├── __init__.py
│   ├── document_processor.py
│   ├── chunker.py
│   ├── integration.py
│   └── requirements.txt
└── gpt_researcher_legal_integration.py
```

### **1.2 Set Environment Variables**
Create a `.env` file with your settings:
```bash
# Copy the template
cp legal-enhancement.env .env

# Edit with your values
nano .env
```

**Required variables:**
```env
OPENAI_API_KEY=your_actual_openai_api_key_here
GPT_RESEARCHER_URL=http://gpt-researcher:8000
LEGAL_ENHANCEMENT_URL=http://legal-enhancement:8001
```

## **Step 2: Deploy in Portainer**

### **2.1 Create New Stack**
1. **Go to Portainer** → **Stacks** → **Add Stack**
2. **Name**: `legal-enhancement`
3. **Build method**: `Upload`
4. **Upload**: `docker-compose.legal-enhancement.yml`

### **2.2 Configure Environment**
1. **Environment variables**: Upload your `.env` file
2. **Access control**: Set appropriate permissions
3. **Resource limits**: 
   - **CPU**: 2 cores
   - **Memory**: 4GB
   - **Storage**: 10GB

### **2.3 Deploy Stack**
1. **Click "Deploy the stack"**
2. **Monitor logs** for any errors
3. **Check health** of both containers

## **Step 3: Verify Deployment**

### **3.1 Check Container Status**
```bash
# In Portainer terminal or SSH
docker ps | grep -E "(gpt-researcher|legal-enhancement)"
```

**Expected output:**
```
gpt-researcher-main     gpt-researcher:latest    Up   0.0.0.0:8000->8000/tcp
legal-enhancement-api   legal-enhancement:latest Up   0.0.0.0:8001->8001/tcp
```

### **3.2 Test API Endpoints**
```bash
# Test Legal Enhancement API
curl http://localhost:8001/health

# Test GPT Researcher API
curl http://localhost:8000/

# Test integration
curl -X POST http://localhost:8001/process-document \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/app/my-docs/test.pdf", "use_enhanced_processing": true}'
```

### **3.3 Check Logs**
```bash
# Legal Enhancement logs
docker logs legal-enhancement-api

# GPT Researcher logs
docker logs gpt-researcher-main
```

## **Step 4: Configure Reverse Proxy (Optional)**

### **4.1 Traefik Configuration**
If using Traefik, add these labels to your services:
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.legal-enhancement.rule=Host(`legal-api.yourdomain.com`)"
  - "traefik.http.routers.legal-enhancement.tls=true"
```

### **4.2 Nginx Configuration**
```nginx
# Legal Enhancement API
location /legal-api/ {
    proxy_pass http://legal-enhancement:8001/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

# GPT Researcher
location /gpt-researcher/ {
    proxy_pass http://gpt-researcher:8000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## **Step 5: Test with Real Documents**

### **5.1 Upload Test Documents**
```bash
# Copy test documents to the shared volume
cp /path/to/your/legal/docs/* /mnt/data/gpt-researcher/my-docs/
```

### **5.2 Test Processing**
```python
# Test script
import requests

# Process a legal document
response = requests.post('http://localhost:8001/process-document', json={
    'file_path': '/app/my-docs/contract.pdf',
    'use_enhanced_processing': True,
    'use_semantic_chunking': True
})

print(response.json())
```

## **Step 6: Monitor and Maintain**

### **6.1 Health Monitoring**
- **Portainer**: Check container health in dashboard
- **API Health**: `curl http://localhost:8001/health`
- **Logs**: Monitor for errors and warnings

### **6.2 Performance Tuning**
```yaml
# Adjust resource limits based on usage
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
    reservations:
      cpus: '1.0'
      memory: 2G
```

### **6.3 Backup Strategy**
```bash
# Backup legal enhancement data
docker run --rm -v gpt-data:/data -v /backup:/backup alpine \
  tar czf /backup/legal-enhancement-$(date +%Y%m%d).tar.gz -C /data .
```

## **Troubleshooting**

### **Common Issues:**

1. **Container won't start**
   - Check logs: `docker logs legal-enhancement-api`
   - Verify environment variables
   - Check resource limits

2. **API not responding**
   - Check port mapping: `docker port legal-enhancement-api`
   - Verify network connectivity
   - Check firewall rules

3. **Dependencies missing**
   - Check build logs for missing packages
   - Verify Dockerfile includes all dependencies
   - Rebuild container if needed

4. **Memory issues**
   - Increase memory limits
   - Check for memory leaks in logs
   - Consider using GPU if available

### **Useful Commands:**
```bash
# Rebuild legal enhancement container
docker-compose -f docker-compose.legal-enhancement.yml build legal-enhancement

# Restart services
docker-compose -f docker-compose.legal-enhancement.yml restart

# View logs
docker-compose -f docker-compose.legal-enhancement.yml logs -f legal-enhancement

# Scale services
docker-compose -f docker-compose.legal-enhancement.yml up -d --scale legal-enhancement=2
```

## **Success Indicators**

✅ **Legal Enhancement API responding** on port 8001  
✅ **GPT Researcher still working** on port 8000  
✅ **Documents processing** with enhanced capabilities  
✅ **Semantic chunking** working for legal documents  
✅ **No conflicts** between containers  
✅ **Logs clean** with no errors  

## **Next Steps**

1. **Test with your 7500-page legal corpus**
2. **Configure custom models** if needed
3. **Set up monitoring** and alerts
4. **Create backup procedures**
5. **Document your specific use cases**

---

**🎉 Congratulations!** You now have a powerful legal document enhancement system running alongside GPT Researcher! :-)