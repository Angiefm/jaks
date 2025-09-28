"""dashboard de control de calidad"""
import logging
from typing import List, Dict, Any
import pandas as pd
import numpy as np

from .quality_classifier import QualityClassifier
from .anomaly_detector import AnomalyDetector
from .quality_metrics import QualityMetrics

class QualityDashboard:
    """dashboard para análisis de calidad del corpus"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.classifier = QualityClassifier()
        self.anomaly_detector = AnomalyDetector()
        self.metrics_extractor = QualityMetrics()
    
    def generate_quality_report(self, documents: List) -> Dict[str, Any]:
        """genero un reporte completo de calidad"""
        self.logger.info(f"generando reporte de calidad para {len(documents)} documentos")
        
        # hago análisis de calidad
        quality_results = []
        anomaly_results = []
        
        for doc in documents:
            # clasifico calidad
            if self.classifier.is_trained:
                quality_info = self.classifier.predict_quality(doc)
                quality_results.append({
                    'document_id': doc.id,
                    'title': doc.title,
                    'quality_class': quality_info['quality_class'],
                    'quality_score': quality_info['quality_score'],
                    'confidence': quality_info['confidence']
                })
        
        # detecto anomalías
        if self.anomaly_detector.is_trained and documents:
            anomaly_summary = self.anomaly_detector.get_anomaly_summary(documents)
            anomaly_results = self.anomaly_detector.detect_anomalies(documents)
        
        # saco estadísticas generales
        stats = self._calculate_corpus_stats(documents)
        
        # genero recomendaciones
        recommendations = self._generate_recommendations(quality_results, anomaly_results, stats)
        
        return {
            'corpus_stats': stats,
            'quality_distribution': self._analyze_quality_distribution(quality_results),
            'anomaly_summary': anomaly_summary if anomaly_results else {},
            'top_quality_docs': sorted(quality_results, 
                                     key=lambda x: x['quality_score'], 
                                     reverse=True)[:10] if quality_results else [],
            'problematic_docs': [r for r in anomaly_results if r['is_anomaly']][:10],
            'recommendations': recommendations
        }
    
    def _calculate_corpus_stats(self, documents: List) -> Dict[str, Any]:
        """calculo estadísticas básicas del corpus"""
        if not documents:
            return {}
        
        # saco métricas básicas
        lengths = [len(doc.content) for doc in documents]
        word_counts = [len(doc.content.split()) for doc in documents]
        
        # tipos de archivos
        file_types = {}
        for doc in documents:
            file_types[doc.doc_type] = file_types.get(doc.doc_type, 0) + 1
        
        # fuentes
        sources = {}
        for doc in documents:
            source = doc.file_path.split('_')[0] if '_' in doc.file_path else 'unknown'
            sources[source] = sources.get(source, 0) + 1
        
        return {
            'total_documents': len(documents),
            'avg_content_length': np.mean(lengths),
            'median_content_length': np.median(lengths),
            'avg_word_count': np.mean(word_counts),
            'file_types': file_types,
            'top_sources': dict(sorted(sources.items(), 
                                     key=lambda x: x[1], 
                                     reverse=True)[:5]),
            'length_distribution': {
                'short': len([l for l in lengths if l < 500]),
                'medium': len([l for l in lengths if 500 <= l < 2000]),
                'long': len([l for l in lengths if l >= 2000])
            }
        }
    
    def _analyze_quality_distribution(self, quality_results: List[Dict]) -> Dict[str, Any]:
        """analizo distribución de calidad"""
        if not quality_results:
            return {}
        
        classes = [r['quality_class'] for r in quality_results]
        scores = [r['quality_score'] for r in quality_results]
        
        class_names = {0: 'low', 1: 'medium', 2: 'high'}
        class_distribution = {}
        for class_id in [0, 1, 2]:
            count = classes.count(class_id)
            class_distribution[class_names[class_id]] = {
                'count': count,
                'percentage': count / len(quality_results) * 100
            }
        
        return {
            'class_distribution': class_distribution,
            'avg_quality_score': np.mean(scores),
            'median_quality_score': np.median(scores),
            'score_range': {'min': min(scores), 'max': max(scores)},
            'high_quality_percentage': class_distribution['high']['percentage']
        }
    
    def _generate_recommendations(self, quality_results: List, 
                                anomaly_results: List, 
                                stats: Dict) -> List[str]:
        """genero recomendaciones para mejorar la calidad del corpus"""
        recommendations = []
        
        if quality_results:
            high_quality_pct = len([r for r in quality_results if r['quality_class'] == 2]) / len(quality_results) * 100
            
            if high_quality_pct < 30:
                recommendations.append(
                    f"solo {high_quality_pct:.1f}% de documentos son de alta calidad. "
                    "considera agregar más documentación oficial y tutoriales completos."
                )
            
            low_quality_count = len([r for r in quality_results if r['quality_class'] == 0])
            if low_quality_count > 5:
                recommendations.append(
                    f"hay {low_quality_count} documentos de baja calidad. "
                    "revisa y mejora o elimina estos documentos."
                )
        
        if anomaly_results:
            anomaly_count = len([r for r in anomaly_results if r['is_anomaly']])
            if anomaly_count > len(anomaly_results) * 0.2:
                recommendations.append(
                    f"alto número de anomalías detectadas ({anomaly_count}). "
                    "revisa la consistencia del corpus y considera limpiar datos atípicos."
                )
        
        if stats.get('length_distribution', {}).get('short', 0) > stats.get('total_documents', 0) * 0.3:
            recommendations.append(
                "muchos documentos son demasiado cortos. "
                "considera agregar más contenido detallado o combinar documentos relacionados."
            )
        
        return recommendations

# script para generar reporte completo
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    
    from ingestion.document_loader import DocumentLoader
    
    # cargo documentos
    loader = DocumentLoader()
    docs = loader.load_documents_from_directory("data/raw/github_docs")
    
    if not docs:
        print("no hay documentos para analizar.")
        exit(1)
    
    # genero reporte
    dashboard = QualityDashboard()
    report = dashboard.generate_quality_report(docs)
    
    print("=== REPORTE DE CALIDAD DEL CORPUS ===\n")
    
    # estadísticas generales
    stats = report['corpus_stats']
    print(f" estadísticas generales:")
    print(f"   total de documentos: {stats['total_documents']}")
    print(f"   longitud promedio: {stats['avg_content_length']:.0f} caracteres")
    print(f"   palabras promedio: {stats['avg_word_count']:.0f}")
    
    # distribución de calidad
    if 'quality_distribution' in report and report['quality_distribution']:
        qual = report['quality_distribution']
        print(f"\n distribución de calidad:")
        print(f"   alta calidad: {qual['class_distribution']['high']['count']} ({qual['class_distribution']['high']['percentage']:.1f}%)")
        print(f"   calidad media: {qual['class_distribution']['medium']['count']} ({qual['class_distribution']['medium']['percentage']:.1f}%)")
        print(f"   baja calidad: {qual['class_distribution']['low']['count']} ({qual['class_distribution']['low']['percentage']:.1f}%)")
    
    # anomalías
    if 'anomaly_summary' in report and report['anomaly_summary']:
        anom = report['anomaly_summary']
        print(f"\n  anomalías detectadas:")
        print(f"   documentos anómalos: {anom['anomalies_count']} ({anom['anomaly_rate']:.1%})")
    
    # recomendaciones
    if report['recommendations']:
        print(f"\n recomendaciones:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"   {i}. {rec}")
