import logging
from typing import List, Dict, Any, Optional
import numpy as np
from dataclasses import dataclass

@dataclass
class SearchResult:
    """resultado de búsqueda estructurado"""
    document_id: str
    title: str
    content_preview: str
    similarity_score: float
    metadata: Dict[str, Any]
    file_path: str

class SemanticSearch:
    """motor de búsqueda semántica mejorado"""
    
    def __init__(self, vector_store, embedding_engine):
        self.vector_store = vector_store
        self.embedding_engine = embedding_engine
        self.logger = logging.getLogger(__name__)
    
    def search(self, query: str, top_k: int = 10, min_similarity: float = 0.1) -> List[SearchResult]:
        """búsqueda semántica con filtrado"""
        try:
            # genero el embedding del query
            query_embedding = self.embedding_engine.encode_query(query)
            
            # busco en el vector store
            raw_results = self.vector_store.search_similar(query_embedding, top_k=top_k)
            
            # filtro y estructuro los resultados
            search_results = []
            for result in raw_results:
                if result['similarity'] >= min_similarity:
                    search_result = SearchResult(
                        document_id=result['id'],
                        title=result['metadata'].get('title', 'Unknown'),
                        content_preview=self._create_preview(result['content_preview']),
                        similarity_score=round(result['similarity'], 3),
                        metadata=result['metadata'],
                        file_path=result['metadata'].get('file_path', '')
                    )
                    search_results.append(search_result)
            
            self.logger.info(f"Found {len(search_results)} results for query: '{query}'")
            return search_results
            
        except Exception as e:
            self.logger.error(f"Error in semantic search: {e}")
            return []
    
    def _create_preview(self, content: str, max_length: int = 200) -> str:
        """crear preview del contenido"""
        if len(content) <= max_length:
            return content
        return content[:max_length].rsplit(' ', 1)[0] + "..."
    
    def get_search_suggestions(self, query: str) -> List[str]:
        """generar sugerencias de búsqueda"""
        # esta es una implementación simple, luego puedo mejorarla
        base_suggestions = [
            "Spring Boot REST API",
            "Java annotations",
            "microservices architecture",
            "Spring Boot configuration",
            "HTTP request mapping"
        ]
        
        # filtro las sugerencias por relevancia básica
        relevant = [s for s in base_suggestions if any(word.lower() in s.lower() for word in query.split())]
        return relevant[:3] if relevant else base_suggestions[:3]