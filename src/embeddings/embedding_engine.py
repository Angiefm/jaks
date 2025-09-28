import os
import logging
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import torch

from ingestion.document_loader import Document

class EmbeddingEngine:
    """motor de embeddings usando sentence-transformers"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v1", device: str = "cpu"):
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.device = device
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """acá cargo el modelo de sentence-transformers"""
        try:
            self.logger.info(f"cargando modelo de embeddings: {self.model_name}")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            self.logger.info("modelo cargado exitosamente")
        except Exception as e:
            self.logger.error(f"error cargando modelo: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """acá obtengo la dimensión de los embeddings"""
        return self.model.get_sentence_embedding_dimension()
    
    def encode_text(self, text: str) -> np.ndarray:
        """acá genero embedding para un texto"""
        if not text or not text.strip():
            # si el texto está vacío retorno un embedding de ceros
            return np.zeros(self.get_embedding_dimension())
        
        try:
            # acá limpio el texto y lo limito a 5000 caracteres
            text = text.strip()[:5000]
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            self.logger.error(f"error generando embedding: {e}")
            return np.zeros(self.get_embedding_dimension())
    
    def encode_documents(self, documents: List[Document], batch_size: int = 16) -> Dict[str, np.ndarray]:
        """acá genero embeddings para múltiples documentos"""
        embeddings = {}
        
        # acá preparo ids y textos
        doc_ids = []
        texts = []
        
        for doc in documents:
            if doc.content and doc.content.strip():
                doc_ids.append(doc.id)
                # uso título + contenido para dar más contexto
                full_text = f"{doc.title}\n\n{doc.content}"
                texts.append(full_text.strip()[:5000])
        
        if not texts:
            self.logger.warning("no encontré textos válidos para codificar")
            return embeddings
        
        try:
            self.logger.info(f"codificando {len(texts)} documentos en lotes de {batch_size}")
            
            # acá proceso en lotes
            all_embeddings = []
            for i in tqdm(range(0, len(texts), batch_size), desc="codificando lotes"):
                batch_texts = texts[i:i + batch_size]
                batch_embeddings = self.model.encode(
                    batch_texts, 
                    convert_to_numpy=True,
                    show_progress_bar=False
                )
                all_embeddings.extend(batch_embeddings)
            
            # acá mapeo embeddings con sus ids
            for doc_id, embedding in zip(doc_ids, all_embeddings):
                embeddings[doc_id] = embedding
            
            self.logger.info(f"codifiqué exitosamente {len(embeddings)} documentos")
            
        except Exception as e:
            self.logger.error(f"error en la codificación por lotes: {e}")
            # si falla hago un fallback a codificación individual
            for doc in tqdm(documents, desc="codificando individualmente"):
                embeddings[doc.id] = self.encode_text(f"{doc.title}\n\n{doc.content}")
        
        return embeddings
    
    def encode_query(self, query: str) -> np.ndarray:
        """acá genero embedding para una consulta"""
        return self.encode_text(query)

# acá hago un test básico
if __name__ == "__main__":
    # acá configuro logging
    logging.basicConfig(level=logging.INFO)
    
    # test del motor de embeddings
    engine = EmbeddingEngine()
    print(f"dimensión del embedding: {engine.get_embedding_dimension()}")
    
    # test con texto simple
    test_text = "spring boot es un framework para java"
    embedding = engine.encode_text(test_text)
    print(f"forma del embedding generado: {embedding.shape}")
    print("embeddingengine funciona correctamente!")
