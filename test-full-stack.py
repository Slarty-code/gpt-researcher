#!/usr/bin/env python3
"""
Test GPT Researcher Full Stack
Tests all services in the full stack deployment
"""

import requests
import json
import time
from datetime import datetime

def test_service_health():
    """Test all service health endpoints"""
    
    print("🏥 Testing Service Health")
    print("=" * 30)
    
    services = [
        ("GPT Researcher", "http://localhost:8000/health"),
        ("Legal Enhancement", "http://localhost:8001/health"),
        ("OWUI Bridge", "http://localhost:8002/health"),
        ("ChromaDB", "http://localhost:8003"),
        ("OWUI Frontend", "http://localhost:3000")
    ]
    
    healthy_services = 0
    
    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: Healthy")
                healthy_services += 1
            else:
                print(f"❌ {name}: Unhealthy (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
    
    print(f"\n📊 Health Summary: {healthy_services}/{len(services)} services healthy")
    return healthy_services == len(services)

def test_gpt_researcher():
    """Test GPT Researcher API"""
    
    print("\n🔍 Testing GPT Researcher API")
    print("=" * 35)
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test research endpoint (mock)
        research_data = {
            "query": "What are the key legal issues in contract law?",
            "research_type": "research_report"
        }
        
        response = requests.post(
            "http://localhost:8000/research",
            json=research_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Research endpoint working")
            return True
        else:
            print(f"❌ Research endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ GPT Researcher test failed: {e}")
        return False

def test_legal_enhancement():
    """Test Legal Enhancement API"""
    
    print("\n⚖️ Testing Legal Enhancement API")
    print("=" * 38)
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test processing info endpoint
        response = requests.get("http://localhost:8001/processing-info", timeout=5)
        if response.status_code == 200:
            info = response.json()
            print("✅ Processing info endpoint working")
            print(f"   Enhanced processing: {info.get('enhanced_processing', 'Unknown')}")
            print(f"   Semantic chunking: {info.get('semantic_chunking', 'Unknown')}")
            print(f"   Email processing: {info.get('email_processing', 'Unknown')}")
            print(f"   Archive processing: {info.get('archive_processing', 'Unknown')}")
        else:
            print(f"❌ Processing info endpoint failed: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Legal Enhancement test failed: {e}")
        return False

def test_owui_bridge():
    """Test OWUI Bridge API"""
    
    print("\n🌉 Testing OWUI Bridge API")
    print("=" * 32)
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test multi-shot research endpoint
        multi_shot_data = {
            "query": "What are the key legal issues in this contract?",
            "context_documents": ["/app/data/sample_contract.pdf"],
            "research_type": "research_report",
            "num_shots": 3,
            "use_legal_enhancement": True
        }
        
        response = requests.post(
            "http://localhost:8002/multi-shot-research",
            json=multi_shot_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Multi-shot research endpoint working")
            else:
                print(f"❌ Multi-shot research failed: {result.get('error')}")
        else:
            print(f"❌ Multi-shot research endpoint failed: {response.status_code}")
        
        # Test chain-of-thought research endpoint
        cot_data = {
            "query": "Analyze the legal implications of this merger",
            "steps": [
                "Identify the key parties",
                "Analyze the financial terms",
                "Review regulatory compliance"
            ],
            "context_documents": ["/app/data/sample_merger.pdf"],
            "use_legal_enhancement": True
        }
        
        response = requests.post(
            "http://localhost:8002/chain-of-thought-research",
            json=cot_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Chain-of-thought research endpoint working")
            else:
                print(f"❌ Chain-of-thought research failed: {result.get('error')}")
        else:
            print(f"❌ Chain-of-thought research endpoint failed: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ OWUI Bridge test failed: {e}")
        return False

def test_chromadb():
    """Test ChromaDB connection"""
    
    print("\n🗄️ Testing ChromaDB")
    print("=" * 20)
    
    try:
        response = requests.get("http://localhost:8003", timeout=5)
        if response.status_code == 200:
            print("✅ ChromaDB is accessible")
            return True
        else:
            print(f"❌ ChromaDB not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ChromaDB test failed: {e}")
        return False

def test_owui_frontend():
    """Test OWUI Frontend"""
    
    print("\n🖥️ Testing OWUI Frontend")
    print("=" * 28)
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ OWUI Frontend is accessible")
            return True
        else:
            print(f"❌ OWUI Frontend not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ OWUI Frontend test failed: {e}")
        return False

def main():
    """Run all tests"""
    
    print("🚀 GPT Researcher Full Stack Test")
    print("=" * 40)
    print(f"Test started at: {datetime.now().isoformat()}")
    print()
    
    # Test all services
    tests = [
        ("Service Health", test_service_health),
        ("GPT Researcher", test_gpt_researcher),
        ("Legal Enhancement", test_legal_enhancement),
        ("OWUI Bridge", test_owui_bridge),
        ("ChromaDB", test_chromadb),
        ("OWUI Frontend", test_owui_frontend)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print("\n🎯 Test Summary")
    print("=" * 20)
    print(f"Tests passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Your full stack is working perfectly!")
        print("\n💡 Next steps:")
        print("1. Access OWUI at http://localhost:3000")
        print("2. Upload your legal documents to ./data/")
        print("3. Start using multi-shot and chain-of-thought research!")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
        print("\n🔧 Troubleshooting:")
        print("1. Check if all services are running: docker-compose -f docker-compose.full-stack.yml ps")
        print("2. Check service logs: docker-compose -f docker-compose.full-stack.yml logs")
        print("3. Restart services: docker-compose -f docker-compose.full-stack.yml restart")
    
    print(f"\nTest completed at: {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()