#!/usr/bin/env python3
"""
Legal Document Enhancement API Server
Runs alongside GPT Researcher to provide enhanced document processing
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import our legal enhancement module
from legal_document_enhancement.integration import LegalDocumentEnhancement

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Legal Document Enhancement API",
    description="Enhanced document processing for legal documents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize legal enhancement
legal_enhancement = LegalDocumentEnhancement(
    use_semantic_chunking=True,
    similarity_threshold=0.75
)

# Pydantic models
class ProcessDocumentRequest(BaseModel):
    file_path: str
    use_enhanced_processing: bool = True
    use_semantic_chunking: bool = True

class ProcessDocumentResponse(BaseModel):
    success: bool
    document: Optional[Dict[str, Any]] = None
    chunks: Optional[List[Dict[str, Any]]] = None
    processing_info: Dict[str, Any]
    error: Optional[str] = None

class ChunkDocumentRequest(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None
    use_semantic_chunking: bool = True

class ChunkDocumentResponse(BaseModel):
    success: bool
    chunks: Optional[List[Dict[str, Any]]] = None
    chunking_method: Optional[str] = None
    error: Optional[str] = None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Legal Document Enhancement API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    processing_info = legal_enhancement.get_processing_info()
    return {
        "status": "healthy",
        "enhanced_processing": processing_info["enhanced_processing"],
        "semantic_chunking": processing_info["semantic_chunking"],
        "document_processor_available": processing_info["document_processor_available"],
        "chunker_available": processing_info["chunker_available"]
    }

@app.post("/process-document", response_model=ProcessDocumentResponse)
async def process_document(request: ProcessDocumentRequest):
    """Process a single document with enhanced capabilities"""
    try:
        file_path = Path(request.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Process the document
        if request.use_enhanced_processing:
            result = await legal_enhancement.process_document(file_path)
        else:
            # Fallback to basic processing
            result = {
                "raw_content": file_path.read_text(encoding='utf-8', errors='ignore'),
                "url": str(file_path),
                "enhanced_processing": False,
                "metadata": {
                    "file_type": file_path.suffix.lower(),
                    "processing_method": "basic"
                }
            }
        
        # Chunk the document if requested
        chunks = None
        if request.use_semantic_chunking:
            from langchain.docstore.document import Document
            doc = Document(
                page_content=result["raw_content"],
                metadata=result["metadata"]
            )
            chunked_docs = legal_enhancement.chunk_document(doc)
            chunks = [
                {
                    "content": chunk.page_content,
                    "metadata": chunk.metadata
                }
                for chunk in chunked_docs
            ]
        
        return ProcessDocumentResponse(
            success=True,
            document=result,
            chunks=chunks,
            processing_info=legal_enhancement.get_processing_info()
        )
        
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        return ProcessDocumentResponse(
            success=False,
            error=str(e),
            processing_info=legal_enhancement.get_processing_info()
        )

@app.post("/chunk-document", response_model=ChunkDocumentResponse)
async def chunk_document(request: ChunkDocumentRequest):
    """Chunk a document using enhanced semantic chunking"""
    try:
        from langchain.docstore.document import Document
        
        doc = Document(
            page_content=request.content,
            metadata=request.metadata or {}
        )
        
        if request.use_semantic_chunking:
            chunked_docs = legal_enhancement.chunk_document(doc)
            chunking_method = "semantic"
        else:
            # Fallback to basic chunking
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunked_docs = splitter.split_documents([doc])
            chunking_method = "basic"
        
        chunks = [
            {
                "content": chunk.page_content,
                "metadata": chunk.metadata
            }
            for chunk in chunked_docs
        ]
        
        return ChunkDocumentResponse(
            success=True,
            chunks=chunks,
            chunking_method=chunking_method
        )
        
    except Exception as e:
        logger.error(f"Error chunking document: {e}")
        return ChunkDocumentResponse(
            success=False,
            error=str(e)
        )

@app.post("/process-documents-batch")
async def process_documents_batch(file_paths: List[str]):
    """Process multiple documents in batch"""
    try:
        results = await legal_enhancement.process_documents_batch(
            [Path(fp) for fp in file_paths]
        )
        return {
            "success": True,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error processing documents batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-email-file")
async def process_email_file(request: ProcessDocumentRequest):
    """Process a single email file (MSG, EML, or PST)"""
    try:
        file_path = Path(request.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Email file not found")
        
        result = await legal_enhancement.process_email_file(file_path)
        
        return ProcessDocumentResponse(
            success=True,
            document=result,
            processing_info=legal_enhancement.get_processing_info()
        )
        
    except Exception as e:
        logger.error(f"Error processing email file: {e}")
        return ProcessDocumentResponse(
            success=False,
            error=str(e),
            processing_info=legal_enhancement.get_processing_info()
        )

@app.post("/process-email-files-batch")
async def process_email_files_batch(file_paths: List[str]):
    """Process multiple email files in batch"""
    try:
        results = await legal_enhancement.process_email_files_batch(
            [Path(fp) for fp in file_paths]
        )
        return {
            "success": True,
            "results": results,
            "count": len(results),
            "email_processing": legal_enhancement.get_processing_info()["email_processing"],
            "pst_processing": legal_enhancement.get_processing_info()["pst_processing"]
        }
    except Exception as e:
        logger.error(f"Error processing email files batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-archive-file")
async def process_archive_file(request: ProcessDocumentRequest):
    """Process a single archive file (ZIP, RAR, TAR)"""
    try:
        file_path = Path(request.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Archive file not found")
        
        result = await legal_enhancement.process_archive_file(file_path)
        
        return ProcessDocumentResponse(
            success=True,
            document=result,
            processing_info=legal_enhancement.get_processing_info()
        )
        
    except Exception as e:
        logger.error(f"Error processing archive file: {e}")
        return ProcessDocumentResponse(
            success=False,
            error=str(e),
            processing_info=legal_enhancement.get_processing_info()
        )

@app.post("/process-archive-files-batch")
async def process_archive_files_batch(file_paths: List[str]):
    """Process multiple archive files in batch"""
    try:
        results = await legal_enhancement.process_archive_files_batch(
            [Path(fp) for fp in file_paths]
        )
        return {
            "success": True,
            "results": results,
            "count": len(results),
            "archive_processing": legal_enhancement.get_processing_info()["archive_processing"],
            "zip_processing": legal_enhancement.get_processing_info()["zip_processing"],
            "rar_processing": legal_enhancement.get_processing_info()["rar_processing"]
        }
    except Exception as e:
        logger.error(f"Error processing archive files batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "legal_api_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )