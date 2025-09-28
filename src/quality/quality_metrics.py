import re
import logging
from typing import Dict, Any, List
from datetime import datetime
import numpy as np

class QualityMetrics:
    """extractor de features para evaluación de calidad de documentos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # defino patrones para detectar código
        self.code_patterns = [
            r'```[\s\S]*?```',  # bloques de código markdown
            r'`[^`\n]+`',       # código inline
            r'@\w+',            # anotaciones java
            r'public\s+class',  # clases java
            r'import\s+\w+',    # imports
            r'\{[\s\S]*?\}',    # bloques con llaves
        ]
        
        # defino indicadores de calidad
        self.quality_keywords = [
            'example', 'tutorial', 'guide', 'documentation', 'api', 
            'reference', 'usage', 'getting started', 'quickstart',
            'configuration', 'setup', 'installation', 'best practices'
        ]
        
        # defino indicadores de baja calidad
        self.low_quality_indicators = [
            'todo', 'fixme', 'hack', 'temporary', 'placeholder',
            'coming soon', 'under construction', 'work in progress'
        ]
    
    def extract_features(self, document) -> Dict[str, Any]:
        """extraigo todas las features de calidad de un documento"""
        content = document.content.lower()
        title = document.title.lower()
        
        features = {
            # features básicas
            'content_length': len(document.content),
            'title_length': len(document.title),
            'word_count': len(document.content.split()),
            'paragraph_count': len([p for p in document.content.split('\n\n') if p.strip()]),
            
            # features de estructura
            'has_headers': self._count_headers(document.content),
            'has_lists': self._count_lists(document.content),
            'code_blocks': self._count_code_blocks(document.content),
            'code_inline': self._count_inline_code(document.content),
            
            # features de contenido
            'quality_keywords': self._count_quality_keywords(content + ' ' + title),
            'low_quality_indicators': self._count_low_quality_indicators(content + ' ' + title),
            'technical_terms': self._count_technical_terms(content),
            'external_links': self._count_external_links(document.content),
            
            # features de legibilidad
            'avg_sentence_length': self._avg_sentence_length(document.content),
            'readability_score': self._simple_readability_score(document.content),
            
            # features específicas de java/spring
            'java_keywords': self._count_java_keywords(content),
            'spring_keywords': self._count_spring_keywords(content),
            
            # features de metadatos
            'file_type': document.doc_type,
            'source_reliability': self._assess_source_reliability(document.file_path)
        }
        
        return features
    
    def _count_headers(self, content: str) -> int:
        """cuento headers markdown"""
        return len(re.findall(r'^#{1,6}\s+.+$', content, re.MULTILINE))
    
    def _count_lists(self, content: str) -> int:
        """cuento elementos de lista"""
        bullet_lists = len(re.findall(r'^\s*[-*+]\s+', content, re.MULTILINE))
        numbered_lists = len(re.findall(r'^\s*\d+\.\s+', content, re.MULTILINE))
        return bullet_lists + numbered_lists
    
    def _count_code_blocks(self, content: str) -> int:
        """cuento bloques de código"""
        return len(re.findall(self.code_patterns[0], content))
    
    def _count_inline_code(self, content: str) -> int:
        """cuento código inline"""
        return len(re.findall(self.code_patterns[1], content))
    
    def _count_quality_keywords(self, text: str) -> int:
        """cuento palabras clave de calidad"""
        return sum(1 for keyword in self.quality_keywords if keyword in text)
    
    def _count_low_quality_indicators(self, text: str) -> int:
        """cuento indicadores de baja calidad"""
        return sum(1 for indicator in self.low_quality_indicators if indicator in text)
    
    def _count_technical_terms(self, content: str) -> int:
        """cuento términos técnicos"""
        tech_terms = [
            'api', 'rest', 'http', 'json', 'xml', 'database', 'sql',
            'framework', 'library', 'dependency', 'configuration',
            'annotation', 'interface', 'abstract', 'inheritance'
        ]
        return sum(1 for term in tech_terms if term in content)
    
    def _count_external_links(self, content: str) -> int:
        """cuento enlaces externos"""
        return len(re.findall(r'https?://[^\s\]]+', content))
    
    def _avg_sentence_length(self, content: str) -> float:
        """calculo longitud promedio de oraciones"""
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences:
            return 0
        return sum(len(s.split()) for s in sentences) / len(sentences)
    
    def _simple_readability_score(self, content: str) -> float:
        """calculo un score simple de legibilidad (0-100)"""
        words = content.split()
        sentences = re.split(r'[.!?]+', content)
        sentences = [s for s in sentences if s.strip()]
        
        if not sentences or not words:
            return 0
        
        avg_sentence_length = len(words) / len(sentences)
        # score inverso: oraciones más cortas = mayor legibilidad
        readability = max(0, 100 - (avg_sentence_length - 15) * 2)
        return min(100, readability)
    
    def _count_java_keywords(self, content: str) -> int:
        """cuento keywords específicas de java"""
        java_keywords = [
            'java', 'class', 'interface', 'extends', 'implements',
            'public', 'private', 'protected', 'static', 'final',
            'abstract', 'synchronized', 'package', 'import'
        ]
        return sum(1 for keyword in java_keywords if keyword in content)
    
    def _count_spring_keywords(self, content: str) -> int:
        """cuento keywords específicas de spring"""
        spring_keywords = [
            'spring', 'boot', 'mvc', 'rest', 'controller', 'service',
            'repository', 'component', 'autowired', 'bean', 'configuration'
        ]
        return sum(1 for keyword in spring_keywords if keyword in content)
    
    def _assess_source_reliability(self, file_path: str) -> float:
        """evalúo confiabilidad de la fuente (0-1)"""
        path_lower = file_path.lower()
        
        # fuentes muy confiables
        if any(source in path_lower for source in ['spring_projects', 'oracle', 'apache']):
            return 1.0
        
        # fuentes confiables
        if any(source in path_lower for source in ['eugenp', 'baeldung', 'tutorial']):
            return 0.8
        
        # fuentes moderadamente confiables
        if 'github' in path_lower:
            return 0.6
        
        # fuentes desconocidas
        return 0.4
    
    def calculate_quality_score(self, features: Dict[str, Any]) -> float:
        """calculo score de calidad global (0-100)"""
        score = 0
        
        # longitud de contenido (25 puntos máximo)
        if features['content_length'] > 1000:
            score += 25
        elif features['content_length'] > 500:
            score += 15
        elif features['content_length'] > 200:
            score += 10
        
        # estructura del documento (20 puntos máximo)
        if features['has_headers'] > 0:
            score += 8
        if features['has_lists'] > 0:
            score += 6
        if features['code_blocks'] > 0:
            score += 6
        
        # contenido técnico (20 puntos máximo)
        score += min(10, features['technical_terms'] * 2)
        score += min(10, features['java_keywords'] + features['spring_keywords'])
        
        # calidad del contenido (20 puntos máximo)
        score += min(10, features['quality_keywords'] * 2)
        score -= features['low_quality_indicators'] * 3
        score += min(10, features['readability_score'] / 10)
        
        # confiabilidad de la fuente (15 puntos máximo)
        score += features['source_reliability'] * 15
        
        return max(0, min(100, score))

# test de las métricas
if __name__ == "__main__":
    from ingestion.document_loader import Document
    
    # documento de prueba
    test_doc = Document(
        id="test_1",
        title="Spring Boot REST API Tutorial",
        content="""
# Spring Boot REST API Tutorial

This tutorial shows how to create REST APIs with Spring Boot.

## Prerequisites
- Java 8 or higher
- Maven or Gradle

## Steps

### 1. Create Controller
```java
@RestController
public class UserController {
    @GetMapping("/users")
    public List<User> getUsers() {
        return userService.findAll();
    }
}
"""
    )
