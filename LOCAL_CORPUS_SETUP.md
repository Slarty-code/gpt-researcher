# Local Corpus Access Setup for GPT Researcher

This guide explains how to configure GPT Researcher to access multiple local document corpora with OCR support for scanned documents.

## Overview

GPT Researcher now supports:
- **Multiple corpus paths** via Docker volume mounting
- **OCR processing** for scanned PDFs and handwritten documents via Apache Tika
- **Local-only research** mode
- **Hybrid research** mode (local documents + web search)
- **Large document support** (300+ page PDFs)

## Quick Start

### 1. Prerequisites

- Docker and Docker Compose installed
- Apache Tika server running on port 9998
- Your document corpora accessible on the host system

### 2. Configure Corpus Paths

Edit your `docker-compose.yml` to mount your corpus directories:

```yaml
volumes:
  # Multiple corpus directories mounted as subdirectories
  - ${PWD}/my-docs:/usr/src/app/my-docs:rw
  - ${CORPUS_PATH_1:-/host/corpus1}:/usr/src/app/my-docs/corpus1:ro
  - ${CORPUS_PATH_2:-/host/corpus2}:/usr/src/app/my-docs/corpus2:ro
  - ${CORPUS_PATH_3:-/host/corpus3}:/usr/src/app/my-docs/corpus3:ro
```

### 3. Set Environment Variables

```bash
# Set your corpus paths
export CORPUS_PATH_1="/path/to/your/first/corpus"
export CORPUS_PATH_2="/path/to/your/second/corpus"
export CORPUS_PATH_3="/path/to/your/third/corpus"

# Tika server URL
export TIKA_SERVER_URL="http://host.docker.internal:9998"
```

### 4. Start the Services

```bash
docker-compose up --build
```

## Usage Examples

### Local-Only Research

```python
from gpt_researcher import GPTResearcher
import asyncio

async def local_research():
    researcher = GPTResearcher(
        query="What information is available in the local documents?",
        report_type="research_report",
        report_source="local"  # Local documents only
    )
    
    await researcher.conduct_research()
    report = await researcher.write_report()
    return report

# Run the research
report = asyncio.run(local_research())
print(report)
```

### Hybrid Research (Recommended)

```python
async def hybrid_research():
    researcher = GPTResearcher(
        query="What are the latest AI trends and how do they relate to our local data?",
        report_type="research_report",
        report_source="hybrid"  # Local docs + web search
    )
    
    await researcher.conduct_research()
    report = await researcher.write_report()
    return report

# Run the research
report = asyncio.run(hybrid_research())
print(report)
```

### Using the Web Interface

1. Navigate to `http://localhost:8067`
2. Select **"My Documents"** from the "Report Source" dropdown
3. Enter your query and run the research

## Supported File Formats

GPT Researcher can process these file types from your local corpus:

| Format | Extension | OCR Support | Notes |
|--------|-----------|-------------|-------|
| PDF | `.pdf` | ✅ Yes | Scanned PDFs processed via Tika |
| Word | `.doc`, `.docx` | ❌ No | Native text extraction |
| PowerPoint | `.pptx` | ❌ No | Native text extraction |
| Excel | `.xls`, `.xlsx` | ❌ No | Native text extraction |
| CSV | `.csv` | ❌ No | Native text extraction |
| Markdown | `.md` | ❌ No | Native text extraction |
| Text | `.txt` | ❌ No | Native text extraction |
| HTML | `.html`, `.htm` | ❌ No | Native text extraction |

## OCR Processing with Apache Tika

### Why Tika?

Apache Tika provides superior OCR capabilities compared to basic Tesseract:
- **Better accuracy** for scanned documents
- **Handwriting recognition** support
- **Multiple language support**
- **Better handling** of complex layouts
- **Efficient processing** of large documents

### Tika Server Setup

Make sure your Tika server is running and accessible:

```bash
# Test Tika connection
curl http://localhost:9998/tika
```

### OCR Processing Flow

1. **PDF Detection**: GPT Researcher first tries standard PyMuPDF extraction
2. **Text Check**: If no text is found, assumes it's a scanned document
3. **Tika Processing**: Sends the PDF to Tika server for OCR
4. **Text Extraction**: Returns extracted text with metadata

## Directory Structure

Your mounted corpus structure will look like:

```
/usr/src/app/my-docs/
├── corpus1/              # Your first corpus
│   ├── document1.pdf
│   ├── document2.docx
│   └── subfolder/
│       └── document3.pdf
├── corpus2/              # Your second corpus
│   ├── scanned_doc.pdf   # Will be processed with OCR
│   └── handwritten.pdf   # Will be processed with OCR
├── corpus3/              # Your third corpus
│   └── large_doc.pdf     # 300+ pages, handled efficiently
└── other-docs/           # Any additional documents
    └── notes.txt
```

## Testing Your Setup

Run the included test script to verify everything works:

```bash
python test_local_corpus.py
```

This will test:
- ✅ Tika server connection
- ✅ Document loading from all corpus paths
- ✅ Local-only research mode
- ✅ Hybrid research mode

## Performance Considerations

### Large Documents (300+ pages)

- **Memory Usage**: PyMuPDF is efficient for large PDFs
- **Processing Time**: OCR processing scales with document size
- **Docker Resources**: Monitor container memory usage

### OCR Processing

- **Timeout**: 60-second timeout for Tika processing
- **Concurrent Processing**: Multiple documents processed in parallel
- **Caching**: Consider preprocessing scanned documents offline

## Troubleshooting

### Common Issues

**Issue**: "Tika connection failed"
- **Solution**: Ensure Tika server is running on port 9998
- **Check**: `curl http://localhost:9998/tika`

**Issue**: "No documents found"
- **Solution**: Check volume mounting in docker-compose.yml
- **Check**: Verify corpus paths exist on host system

**Issue**: "OCR processing failed"
- **Solution**: Check Tika server logs for errors
- **Fallback**: Documents will still be processed with standard loaders

**Issue**: "Memory issues with large PDFs"
- **Solution**: Increase Docker memory limits
- **Check**: Monitor container resource usage

### Debug Mode

Enable verbose logging:

```python
researcher = GPTResearcher(query="...", report_source="local")
researcher.set_verbose(True)
```

## Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DOC_PATH` | `/usr/src/app/my-docs` | Main document directory |
| `TIKA_SERVER_URL` | `http://localhost:9998` | Tika server URL |
| `CORPUS_PATH_1` | `/host/corpus1` | First corpus path |
| `CORPUS_PATH_2` | `/host/corpus2` | Second corpus path |
| `CORPUS_PATH_3` | `/host/corpus3` | Third corpus path |

### Docker Compose Configuration

```yaml
environment:
  DOC_PATH: "/usr/src/app/my-docs"
  TIKA_SERVER_URL: "http://host.docker.internal:9998"

volumes:
  - ${PWD}/my-docs:/usr/src/app/my-docs:rw
  - ${CORPUS_PATH_1}:/usr/src/app/my-docs/corpus1:ro
  - ${CORPUS_PATH_2}:/usr/src/app/my-docs/corpus2:ro
  - ${CORPUS_PATH_3}:/usr/src/app/my-docs/corpus3:ro
```

## Advanced Usage

### Custom Document Processing

You can extend the document processing by modifying `gpt_researcher/document/document.py`:

```python
# Add custom file type support
loader_dict = {
    # ... existing loaders ...
    "custom": CustomDocumentLoader(file_path),
}
```

### Integration with Vector Stores

For large corpora, consider using vector stores:

```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# Create vector store
vector_store = FAISS.from_documents(documents, OpenAIEmbeddings())

# Use with GPT Researcher
researcher = GPTResearcher(
    query=query,
    report_source="langchain_vectorstore",
    vector_store=vector_store
)
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Run the test script to identify problems
3. Check Docker and Tika server logs
4. Review the GPT Researcher documentation

---

**Note**: This setup provides robust local corpus access with OCR support. The hybrid mode is recommended for most use cases as it combines the best of local and web research. :-)

