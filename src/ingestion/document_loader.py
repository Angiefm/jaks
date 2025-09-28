import os
import logging
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import PyPDF2
from tqdm import tqdm

@dataclass
class Document:
    """estructura básica para documentos"""
    id: str
    title: str
    content: str
    file_path: str
    doc_type: str  # acá defino si es 'pdf' o 'txt'
    
class DocumentLoader:
    """cargador simple de documentos pdf y texto"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def load_text_file(self, file_path: Path) -> Optional[Document]:
        """cargo archivo de texto plano"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # acá uso el nombre del archivo como título
            title = file_path.stem
            doc_id = f"txt_{file_path.stem}"
            
            return Document(
                id=doc_id,
                title=title,
                content=content,
                file_path=str(file_path),
                doc_type='txt'
            )
        except Exception as e:
            self.logger.error(f"error cargando archivo de texto {file_path}: {e}")
            return None
    
    def load_pdf_file(self, file_path: Path) -> Optional[Document]:
        """cargo archivo pdf básico"""
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                content = ""
                
                # acá recorro todas las páginas y extraigo el texto
                for page in reader.pages:
                    content += page.extract_text() + "\n"
            
            # acá limpio el contenido básico
            content = content.strip()
            if not content:
                self.logger.warning(f"pdf {file_path} parece estar vacío")
                return None
            
            title = file_path.stem
            doc_id = f"pdf_{file_path.stem}"
            
            return Document(
                id=doc_id,
                title=title,
                content=content,
                file_path=str(file_path),
                doc_type='pdf'
            )
        except Exception as e:
            self.logger.error(f"error cargando pdf {file_path}: {e}")
            return None
    
    def load_documents_from_directory(self, directory: Path) -> List[Document]:
        """cargo todos los documentos de un directorio"""
        documents = []
        directory = Path(directory)
        
        # acá busco archivos pdf y txt
        pdf_files = list(directory.glob('**/*.pdf'))
        txt_files = list(directory.glob('**/*.txt'))
        all_files = pdf_files + txt_files
        
        self.logger.info(f"encontré {len(all_files)} archivos para procesar")
        
        for file_path in tqdm(all_files, desc="cargando documentos"):
            if file_path.suffix.lower() == '.pdf':
                doc = self.load_pdf_file(file_path)
            elif file_path.suffix.lower() == '.txt':
                doc = self.load_text_file(file_path)
            else:
                continue
                
            if doc:
                documents.append(doc)
        
        self.logger.info(f"cargué exitosamente {len(documents)} documentos")
        return documents
    
    def load_single_document(self, file_path: str) -> Optional[Document]:
        """cargo un solo documento"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            self.logger.error(f"archivo {file_path} no encontrado")
            return None
        
        if file_path.suffix.lower() == '.pdf':
            return self.load_pdf_file(file_path)
        elif file_path.suffix.lower() == '.txt':
            return self.load_text_file(file_path)
        else:
            self.logger.error(f"tipo de archivo no soportado: {file_path.suffix}")
            return None

# acá hago un test básico
if __name__ == "__main__":
    # acá configuro logging básico
    logging.basicConfig(level=logging.INFO)
    
    loader = DocumentLoader()
    print("documentloader creado exitosamente!")
    print("listo para cargar documentos...")

# mini sistema para leer archivos PDF y TXT desde una ruta, cargarlos en memoria como objetos bien estructurados (Document), y manejar errores/logs de forma ordenada