import streamlit as st
import sys
from pathlib import Path
import numpy as np

# agrego la ruta src al path del sistema
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from storage.vector_store import VectorStore
from clustering.cluster_engine import ClusterEngine
from clustering.dimensionality_reducer import DimensionalityReducer
from visualization.cluster_visualizer import ClusterVisualizer
from ingestion.document_loader import DocumentLoader

def show_exploration_page():
    """pagina de exploracion visual de clusters"""
    
    st.title("Exploracion Visual de Documentos")
    
    # cargo los datos del vector store
    with st.spinner("Cargando datos..."):
        vector_store = VectorStore()
        doc_count = vector_store.get_document_count()
        
        if doc_count == 0:
            st.warning("No hay documentos cargados")
            return
        
        # obtengo los embeddings y metadatos
        collection = vector_store.collection
        results = collection.get(include=['embeddings', 'metadatas'])
        
        embeddings = np.array(results['embeddings'])
        titles = [m.get('title', 'Unknown') for m in results['metadatas']]
        doc_ids = results['ids']
    
    st.success(f"{doc_count} documentos cargados")
    
    # configuro el panel lateral con los controles
    st.sidebar.header("Configuracion")
    
    # selecciono el metodo de clustering
    clustering_method = st.sidebar.selectbox(
        "Metodo de Clustering",
        ["HDBSCAN", "K-Means"]
    )
    
    # defino los parametros segun el metodo elegido
    if clustering_method == "K-Means":
        n_clusters = st.sidebar.slider("Numero de Clusters", 2, 15, 8)
    else:
        min_cluster_size = st.sidebar.slider("Tamano Minimo de Cluster", 2, 10, 3)
    
    # ejecuto el clustering cuando presiono el boton
    if st.sidebar.button("Ejecutar Clustering", type="primary"):
        with st.spinner("Ejecutando clustering..."):
            cluster_engine = ClusterEngine()
            
            if clustering_method == "HDBSCAN":
                results = cluster_engine.cluster_hdbscan(
                    embeddings, 
                    min_cluster_size=min_cluster_size
                )
            else:
                results = cluster_engine.cluster_kmeans(embeddings, n_clusters=n_clusters)
            
            st.session_state['cluster_results'] = results
            st.session_state['cluster_labels'] = cluster_engine.cluster_labels
            st.success("Clustering completado")
    
    # muestro resultados si ya hay clustering hecho
    if 'cluster_results' in st.session_state:
        results = st.session_state['cluster_results']
        labels = st.session_state['cluster_labels']
        
        # muestro metricas principales
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Clusters Encontrados", results['n_clusters'])
        with col2:
            if 'n_noise' in results:
                st.metric("Documentos Ruido", results['n_noise'])
        with col3:
            silhouette = results['metrics'].get('silhouette', 0)
            st.metric("Silhouette Score", f"{silhouette:.3f}")
        
        # hago la reduccion dimensional y visualizo los clusters
        st.subheader("Visualizacion de Clusters")
        
        viz_type = st.radio("Tipo de Visualizacion", ["2D", "3D"], horizontal=True)
        
        with st.spinner("Generando visualizacion..."):
            reducer = DimensionalityReducer()
            visualizer = ClusterVisualizer()
            
            if viz_type == "2D":
                embeddings_2d = reducer.fit_transform_2d(embeddings)
                fig = visualizer.plot_clusters_2d(embeddings_2d, labels, titles)
            else:
                embeddings_3d = reducer.fit_transform_3d(embeddings)
                fig = visualizer.plot_clusters_3d(embeddings_3d, labels, titles)
            
            st.plotly_chart(fig, use_container_width=True)
        
        # grafico la distribucion de tamanos de cluster
        st.subheader("Distribucion de Clusters")
        size_fig = visualizer.plot_cluster_sizes(results)
        st.plotly_chart(size_fig, use_container_width=True)
        
        # muestro los documentos por cluster
        st.subheader("Documentos por Cluster")
        
        unique_labels = sorted(set(labels))
        selected_cluster = st.selectbox(
            "Seleccionar Cluster",
            unique_labels,
            format_func=lambda x: f"Cluster {x}" if x != -1 else "Ruido"
        )
        
        # muestro los documentos del cluster seleccionado
        cluster_mask = labels == selected_cluster
        cluster_docs = [titles[i] for i in range(len(titles)) if cluster_mask[i]]
        
        st.write(f"{len(cluster_docs)} documentos en este cluster:")
        for doc in cluster_docs[:20]:  # muestro los primeros 20
            st.write(f"- {doc}")

if __name__ == "__main__":
    show_exploration_page()