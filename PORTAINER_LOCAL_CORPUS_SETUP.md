# Portainer Setup for Local Corpus Access

This guide explains how to configure GPT Researcher with local corpus access using Portainer.

## Overview

The Portainer setup includes:
- **Multi-corpus volume mounting** via Portainer volumes
- **Apache Tika integration** for OCR processing
- **Traefik reverse proxy** configuration
- **NextJS frontend** for easy document management

## Prerequisites

1. **Portainer** running and accessible
2. **Apache Tika** server running on port 9998
3. **Ollama** running (for LLM models)
4. **Traefik** configured (optional, for reverse proxy)

## Quick Setup

### 1. Prepare Your Corpus Directories

Ensure your corpus directories exist on the host system:

```bash
# Example structure
/path/to/your/corpus1/
├── document1.pdf
├── document2.docx
└── subfolder/
    └── document3.pdf

/path/to/your/corpus2/
├── scanned_doc.pdf
└── handwritten.pdf

/path/to/your/corpus3/
└── large_document.pdf
```

### 2. Update Volume Paths

Edit `portainer-stack-local-corpus.yml` and update the volume device paths:

```yaml
volumes:
  gpt-local-docs:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /host/path/to/your/main/docs  # ← Change this
  
  corpus1:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /host/path/to/corpus1  # ← Change this
  
  corpus2:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /host/path/to/corpus2  # ← Change this
  
  corpus3:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /host/path/to/corpus3  # ← Change this
```

### 3. Deploy in Portainer

1. **Open Portainer** web interface
2. **Navigate to Stacks** → **Add Stack**
3. **Name**: `gpt-researcher-local-corpus`
4. **Build method**: Upload
5. **Upload** the `portainer-stack-local-corpus.yml` file
6. **Deploy the stack**

### 4. Verify Deployment

Check that all services are running:
- `gpt-researcher-local` (port 8068)
- `gptr-nextjs-local` (port 3038)

## Configuration Details

### Environment Variables

The stack includes these key environment variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `DOC_PATH` | `/usr/src/app/my-docs` | Main document directory |
| `TIKA_SERVER_URL` | `http://host.docker.internal:9998` | Tika server for OCR |
| `OPENAI_API_KEY` | `ollama` | Uses Ollama models |
| `FAST_LLM` | `ollama:gpt-oss:20b` | Fast model for summaries |
| `SMART_LLM` | `ollama:gpt-oss:20b` | Smart model for research |
| `STRATEGIC_LLM` | `ollama:qwen3-coder:latest` | Strategic model for planning |

### Volume Mounting

The stack creates this directory structure inside the container:

```
/usr/src/app/my-docs/
├── corpus1/          # Your first corpus (read-only)
├── corpus2/          # Your second corpus (read-only)
├── corpus3/          # Your third corpus (read-only)
└── other-docs/       # Main docs directory (read-write)
```

### Network Configuration

- **Network**: `gpt-local-network` (bridge driver)
- **GPT Researcher**: Port 8068 (external) → 8000 (internal)
- **NextJS Frontend**: Port 3038 (external) → 3038 (internal)

## Usage

### Web Interface

1. **Navigate to**: `http://your-server:3038`
2. **Select "My Documents"** from the Report Source dropdown
3. **Enter your query** and run research

### API Usage

```python
from gpt_researcher import GPTResearcher
import asyncio

async def local_research():
    researcher = GPTResearcher(
        query="What information is in the local documents?",
        report_type="research_report",
        report_source="local"  # or "hybrid"
    )
    
    await researcher.conduct_research()
    report = await researcher.write_report()
    return report

# Run research
report = asyncio.run(local_research())
```

### API Endpoints

- **Health Check**: `http://your-server:8068/health`
- **Research API**: `http://your-server:8068/research`
- **WebSocket**: `ws://your-server:8068/ws`

## Traefik Configuration (Optional)

If using Traefik reverse proxy, the stack includes labels for:

- **GPT Researcher**: `gpt-local.yourdomain.com`
- **NextJS Frontend**: `gpt-ui-local.yourdomain.com`

Update the domain names in the stack file:

```yaml
labels:
  - "traefik.http.routers.gpt-researcher-local.rule=Host(`gpt-local.yourdomain.com`)"
  - "traefik.http.routers.gptr-nextjs-local.rule=Host(`gpt-ui-local.yourdomain.com`)"
```

## Troubleshooting

### Common Issues

**Issue**: "Volume mount failed"
- **Solution**: Check that corpus paths exist on host system
- **Check**: Verify file permissions (containers run as root)

**Issue**: "Tika connection failed"
- **Solution**: Ensure Tika server is running on port 9998
- **Check**: Test with `curl http://localhost:9998/tika`

**Issue**: "No documents found"
- **Solution**: Check volume mounting in Portainer
- **Check**: Verify `DOC_PATH` environment variable

**Issue**: "Ollama connection failed"
- **Solution**: Ensure Ollama is running and accessible
- **Check**: Test with `curl http://localhost:11434/api/tags`

### Debug Steps

1. **Check container logs** in Portainer
2. **Verify volume mounts** in container details
3. **Test Tika connection** from inside container
4. **Check file permissions** on host directories

### Log Locations

- **Application logs**: `/usr/src/app/logs/`
- **Container logs**: Available in Portainer interface
- **Output files**: `/usr/src/app/outputs/`

## Security Considerations

### Volume Security

- **Corpus volumes**: Mounted as read-only for security
- **Main docs volume**: Read-write for outputs and temporary files
- **User permissions**: Container runs as root for file access

### Network Security

- **Internal network**: Services communicate via internal network
- **External access**: Only necessary ports exposed
- **TLS**: Configured via Traefik labels

## Monitoring

### Health Checks

The stack includes health checks for:
- **GPT Researcher**: HTTP health endpoint
- **NextJS Frontend**: Container health check

### Resource Monitoring

Monitor these resources in Portainer:
- **CPU usage** during OCR processing
- **Memory usage** with large documents
- **Disk space** for outputs and logs

## Scaling

### Horizontal Scaling

For high-volume processing:
1. **Increase replicas** of GPT Researcher service
2. **Use load balancer** for multiple instances
3. **Consider external Tika cluster**

### Vertical Scaling

For large documents:
1. **Increase memory limits** in Portainer
2. **Adjust timeout settings** for Tika processing
3. **Monitor resource usage**

## Backup Strategy

### Volume Backups

```bash
# Backup corpus data
docker run --rm -v corpus1:/data -v /backup:/backup alpine tar czf /backup/corpus1.tar.gz -C /data .

# Restore corpus data
docker run --rm -v corpus1:/data -v /backup:/backup alpine tar xzf /backup/corpus1.tar.gz -C /data
```

### Configuration Backups

- **Stack configuration**: Export from Portainer
- **Environment variables**: Document in version control
- **Volume configurations**: Include in backup scripts

## Advanced Configuration

### Custom Tika Settings

To use a different Tika server:

```yaml
environment:
  TIKA_SERVER_URL: "http://your-tika-server:9998"
```

### Custom Model Configuration

To use different Ollama models:

```yaml
environment:
  FAST_LLM: "ollama:your-fast-model"
  SMART_LLM: "ollama:your-smart-model"
  STRATEGIC_LLM: "ollama:your-strategic-model"
```

### Custom Volume Drivers

For network storage:

```yaml
volumes:
  corpus1:
    driver: nfs
    driver_opts:
      type: nfs
      o: addr=your-nfs-server,rw
      device: ":/path/to/corpus1"
```

## Support

For issues with the Portainer setup:

1. **Check container logs** in Portainer interface
2. **Verify volume mounts** are working correctly
3. **Test external dependencies** (Tika, Ollama)
4. **Review this documentation** for common solutions

---

**Note**: This Portainer setup provides a production-ready deployment of GPT Researcher with local corpus access and OCR support. The configuration is optimized for security and performance in a containerized environment. :-)

