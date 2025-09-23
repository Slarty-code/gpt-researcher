#!/usr/bin/env python3
"""
Basic integration test for Legal Document Enhancement

This test verifies the module structure and basic functionality
without requiring heavy dependencies like torch, paddleocr, etc.
"""

import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_module_structure():
    """Test that the module structure is correct."""
    
    print("🧪 Testing Module Structure")
    print("=" * 30)
    
    # Test 1: Check if the module directory exists
    module_dir = Path("legal_document_enhancement")
    if module_dir.exists():
        print("✅ Module directory exists")
    else:
        print("❌ Module directory not found")
        return False
    
    # Test 2: Check if __init__.py exists
    init_file = module_dir / "__init__.py"
    if init_file.exists():
        print("✅ __init__.py exists")
    else:
        print("❌ __init__.py not found")
        return False
    
    # Test 3: Check if main modules exist
    required_files = [
        "document_processor.py",
        "chunker.py", 
        "integration.py",
        "requirements.txt"
    ]
    
    for file_name in required_files:
        file_path = module_dir / file_name
        if file_path.exists():
            print(f"✅ {file_name} exists")
        else:
            print(f"❌ {file_name} not found")
            return False
    
    print("✅ All required files exist")
    return True

def test_import_structure():
    """Test that the import structure works (without heavy dependencies)."""
    
    print("\n📦 Testing Import Structure")
    print("=" * 30)
    
    try:
        # Test basic imports
        import legal_document_enhancement
        print("✅ Main module imports successfully")
        
        # Test that the module has the expected attributes
        expected_attrs = ["LegalDocumentProcessor", "LegalChunker"]
        for attr in expected_attrs:
            if hasattr(legal_document_enhancement, attr):
                print(f"✅ {attr} is available")
            else:
                print(f"❌ {attr} not found")
                return False
        
        print("✅ All expected attributes are available")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_fallback_functionality():
    """Test fallback functionality without heavy dependencies."""
    
    print("\n🔄 Testing Fallback Functionality")
    print("=" * 30)
    
    try:
        # Test the integration module directly
        sys.path.insert(0, str(Path.cwd()))
        
        # Mock the heavy dependencies
        import unittest.mock as mock
        
        with mock.patch.dict('sys.modules', {
            'torch': mock.MagicMock(),
            'paddleocr': mock.MagicMock(),
            'transformers': mock.MagicMock(),
            'camelot': mock.MagicMock(),
            'sentence_transformers': mock.MagicMock()
        }):
            from legal_document_enhancement.integration import LegalDocumentEnhancement
            
            # Test initialization in fallback mode
            enhancement = LegalDocumentEnhancement(
                use_enhanced_processing=False,
                use_semantic_chunking=False
            )
            
            print("✅ Enhancement initialized in fallback mode")
            
            # Test get_processing_info
            info = enhancement.get_processing_info()
            print(f"✅ Processing info: {info}")
            
            # Test that it has the expected methods
            expected_methods = [
                'process_document',
                'chunk_document', 
                'process_documents_batch',
                'chunk_documents',
                'get_processing_info'
            ]
            
            for method in expected_methods:
                if hasattr(enhancement, method):
                    print(f"✅ Method {method} exists")
                else:
                    print(f"❌ Method {method} not found")
                    return False
            
            print("✅ All expected methods are available")
            return True
            
    except Exception as e:
        print(f"❌ Error testing fallback functionality: {e}")
        return False

def test_requirements_file():
    """Test that the requirements file is properly formatted."""
    
    print("\n📋 Testing Requirements File")
    print("=" * 30)
    
    try:
        requirements_file = Path("legal_document_enhancement/requirements.txt")
        
        if not requirements_file.exists():
            print("❌ Requirements file not found")
            return False
        
        with open(requirements_file, 'r') as f:
            requirements = f.read()
        
        # Check for key dependencies
        key_deps = [
            "paddleocr",
            "transformers", 
            "sentence-transformers",
            "camelot"
        ]
        
        for dep in key_deps:
            if dep in requirements:
                print(f"✅ {dep} found in requirements")
            else:
                print(f"❌ {dep} not found in requirements")
                return False
        
        print("✅ Requirements file looks good")
        return True
        
    except Exception as e:
        print(f"❌ Error testing requirements file: {e}")
        return False

def main():
    """Run all tests."""
    
    print("🧪 Legal Document Enhancement - Basic Integration Test")
    print("=" * 60)
    
    tests = [
        test_module_structure,
        test_import_structure,
        test_fallback_functionality,
        test_requirements_file
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with error: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The module structure is correct.")
        print("\nNext steps:")
        print("1. Install the requirements: pip install -r legal_document_enhancement/requirements.txt")
        print("2. Test with actual documents")
        print("3. Integrate with GPT Researcher")
    else:
        print("❌ Some tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)