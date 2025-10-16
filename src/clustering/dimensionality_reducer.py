import logging
import numpy as np
import joblib
from typing import Tuple, Dict, Any
from pathlib import Path
import umap
from sklearn.decomposition import PCA

class DimensionalityReducer:
    """Reductor de dimensionalidad para visualización"""
    
    def __init__(self, model_path: str = "data/models/dim_reducer.joblib"):
        self.logger = logging.getLogger(__name__)
        self.model_path = Path(model_path)
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.umap_2d = None
        self.umap_3d = None
        self.pca = None
        self.is_trained = False
        
        self._load_model()
    
    def _load_model(self):
        """Cargar modelo pre-entrenado"""
        try:
            if self.model_path.exists():
                saved_data = joblib.load(self.model_path)
                self.umap_2d = saved_data.get('umap_2d')
                self.umap_3d = saved_data.get('umap_3d')
                self.pca = saved_data.get('pca')
                self.is_trained = True
                self.logger.info("Reductor dimensional cargado")
        except Exception as e:
            self.logger.warning(f"No se pudo cargar reductor: {e}")
    
    def fit_transform_2d(self, embeddings: np.ndarray) -> np.ndarray:
        """Reducir a 2D con UMAP"""
        self.logger.info(f"Reduciendo {embeddings.shape} a 2D con UMAP")
        
        self.umap_2d = umap.UMAP(
            n_components=2,
            n_neighbors=15,
            min_dist=0.1,
            metric='cosine',
            random_state=42
        )
        
        embeddings_2d = self.umap_2d.fit_transform(embeddings)
        self.is_trained = True
        self._save_model()
        
        return embeddings_2d
    
    def fit_transform_3d(self, embeddings: np.ndarray) -> np.ndarray:
        """Reducir a 3D con UMAP"""
        self.logger.info(f"Reduciendo {embeddings.shape} a 3D con UMAP")
        
        self.umap_3d = umap.UMAP(
            n_components=3,
            n_neighbors=15,
            min_dist=0.1,
            metric='cosine',
            random_state=42
        )
        
        embeddings_3d = self.umap_3d.fit_transform(embeddings)
        self._save_model()
        
        return embeddings_3d
    
    def fit_pca(self, embeddings: np.ndarray, n_components: int = 50) -> np.ndarray:
        """Reducir dimensionalidad con PCA (pre-procesamiento)"""
        self.logger.info(f"Aplicando PCA: {embeddings.shape[1]} -> {n_components}")
        
        self.pca = PCA(n_components=n_components, random_state=42)
        embeddings_pca = self.pca.fit_transform(embeddings)
        
        variance_explained = self.pca.explained_variance_ratio_.sum()
        self.logger.info(f"Varianza explicada: {variance_explained:.2%}")
        
        return embeddings_pca
    
    def _save_model(self):
        """Guardar modelos"""
        try:
            save_data = {
                'umap_2d': self.umap_2d,
                'umap_3d': self.umap_3d,
                'pca': self.pca
            }
            joblib.dump(save_data, self.model_path)
            self.logger.info("Reductor guardado")
        except Exception as e:
            self.logger.error(f"Error guardando reductor: {e}")