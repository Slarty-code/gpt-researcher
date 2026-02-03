#!/usr/bin/env python3
"""
Test script to verify Ollama integration is working properly.
This script tests the basic functionality without running the full research pipeline.
"""

import os
import asyncio
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the Python path
sys.path.insert(0, '/mnt/data/gpt-researcher')

async def test_ollama_llm():
    """Test Ollama LLM provider"""
    print("Testing Ollama LLM provider...")
    
    try:
        from gpt_researcher.llm_provider.generic.base import GenericLLMProvider
        
        # Test LLM provider initialization
        llm_provider = GenericLLMProvider.from_provider(
            provider="ollama",
            model="gpt-oss:20b",
            temperature=0.1
        )
        print("✅ Ollama LLM provider initialized successfully")
        
        # Test a simple chat completion
        messages = [
            {"role": "user", "content": "Hello, can you respond with just 'Test successful'?"}
        ]
        
        response = await llm_provider.get_chat_response(messages, stream=False)
        print(f"✅ LLM Response: {response}")
        
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        return False
    
    return True

async def test_ollama_embeddings():
    """Test Ollama embeddings"""
    print("\nTesting Ollama embeddings...")
    
    try:
        from gpt_researcher.memory.embeddings import Memory
        
        # Test embeddings initialization
        memory = Memory(
            embedding_provider="ollama",
            model="snowflake-arctic-embed2"
        )
        print("✅ Ollama embeddings initialized successfully")
        
        # Test embedding generation
        test_text = "This is a test document for embedding generation."
        embeddings = memory.get_embeddings()
        result = await embeddings.aembed_query(test_text)
        print(f"✅ Embeddings generated successfully (dimension: {len(result)})")
        
    except Exception as e:
        print(f"❌ Embeddings test failed: {e}")
        return False
    
    return True

async def test_config_parsing():
    """Test configuration parsing"""
    print("\nTesting configuration parsing...")
    
    try:
        from gpt_researcher.config.config import Config
        
        # Test config initialization
        config = Config()
        print(f"✅ Config initialized successfully")
        print(f"   - Fast LLM: {config.fast_llm_provider}:{config.fast_llm_model}")
        print(f"   - Smart LLM: {config.smart_llm_provider}:{config.smart_llm_model}")
        print(f"   - Strategic LLM: {config.strategic_llm_provider}:{config.strategic_llm_model}")
        print(f"   - Embedding: {config.embedding_provider}:{config.embedding_model}")
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False
    
    return True

async def main():
    """Run all tests"""
    print("🧪 Testing Ollama Integration for GPT Researcher")
    print("=" * 50)
    
    # Check environment variables
    print("Environment variables:")
    print(f"   - OLLAMA_BASE_URL: {os.environ.get('OLLAMA_BASE_URL', 'NOT SET')}")
    print(f"   - OPENAI_BASE_URL: {os.environ.get('OPENAI_BASE_URL', 'NOT SET')}")
    print(f"   - FAST_LLM: {os.environ.get('FAST_LLM', 'NOT SET')}")
    print(f"   - EMBEDDING: {os.environ.get('EMBEDDING', 'NOT SET')}")
    print()
    
    # Run tests
    tests = [
        test_config_parsing,
        test_ollama_llm,
        test_ollama_embeddings
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Ollama integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)