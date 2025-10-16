import logging
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from typing import List, Dict, Any, Optional

class ClusterVisualizer:
    """Visualizador de clusters con Plotly"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def plot_clusters_2d(self, embeddings_2d: np.ndarray, 
                        labels: np.ndarray,
                        titles: List[str] = None,
                        hover_text: List[str] = None) -> go.Figure:
        """Visualización 2D de clusters"""
        
        # Preparar colores
        unique_labels = sorted(set(labels))
        color_map = {label: i for i, label in enumerate(unique_labels)}
        colors = [color_map[label] for label in labels]
        
        # Crear figura
        fig = go.Figure()
        
        # Agregar puntos por cluster
        for label in unique_labels:
            mask = labels == label
            cluster_name = f"Cluster {label}" if label != -1 else "Ruido"
            
            fig.add_trace(go.Scatter(
                x=embeddings_2d[mask, 0],
                y=embeddings_2d[mask, 1],
                mode='markers',
                name=cluster_name,
                text=[titles[i] if titles else f"Doc {i}" for i in range(len(labels)) if mask[i]],
                hovertext=[hover_text[i] if hover_text else "" for i in range(len(labels)) if mask[i]],
                marker=dict(
                    size=8,
                    opacity=0.6 if label != -1 else 0.3,
                    line=dict(width=0.5, color='white')
                )
            ))
        
        fig.update_layout(
            title="Visualización de Clusters de Documentos",
            xaxis_title="UMAP Dimensión 1",
            yaxis_title="UMAP Dimensión 2",
            hovermode='closest',
            height=600,
            template='plotly_white'
        )
        
        return fig
    
    def plot_clusters_3d(self, embeddings_3d: np.ndarray,
                        labels: np.ndarray,
                        titles: List[str] = None) -> go.Figure:
        """Visualización 3D de clusters"""
        
        unique_labels = sorted(set(labels))
        
        fig = go.Figure()
        
        for label in unique_labels:
            mask = labels == label
            cluster_name = f"Cluster {label}" if label != -1 else "Ruido"
            
            fig.add_trace(go.Scatter3d(
                x=embeddings_3d[mask, 0],
                y=embeddings_3d[mask, 1],
                z=embeddings_3d[mask, 2],
                mode='markers',
                name=cluster_name,
                text=[titles[i] if titles else f"Doc {i}" for i in range(len(labels)) if mask[i]],
                marker=dict(
                    size=5,
                    opacity=0.6 if label != -1 else 0.3
                )
            ))
        
        fig.update_layout(
            title="Visualización 3D de Clusters",
            scene=dict(
                xaxis_title="UMAP Dim 1",
                yaxis_title="UMAP Dim 2",
                zaxis_title="UMAP Dim 3"
            ),
            height=700,
            template='plotly_white'
        )
        
        return fig
    
    def plot_cluster_sizes(self, cluster_info):
        """Gráfico de tamaños de clusters"""
        import numpy as np
        import plotly.graph_objects as go
    
        # Detectar dónde están los tamaños
        if "sizes" in cluster_info:
            sizes = cluster_info["sizes"]
        elif "cluster_sizes" in cluster_info:
            sizes = cluster_info["cluster_sizes"]
        elif "labels" in cluster_info:
            labels_array = np.array(cluster_info["labels"])
            unique, counts = np.unique(labels_array, return_counts=True)
            sizes = {int(k): int(v) for k, v in zip(unique, counts)}
        else:
            raise KeyError("El diccionario 'cluster_info' debe tener 'sizes', 'cluster_sizes' o 'labels'.")
    
        labels = [f"Cluster {k}" if k != -1 else "Ruido" for k in sizes.keys()]
        values = list(sizes.values())
    
        fig = go.Figure(data=[
            go.Bar(x=labels, y=values, marker_color='lightblue')
        ])
    
        fig.update_layout(
            title="Distribución de Documentos por Cluster",
            xaxis_title="Cluster",
            yaxis_title="Número de Documentos",
            template='plotly_white'
        )
    
        return fig
    
        