# 🔄 Concurrent Stacks Guide

## **🎯 Overview**

This guide shows you how to run multiple GPT Researcher stacks concurrently in Portainer, allowing you to test different configurations simultaneously.

## **📊 Concurrent Stack Options**

### **Option 1: Different Ports (Recommended)**

| Stack | Services | Ports | Use Case |
|-------|----------|-------|----------|
| **Basic** | GPT Researcher | 8000 | Simple research |
| **Enhanced** | GPT Researcher + Legal Enhancement | 8010, 8011 | Legal document processing |
| **OWUI Bridge** | GPT Researcher + Legal Enhancement + OWUI Bridge | 8020, 8021, 8022 | API-only multi-shot/chain-of-thought |
| **OWUI Complete** | All services + OWUI + ChromaDB + Redis | 8030-8035 | Complete web interface |

### **Option 2: Same Ports (Sequential)**

| Stack | Services | Ports | Use Case |
|-------|----------|-------|----------|
| **Basic** | GPT Researcher | 8000 | Simple research |
| **Enhanced** | GPT Researcher + Legal Enhancement | 8000, 8001 | Legal document processing |
| **OWUI Bridge** | GPT Researcher + Legal Enhancement + OWUI Bridge | 8000, 8001, 8002 | API-only multi-shot/chain-of-thought |
| **OWUI Complete** | All services + OWUI + ChromaDB + Redis | 8000, 8001, 8002, 3000, 8003, 6379 | Complete web interface |

## **🚀 Concurrent Deployment Methods**

### **Method 1: Single Concurrent Stack (Recommended)**

**File:** `docker-compose.concurrent.yml`

```bash
# Deploy all stacks concurrently
docker-compose -f docker-compose.concurrent.yml up -d

# Check all services
docker-compose -f docker-compose.concurrent.yml ps
```

**Portainer Setup:**
1. **Go to Portainer → Stacks → Add Stack**
2. **Name:** `gpt-researcher-concurrent`
3. **Repository:** `https://github.com/assafelovic/gpt-researcher.git`
4. **Compose path:** `docker-compose.concurrent.yml`
5. **Deploy**

### **Method 2: Multiple Separate Stacks**

**Create 4 separate stacks in Portainer:**

#### **Stack 1: Basic (Ports 8000-8009)**
- **Name:** `gpt-researcher-basic`
- **Compose path:** `docker-compose.basic.yml`
- **Ports:** 8000

#### **Stack 2: Enhanced (Ports 8010-8019)**
- **Name:** `gpt-researcher-enhanced`
- **Compose path:** `docker-compose.enhanced.yml`
- **Modify ports:** 8010, 8011

#### **Stack 3: OWUI Bridge (Ports 8020-8029)**
- **Name:** `gpt-researcher-owui-bridge`
- **Compose path:** `docker-compose.owui-bridge.yml`
- **Modify ports:** 8020, 8021, 8022

#### **Stack 4: OWUI Complete (Ports 8030-8039)**
- **Name:** `gpt-researcher-owui-complete`
- **Compose path:** `docker-compose.owui-complete.yml`
- **Modify ports:** 8030-8035

## **🔧 Port Mapping Strategy**

### **Port Ranges:**

| Stack | Port Range | Services |
|-------|------------|----------|
| **Basic** | 8000-8009 | GPT Researcher (8000) |
| **Enhanced** | 8010-8019 | GPT Researcher (8010), Legal Enhancement (8011) |
| **OWUI Bridge** | 8020-8029 | GPT Researcher (8020), Legal Enhancement (8021), OWUI Bridge (8022) |
| **OWUI Complete** | 8030-8039 | GPT Researcher (8030), Legal Enhancement (8031), OWUI Bridge (8032), OWUI (8033), ChromaDB (8034), Redis (8035) |

### **Portainer Configuration:**

```yaml
# Example: Enhanced Stack with different ports
services:
  gpt-researcher:
    ports:
      - "8010:8000"  # External:Internal
  legal-enhancement:
    ports:
      - "8011:8001"  # External:Internal
```

## **📈 Resource Management**

### **Resource Requirements (Concurrent):**

| Configuration | RAM | CPU | Storage | Notes |
|---------------|-----|-----|---------|-------|
| **Basic Only** | 2GB | 1 core | 5GB | Minimal resources |
| **Enhanced Only** | 4GB | 2 cores | 10GB | Medium resources |
| **OWUI Bridge Only** | 4GB | 2 cores | 10GB | Medium resources |
| **OWUI Complete Only** | 8GB | 4 cores | 20GB | High resources |
| **All Concurrent** | 16GB | 8 cores | 40GB | **Very high resources** |

### **Resource Optimization:**

```yaml
# Limit resources per service
services:
  gpt-researcher-basic:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

## **🔄 Stack Management**

### **Starting Stacks:**

```bash
# Start all concurrent stacks
docker-compose -f docker-compose.concurrent.yml up -d

# Start specific stacks
docker-compose -f docker-compose.basic.yml up -d
docker-compose -f docker-compose.enhanced.yml up -d
```

### **Stopping Stacks:**

```bash
# Stop all concurrent stacks
docker-compose -f docker-compose.concurrent.yml down

# Stop specific stacks
docker-compose -f docker-compose.basic.yml down
docker-compose -f docker-compose.enhanced.yml down
```

### **Portainer Management:**

| Action | Description |
|--------|-------------|
| **Start** | Start a stopped stack |
| **Stop** | Stop a running stack |
| **Restart** | Restart a running stack |
| **Update** | Update stack from repository |
| **Delete** | Delete stack and containers |

## **🔍 Monitoring Concurrent Stacks**

### **Health Checks:**

```bash
# Check all services
curl http://localhost:8000/health  # Basic
curl http://localhost:8010/health  # Enhanced GPT Researcher
curl http://localhost:8011/health  # Enhanced Legal Enhancement
curl http://localhost:8020/health  # OWUI Bridge GPT Researcher
curl http://localhost:8021/health  # OWUI Bridge Legal Enhancement
curl http://localhost:8022/health  # OWUI Bridge
curl http://localhost:8030/health  # Complete GPT Researcher
curl http://localhost:8031/health  # Complete Legal Enhancement
curl http://localhost:8032/health  # Complete OWUI Bridge
curl http://localhost:8033         # Complete OWUI Frontend
```

### **Resource Monitoring:**

```bash
# Check resource usage
docker stats

# Check specific containers
docker stats gpt-researcher-basic gpt-researcher-enhanced

# Check logs
docker-compose -f docker-compose.concurrent.yml logs -f
```

## **💡 Best Practices**

### **1. Resource Planning:**

- **Start small** - Deploy one stack at a time
- **Monitor resources** - Watch CPU, memory, disk usage
- **Scale gradually** - Add more stacks as needed

### **2. Port Management:**

- **Use port ranges** - 8000-8009, 8010-8019, etc.
- **Document ports** - Keep track of which ports are used
- **Avoid conflicts** - Don't use overlapping ports

### **3. Data Management:**

- **Shared volumes** - All stacks use same `./data` directory
- **Backup data** - Regular backups of shared data
- **Cleanup logs** - Regular cleanup of log files

### **4. Testing Strategy:**

- **A/B testing** - Compare different stacks
- **Load testing** - Test under different loads
- **Performance monitoring** - Monitor response times

## **⚠️ Considerations**

### **Resource Requirements:**

- **High memory usage** - Each stack uses 2-8GB RAM
- **High CPU usage** - Each stack uses 1-4 CPU cores
- **High disk usage** - Each stack uses 5-20GB storage

### **Network Considerations:**

- **Port conflicts** - Ensure no overlapping ports
- **Network isolation** - Each stack uses separate network
- **API communication** - Stacks communicate via HTTP

### **Data Consistency:**

- **Shared data** - All stacks share same `./data` directory
- **Concurrent access** - Multiple stacks can access same files
- **Backup strategy** - Regular backups of shared data

## **🎯 Recommended Approach**

### **For Development:**

1. **Start with Basic** - Deploy basic stack first
2. **Add Enhanced** - Deploy enhanced stack with different ports
3. **Test both** - Compare performance and features
4. **Add more** - Deploy additional stacks as needed

### **For Production:**

1. **Choose one stack** - Deploy only the stack you need
2. **Optimize resources** - Tune for your specific use case
3. **Monitor performance** - Keep an eye on resource usage
4. **Scale as needed** - Add more instances if needed

## **✅ Success!**

You can now run multiple GPT Researcher stacks concurrently:

- ✅ **Different ports** - No conflicts
- ✅ **Separate networks** - Isolated communication
- ✅ **Shared data** - All stacks access same documents
- ✅ **Easy management** - Start/stop individual stacks
- ✅ **Resource monitoring** - Track usage per stack

**Ready to run multiple stacks concurrently!** :-)