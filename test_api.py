#!/usr/bin/env python3
import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing API endpoints...")
    
    # Test health
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health: {response.json()}")
    except:
        print("❌ API not running. Start with: python scripts/run_api.py")
        return
    
    # Test system info
    try:
        response = requests.get(f"{base_url}/system/info")
        print(f"📊 System Info: {response.json()}")
    except Exception as e:
        print(f"❌ System info failed: {e}")
    
    # Test search
    try:
        response = requests.get(f"{base_url}/search?q=Spring Boot REST&top_k=3")
        results = response.json()
        print(f"🔍 Search Results: {results['total_results']} found")
        for i, result in enumerate(results['results'][:2], 1):
            print(f"  {i}. {result['title']} ({result['similarity_score']})")
    except Exception as e:
        print(f"❌ Search failed: {e}")

if __name__ == "__main__":
    test_api()