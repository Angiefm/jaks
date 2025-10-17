import streamlit as st  
import sys  
from pathlib import Path  
import os  
from dotenv import load_dotenv
import random

load_dotenv()
  
st.set_page_config(  
    page_title="java API knowledge system",  
    page_icon="☕",  
    layout="wide",  
    initial_sidebar_state="expanded"  
)  
  
sys.path.append(str(Path(__file__).parent.parent / "src"))  
  
from search.semantic_search import SemanticSearch  
from storage.vector_store import VectorStore  
from embeddings.embedding_engine import EmbeddingEngine  
from chat.rag_engine import RAGEngine  
  
st.markdown("""  
<style>
    .stApp {
        background-color: #f3e8ff;
    }
    
    [data-testid="stSidebar"] {
        background-color: #1a1a1a;
    }
    
    [data-testid="stSidebar"] * {
        color: #e5e5e5 !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] .css-10trblm,
    [data-testid="stSidebar"] .css-16idsys {
        color: #fbbf24 !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: #c4b5fd !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: bold !important;
    }
    
    .main-header {  
        font-size: 2.5rem;  
        color: #7c3aed;
        text-align: center;  
        margin-bottom: 2rem;
        text-shadow: 0 0 20px rgba(124, 58, 237, 0.2);
        font-weight: bold;
    }
    
    .subtitle {
        color: #a78bfa;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    .stButton > button {  
        background: linear-gradient(135deg, #a7f3d0, #6ee7b7);
        color: #064e3b;
        border-radius: 12px;  
        border: none;  
        padding: 0.6rem 1.2rem;  
        font-size: 1rem;  
        font-weight: bold;  
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(167, 243, 208, 0.2);
    }
    
    .stButton > button:hover {  
        background: linear-gradient(135deg, #6ee7b7, #34d399);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(167, 243, 208, 0.3);
    }
    
    .stChatInput {
        background-color: #f3e8ff !important;
    }
    
    .stChatInput > div {
        background: linear-gradient(135deg, #fae8ff, #f3e8ff) !important;
        border-radius: 20px !important;
        border: 2px solid #e9d5ff !important;
        box-shadow: 0 4px 20px rgba(233, 213, 255, 0.3) !important;
    }
    
    .stChatInput > div > div {
        background: transparent !important;
    }
    
    .stChatInput > div > div > input {
        background: transparent !important;
        color: #6b21a8 !important;
        border: none !important;
        border-radius: 20px !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
    
    .stChatInput > div > div > input::placeholder {
        color: #a78bfa !important;
        opacity: 0.7 !important;
    }
    
    .stChatInput textarea {
        background: linear-gradient(135deg, #fae8ff, #f3e8ff) !important;
        color: #6b21a8 !important;
        border: 2px solid #e9d5ff !important;
        border-radius: 20px !important;
    }
    
    .stChatMessage[data-testid*="user"] {
        background: linear-gradient(135deg, #ede9fe, #e9d5ff) !important;
        border-radius: 16px !important;
        border: 2px solid #a78bfa !important;
        margin-bottom: 1rem !important;
        padding: 1rem !important;
        box-shadow: 0 4px 15px rgba(167, 139, 250, 0.2) !important;
    }
    
    .stChatMessage[data-testid*="assistant"] {
        background: linear-gradient(135deg, #fef3c7, #fde68a) !important;
        border-radius: 16px !important;
        border: 2px solid #fcd34d !important;
        margin-bottom: 1rem !important;
        padding: 1rem !important;
        box-shadow: 0 4px 15px rgba(252, 211, 77, 0.2) !important;
    }
    
    .stChatMessage {
        border-radius: 16px !important;
        margin-bottom: 1rem !important;
        padding: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stChatMessage:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(167, 139, 250, 0.3) !important;
    }
    
    .stChatMessage[data-testid*="user"] [data-testid="chatAvatarIcon"] {
        background: linear-gradient(135deg, #a78bfa, #c4b5fd) !important;
        border-radius: 50% !important;
        padding: 0.5rem !important;
        box-shadow: 0 0 15px rgba(167, 139, 250, 0.5) !important;
    }
    
    .stChatMessage[data-testid*="assistant"] [data-testid="chatAvatarIcon"] {
        background: linear-gradient(135deg, #fde047, #fbbf24) !important;
        border-radius: 50% !important;
        padding: 0.5rem !important;
        box-shadow: 0 0 15px rgba(251, 191, 36, 0.5) !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #fbbf24;
        font-weight: bold;
    }
    
    [data-testid="stMetricLabel"] {
        color: #c4b5fd !important;
    }
    
    .stMarkdown, p, div, span, label, h1, h2, h3, h4, h5, h6 {
        color: #1f2937 !important;
    }
    
    .stChatMessage[data-testid*="user"] p, 
    .stChatMessage[data-testid*="user"] div, 
    .stChatMessage[data-testid*="user"] span {
        color: #1f2937 !important;
    }
    
    .stChatMessage[data-testid*="assistant"] p, 
    .stChatMessage[data-testid*="assistant"] div, 
    .stChatMessage[data-testid*="assistant"] span {
        color: #1f2937 !important;
    }
    
    .css-10trblm, .css-16idsys, [data-testid="stSidebarNav"] {
        color: #fbbf24 !important;
    }
    
    .stTextInput label, .stChatInput label {
        color: #7c3aed !important;
        font-weight: 600 !important;
    }
    
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #c4b5fd, #fbb6ce) !important;
    }
    
    [data-testid="stSidebar"] .stSlider label {
        color: #e5e5e5 !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stSidebar"] .stSlider [data-testid="stTickBarMin"],
    [data-testid="stSidebar"] .stSlider [data-testid="stTickBarMax"],
    [data-testid="stSidebar"] .stSlider div {
        color: #e5e5e5 !important;
    }
    
    [data-testid="stSidebar"] .stTextInput input {
        background-color: #2a2a2a !important;
        color: #e5e5e5 !important;
        border: 2px solid #c4b5fd !important;
        border-radius: 12px !important;
        padding: 0.6rem !important;
        font-size: 0.95rem !important;
    }
    
    [data-testid="stSidebar"] .stTextInput input::placeholder {
        color: #8b8b8b !important;
    }
    
    [data-testid="stSidebar"] .stTextInput input:focus {
        border-color: #a78bfa !important;
        box-shadow: 0 0 10px rgba(196, 181, 253, 0.3) !important;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background-color: #2a2a2a !important;
        color: #e5e5e5 !important;
        border-radius: 8px !important;
        border: 1px solid #3a3a3a !important;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        background-color: #333333 !important;
        border-color: #c4b5fd !important;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderContent {
        background-color: #252525 !important;
        border-radius: 0 0 8px 8px !important;
        color: #e5e5e5 !important;
    }
    
    [data-testid="stSidebar"] .stSuccess {
        background-color: #1a2e1a !important;
        color: #a7f3d0 !important;
    }
    
    [data-testid="stSidebar"] .stInfo {
        background-color: #1a1f2e !important;
        color: #c4b5fd !important;
    }
    
    [data-testid="stSidebar"] .stError {
        background-color: #2e1a1a !important;
        color: #fbb6ce !important;
    }
    
    [data-testid="stSidebar"] .stSpinner > div {
        border-top-color: #c4b5fd !important;
    }
    
    [data-testid="stSidebar"] .stTextInput [data-testid="stTooltipIcon"] {
        color: #c4b5fd !important;
    }
    
    .stAlert {
        background-color: #1a1a1a !important;
        border-radius: 12px !important;
        color: #e5e5e5 !important;
    }
    
    .stWarning {
        background-color: #2d1f0a !important;
        border-left: 4px solid #fbbf24 !important;
    }
    
    .stError {
        background-color: #2d0a0a !important;
        border-left: 4px solid #fbb6ce !important;
    }
    
    .stSuccess {
        background-color: #0a2d1a !important;
        border-left: 4px solid #a7f3d0 !important;
    }
    
    .stSpinner > div {
        border-top-color: #c4b5fd !important;
    }
    
    .stCodeBlock {
        background-color: #1a1a1a !important;
        border: 1px solid #c4b5fd !important;
        border-radius: 8px !important;
    }
    
    code {
        color: #a7f3d0 !important;
    }
    
    hr {
        border-color: #2a2a2a !important;
    }
    
    strong, b {
        color: #fbbf24 !important;
    }
    
    a {
        color: #7c3aed !important;
        text-decoration: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    a:hover {
        color: #a78bfa !important;
        text-shadow: 0 0 10px rgba(124, 58, 237, 0.3) !important;
    }
    
    li {
        color: #1f2937 !important;
    }
    
    li a {
        color: #7c3aed !important;
    }
    
    li a:hover {
        color: #a78bfa !important;
    }
    
    ol li::marker {
        color: #7c3aed !important;
        font-weight: bold !important;
    }
    
    ul li::marker {
        color: #fbbf24 !important;
    }
    
    .stChatMessage strong {
        color: #7c3aed !important;
        font-weight: 700 !important;
    }
    
    .stChatMessage p:has(strong:contains("Fuentes")) {
        color: #7c3aed !important;
    }
</style>  
""", unsafe_allow_html=True)  
  
@st.cache_resource  
def initialize_components():  
    """inicializo componentes con cache"""  
    try:  
        vector_store = VectorStore()  
        embedding_engine = EmbeddingEngine()  
        search_engine = SemanticSearch(vector_store, embedding_engine)  
          
        rag_engine = RAGEngine(search_engine, api_key=os.getenv("GEMINI_API_KEY"))  
          
        return vector_store, embedding_engine, search_engine, rag_engine  
    except Exception as e:  
        st.error(f"error inicializando componentes: {e}")  
        return None, None, None, None

CUTE_EMOJIS = ["🦄", "🌸", "🎀", "🌙", "💝", "🧸", "🍓", "🦋"]

def get_user_emoji():
    """obtengo un emoji aleatorio cute para el usuario"""
    return random.choice(CUTE_EMOJIS)
  
def main():  
    st.markdown('<h1 class="main-header">☕ java API knowledge system - Chat</h1>', unsafe_allow_html=True)  
    st.markdown('<p class="subtitle">sistema inteligente de búsqueda de documentación Java</p>', unsafe_allow_html=True)  
  
    vector_store, embedding_engine, search_engine, rag_engine = initialize_components()  
  
    if not all([vector_store, embedding_engine, search_engine, rag_engine]):  
        st.error("error al inicializar el sistema, verifica la configuración")  
        return  
      
    st.sidebar.header("info del sistema")  
    doc_count = vector_store.get_document_count()  
    st.sidebar.metric("documentos cargados", doc_count)  
    st.sidebar.metric("modelo de embeddings", "all-MiniLM-L6-v1")  
    st.sidebar.metric("LLM", "Gemini 1.5 Flash")  
  
    if doc_count == 0:  
        st.warning("no hay documentos cargados, ejecuta primero el pipeline de ingesta")  
        st.code("python scripts/ingest_documents.py data/raw/test")  
        return  
      
    st.sidebar.header("config")  
    top_k = st.sidebar.slider("numero de resultados", 1, 10, 3)  
      
    if "messages" not in st.session_state:  
        st.session_state.messages = []  
      
    for message in st.session_state.messages:  
        if message["role"] == "user":
            avatar = message.get("avatar", get_user_emoji())
        else:
            avatar = "✨"
        with st.chat_message(message["role"], avatar=avatar):  
            st.markdown(message["content"])  
      
    if prompt := st.chat_input("Pregunta sobre Java/Spring Boot"):  
        user_emoji = get_user_emoji()
        
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt,
            "avatar": user_emoji
        })  
        with st.chat_message("user", avatar=user_emoji):  
            st.write(prompt)  
          
        with st.chat_message("assistant", avatar="✨"):  
            with st.spinner("generando respuesta..."):  
                try:  
                    result = rag_engine.generate_answer(prompt, top_k=top_k)  
                      
                    st.markdown(result["answer"])  
                      
                    if result["sources"]:  
                        st.markdown("---")  
                        st.markdown("**fuentes:**")  
                        for source in result["sources"]:  
                            st.markdown(
                                f'<p style="margin: 0.5rem 0;">🔗 <a href="#" style="color: #7c3aed !important; font-weight: 600;">{source["title"]}</a> '
                                f'<span style="color: #7c3aed; font-weight: 500;">(similaridad: {source["score"]:.2f})</span></p>',
                                unsafe_allow_html=True
                            )  
                      
                    st.session_state.messages.append({  
                        "role": "assistant",   
                        "content": result["answer"]  
                    })  
                      
                except Exception as e:  
                    error_msg = f"error generando respuesta: {e}"  
                    st.error(error_msg)  
                    st.session_state.messages.append({  
                        "role": "assistant",  
                        "content": error_msg  
                    })  
      
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