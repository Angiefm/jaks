import os
import logging
from typing import List, Dict, Any, Tuple, Optional
import chromadb
from chromadb.config import Settings
import numpy as np
from pathlib import Path

from ingestion.document_loader import Document

class VectorStore:
    """almacenamiento vectorial usando chromadb"""
    
    def __init__(self, db_path: str = "./data/vectordb"):
        self.logger = logging.getLogger(__name__)
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # acá inicializo chromadb
        self.client = None
        self.collection = None
        self._initialize_db()
    
    def _initialize_db(self):
        """acá inicializo la conexión a chromadb"""
        try:
            self.client = chromadb.PersistentClient(path=str(self.db_path))
            
            # acá creo o reutilizo la colección
            collection_name = "java_api_docs"
            try:
                self.collection = self.client.create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"}  # acá uso similaridad coseno
                )
                self.logger.info(f"creé nueva colección: {collection_name}")
            except Exception:
                # si ya existe la colección, la reutilizo
                self.collection = self.client.get_collection(collection_name)
                self.logger.info(f"uso colección existente: {collection_name}")
                
        except Exception as e:
            self.logger.error(f"error inicializando chromadb: {e}")
            raise
    
    def add_documents(self, documents: List[Document], embeddings: Dict[str, np.ndarray]):
        """acá agrego documentos y sus embeddings"""
        if not documents or not embeddings:
            self.logger.warning("no hay documentos o embeddings para agregar")
            return
        
        try:
            # acá preparo los datos para chromadb
            ids = []
            embeddings_list = []
            metadatas = []
            documents_list = []
            
            for doc in documents:
                if doc.id in embeddings:
                    ids.append(doc.id)
                    embeddings_list.append(embeddings[doc.id].tolist())
                    
                    # metadatos básicos
                    metadata = {
                        "title": doc.title,
                        "file_path": doc.file_path,
                        "doc_type": doc.doc_type,
                        "content_length": len(doc.content)
                    }
                    metadatas.append(metadata)
                    
                    # acá recorto el contenido para guardarlo en chromadb
                    content = doc.content[:1000] + "..." if len(doc.content) > 1000 else doc.content
                    documents_list.append(content)
            
            # acá agrego a chromadb
            self.collection.add(
                ids=ids,
                embeddings=embeddings_list,
                metadatas=metadatas,
                documents=documents_list
            )
            
            self.logger.info(f"agregué {len(ids)} documentos al vector store")
            
        except Exception as e:
            self.logger.error(f"error agregando documentos: {e}")
            raise
    
    def search_similar(self, query_embedding: np.ndarray, top_k: int = 10) -> List[Dict[str, Any]]:
        """acá busco documentos similares"""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k
            )
            
            # acá formateo los resultados
            similar_docs = []
            
            if results and 'ids' in results and results['ids']:
                ids = results['ids'][0]
                distances = results['distances'][0]
                metadatas = results['metadatas'][0]
                documents = results['documents'][0]
                
                for i in range(len(ids)):
                    similar_docs.append({
                        'id': ids[i],
                        'similarity': 1 - distances[i],  # acá convierto distancia a similaridad
                        'metadata': metadatas[i],
                        'content_preview': documents[i]
                    })
            
            return similar_docs
            
        except Exception as e:
            self.logger.error(f"error buscando documentos similares: {e}")
            return []
    
    def get_document_count(self) -> int:
        """acá obtengo el número de documentos almacenados"""
        try:
            count = self.collection.count()
            return count
        except Exception as e:
            self.logger.error(f"error obteniendo número de documentos: {e}")
            return 0
    
    def delete_all_documents(self):
        """acá elimino todos los documentos (para testing)"""
        try:
            # acá obtengo todos los ids y los borro
            results = self.collection.get()
            if results and 'ids' in results:
                self.collection.delete(ids=results['ids'])
                self.logger.info("eliminé todos los documentos del vector store")
        except Exception as e:
            self.logger.error(f"error eliminando documentos: {e}")
    
    def get_collection_info(self) -> Dict[str, Any]:
        """acá obtengo información de la colección"""
        try:
            count = self.get_document_count()
            return {
                "name": self.collection.name,
                "document_count": count,
                "db_path": str(self.db_path)
            }
        except Exception as e:
            self.logger.error(f"error obteniendo info de la colección: {e}")
            return {}

# acá hago un test básico
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # test del vector store
    store = VectorStore()
    info = store.get_collection_info()
    print(f"info del vector store: {info}")
    print("vectorstore funciona correctamente")