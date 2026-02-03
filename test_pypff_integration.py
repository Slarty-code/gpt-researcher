#!/usr/bin/env python3
"""
Test pypff integration with legal enhancement
Verifies PST file support works correctly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'legal_document_enhancement'))

from legal_document_enhancement.integration import LegalDocumentEnhancement
from pathlib import Path
import asyncio

async def test_pypff_integration():
    """Test pypff integration with legal enhancement"""
    
    print("🔧 pypff Integration Test")
    print("=" * 40)
    
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
    
    # Test pypff import
    print("🧪 Testing pypff Import:")
    print("-" * 25)
    try:
        import pypff
        print(f"✅ pypff imported successfully")
        print(f"   Version: {pypff.get_version()}")
        print(f"   Available: {info['pst_processing']}")
    except ImportError as e:
        print(f"❌ pypff import failed: {e}")
        print(f"   Available: {info['pst_processing']}")
    print()
    
    # Test PST file processing (if file exists)
    print("📁 Testing PST File Processing:")
    print("-" * 30)
    
    test_pst_files = [
        "test_archive.pst",
        "sample.pst",
        "outlook.pst"
    ]
    
    pst_found = False
    for pst_file in test_pst_files:
        if Path(pst_file).exists():
            pst_found = True
            print(f"✅ Found {pst_file}")
            try:
                result = await enhancement.process_email_file(pst_file)
                print(f"   Status: {'Success' if result.get('enhanced_processing') else 'Fallback'}")
                print(f"   Content length: {len(result['raw_content'])} characters")
                print(f"   Message count: {result['metadata'].get('message_count', 'N/A')}")
                print(f"   Processing method: {result['metadata'].get('processing_method', 'unknown')}")
                print()
            except Exception as e:
                print(f"   ❌ Error: {e}")
                print()
        else:
            print(f"⏭️  {pst_file} not found (skipping)")
    
    if not pst_found:
        print("ℹ️  No PST files found for testing")
        print("   Create a test PST file to verify full functionality")
    print()
    
    # Test with sample EML (should work regardless)
    print("📧 Testing EML Processing (baseline):")
    print("-" * 35)
    
    sample_eml = """From: legal@firm.com
To: client@company.com
Subject: Contract Review - Final Draft
Date: Mon, 20 Jan 2024 14:30:00 +0000
Content-Type: text/plain

Dear Client,

Please find attached the final draft of the contract with all requested modifications:

1. Termination clause updated to 90 days notice
2. Force majeure provisions clarified
3. Indemnification limits increased to $1M

Please review and let me know if you have any questions.

Best regards,
Legal Team
"""
    
    # Create temporary EML file
    temp_eml = Path("temp_legal_email.eml")
    temp_eml.write_text(sample_eml)
    
    try:
        result = await enhancement.process_email_file(temp_eml)
        print(f"✅ EML processing successful")
        print(f"   Subject: {result['metadata'].get('subject', 'N/A')}")
        print(f"   Sender: {result['metadata'].get('sender', 'N/A')}")
        print(f"   Content length: {len(result['raw_content'])} characters")
        print()
    except Exception as e:
        print(f"❌ EML processing failed: {e}")
    finally:
        # Clean up
        if temp_eml.exists():
            temp_eml.unlink()
    
    # Summary
    print("🎯 Integration Summary:")
    print("-" * 20)
    print(f"✅ pypff installed: {info['pst_processing']}")
    print(f"✅ Email processing: {info['email_processing']}")
    print(f"✅ Enhanced processing: {info['enhanced_processing']}")
    print(f"✅ Semantic chunking: {info['semantic_chunking']}")
    print()
    
    if info['pst_processing']:
        print("🚀 PST File Support: READY")
        print("   - Can process Outlook PST files")
        print("   - Extracts all messages with metadata")
        print("   - Integrates with GPT Researcher")
    else:
        print("⚠️  PST File Support: NOT AVAILABLE")
        print("   - Install libpff-python for PST support")
        print("   - MSG/EML files still work")
    
    print()
    print("💡 Next Steps:")
    print("   1. Deploy with pypff in Docker container")
    print("   2. Add PST files to your legal corpus")
    print("   3. GPT Researcher can now RAG from email archives!")

if __name__ == "__main__":
    asyncio.run(test_pypff_integration())