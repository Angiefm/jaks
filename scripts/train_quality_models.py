"""script para entrenar modelos de calidad y anomalías"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "src"))

import logging
from ingestion.document_loader import DocumentLoader
from quality.quality_classifier import QualityClassifier
from quality.anomaly_detector import AnomalyDetector
from quality.dashboard import QualityDashboard

def main():
    logging.basicConfig(level=logging.INFO)
    
    print("iniciando entrenamiento de modelos de calidad...")
    
    # cargo documentos
    loader = DocumentLoader()
    docs = loader.load_documents_from_directory("data/raw/github_docs")
    
    if len(docs) < 10:
        print("necesito al menos 10 documentos para entrenar")
        print("ejecuta: python scripts/download_github_docs.py")
        return 1
    
    print(f"cargué {len(docs)} documentos")
    
    # entreno clasificador de calidad
    print("\n 1. entrenando clasificador de calidad...")
    classifier = QualityClassifier()
    quality_report = classifier.train(docs)
    print(f"   accuracy: {quality_report['accuracy']:.3f}")
    
    # entreno detector de anomalías
    print("\n 2. entrenando detector de anomalías...")
    detector = AnomalyDetector()
    anomaly_report = detector.train(docs, contamination=0.15)
    print(f"   anomalías detectadas: {anomaly_report['anomalies_detected']}")
    
    # genero reporte completo
    print("\n 3. generando reporte de calidad...")
    dashboard = QualityDashboard()
    full_report = dashboard.generate_quality_report(docs)
    
    print("\n" + "="*50)
    print("reporte final:")
    print(f"   documentos analizados: {full_report['corpus_stats']['total_documents']}")
    
    if full_report.get('quality_distribution'):
        qd = full_report['quality_distribution']
        print(f"   alta calidad: {qd['class_distribution']['high']['percentage']:.1f}%")
        print(f"   calidad promedio: {qd['avg_quality_score']:.1f}/100")
    
    if full_report.get('anomaly_summary'):
        ans = full_report['anomaly_summary']
        print(f"   anomalías: {ans['anomaly_rate']:.1%}")
    
    print("\nrecomendaciones:")
    for rec in full_report.get('recommendations', [])[:3]:
        print(f"   - {rec}")
    
    print("\nentrenamiento completado exitosamente")
    return 0

if __name__ == "__main__":
    exit(main())
