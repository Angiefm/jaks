#!/usr/bin/env python3
"""Test rápido del pipeline"""
import sys
import os
from pathlib import Path

# Agregar src al PYTHONPATH
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Ahora importar sin el prefijo src.
from storage.vector_store import VectorStore
from embeddings.embedding_engine import EmbeddingEngine

def test_pipeline():
    print("🧪 Testing pipeline components...")
    
    # Test vector store
    print("\n1. Testing Vector Store...")
    try:
        store = VectorStore()
        info = store.get_collection_info()
        print(f"   Documents in store: {info.get('document_count', 0)}")
        
        # Test search si hay documentos
        if info.get('document_count', 0) > 0:
            print("\n2. Testing Search...")
            engine = EmbeddingEngine()
            query = "Spring Boot REST API"
            query_embedding = engine.encode_query(query)
            
            results = store.search_similar(query_embedding, top_k=3)
            print(f"   Found {len(results)} similar documents for query: '{query}'")
            
            for i, result in enumerate(results, 1):
                title = result['metadata'].get('title', 'Unknown')
                similarity = result.get('similarity', 0)
                print(f"   {i}. {title} (similarity: {similarity:.3f})")
        else:
            print("\n   No documents in store yet. Run ingestion first!")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n✅ Pipeline test completed!")
    return True

if __name__ == "__main__":
    test_pipeline()