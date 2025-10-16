import logging
import numpy as np
import joblib
from typing import List, Dict, Any, Tuple
from pathlib import Path
import hdbscan
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score

class ClusterEngine:
    """Motor de clustering para documentos"""
    
    def __init__(self, model_path: str = "data/models/cluster_model.joblib"):
        self.logger = logging.getLogger(__name__)
        self.model_path = Path(model_path)
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.model = None
        self.cluster_labels = None
        self.cluster_info = {}
        self.is_trained = False
        
        self._load_model()
    
    def _load_model(self):
        """Cargar modelo pre-entrenado"""
        try:
            if self.model_path.exists():
                saved_data = joblib.load(self.model_path)
                self.model = saved_data['model']
                self.cluster_labels = saved_data.get('labels')
                self.cluster_info = saved_data.get('cluster_info', {})
                self.is_trained = True
                self.logger.info("Modelo de clustering cargado")
        except Exception as e:
            self.logger.warning(f"No se pudo cargar modelo: {e}")
    
    def cluster_hdbscan(self, embeddings: np.ndarray, 
                       min_cluster_size: int = 3,
                       min_samples: int = 2) -> Dict[str, Any]:
        """Clustering con HDBSCAN"""
        self.logger.info(f"Clustering con HDBSCAN: {embeddings.shape[0]} documentos")
        
        # Entrenar HDBSCAN
        self.model = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            metric='euclidean',
            cluster_selection_method='eom'
        )
        
        self.cluster_labels = self.model.fit_predict(embeddings)
        
        # Analizar resultados
        n_clusters = len(set(self.cluster_labels)) - (1 if -1 in self.cluster_labels else 0)
        n_noise = list(self.cluster_labels).count(-1)
        
        self.logger.info(f"Clusters encontrados: {n_clusters}, Ruido: {n_noise}")
        
        # Calcular métricas
        metrics = self._calculate_metrics(embeddings, self.cluster_labels)
        
        # Guardar información de clusters
        self.cluster_info = self._analyze_clusters(self.cluster_labels)
        
        # Guardar modelo
        self._save_model()
        self.is_trained = True
        
        return {
            'n_clusters': n_clusters,
            'n_noise': n_noise,
            'noise_ratio': n_noise / len(self.cluster_labels),
            'metrics': metrics,
            'cluster_sizes': self.cluster_info['sizes']
        }
    
    def cluster_kmeans(self, embeddings: np.ndarray, n_clusters: int = 8) -> Dict[str, Any]:
        """Clustering con K-Means (alternativa más simple)"""
        self.logger.info(f"Clustering con K-Means: {n_clusters} clusters")
        
        self.model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.cluster_labels = self.model.fit_predict(embeddings)
        
        metrics = self._calculate_metrics(embeddings, self.cluster_labels)
        self.cluster_info = self._analyze_clusters(self.cluster_labels)
        
        self._save_model()
        self.is_trained = True
        
        return {
            'n_clusters': n_clusters,
            'metrics': metrics,
            'cluster_sizes': self.cluster_info['sizes']
        }
    
    def _calculate_metrics(self, embeddings: np.ndarray, labels: np.ndarray) -> Dict[str, float]:
        """Calcular métricas de calidad del clustering"""
        try:
            # Filtrar ruido para métricas
            mask = labels != -1
            if mask.sum() < 2:
                return {'silhouette': 0, 'calinski_harabasz': 0}
            
            filtered_embeddings = embeddings[mask]
            filtered_labels = labels[mask]
            
            silhouette = silhouette_score(filtered_embeddings, filtered_labels)
            calinski = calinski_harabasz_score(filtered_embeddings, filtered_labels)
            
            return {
                'silhouette': float(silhouette),
                'calinski_harabasz': float(calinski)
            }
        except Exception as e:
            self.logger.error(f"Error calculando métricas: {e}")
            return {'silhouette': 0, 'calinski_harabasz': 0}
    
    def _analyze_clusters(self, labels: np.ndarray) -> Dict[str, Any]:
        """Analizar composición de clusters"""
        unique_labels = set(labels)
        
        cluster_sizes = {}
        for label in unique_labels:
            size = list(labels).count(label)
            cluster_sizes[int(label)] = size
        
        return {
            'sizes': cluster_sizes,
            'n_clusters': len(unique_labels) - (1 if -1 in unique_labels else 0),
            'total_points': len(labels)
        }
    
    def _save_model(self):
        """Guardar modelo"""
        try:
            save_data = {
                'model': self.model,
                'labels': self.cluster_labels,
                'cluster_info': self.cluster_info
            }
            joblib.dump(save_data, self.model_path)
            self.logger.info(f"Modelo guardado en {self.model_path}")
        except Exception as e:
            self.logger.error(f"Error guardando modelo: {e}")
    
    def get_cluster_label(self, embedding: np.ndarray) -> int:
        """Obtener cluster para un nuevo embedding"""
        if not self.is_trained:
            return -1
        
        if isinstance(self.model, hdbscan.HDBSCAN):
            # HDBSCAN no tiene predict directo, usar aproximación
            return self.model.labels_[0]  # Simplificación
        else:
            return int(self.model.predict(embedding.reshape(1, -1))[0])
    
    def get_cluster_summary(self) -> Dict[str, Any]:
        """Obtener resumen de clusters"""
        if not self.is_trained:
            return {}
        
        return {
            'total_clusters': self.cluster_info['n_clusters'],
            'cluster_sizes': self.cluster_info['sizes'],
            'largest_cluster': max(self.cluster_info['sizes'].values()),
            'smallest_cluster': min([s for s in self.cluster_info['sizes'].values() if s > 0])
        }