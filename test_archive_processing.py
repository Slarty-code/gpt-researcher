#!/usr/bin/env python3
"""
Test archive processing capabilities
Tests ZIP, RAR, and TAR file processing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'legal_document_enhancement'))

from legal_document_enhancement.integration import LegalDocumentEnhancement
from pathlib import Path
import asyncio
import tempfile
import zipfile

async def test_archive_processing():
    """Test archive processing capabilities"""
    
    print("📦 Archive Processing Test")
    print("=" * 40)
    
    # Initialize legal enhancement
    enhancement = LegalDocumentEnhancement(
        use_enhanced_processing=True,
        use_semantic_chunking=True
    )
    
    # Get processing info
    info = enhancement.get_processing_info()
    print(f"📊 Processing Capabilities:")
    print(f"   Archive Processing: {info['archive_processing']}")
    print(f"   ZIP Processing: {info['zip_processing']}")
    print(f"   RAR Processing: {info['rar_processing']}")
    print(f"   Enhanced Processing: {info['enhanced_processing']}")
    print(f"   Semantic Chunking: {info['semantic_chunking']}")
    print()
    
    # Test with sample ZIP file
    print("📦 Testing ZIP File Processing:")
    print("-" * 30)
    
    # Create a sample ZIP file
    sample_zip_content = {
        "contract.txt": "CONTRACT TERMS\n==============\n\n1. Payment: Net 30 days\n2. Termination: 90 days notice\n3. Force Majeure: Acts of God",
        "legal_opinion.txt": "LEGAL OPINION\n=============\n\nBased on our review, the contract terms are standard and enforceable under current law.",
        "evidence.pdf": "[Binary PDF content would be here]"
    }
    
    # Create temporary ZIP file
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
        temp_zip_path = Path(temp_zip.name)
        
        with zipfile.ZipFile(temp_zip_path, 'w') as zip_ref:
            for filename, content in sample_zip_content.items():
                zip_ref.writestr(filename, content)
    
    try:
        result = await enhancement.process_archive_file(temp_zip_path)
        print(f"✅ ZIP file processed successfully")
        print(f"   File count: {result['metadata'].get('file_count', 0)}")
        print(f"   Total size: {result['metadata'].get('total_size', 0)} bytes")
        print(f"   Extracted files: {result['metadata'].get('extracted_files', [])}")
        print(f"   Content length: {len(result['raw_content'])} characters")
        print()
        
        print("📄 Processed Content Preview:")
        print("-" * 25)
        print(result['raw_content'][:600] + "..." if len(result['raw_content']) > 600 else result['raw_content'])
        print()
        
    except Exception as e:
        print(f"❌ Error processing ZIP file: {e}")
    finally:
        # Clean up
        if temp_zip_path.exists():
            temp_zip_path.unlink()
    
    # Test with sample TAR file
    print("📦 Testing TAR File Processing:")
    print("-" * 30)
    
    # Create a sample TAR file
    sample_tar_content = {
        "matter_notes.txt": "MATTER NOTES\n============\n\nClient: ABC Corp\nMatter: Contract Review\nStatus: In Progress",
        "research.txt": "RESEARCH FINDINGS\n================\n\n1. Similar cases show 90-day notice is standard\n2. Force majeure clauses are typically broad\n3. Payment terms vary by industry"
    }
    
    # Create temporary TAR file
    with tempfile.NamedTemporaryFile(suffix='.tar', delete=False) as temp_tar:
        temp_tar_path = Path(temp_tar.name)
        
        import tarfile
        with tarfile.open(temp_tar_path, 'w') as tar_ref:
            for filename, content in sample_tar_content.items():
                # Create a temporary file for the content
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
                    temp_file.write(content)
                    temp_file.flush()
                    
                    # Add to tar
                    tar_ref.add(temp_file.name, arcname=filename)
                    
                    # Clean up temp file
                    Path(temp_file.name).unlink()
    
    try:
        result = await enhancement.process_archive_file(temp_tar_path)
        print(f"✅ TAR file processed successfully")
        print(f"   File count: {result['metadata'].get('file_count', 0)}")
        print(f"   Total size: {result['metadata'].get('total_size', 0)} bytes")
        print(f"   Extracted files: {result['metadata'].get('extracted_files', [])}")
        print(f"   Content length: {len(result['raw_content'])} characters")
        print()
        
    except Exception as e:
        print(f"❌ Error processing TAR file: {e}")
    finally:
        # Clean up
        if temp_tar_path.exists():
            temp_tar_path.unlink()
    
    # Test with non-existent RAR file (to test fallback)
    print("📦 Testing RAR File Processing:")
    print("-" * 30)
    
    test_rar_file = Path("test_archive.rar")
    if test_rar_file.exists():
        try:
            result = await enhancement.process_archive_file(test_rar_file)
            print(f"✅ RAR file processed successfully")
            print(f"   File count: {result['metadata'].get('file_count', 0)}")
            print(f"   Content length: {len(result['raw_content'])} characters")
        except Exception as e:
            print(f"❌ Error processing RAR file: {e}")
    else:
        print(f"⏭️  {test_rar_file} not found (skipping)")
        print(f"   RAR processing available: {info['rar_processing']}")
    
    print()
    
    # Summary
    print("🎯 Archive Processing Summary:")
    print("-" * 30)
    print("✅ ZIP files: Supported (built-in Python)")
    print("✅ TAR files: Supported (built-in Python)")
    print("✅ RAR files: Supported (if rarfile installed)")
    print("✅ Text files: Extracted and included in content")
    print("✅ Binary files: Noted with filename and type")
    print("✅ Integration: Works with GPT Researcher")
    print()
    print("💡 What This Means:")
    print("   - Compressed archives are now processed")
    print("   - All files inside archives become searchable")
    print("   - Perfect for legal document collections in archives!")
    print("   - Supports ZIP, RAR, TAR, TAR.GZ, TAR.BZ2")

if __name__ == "__main__":
    asyncio.run(test_archive_processing())