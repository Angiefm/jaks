import logging
import numpy as np
import joblib
from typing import List, Dict, Any, Tuple
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import pandas as pd
from pathlib import Path

from .quality_metrics import QualityMetrics

class AnomalyDetector:
    """detector de anomalías en documentos usando isolation forest"""
    
    def __init__(self, model_path: str = "data/models/anomaly_detector.joblib"):
        self.logger = logging.getLogger(__name__)
        self.model_path = Path(model_path)
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.metrics_extractor = QualityMetrics()
        self.model = None
        self.scaler = None
        self.pca = None
        self.feature_names = None
        self.is_trained = False
        
        # intento cargar modelo existente
        self._load_model()
    
    def _load_model(self):
        """cargo modelo pre-entrenado si existe"""
        try:
            if self.model_path.exists():
                saved_data = joblib.load(self.model_path)
                self.model = saved_data['model']
                self.scaler = saved_data['scaler']
                self.pca = saved_data.get('pca')
                self.feature_names = saved_data['feature_names']
                self.is_trained = True
                self.logger.info("detector de anomalías cargado exitosamente")
        except Exception as e:
            self.logger.warning(f"no se pudo cargar detector existente: {e}")
    
    def prepare_features(self, documents: List) -> np.ndarray:
        """preparo features numéricas para detección de anomalías"""
        features_list = []
        
        for doc in documents:
            features = self.metrics_extractor.extract_features(doc)
            
            # selecciono solo features numéricas relevantes
            numeric_features = {
                'content_length': features['content_length'],
                'word_count': features['word_count'],
                'paragraph_count': features['paragraph_count'],
                'has_headers': features['has_headers'],
                'has_lists': features['has_lists'],
                'code_blocks': features['code_blocks'],
                'code_inline': features['code_inline'],
                'quality_keywords': features['quality_keywords'],
                'low_quality_indicators': features['low_quality_indicators'],
                'technical_terms': features['technical_terms'],
                'external_links': features['external_links'],
                'avg_sentence_length': features['avg_sentence_length'],
                'readability_score': features['readability_score'],
                'java_keywords': features['java_keywords'],
                'spring_keywords': features['spring_keywords'],
                'source_reliability': features['source_reliability']
            }
            
            features_list.append(numeric_features)
        
        # convierto a dataframe
        df = pd.DataFrame(features_list)
        self.feature_names = df.columns.tolist()
        
        return df.values
    
    def train(self, documents: List, contamination: float = 0.1) -> Dict[str, Any]:
        """entreno el detector de anomalías"""
        self.logger.info(f"entrenando detector de anomalías con {len(documents)} documentos")
        
        if len(documents) < 10:
            raise ValueError("necesitas al menos 10 documentos para entrenar")
        
        # preparo features
        X = self.prepare_features(documents)
        
        # normalizo datos
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # reducción dimensional opcional (si hay muchas features)
        if X_scaled.shape[1] > 10:
            self.pca = PCA(n_components=min(10, X_scaled.shape[1]))
            X_scaled = self.pca.fit_transform(X_scaled)
        
        # entreno isolation forest
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        
        self.model.fit(X_scaled)
        
        # evalúo en datos de entrenamiento
        predictions = self.model.predict(X_scaled)
        anomaly_scores = self.model.decision_function(X_scaled)
        
        n_anomalies = np.sum(predictions == -1)
        anomaly_rate = n_anomalies / len(documents)
        
        self.logger.info(f"detección completada: {n_anomalies} anomalías ({anomaly_rate:.2%})")
        
        # guardo modelo
        self._save_model()
        self.is_trained = True
        
        # identifico anomalías para reporte
        anomaly_indices = np.where(predictions == -1)[0]
        anomaly_docs = [(i, documents[i].title, anomaly_scores[i]) for i in anomaly_indices]
        anomaly_docs.sort(key=lambda x: x[2])  # ordeno por score
        
        return {
            'total_documents': len(documents),
            'anomalies_detected': n_anomalies,
            'anomaly_rate': anomaly_rate,
            'contamination_used': contamination,
            'anomaly_examples': anomaly_docs[:5],  # top 5 anomalías
            'feature_count': len(self.feature_names)
        }
    
    def _save_model(self):
        """guardo modelo entrenado"""
        try:
            save_data = {
                'model': self.model,
                'scaler': self.scaler,
                'pca': self.pca,
                'feature_names': self.feature_names
            }
            joblib.dump(save_data, self.model_path)
            self.logger.info(f"detector guardado en {self.model_path}")
        except Exception as e:
            self.logger.error(f"error guardando detector: {e}")
    
    def detect_anomalies(self, documents: List) -> List[Dict[str, Any]]:
        """detecto anomalías en lista de documentos"""
        if not self.is_trained:
            self.logger.warning("detector no entrenado. entrenando automáticamente...")
            self.train(documents)
        
        # preparo features
        X = self.prepare_features(documents)
        
        # transformo datos
        X_scaled = self.scaler.transform(X)
        if self.pca:
            X_scaled = self.pca.transform(X_scaled)
        
        # detecto anomalías
        predictions = self.model.predict(X_scaled)
        scores = self.model.decision_function(X_scaled)
        
        # preparo resultados
        results = []
        for i, (doc, pred, score) in enumerate(zip(documents, predictions, scores)):
            results.append({
                'document_id': doc.id,
                'title': doc.title,
                'is_anomaly': pred == -1,
                'anomaly_score': float(score),
                'confidence': float(1 / (1 + np.exp(-abs(score)))),  # aplico sigmoid
                'file_path': doc.file_path
            })
        
        # ordeno por score (anomalías más extremas primero)
        results.sort(key=lambda x: x['anomaly_score'])
        
        return results
    
    def detect_single_document(self, document) -> Dict[str, Any]:
        """detecto si un documento es anómalo"""
        results = self.detect_anomalies([document])
        return results[0] if results else {}
    
    def get_anomaly_summary(self, documents: List) -> Dict[str, Any]:
        """obtengo resumen de anomalías detectadas"""
        results = self.detect_anomalies(documents)
        
        anomalies = [r for r in results if r['is_anomaly']]
        normal_docs = [r for r in results if not r['is_anomaly']]
        
        return {
            'total_documents': len(documents),
            'anomalies_count': len(anomalies),
            'normal_count': len(normal_docs),
            'anomaly_rate': len(anomalies) / len(documents) if documents else 0,
            'top_anomalies': anomalies[:5],
            'avg_anomaly_score': np.mean([a['anomaly_score'] for a in anomalies]) if anomalies else 0,
            'score_distribution': {
                'min': float(np.min([r['anomaly_score'] for r in results])),
                'max': float(np.max([r['anomaly_score'] for r in results])),
                'mean': float(np.mean([r['anomaly_score'] for r in results])),
                'std': float(np.std([r['anomaly_score'] for r in results]))
            }
        }

# test del detector
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    
    from ingestion.document_loader import DocumentLoader
    
    # cargo documentos
    loader = DocumentLoader()
    docs = loader.load_documents_from_directory("data/raw/github_docs")
    
    if len(docs) < 10:
        print("necesitas más documentos para entrenar el detector.")
        exit(1)
    
    # entreno y pruebo detector
    detector = AnomalyDetector()
    train_report = detector.train(docs, contamination=0.15)
    
    print("detector de anomalías entrenado:")
    print(f"  documentos analizados: {train_report['total_documents']}")
    print(f"  anomalías detectadas: {train_report['anomalies_detected']}")
    print(f"  tasa de anomalías: {train_report['anomaly_rate']:.2%}")
