from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
from pathlib import Path
import logging

# agrego src al path
sys.path.append(str(Path(__file__).parent.parent))

from search.semantic_search import SemanticSearch, SearchResult
from storage.vector_store import VectorStore
from embeddings.embedding_engine import EmbeddingEngine

# configuro logging
logging.basicConfig(level=logging.INFO)

# creo la app de fastapi
app = FastAPI(
    title="Java API Knowledge System",
    description="sistema inteligente de búsqueda de documentación java",
    version="1.0.0"
)

# configuro cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# modelos pydantic
class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 10
    min_similarity: Optional[float] = 0.1

class SearchResponse(BaseModel):
    query: str
    results: List[dict]
    total_results: int
    suggestions: List[str]

class SystemInfo(BaseModel):
    total_documents: int
    system_status: str
    embedding_model: str

# inicializo componentes globales
vector_store = None
embedding_engine = None
search_engine = None

@app.on_event("startup")
async def startup_event():
    """inicializar componentes al arrancar"""
    global vector_store, embedding_engine, search_engine
    
    try:
        # inicializo componentes
        vector_store = VectorStore()
        embedding_engine = EmbeddingEngine()
        search_engine = SemanticSearch(vector_store, embedding_engine)
        
        logging.info("API components initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing components: {e}")

@app.get("/")
async def root():
    """endpoint raíz"""
    return {"message": "Java API Knowledge System - API funcionando!"}

@app.get("/health")
async def health_check():
    """health check"""
    return {"status": "healthy", "message": "API is running"}

@app.get("/system/info", response_model=SystemInfo)
async def get_system_info():
    """información del sistema"""
    try:
        doc_count = vector_store.get_document_count()
        return SystemInfo(
            total_documents=doc_count,
            system_status="operational",
            embedding_model="all-MiniLM-L6-v1"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """búsqueda semántica de documentos"""
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # hago la búsqueda
        results = search_engine.search(
            query=request.query,
            top_k=request.top_k,
            min_similarity=request.min_similarity
        )
        
        # obtengo sugerencias
        suggestions = search_engine.get_search_suggestions(request.query)
        
        # convierto resultados a diccionarios
        results_dict = []
        for result in results:
            results_dict.append({
                "document_id": result.document_id,
                "title": result.title,
                "content_preview": result.content_preview,
                "similarity_score": result.similarity_score,
                "metadata": result.metadata,
                "file_path": result.file_path
            })
        
        return SearchResponse(
            query=request.query,
            results=results_dict,
            total_results=len(results_dict),
            suggestions=suggestions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in search: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/search")
async def search_documents_get(
    q: str = Query(..., description="Search query"),
    top_k: int = Query(10, ge=1, le=50, description="Number of results"),
    min_similarity: float = Query(0.1, ge=0.0, le=1.0, description="Minimum similarity")
):
    """búsqueda get (para testing fácil)"""
    request = SearchRequest(query=q, top_k=top_k, min_similarity=min_similarity)
    return await search_documents(request)

if __name__ == "__main__":
    import uvicorn
    # corro la app en uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)