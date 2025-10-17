import logging
from typing import Dict
import google.generativeai as genai

class RAGEngine:
    """Motor de generación de respuestas usando RAG con Gemini"""
    
    def __init__(self, search_engine, api_key: str):
        self.search_engine = search_engine
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
        self.logger = logging.getLogger(__name__)
    
    def generate_answer(self, query: str, top_k: int = 3) -> Dict:
        """Genera respuesta basada en documentos"""
        self.logger.info(f"Consulta: {query}")
        
        results = self.search_engine.search(query, top_k=top_k, min_similarity=0.2)
        
        if not results:
            return {"answer": "No encontré información sobre eso en mis documentos.", "sources": []}
        
        context = self._build_context(results)
        answer = self._call_gemini(query, context)
        
        return {
            "answer": answer,
            "sources": [{"title": r.title, "score": r.similarity_score} for r in results]
        }
    
    def _build_context(self, results) -> str:
        context_parts = [f"[{r.title}]\n{r.content_preview}" for r in results]
        context = "\n\n".join(context_parts)
        return context[:8000]
    
    def _call_gemini(self, query: str, context: str) -> str:
        """Llama a Gemini para generar respuesta contextualizada"""
        prompt = f"""Eres un asistente experto en **Java** y **Spring Boot**.  
Tu tarea es responder preguntas basándote principalmente en la documentación proporcionada.  

Documentación disponible:  
{context}  

Pregunta del usuario: {query}  

Instrucciones:  
1. Si la documentación contiene información relevante, úsala para responder.  
2. Si la documentación no da una definición exacta, infiere con base en el contexto y explica claramente.  
3. Si hay ejemplos de código o fragmentos útiles, menciónalos o descríbelos.  
4. Sé conciso, profesional y responde **en español**.  
5. Si no hay información suficiente, dilo explícitamente.  
"""

        try:
            response = self.model.generate_content(prompt)
            if response and hasattr(response, "text"):
                return response.text.strip()
            else:
                return "No se obtuvo respuesta del modelo."
        except Exception as e:
            self.logger.error(f"Error al llamar a Gemini: {e}")
            return "Ocurrió un error al generar la respuesta."
