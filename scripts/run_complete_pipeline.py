#!/usr/bin/env python3
"""Pipeline completo del sistema"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

import logging
import numpy as np

from ingestion.document_loader import DocumentLoader
from embeddings.embedding_engine import EmbeddingEngine
from storage.vector_store import VectorStore
from quality.quality_classifier import QualityClassifier
from quality.anomaly_detector import AnomalyDetector
from clustering.cluster_engine import ClusterEngine
from clustering.dimensionality_reducer import DimensionalityReducer

def main():
    logging.basicConfig(level=logging.INFO)
    
    print("🚀 PIPELINE COMPLETO DEL SISTEMA")
    print("="*50)
    
    # 1. Cargar documentos
    print("\n📚 Paso 1: Cargando documentos...")
    loader = DocumentLoader()
    docs = loader.load_documents_from_directory("data/raw/github_docs")
    print(f"   ✅ {len(docs)} documentos cargados")
    
    # 2. Generar embeddings y almacenar
    print("\n🧠 Paso 2: Generando embeddings...")
    engine = EmbeddingEngine()
    embeddings_dict = engine.encode_documents(docs)
    
    store = VectorStore()
    store.delete_all_documents()
    store.add_documents(docs, embeddings_dict)
    print(f"   ✅ {len(embeddings_dict)} embeddings generados y almacenados")
    
    # 3. Entrenar modelos de calidad
    print("\n🎯 Paso 3: Entrenando modelos de calidad...")
    classifier = QualityClassifier()
    quality_report = classifier.train(docs)
    print(f"   ✅ Clasificador entrenado (Accuracy: {quality_report['accuracy']:.3f})")
    
    detector = AnomalyDetector()
    anomaly_report = detector.train(docs)
    print(f"   ✅ Detector entrenado ({anomaly_report['anomalies_detected']} anomalías)")
    
    # 4. Clustering
    print("\n🗂️ Paso 4: Ejecutando clustering...")
    embeddings_array = np.array(list(embeddings_dict.values()))
    
    cluster_engine = ClusterEngine()
    cluster_results = cluster_engine.cluster_hdbscan(embeddings_array, min_cluster_size=3)
    print(f"   ✅ {cluster_results['n_clusters']} clusters encontrados")
    
    # 5. Reducción dimensional
    print("\n📊 Paso 5: Reducción dimensional...")
    reducer = DimensionalityReducer()
    embeddings_2d = reducer.fit_transform_2d(embeddings_array)
    print(f"   ✅ Reducción a 2D completada")
    
    # Resumen final
    print("\n" + "="*50)
    print("🎉 PIPELINE COMPLETADO EXITOSAMENTE")
    print(f"   📚 Documentos: {len(docs)}")
    print(f"   🎯 Calidad promedio: {quality_report.get('accuracy', 0)*100:.1f}%")
    print(f"   🗂️ Clusters: {cluster_results['n_clusters']}")
    print(f"   ⚠️  Anomalías: {anomaly_report['anomaly_rate']:.1%}")
    print("\n💡 Sistema listo para usar!")
    print("   Ejecuta: python scripts/run_ui.py")

if __name__ == "__main__":
    main()