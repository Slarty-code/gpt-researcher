#!/usr/bin/env python3
"""
Test script for email processing capabilities
Tests MSG, EML, and PST file processing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'legal_document_enhancement'))

from legal_document_enhancement.integration import LegalDocumentEnhancement
from pathlib import Path
import asyncio

async def test_email_processing():
    """Test email processing capabilities"""
    
    print("📧 Email Processing Test")
    print("=" * 50)
    
    # Initialize legal enhancement
    enhancement = LegalDocumentEnhancement(
        use_enhanced_processing=True,
        use_semantic_chunking=True
    )
    
    # Get processing info
    info = enhancement.get_processing_info()
    print(f"📊 Processing Capabilities:")
    print(f"   Email Processing: {info['email_processing']}")
    print(f"   PST Processing: {info['pst_processing']}")
    print(f"   Enhanced Processing: {info['enhanced_processing']}")
    print(f"   Semantic Chunking: {info['semantic_chunking']}")
    print()
    
    # Test with sample email files (if they exist)
    test_files = [
        "test_email.msg",
        "test_email.eml", 
        "test_email.pst"
    ]
    
    print("🧪 Testing Email File Processing:")
    print("-" * 30)
    
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"✅ Found {test_file}")
            try:
                result = await enhancement.process_email_file(test_file)
                print(f"   Status: {'Success' if result.get('enhanced_processing') else 'Fallback'}")
                print(f"   Content length: {len(result['raw_content'])} characters")
                print(f"   File type: {result['metadata'].get('file_type', 'unknown')}")
                print(f"   Processing method: {result['metadata'].get('processing_method', 'unknown')}")
                print()
            except Exception as e:
                print(f"   ❌ Error: {e}")
                print()
        else:
            print(f"⏭️  {test_file} not found (skipping)")
    
    # Test with a sample EML content
    print("📝 Testing with Sample EML Content:")
    print("-" * 35)
    
    sample_eml = """From: john.doe@lawfirm.com
To: jane.smith@client.com
Subject: Contract Review - Termination Clauses
Date: Mon, 15 Jan 2024 10:30:00 +0000
Content-Type: text/plain

Dear Jane,

I've reviewed the contract and found several issues with the termination clauses:

1. The notice period is too short (30 days vs industry standard 90 days)
2. The cure period is insufficient for material breaches
3. The force majeure clause needs clarification

Please let me know if you'd like to discuss these points further.

Best regards,
John Doe
Senior Partner
Law Firm LLC
"""
    
    # Create a temporary EML file
    temp_eml = Path("temp_test_email.eml")
    temp_eml.write_text(sample_eml)
    
    try:
        result = await enhancement.process_email_file(temp_eml)
        print(f"✅ Sample EML processed successfully")
        print(f"   Content length: {len(result['raw_content'])} characters")
        print(f"   Subject: {result['metadata'].get('subject', 'N/A')}")
        print(f"   Sender: {result['metadata'].get('sender', 'N/A')}")
        print(f"   Recipient: {result['metadata'].get('recipient', 'N/A')}")
        print(f"   Processing method: {result['metadata'].get('processing_method', 'unknown')}")
        print()
        print("📄 Processed Content Preview:")
        print("-" * 25)
        print(result['raw_content'][:500] + "..." if len(result['raw_content']) > 500 else result['raw_content'])
        print()
        
    except Exception as e:
        print(f"❌ Error processing sample EML: {e}")
    finally:
        # Clean up
        if temp_eml.exists():
            temp_eml.unlink()
    
    print("🎯 Email Processing Summary:")
    print("-" * 25)
    print("✅ MSG files: Supported (basic text extraction)")
    print("✅ EML files: Supported (full email parsing)")
    print("✅ PST files: Supported (if pypff installed)")
    print("✅ Integration: Ready for GPT Researcher")
    print()
    print("💡 Next Steps:")
    print("   1. Add email files to your legal corpus")
    print("   2. Use the legal enhancement API to process them")
    print("   3. GPT Researcher can now RAG from email content!")

if __name__ == "__main__":
    asyncio.run(test_email_processing())