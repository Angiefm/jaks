"""pipeline completo del sistema"""
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
    
    print("pipeline completo del sistema")
    print("="*50)
    
    print("\npaso 1: cargando documentos...")
    loader = DocumentLoader()
    docs = loader.load_documents_from_directory("data/raw/github_docs")
    print(f"   {len(docs)} documentos cargados")
    
    print("\npaso 2: generando embeddings...")
    engine = EmbeddingEngine()
    embeddings_dict = engine.encode_documents(docs)
    
    store = VectorStore()
    store.delete_all_documents()
    store.add_documents(docs, embeddings_dict)
    print(f"   {len(embeddings_dict)} embeddings generados y almacenados")
    
    print("\npaso 3: entrenando modelos de calidad...")
    classifier = QualityClassifier()
    quality_report = classifier.train(docs)
    print(f"   clasificador entrenado (Accuracy: {quality_report['accuracy']:.3f})")
    
    detector = AnomalyDetector()
    anomaly_report = detector.train(docs)
    print(f"   detector entrenado ({anomaly_report['anomalies_detected']} anomalías)")
    
    print("\npaso 4: ejecutando clustering...")
    embeddings_array = np.array(list(embeddings_dict.values()))
    
    cluster_engine = ClusterEngine()
    cluster_results = cluster_engine.cluster_hdbscan(embeddings_array, min_cluster_size=3)
    print(f"   {cluster_results['n_clusters']} clusters encontrados")
    
    print("\npaso 5: reducción dimensional...")
    reducer = DimensionalityReducer()
    embeddings_2d = reducer.fit_transform_2d(embeddings_array)
    print(f"   reducción a 2D completada")
    
    print("\n" + "="*50)
    print("pipeline completado exitosamente")
    print(f"   documentos: {len(docs)}")
    print(f"   calidad promedio: {quality_report.get('accuracy', 0)*100:.1f}%")
    print(f"   clusters: {cluster_results['n_clusters']}")
    print(f"   anomalías: {anomaly_report['anomaly_rate']:.1%}")
    print("\nsistema listo para usar")
    print("   ejecuta: python scripts/run_ui.py")

if __name__ == "__main__":
    main()