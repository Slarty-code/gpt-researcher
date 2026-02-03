#!/usr/bin/env python3
"""
GPT Researcher + OWUI Integration
Provides multi-shot and chain-of-thought prompting capabilities
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

class GPTResearcherOWUIIntegration:
    """
    Integration class for GPT Researcher with OWUI
    Provides multi-shot and chain-of-thought prompting
    """
    
    def __init__(self, 
                 gpt_researcher_url: str = "http://localhost:8000",
                 legal_enhancement_url: str = "http://localhost:8001",
                 api_key: Optional[str] = None):
        """
        Initialize GPT Researcher + OWUI integration
        
        Args:
            gpt_researcher_url: URL of GPT Researcher API
            legal_enhancement_url: URL of Legal Enhancement API
            api_key: API key for authentication (if required)
        """
        self.gpt_researcher_url = gpt_researcher_url.rstrip('/')
        self.legal_enhancement_url = legal_enhancement_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
        
        logger.info(f"GPT Researcher OWUI Integration initialized")
        logger.info(f"GPT Researcher URL: {self.gpt_researcher_url}")
        logger.info(f"Legal Enhancement URL: {self.legal_enhancement_url}")
    
    async def multi_shot_research(self, 
                                query: str, 
                                context_documents: List[str],
                                research_type: str = "research_report",
                                num_shots: int = 3) -> Dict[str, Any]:
        """
        Perform multi-shot research with context documents
        
        Args:
            query: Research query
            context_documents: List of document paths for context
            research_type: Type of research (research_report, detailed_report, etc.)
            num_shots: Number of examples to use
            
        Returns:
            Research results with multi-shot examples
        """
        try:
            # Step 1: Process context documents
            processed_docs = await self._process_context_documents(context_documents)
            
            # Step 2: Create multi-shot prompt
            multi_shot_prompt = self._create_multi_shot_prompt(
                query, processed_docs, num_shots
            )
            
            # Step 3: Perform research with multi-shot context
            research_result = await self._perform_research(
                multi_shot_prompt, research_type
            )
            
            return {
                "success": True,
                "query": query,
                "research_type": research_type,
                "num_shots": num_shots,
                "context_documents": len(context_documents),
                "result": research_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Multi-shot research failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def chain_of_thought_research(self, 
                                      query: str,
                                      steps: List[str],
                                      context_documents: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Perform chain-of-thought research with step-by-step reasoning
        
        Args:
            query: Research query
            steps: List of reasoning steps
            context_documents: Optional context documents
            
        Returns:
            Chain-of-thought research results
        """
        try:
            # Step 1: Process context documents if provided
            processed_docs = []
            if context_documents:
                processed_docs = await self._process_context_documents(context_documents)
            
            # Step 2: Create chain-of-thought prompt
            cot_prompt = self._create_chain_of_thought_prompt(query, steps, processed_docs)
            
            # Step 3: Perform step-by-step research
            research_steps = []
            for i, step in enumerate(steps):
                step_result = await self._perform_research_step(
                    step, cot_prompt, i + 1, len(steps)
                )
                research_steps.append(step_result)
            
            # Step 4: Synthesize final result
            final_result = await self._synthesize_chain_of_thought(
                query, research_steps, processed_docs
            )
            
            return {
                "success": True,
                "query": query,
                "steps": steps,
                "research_steps": research_steps,
                "final_result": final_result,
                "context_documents": len(processed_docs),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Chain-of-thought research failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _process_context_documents(self, document_paths: List[str]) -> List[Dict[str, Any]]:
        """Process context documents using legal enhancement"""
        processed_docs = []
        
        for doc_path in document_paths:
            try:
                # Try legal enhancement first
                response = self.session.post(
                    f"{self.legal_enhancement_url}/process-document",
                    json={"file_path": doc_path, "use_enhanced_processing": True}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        processed_docs.append(result["document"])
                    else:
                        logger.warning(f"Legal enhancement failed for {doc_path}: {result.get('error')}")
                        # Fallback to basic processing
                        processed_docs.append(await self._basic_document_processing(doc_path))
                else:
                    logger.warning(f"Legal enhancement API error for {doc_path}: {response.status_code}")
                    # Fallback to basic processing
                    processed_docs.append(await self._basic_document_processing(doc_path))
                    
            except Exception as e:
                logger.warning(f"Failed to process {doc_path}: {e}")
                # Fallback to basic processing
                processed_docs.append(await self._basic_document_processing(doc_path))
        
        return processed_docs
    
    async def _basic_document_processing(self, doc_path: str) -> Dict[str, Any]:
        """Basic document processing fallback"""
        try:
            with open(doc_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return {
                "raw_content": content,
                "url": doc_path,
                "enhanced_processing": False,
                "metadata": {
                    "file_type": Path(doc_path).suffix.lower(),
                    "processing_method": "basic_fallback"
                }
            }
        except Exception as e:
            logger.error(f"Basic processing failed for {doc_path}: {e}")
            return {
                "raw_content": f"Error processing {doc_path}: {e}",
                "url": doc_path,
                "enhanced_processing": False,
                "metadata": {
                    "file_type": Path(doc_path).suffix.lower(),
                    "processing_method": "error"
                }
            }
    
    def _create_multi_shot_prompt(self, 
                                query: str, 
                                context_docs: List[Dict[str, Any]], 
                                num_shots: int) -> str:
        """Create multi-shot prompt with examples"""
        
        # Extract examples from context documents
        examples = self._extract_examples_from_docs(context_docs, num_shots)
        
        prompt = f"""
MULTI-SHOT LEGAL RESEARCH PROMPT
================================

RESEARCH QUERY: {query}

CONTEXT DOCUMENTS: {len(context_docs)} documents provided

EXAMPLES FROM CONTEXT:
{self._format_examples(examples)}

INSTRUCTIONS:
1. Use the provided examples to understand the research pattern
2. Apply similar analysis techniques to the current query
3. Follow the same structure and depth as the examples
4. Ensure legal accuracy and proper citation

RESEARCH QUERY: {query}

Please provide a comprehensive research report following the pattern established in the examples.
"""
        return prompt
    
    def _create_chain_of_thought_prompt(self, 
                                      query: str, 
                                      steps: List[str], 
                                      context_docs: List[Dict[str, Any]]) -> str:
        """Create chain-of-thought prompt"""
        
        context_summary = self._summarize_context_docs(context_docs)
        
        prompt = f"""
CHAIN-OF-THOUGHT LEGAL RESEARCH
==============================

RESEARCH QUERY: {query}

CONTEXT: {context_summary}

REASONING STEPS:
{self._format_reasoning_steps(steps)}

INSTRUCTIONS:
1. Follow each reasoning step systematically
2. Provide detailed analysis for each step
3. Build upon previous steps logically
4. Ensure legal accuracy and proper citation
5. Synthesize findings into a comprehensive conclusion

Please proceed with the chain-of-thought analysis.
"""
        return prompt
    
    def _extract_examples_from_docs(self, docs: List[Dict[str, Any]], num_shots: int) -> List[Dict[str, Any]]:
        """Extract examples from context documents"""
        examples = []
        
        for doc in docs[:num_shots]:
            content = doc.get("raw_content", "")
            metadata = doc.get("metadata", {})
            
            # Extract key sections (simplified)
            example = {
                "content": content[:1000] + "..." if len(content) > 1000 else content,
                "metadata": metadata,
                "file_type": metadata.get("file_type", "unknown")
            }
            examples.append(example)
        
        return examples
    
    def _format_examples(self, examples: List[Dict[str, Any]]) -> str:
        """Format examples for prompt"""
        formatted = []
        
        for i, example in enumerate(examples, 1):
            formatted.append(f"""
EXAMPLE {i}:
File Type: {example['file_type']}
Content: {example['content']}
Metadata: {example['metadata']}
---""")
        
        return "\n".join(formatted)
    
    def _summarize_context_docs(self, docs: List[Dict[str, Any]]) -> str:
        """Summarize context documents"""
        if not docs:
            return "No context documents provided"
        
        summary = f"Found {len(docs)} context documents:\n"
        
        for i, doc in enumerate(docs, 1):
            metadata = doc.get("metadata", {})
            file_type = metadata.get("file_type", "unknown")
            processing_method = metadata.get("processing_method", "unknown")
            
            summary += f"{i}. {Path(doc.get('url', 'unknown')).name} ({file_type}) - {processing_method}\n"
        
        return summary
    
    def _format_reasoning_steps(self, steps: List[str]) -> str:
        """Format reasoning steps for prompt"""
        formatted = []
        
        for i, step in enumerate(steps, 1):
            formatted.append(f"{i}. {step}")
        
        return "\n".join(formatted)
    
    async def _perform_research(self, prompt: str, research_type: str) -> Dict[str, Any]:
        """Perform research using GPT Researcher API"""
        try:
            # This would call GPT Researcher API
            # For now, return a mock response
            return {
                "research_type": research_type,
                "prompt": prompt,
                "result": "Research completed (mock response)",
                "sources": [],
                "citations": []
            }
        except Exception as e:
            logger.error(f"Research failed: {e}")
            raise e
    
    async def _perform_research_step(self, step: str, prompt: str, step_num: int, total_steps: int) -> Dict[str, Any]:
        """Perform a single research step"""
        try:
            # This would call GPT Researcher API for the specific step
            return {
                "step_number": step_num,
                "total_steps": total_steps,
                "step_description": step,
                "result": f"Step {step_num} completed (mock response)",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Research step {step_num} failed: {e}")
            raise e
    
    async def _synthesize_chain_of_thought(self, 
                                         query: str, 
                                         research_steps: List[Dict[str, Any]], 
                                         context_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize chain-of-thought results"""
        return {
            "query": query,
            "synthesis": "Chain-of-thought analysis completed (mock response)",
            "steps_completed": len(research_steps),
            "context_used": len(context_docs),
            "timestamp": datetime.now().isoformat()
        }

# Example usage
async def main():
    """Example usage of GPT Researcher OWUI Integration"""
    
    # Initialize integration
    integration = GPTResearcherOWUIIntegration(
        gpt_researcher_url="http://localhost:8000",
        legal_enhancement_url="http://localhost:8001"
    )
    
    # Multi-shot research example
    print("🔍 Multi-Shot Research Example:")
    multi_shot_result = await integration.multi_shot_research(
        query="What are the key legal issues in this contract?",
        context_documents=["contract1.pdf", "contract2.pdf", "legal_opinion.docx"],
        research_type="research_report",
        num_shots=3
    )
    print(json.dumps(multi_shot_result, indent=2))
    
    # Chain-of-thought research example
    print("\n🧠 Chain-of-Thought Research Example:")
    cot_result = await integration.chain_of_thought_research(
        query="Analyze the legal implications of this merger agreement",
        steps=[
            "Identify the key parties and their roles",
            "Analyze the financial terms and conditions",
            "Review regulatory compliance requirements",
            "Assess potential legal risks and liabilities",
            "Provide recommendations for risk mitigation"
        ],
        context_documents=["merger_agreement.pdf", "due_diligence_report.docx"]
    )
    print(json.dumps(cot_result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())