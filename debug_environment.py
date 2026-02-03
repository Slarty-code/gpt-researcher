#!/usr/bin/env python3
"""
Debug script to check environment variables and configuration.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check all relevant environment variables"""
    print("🔍 Environment Variable Debug")
    print("=" * 50)
    
    # Required environment variables for Ollama
    required_vars = [
        "OLLAMA_BASE_URL",
        "OPENAI_BASE_URL", 
        "OPENAI_API_KEY",
        "FAST_LLM",
        "SMART_LLM", 
        "STRATEGIC_LLM",
        "EMBEDDING",
        "EMBEDDING_PROVIDER",
        "OLLAMA_EMBEDDING_MODEL"
    ]
    
    print("Required Environment Variables:")
    for var in required_vars:
        value = os.environ.get(var, "NOT SET")
        status = "✅" if value != "NOT SET" else "❌"
        print(f"   {status} {var}: {value}")
    
    print("\nAll Environment Variables (filtered):")
    ollama_vars = {k: v for k, v in os.environ.items() if any(keyword in k.upper() for keyword in ['OLLAMA', 'OPENAI', 'EMBEDDING', 'LLM', 'TAVILY'])}
    for k, v in sorted(ollama_vars.items()):
        print(f"   {k}: {v}")

def test_imports():
    """Test importing key modules"""
    print("\n🧪 Testing Imports")
    print("=" * 50)
    
    try:
        import gpt_researcher
        print("✅ gpt_researcher imported successfully")
    except Exception as e:
        print(f"❌ gpt_researcher import failed: {e}")
        return False
    
    try:
        from gpt_researcher.config.config import Config
        print("✅ Config imported successfully")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from gpt_researcher.memory.embeddings import Memory
        print("✅ Memory imported successfully")
    except Exception as e:
        print(f"❌ Memory import failed: {e}")
        return False
    
    try:
        from gpt_researcher.llm_provider.generic.base import GenericLLMProvider
        print("✅ GenericLLMProvider imported successfully")
    except Exception as e:
        print(f"❌ GenericLLMProvider import failed: {e}")
        return False
    
    return True

def test_config_creation():
    """Test creating a config object"""
    print("\n⚙️  Testing Config Creation")
    print("=" * 50)
    
    try:
        from gpt_researcher.config.config import Config
        config = Config()
        
        print("✅ Config created successfully")
        print(f"   - Fast LLM: {getattr(config, 'fast_llm_provider', 'N/A')}:{getattr(config, 'fast_llm_model', 'N/A')}")
        print(f"   - Smart LLM: {getattr(config, 'smart_llm_provider', 'N/A')}:{getattr(config, 'smart_llm_model', 'N/A')}")
        print(f"   - Strategic LLM: {getattr(config, 'strategic_llm_provider', 'N/A')}:{getattr(config, 'strategic_llm_model', 'N/A')}")
        print(f"   - Embedding: {getattr(config, 'embedding_provider', 'N/A')}:{getattr(config, 'embedding_model', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"❌ Config creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all debug checks"""
    print("🐛 GPT Researcher Environment Debug")
    print("=" * 50)
    
    # Check environment
    check_environment()
    
    # Test imports
    import_success = test_imports()
    
    # Test config creation
    config_success = test_config_creation()
    
    print("\n" + "=" * 50)
    print("Debug Summary:")
    print(f"   - Imports: {'✅ Success' if import_success else '❌ Failed'}")
    print(f"   - Config: {'✅ Success' if config_success else '❌ Failed'}")
    
    if import_success and config_success:
        print("\n🎉 Environment looks good! The fixes should resolve the issue.")
    else:
        print("\n⚠️  There are still issues. Check the error messages above.")

if __name__ == "__main__":
    main()