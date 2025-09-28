import logging
import joblib
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pandas as pd
from pathlib import Path

from .quality_metrics import QualityMetrics

class QualityClassifier:
    """clasificador de calidad de documentos usando random forest"""
    
    def __init__(self, model_path: str = "data/models/quality_classifier.joblib"):
        self.logger = logging.getLogger(__name__)
        self.model_path = Path(model_path)
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.metrics_extractor = QualityMetrics()
        self.model = None
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
                self.feature_names = saved_data['feature_names']
                self.is_trained = True
                self.logger.info("modelo de calidad cargado exitosamente")
        except Exception as e:
            self.logger.warning(f"no se pudo cargar modelo existente: {e}")
    
    def prepare_training_data(self, documents: List) -> Tuple[np.ndarray, np.ndarray]:
        """preparo datos de entrenamiento con etiquetas automáticas"""
        features_list = []
        labels = []
        
        self.logger.info(f"preparando datos de entrenamiento para {len(documents)} documentos")
        
        for doc in documents:
            # extraigo features
            features = self.metrics_extractor.extract_features(doc)
            features_list.append(features)
            
            # creo etiquetas automáticas basadas en heurísticas
            label = self._create_automatic_label(features, doc)
            labels.append(label)
        
        # convierto a dataframe para manejo más fácil
        df = pd.DataFrame(features_list)

# me quedo solo con columnas numéricas
        df = df.select_dtypes(include=[np.number])

# guardo nombres de features
        self.feature_names = df.columns.tolist()

# convierto a arrays numpy
        X = df.values.astype(float)

        y = np.array(labels)
        
        self.logger.info(f"dataset creado: {X.shape[0]} muestras, {X.shape[1]} features")
        self.logger.info(f"distribución de clases: {np.bincount(y)}")
        
        return X, y
    
    def _create_automatic_label(self, features: Dict[str, Any], doc) -> int:
        """creo etiquetas automáticas basadas en heurísticas"""
        score = 0
        
        # criterios para alta calidad (clase 2)
        if (features['content_length'] > 1000 and 
            features['code_blocks'] > 0 and 
            features['quality_keywords'] > 2 and
            features['source_reliability'] > 0.7):
            score += 3
        
        # criterios para calidad media (clase 1)  
        if (features['content_length'] > 300 and
            features['technical_terms'] > 5 and
            features['readability_score'] > 40):
            score += 2
        
        # criterios para baja calidad (clase 0)
        if (features['low_quality_indicators'] > 2 or
            features['content_length'] < 100 or
            features['readability_score'] < 20):
            score -= 2
        
        # ajustes basados en fuente
        if 'spring_projects' in doc.file_path.lower():
            score += 2
        elif 'tutorial' in doc.file_path.lower():
            score += 1
        
        # convierto score a clase
        if score >= 4:
            return 2  # alta calidad
        elif score >= 1:
            return 1  # calidad media
        else:
            return 0  # baja calidad
    
    def train(self, documents: List, test_size: float = 0.2) -> Dict[str, Any]:
        """entreno el clasificador"""
        self.logger.info("iniciando entrenamiento del clasificador de calidad")
        
        # preparo datos
        X, y = self.prepare_training_data(documents)
        
        if len(X) < 10:
            raise ValueError("necesitas al menos 10 documentos para entrenar")
        
        # verificar si alguna clase tiene muy pocos ejemplos
        class_counts = np.bincount(y)
        if len(class_counts) > 2 and class_counts[2] < 2:
            self.logger.warning("Muy pocos documentos de clase 2 (alta calidad). Se fusionarán con clase 1.")
            y = np.where(y == 2, 1, y)
        
        # divido en train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )

        # creo y entreno modelo
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            class_weight='balanced'  # manejo desbalance
        )
        
        self.model.fit(X_train, y_train)
        
        # evalúo modelo
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        self.logger.info(f"accuracy en test: {accuracy:.3f}")
        
        # guardo modelo
        self._save_model()
        self.is_trained = True
        
        # reporte detallado
        report = {
            'accuracy': accuracy,
            'classification_report': classification_report(y_test, y_pred),
            'feature_importance': dict(zip(
                self.feature_names, 
                self.model.feature_importances_
            )),
            'training_samples': len(X_train),
            'test_samples': len(X_test)
        }
        
        return report
    
    def _save_model(self):
        """guardo modelo entrenado"""
        try:
            save_data = {
                'model': self.model,
                'feature_names': self.feature_names
            }
            joblib.dump(save_data, self.model_path)
            self.logger.info(f"modelo guardado en {self.model_path}")
        except Exception as e:
            self.logger.error(f"error guardando modelo: {e}")
    
    def predict_quality(self, document) -> Dict[str, Any]:
        """predigo calidad de un documento"""
        if not self.is_trained:
            return {'quality_class': 1, 'confidence': 0.5, 'quality_score': 50}
        
        # extraigo features
        features = self.metrics_extractor.extract_features(document)
        
        # convierto a array
        feature_array = np.array([[features[name] for name in self.feature_names]])
        
        # predigo
        prediction = self.model.predict(feature_array)[0]
        probabilities = self.model.predict_proba(feature_array)[0]
        
        # calculo score numérico también
        quality_score = self.metrics_extractor.calculate_quality_score(features)
        
        return {
            'quality_class': int(prediction),
            'confidence': float(np.max(probabilities)),
            'quality_score': float(quality_score),
            'class_probabilities': {
                'low': float(probabilities[0]),
                'medium': float(probabilities[1]),  
                'high': float(probabilities[2]) if len(probabilities) > 2 else 0.0
            }
        }
    
    def get_feature_importance(self) -> Dict[str, float]:
        """obtengo importancia de features"""
        if not self.is_trained:
            return {}
        
        return dict(zip(self.feature_names, self.model.feature_importances_))

# script de entrenamiento
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    
    from storage.vector_store import VectorStore
    from ingestion.document_loader import DocumentLoader
    
    # cargo documentos existentes
    loader = DocumentLoader()
    docs = loader.load_documents_from_directory("data/raw/github_docs")
    
    if len(docs) < 10:
        print("necesitas más documentos para entrenar. descarga más primero.")
        exit(1)
    
    # entreno clasificador
    classifier = QualityClassifier()
    report = classifier.train(docs)
    
    print("entrenamiento completado:")
    print(f"accuracy: {report['accuracy']:.3f}")
    print("\ntop 5 features más importantes:")
    importance = sorted(report['feature_importance'].items(), 
                       key=lambda x: x[1], reverse=True)[:5]
    for feature, score in importance:
        print(f"  {feature}: {score:.3f}")
