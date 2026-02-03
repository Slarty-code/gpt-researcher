#!/usr/bin/env python3
"""
GPT Researcher Integration with Legal Enhancement
This integrates the legal enhancement API with GPT Researcher
"""

import asyncio
import logging
import requests
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class GPTResearcherLegalIntegration:
    """
    Integrates GPT Researcher with the Legal Enhancement API
    """
    
    def __init__(self, 
                 gpt_researcher_url: str = "http://localhost:8000",
                 legal_enhancement_url: str = "http://localhost:8001"):
        self.gpt_researcher_url = gpt_researcher_url
        self.legal_enhancement_url = legal_enhancement_url
        
    async def process_legal_documents(self, 
                                    file_paths: List[str],
                                    query: str,
                                    use_enhanced_processing: bool = True) -> Dict[str, Any]:
        """
        Process legal documents with enhanced capabilities and then research
        """
        try:
            # Step 1: Process documents with legal enhancement
            if use_enhanced_processing:
                logger.info("Processing documents with legal enhancement...")
                processed_docs = await self._process_documents_with_enhancement(file_paths)
            else:
                logger.info("Using basic document processing...")
                processed_docs = await self._process_documents_basic(file_paths)
            
            # Step 2: Use GPT Researcher for research
            logger.info("Starting GPT Researcher analysis...")
            research_result = await self._research_with_gpt_researcher(query, processed_docs)
            
            return {
                "success": True,
                "processed_documents": processed_docs,
                "research_result": research_result,
                "enhancement_used": use_enhanced_processing
            }
            
        except Exception as e:
            logger.error(f"Error in legal document processing: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _process_documents_with_enhancement(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Process documents using the legal enhancement API"""
        try:
            response = requests.post(
                f"{self.legal_enhancement_url}/process-documents-batch",
                json=file_paths,
                timeout=300  # 5 minutes timeout for document processing
            )
            response.raise_for_status()
            return response.json()["results"]
        except Exception as e:
            logger.warning(f"Legal enhancement failed: {e}")
            return await self._process_documents_basic(file_paths)
    
    async def _process_documents_basic(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Fallback to basic document processing"""
        processed_docs = []
        for file_path in file_paths:
            try:
                content = Path(file_path).read_text(encoding='utf-8', errors='ignore')
                processed_docs.append({
                    "raw_content": content,
                    "url": file_path,
                    "enhanced_processing": False,
                    "metadata": {
                        "file_type": Path(file_path).suffix.lower(),
                        "processing_method": "basic"
                    }
                })
            except Exception as e:
                logger.warning(f"Failed to process {file_path}: {e}")
        return processed_docs
    
    async def _research_with_gpt_researcher(self, query: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Use GPT Researcher for the actual research"""
        try:
            # Prepare the research request
            research_request = {
                "query": query,
                "sources": [doc["url"] for doc in documents],
                "enhanced_processing": any(doc.get("enhanced_processing", False) for doc in documents)
            }
            
            # Call GPT Researcher API
            response = requests.post(
                f"{self.gpt_researcher_url}/research",
                json=research_request,
                timeout=600  # 10 minutes timeout for research
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"GPT Researcher API call failed: {e}")
            return {
                "query": query,
                "sources_used": len(documents),
                "research_completed": False,
                "error": str(e),
                "note": "GPT Researcher API integration needed"
            }

# Example usage
async def main():
    """Example of how to use the integration"""
    integration = GPTResearcherLegalIntegration()
    
    # Process legal documents
    result = await integration.process_legal_documents(
        file_paths=["/path/to/contract1.pdf", "/path/to/contract2.pdf"],
        query="What are the termination clauses in these contracts?",
        use_enhanced_processing=True
    )
    
    print(f"Processing result: {result}")

if __name__ == "__main__":
    asyncio.run(main())