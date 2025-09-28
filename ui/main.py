import streamlit as st
import sys
from pathlib import Path
import requests
import json

# configuro la página

st.set_page_config(
    page_title="java API knowledge system",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# agrego src al path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from search.semantic_search import SemanticSearch
from storage.vector_store import VectorStore
from embeddings.embedding_engine import EmbeddingEngine

# CSS personalizado

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #e396e8;
        text-align: center;
        margin-bottom: 2rem;
    }
            
    .seearch-box {
        font-size: 1.1rem;
    }
    .result-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        backgroud-color: #fee5f6;
    }
    .similarity-score {
        color: #e154db;
        font-weight: bold;
    }
    .doc-title {
        color: #1f5f7a;
        font-size: 1.2rem;
        font-weight: bold
    }
            
            .stButton > button {
    background-color: #d739fc;  /* color de fondo */
    color: white;              /* color del texto */
    border-radius: 8px;        /* bordes redondeados */
    border: none;              /* sin borde */
    padding: 0.6rem 1.2rem;    /* espacio interno */
    font-size: 1rem;
    font-weight: bold;
    cursor: pointer;
    }
    
    /* color al pasar el mouse */
    .stButton > button:hover {
        background-color: #e66fff;
    }
            
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_components():
    """inicializar componentes con chache"""
    try:
        vector_store = VectorStore()
        embedding_engine = EmbeddingEngine()
        search_engine = SemanticSearch(vector_store, embedding_engine)
        return vector_store, embedding_engine, search_engine
    except Exception as e:
        st.error(f"error inicializando componentes: {e}")
        return None,None, None
    
def main():
    # header principal
    st.markdown('<h1 class="main-header"> ☕ java API knowledge system </h1>', unsafe_allow_html=True)
    st.markdown("***sistema inteligente de busqueda de documentación Java***")

    # inicializar componentes
    vector_store, embedding_engine, search_engine = initialize_components()

    if not all([vector_store, embedding_engine, search_engine]):
        st.error("error al inicializar el sistema, verifia la configuración")
        return
    
    # sidebar con info del sistema
    st.sidebar.header("info del sistema")
    doc_count = vector_store.get_document_count()
    st.sidebar.metric("documentos cargados", doc_count)
    st.sidebar.metric("modelo de embeddings", "all-MiniLM-L6-v1")

    if doc_count == 0:
        st.warning("no hay documentos cargados, ejecuta primero el pipeline de ingesta")
        st.code("python scripts/ingest_documents.py data/raw/test")
        return
    
    # config de busqueda en sidebar
    st.sidebar.header("config")
    top_k = st.sidebar.slider("numero de resultados", 1, 20, 10)
    min_similarity = st.sidebar.slider("Similaridad mínima", 0.0, 1.0, 0.1, 0.05)
    
    # area principal de búsqueda
    st.header("busqueda semántica")
    
    # Ejemplos de consultas
    st.subheader("consultas de ejemplo:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("spring Boot annotations"):
            st.session_state.search_query = "Spring Boot annotations"
    
    with col2:
        if st.button("REST API development"):
            st.session_state.search_query = "REST API development"
    
    with col3:
        if st.button("spring configuration"):
            st.session_state.search_query = "Spring configuration"
    
    # Caja de búsqueda
    search_query = st.text_input(
        "escribe tu consulta:",
        value=st.session_state.get('search_query', ''),
        placeholder="Ejemplo: How to create REST controllers in Spring Boot?",
        key="search_input"
    )
    
    # boton de búsqueda
    if st.button("buscar", type="primary") or search_query:
        if search_query.strip():
            with st.spinner("buscando documentos relevantes..."):
                try:
                    # Realizar búsqueda
                    results = search_engine.search(
                        query=search_query,
                        top_k=top_k,
                        min_similarity=min_similarity
                    )
                    
                    # Mostrar resultados
                    st.header(f"resultados para: '{search_query}'")
                    
                    if results:
                        st.success(f"se encontraron {len(results)} documentos relevantes")
                        
                        for i, result in enumerate(results, 1):
                            with st.container():
                                # card de resultado
                                st.markdown(f"""
                                <div class="result-card">
                                    <div class="doc-title">{i}. {result.title}</div>
                                    <div class="similarity-score">Similaridad: {result.similarity_score:.3f}</div>
                                    <p><strong>Preview:</strong> {result.content_preview}</p>
                                    <small><strong>Archivo:</strong> {result.file_path}</small>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # aqui expandir para ver mas detalles
                                with st.expander(f"Ver detalles de {result.title}"):
                                    st.json(result.metadata)
                    else:
                        st.warning("no se encontraron documentos con la similaridad minima especificada")
                        st.info("intenta reducir la similaridad minima o usar terminos más generales")
                        
                except Exception as e:
                    st.error(f"error en la búsqueda: {e}")
        else:
            st.warning("por favor, escribe una consulta para buscar")
    
    # footer con estadisticas
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("total de Documentos", doc_count)
    
    with col2:
        st.metric("dimensiones de Embeddings", "384")
    
    with col3:
        st.metric("base de Datos", "ChromaDB")

if __name__ == "__main__":
    main()

