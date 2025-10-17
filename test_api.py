import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    
    print("testing API endpoints...")
    
    try:
        response = requests.get(f"{base_url}/health")
        print(f"health: {response.json()}")
    except:
        print("API not running. Start with: python scripts/run_api.py")
        return
    
    try:
        response = requests.get(f"{base_url}/system/info")
        print(f"system info: {response.json()}")
    except Exception as e:
        print(f"system info failed: {e}")
    
    try:
        response = requests.get(f"{base_url}/search?q=Spring Boot REST&top_k=3")
        results = response.json()
        print(f"search results: {results['total_results']} found")
        for i, result in enumerate(results['results'][:2], 1):
            print(f"  {i}. {result['title']} ({result['similarity_score']})")
    except Exception as e:
        print(f"search failed: {e}")

if __name__ == "__main__":
    test_api()