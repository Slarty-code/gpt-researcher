---
name: Client Document Corpus Review Implementation
overview: ""
todos:
  - id: 18e34d68-1b6b-418a-8b85-42d2572e6c7d
    content: Create client_document_reviewer.py that integrates GPTResearcher with LegalDocumentEnhancement for the client corpus
    status: pending
  - id: 1e2cb535-2b44-4466-ad97-f98809fea24d
    content: Test document loading from /mnt/data/ragstack/data/raw/_archive to ensure all formats are properly supported
    status: pending
  - id: a9d7e8da-66b7-40fd-95ce-509c43d5c53a
    content: Run test queries (specific questions, extraction, comparative) to validate the implementation
    status: pending
  - id: 70abf67a-8e8b-4771-91bc-f1308de47e7f
    content: Create example scripts showing different query patterns for the client document review
    status: pending
isProject: false
---

# Client Document Corpus Review Implementation

## Overview

Configure GPT Researcher to process your client's document corpus at `/mnt/data/ragstack/data/raw/_archive` using the existing legal document enhancement features. This will enable hybrid search capabilities (local documents + web) for answering specific questions, extracting information, and performing comparative analysis.

## Implementation Approach

### 1. Standard GPT Researcher Setup (Official Documentation)

**Quick Start - Using Web Interface:**

1. Set the `DOC_PATH` environment variable:

```bash
   export DOC_PATH="/mnt/data/ragstack/data/raw/_archive"
   

```

1. Configure API keys (add to `.env` file or export):

```bash
   export OPENAI_API_KEY=your_key_here
   export TAVILY_API_KEY=your_key_here
   

```

1. Run GPT Researcher from the repo:

```bash
   cd /mnt/data/gpt-researcher
   python -m uvicorn main:app --reload
   

```

1. Open `http://localhost:8000` and select "My Documents" or "Hybrid" from Report Source dropdown

**Alternative - Using PIP Package in Python:**

```python
from gpt_researcher import GPTResearcher
import asyncio
import os

os.environ['DOC_PATH'] = '/mnt/data/ragstack/data/raw/_archive'

async def research(query: str, mode: str = "local"):
    researcher = GPTResearcher(query=query, report_source=mode)
    await researcher.conduct_research()
    return await researcher.write_report()

# Local only: mode="local"
# Hybrid (local + web): mode="hybrid"
report = asyncio.run(research("Your question here", mode="local"))
```

**Important Notes from Documentation:**

- Supported formats: PDF, TXT, DOCX, CSV, XLSX, PPTX, MD, HTML
- ZIP files need to be extracted first (or use legal enhancement for auto-extraction)
- Default `DOC_PATH` is `./my-docs` if not set

### 2. Integration with Legal Document Enhancement

Leverage the existing `legal_document_enhancement` module already in the codebase:

- Use `LegalDocumentEnhancement` class from `/mnt/data/gpt-researcher/legal_document_enhancement/integration.py`
- Enable enhanced processing for better OCR and document extraction
- Utilize semantic chunking for improved context retrieval
- Support for archive files (.zip) which exist in your corpus

### 3. Create Integration Script

Create a new script `client_document_reviewer.py` that:

- Initializes `LegalDocumentEnhancement` with enhanced processing enabled
- Sets up `GPTResearcher` to work with the processed documents
- Provides a simple interface for different query types:
  - Specific questions about documents
  - Information extraction (dates, parties, amounts)
  - Comparative analysis across documents
- Supports both local-only and hybrid (local + web) research modes

### 4. Key Files to Work With

- **New file**: `client_document_reviewer.py` - Main integration script
- **Existing**: `gpt_researcher/document/document.py` - Document loading (supports PDF, DOCX, TXT, XLSX, etc.)
- **Existing**: `legal_document_enhancement/integration.py` - Enhanced processing
- **Existing**: `gpt_researcher/skills/researcher.py` - Handles hybrid search at lines 138-147

### 5. Usage Pattern

```python
# Example usage
from client_document_reviewer import ClientDocumentReviewer

reviewer = ClientDocumentReviewer(
    doc_path="/mnt/data/ragstack/data/raw/_archive",
    use_enhanced_processing=True
)

# Specific question
report = await reviewer.research(
    query="What are the key legal issues mentioned across all correspondence with Clayton Utz?",
    mode="local"  # or "hybrid" for web + local
)

# Extract information
report = await reviewer.research(
    query="Extract all dates, parties, and monetary amounts from the AFCA complaints",
    mode="local"
)

# Comparative analysis
report = await reviewer.research(
    query="Compare the claims process across BizCover and Lloyds insurance documents",
    mode="hybrid"  # uses web for context on insurance practices
)
```

## Technical Details

### Document Support

Your archive contains:

- **PDFs**: Legal letters, complaints, insurance docs (majority of corpus)
- **DOCX**: Draft letters and responses
- **XLSX**: Financial statements and beneficiary reports  
- **TXT**: Tax legislation files
- **PNG**: VicPol firearm documents
- **ZIP**: Archive folders (Attachments, C Brice, email for GPT, etc.)

All these formats are supported by GPT Researcher's `DocumentLoader` class.

### Enhanced Processing Benefits

The legal enhancement module provides:

- Better OCR for scanned PDFs (many legal documents are scanned)
- Semantic chunking preserving document structure
- Archive extraction (handles .zip files in your corpus)
- Fallback to standard GPT Researcher if enhancement fails

### Report Output

Uses standard GPT Researcher output formats:

- Markdown reports with citations
- Comprehensive analysis with source tracking
- Support for follow-up questions

## Implementation Steps

1. Create the integration script with proper configuration
2. Test with a small subset of documents first
3. Validate document loading and processing
4. Run sample queries to verify functionality
5. Document usage patterns and examples

:-)