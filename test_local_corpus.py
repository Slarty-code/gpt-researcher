#!/usr/bin/env python3
"""
Test script for local corpus access with GPT Researcher
Tests both local-only and hybrid research modes with multiple corpus paths
"""

import asyncio
import os
from gpt_researcher import GPTResearcher

async def test_local_research():
    """Test local-only research mode."""
    print("🔍 Testing Local-Only Research Mode")
    print("=" * 50)
    
    # Test query
    query = "What information is available in the local documents?"
    
    try:
        researcher = GPTResearcher(
            query=query,
            report_type="research_report",
            report_source="local"
        )
        
        print(f"Query: {query}")
        print("Conducting research...")
        
        # Conduct research
        research_result = await researcher.conduct_research()
        print("✅ Research completed")
        
        # Write report
        report = await researcher.write_report()
        print("✅ Report generated")
        
        print(f"\nReport Preview (first 500 chars):")
        print("-" * 30)
        print(report[:500] + "..." if len(report) > 500 else report)
        
        return True
        
    except Exception as e:
        print(f"❌ Local research failed: {e}")
        return False

async def test_hybrid_research():
    """Test hybrid research mode (local + web)."""
    print("\n🌐 Testing Hybrid Research Mode")
    print("=" * 50)
    
    # Test query
    query = "What are the latest trends in AI and how do they relate to the information in local documents?"
    
    try:
        researcher = GPTResearcher(
            query=query,
            report_type="research_report",
            report_source="hybrid"
        )
        
        print(f"Query: {query}")
        print("Conducting hybrid research...")
        
        # Conduct research
        research_result = await researcher.conduct_research()
        print("✅ Hybrid research completed")
        
        # Write report
        report = await researcher.write_report()
        print("✅ Hybrid report generated")
        
        print(f"\nReport Preview (first 500 chars):")
        print("-" * 30)
        print(report[:500] + "..." if len(report) > 500 else report)
        
        return True
        
    except Exception as e:
        print(f"❌ Hybrid research failed: {e}")
        return False

async def test_document_loading():
    """Test document loading from multiple corpus paths."""
    print("\n📄 Testing Document Loading")
    print("=" * 50)
    
    from gpt_researcher.document.document import DocumentLoader
    
    # Get DOC_PATH from environment
    doc_path = os.getenv('DOC_PATH', './my-docs')
    print(f"Loading documents from: {doc_path}")
    
    try:
        loader = DocumentLoader(doc_path)
        documents = await loader.load()
        
        print(f"✅ Loaded {len(documents)} documents")
        
        # Show document info
        for i, doc in enumerate(documents[:5]):  # Show first 5 docs
            print(f"  Document {i+1}: {doc['url']} ({len(doc['raw_content'])} chars)")
        
        if len(documents) > 5:
            print(f"  ... and {len(documents) - 5} more documents")
            
        return True
        
    except Exception as e:
        print(f"❌ Document loading failed: {e}")
        return False

async def test_tika_connection():
    """Test connection to Apache Tika server."""
    print("\n🔧 Testing Tika Connection")
    print("=" * 50)
    
    try:
        import requests
        
        tika_url = os.getenv('TIKA_SERVER_URL', 'http://localhost:9998')
        print(f"Testing connection to: {tika_url}")
        
        # Test Tika server health
        response = requests.get(f"{tika_url}/tika", timeout=10)
        
        if response.status_code == 200:
            print("✅ Tika server is accessible")
            return True
        else:
            print(f"⚠️  Tika server returned status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Tika connection failed: {e}")
        print("   Make sure Tika is running on port 9998")
        return False

async def main():
    """Run all tests."""
    print("🚀 GPT Researcher Local Corpus Test Suite")
    print("=" * 60)
    
    # Check environment
    doc_path = os.getenv('DOC_PATH', './my-docs')
    tika_url = os.getenv('TIKA_SERVER_URL', 'http://localhost:9998')
    
    print(f"DOC_PATH: {doc_path}")
    print(f"TIKA_SERVER_URL: {tika_url}")
    print()
    
    # Run tests
    tests = [
        ("Tika Connection", test_tika_connection),
        ("Document Loading", test_document_loading),
        ("Local Research", test_local_research),
        ("Hybrid Research", test_hybrid_research),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(results.values())
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your local corpus setup is working.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    asyncio.run(main())

