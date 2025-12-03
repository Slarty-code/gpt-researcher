# Simple Local Corpus Setup

The **easiest way** to use GPT Researcher with your local documents is to simply copy them to the `my-docs` directory. No complex volume mounting required!

## 🚀 Quick Start (3 Steps)

### 1. **Copy Your Documents**
```bash
# Copy your corpus files to the my-docs directory
cp -r /path/to/your/corpus1/* /mnt/data/gpt-researcher/my-docs/corpus1/
cp -r /path/to/your/corpus2/* /mnt/data/gpt-researcher/my-docs/corpus2/
cp -r /path/to/your/corpus3/* /mnt/data/gpt-researcher/my-docs/corpus3/

# Or copy individual files
cp /path/to/document.pdf /mnt/data/gpt-researcher/my-docs/
cp /path/to/scanned.pdf /mnt/data/gpt-researcher/my-docs/
```

### 2. **Start GPT Researcher**
```bash
# Use the simple configuration
docker-compose -f docker-compose.simple.yml up --build

# Or use the regular docker-compose.yml (it already has the right settings)
docker-compose up --build
```

### 3. **Test It**
```bash
python test_local_corpus.py
```

## 📁 Directory Structure

Your `my-docs` directory will look like this:

```
/mnt/data/gpt-researcher/my-docs/
├── corpus1/                    # Your first corpus
│   ├── document1.pdf
│   ├── document2.docx
│   └── subfolder/
│       └── document3.pdf
├── corpus2/                    # Your second corpus
│   ├── scanned_doc.pdf         # Will use Tika OCR
│   └── handwritten.pdf         # Will use Tika OCR
├── corpus3/                    # Your third corpus
│   └── large_document.pdf      # 300+ pages, handled efficiently
├── other_documents/            # Any other files
│   └── notes.txt
└── individual_files/           # Files at root level
    ├── report.pdf
    └── data.xlsx
```

## 🔧 How It Works

### Document Discovery
GPT Researcher's `DocumentLoader` automatically:
- **Recursively searches** the `my-docs` directory
- **Finds all supported files** in any subdirectory
- **Processes them** with appropriate loaders
- **Uses Tika OCR** for scanned PDFs automatically

### Supported File Types
- **PDF** (including scanned PDFs via Tika OCR)
- **Word** (.doc, .docx)
- **PowerPoint** (.pptx)
- **Excel** (.xls, .xlsx)
- **CSV** files
- **Markdown** (.md)
- **Text** (.txt)
- **HTML** (.html, .htm)

## 💻 Usage Examples

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

### Web Interface
1. Navigate to `http://localhost:8067`
2. Select **"My Documents"** from the "Report Source" dropdown
3. Enter your query and run the research

## 🔍 OCR Processing

### Automatic OCR Detection
- **Regular PDFs**: Uses PyMuPDF (fast)
- **Scanned PDFs**: Automatically detects and uses Tika OCR
- **Handwritten content**: Processed via Tika for better accuracy

### Tika Server
Make sure your Tika server is running on port 9998:
```bash
# Test Tika connection
curl http://localhost:9998/tika
```

## 📊 Testing Your Setup

Run the test script to verify everything works:

```bash
python test_local_corpus.py
```

This will test:
- ✅ Tika server connection
- ✅ Document loading from my-docs directory
- ✅ Local-only research mode
- ✅ Hybrid research mode

## 🚨 Troubleshooting

### Common Issues

**Issue**: "No documents found"
- **Solution**: Check that files are in `/mnt/data/gpt-researcher/my-docs/`
- **Check**: Verify file permissions (containers run as root)

**Issue**: "Tika connection failed"
- **Solution**: Ensure Tika server is running on port 9998
- **Check**: Test with `curl http://localhost:9998/tika`

**Issue**: "OCR processing failed"
- **Solution**: Check Tika server logs
- **Fallback**: Documents will still be processed with standard loaders

### Debug Steps

1. **Check file locations**:
   ```bash
   ls -la /mnt/data/gpt-researcher/my-docs/
   ```

2. **Test Tika connection**:
   ```bash
   curl http://localhost:9998/tika
   ```

3. **Check container logs**:
   ```bash
   docker-compose logs gpt-researcher
   ```

## 🔄 Adding More Documents

To add more documents later:

```bash
# Copy new documents
cp /path/to/new/document.pdf /mnt/data/gpt-researcher/my-docs/

# Or create a new subdirectory
mkdir /mnt/data/gpt-researcher/my-docs/new_corpus/
cp /path/to/corpus/* /mnt/data/gpt-researcher/my-docs/new_corpus/

# Restart the container to pick up new files
docker-compose restart gpt-researcher
```

## 📈 Performance Tips

### Large Documents
- **300+ page PDFs**: Handled efficiently by PyMuPDF
- **Scanned documents**: Tika processing may take longer
- **Memory usage**: Monitor container resources

### File Organization
- **Group related documents** in subdirectories
- **Use descriptive names** for easy identification
- **Avoid very deep nesting** (keeps paths manageable)

## 🔒 Security Notes

- **File permissions**: Container runs as root for file access
- **Read-only access**: Documents are read-only during processing
- **Output files**: Generated in `/usr/src/app/outputs/`

## 🎯 Benefits of Simple Approach

- **No complex configuration** needed
- **Easy to add/remove documents**
- **Works with existing docker-compose.yml**
- **Perfect for development and testing**
- **All OCR and processing features included**

---

**This simple approach gives you all the power of local corpus access with OCR support, but without the complexity of multi-volume mounting. Perfect for getting started quickly!** :-)

