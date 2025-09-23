#!/usr/bin/env python3
"""
Example usage of Legal Document Enhancement

This example shows how to use the enhanced document processing
alongside GPT Researcher without modifying the core system.
"""

import asyncio
import logging
from pathlib import Path
from legal_document_enhancement import LegalDocumentEnhancement

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main example function."""
    
    print("📚 Legal Document Enhancement Example")
    print("=" * 40)
    
    # Initialize the enhancement
    enhancement = LegalDocumentEnhancement(
        use_enhanced_processing=True,
        use_semantic_chunking=True,
        use_gpu=True,  # Use GPU if available
        ocr_lang='en'
    )
    
    # Example 1: Process a single document
    print("\n1️⃣ Processing a single document")
    print("-" * 30)
    
    # Replace with your actual document path
    document_path = "sample_legal_document.pdf"
    
    if Path(document_path).exists():
        try:
            result = await enhancement.process_document(document_path)
            
            print(f"✅ Document processed successfully!")
            print(f"📄 File: {result['url']}")
            print(f"🔧 Enhanced processing: {result['enhanced_processing']}")
            print(f"📊 Metadata: {result['metadata']}")
            print(f"📝 Content preview: {result['raw_content'][:200]}...")
            
        except Exception as e:
            print(f"❌ Error processing document: {e}")
    else:
        print(f"⚠️  Document not found: {document_path}")
        print("   Create a sample document to test the enhancement")
    
    # Example 2: Process multiple documents
    print("\n2️⃣ Processing multiple documents")
    print("-" * 30)
    
    document_paths = [
        "document1.pdf",
        "document2.docx",
        "document3.txt"
    ]
    
    # Filter to existing files
    existing_files = [path for path in document_paths if Path(path).exists()]
    
    if existing_files:
        try:
            results = await enhancement.process_documents_batch(existing_files)
            
            print(f"✅ Processed {len(results)} documents")
            for i, result in enumerate(results):
                print(f"  Document {i+1}: {result['url']} - {len(result['raw_content'])} chars")
                
        except Exception as e:
            print(f"❌ Error processing documents: {e}")
    else:
        print("⚠️  No documents found for batch processing")
    
    # Example 3: Chunking
    print("\n3️⃣ Document chunking")
    print("-" * 30)
    
    # Create a sample document for chunking
    from langchain.docstore.document import Document
    
    sample_text = """
    This is a sample legal document. It contains multiple paragraphs of text
    that will be processed and chunked using the enhanced chunking capabilities.
    
    The first paragraph discusses the general terms and conditions of the agreement.
    It outlines the basic framework for the legal relationship between the parties.
    
    The second paragraph goes into more specific details about the obligations
    and responsibilities of each party under the agreement.
    
    The third paragraph covers the termination clauses and dispute resolution
    mechanisms that will govern the relationship.
    """
    
    sample_doc = Document(
        page_content=sample_text,
        metadata={"source": "sample_document", "type": "legal"}
    )
    
    try:
        chunks = enhancement.chunk_document(sample_doc)
        
        print(f"✅ Document chunked into {len(chunks)} pieces")
        for i, chunk in enumerate(chunks):
            print(f"  Chunk {i+1}: {len(chunk.page_content)} chars")
            print(f"    Preview: {chunk.page_content[:100]}...")
            print(f"    Metadata: {chunk.metadata}")
            print()
            
    except Exception as e:
        print(f"❌ Error chunking document: {e}")
    
    # Example 4: Integration with GPT Researcher
    print("\n4️⃣ Integration with GPT Researcher")
    print("-" * 30)
    
    print("To integrate with GPT Researcher, you would:")
    print("1. Import the enhancement module")
    print("2. Use it to process documents before feeding to GPT Researcher")
    print("3. Use the enhanced chunks for better retrieval")
    print()
    print("Example integration code:")
    print("""
    from gpt_researcher import GPTResearcher
    from legal_document_enhancement import LegalDocumentEnhancement
    
    # Initialize both systems
    enhancement = LegalDocumentEnhancement()
    researcher = GPTResearcher(query="legal question")
    
    # Process documents with enhancement
    enhanced_docs = await enhancement.process_documents_batch(document_paths)
    
    # Use enhanced documents with GPT Researcher
    # (This would require modifying GPT Researcher's document loading)
    """)
    
    print("✅ Example completed!")

if __name__ == "__main__":
    asyncio.run(main())