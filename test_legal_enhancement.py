#!/usr/bin/env python3
"""
Test script for Legal Document Enhancement

This script tests the enhanced document processing capabilities
without modifying GPT Researcher's core functionality.
"""

import asyncio
import logging
from pathlib import Path
from legal_document_enhancement import LegalDocumentEnhancement

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_enhancement():
    """Test the legal document enhancement."""
    
    print("🚀 Testing Legal Document Enhancement")
    print("=" * 50)
    
    # Initialize the enhancement
    enhancement = LegalDocumentEnhancement(
        use_enhanced_processing=True,
        use_semantic_chunking=True
    )
    
    # Get processing info
    info = enhancement.get_processing_info()
    print(f"📊 Processing Configuration:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    print()
    
    # Test with a sample document (if available)
    test_files = [
        "test_document.pdf",
        "test_document.docx",
        "test_document.txt"
    ]
    
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"📄 Testing with: {test_file}")
            try:
                # Process the document
                result = await enhancement.process_document(test_file)
                
                print(f"  ✅ Processing successful")
                print(f"  📝 Content length: {len(result.get('raw_content', ''))}")
                print(f"  🔧 Enhanced processing: {result.get('enhanced_processing', False)}")
                print(f"  📊 Metadata: {result.get('metadata', {})}")
                
                # Test chunking if we have content
                if result.get('raw_content'):
                    from langchain.docstore.document import Document
                    doc = Document(
                        page_content=result['raw_content'],
                        metadata=result.get('metadata', {})
                    )
                    
                    chunks = enhancement.chunk_document(doc)
                    print(f"  📚 Chunks created: {len(chunks)}")
                    
                    for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
                        print(f"    Chunk {i+1}: {len(chunk.page_content)} chars")
                
                print()
                
            except Exception as e:
                print(f"  ❌ Error processing {test_file}: {e}")
                print()
        else:
            print(f"⚠️  Test file not found: {test_file}")
    
    print("✅ Test completed!")

def test_fallback_mode():
    """Test the enhancement in fallback mode."""
    
    print("\n🔄 Testing Fallback Mode")
    print("=" * 30)
    
    # Initialize with enhanced processing disabled
    enhancement = LegalDocumentEnhancement(
        use_enhanced_processing=False,
        use_semantic_chunking=False
    )
    
    info = enhancement.get_processing_info()
    print(f"📊 Fallback Configuration:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("✅ Fallback mode test completed!")

if __name__ == "__main__":
    print("🧪 Legal Document Enhancement Test Suite")
    print("=" * 50)
    
    # Test normal mode
    asyncio.run(test_enhancement())
    
    # Test fallback mode
    test_fallback_mode()
    
    print("\n🎉 All tests completed!")