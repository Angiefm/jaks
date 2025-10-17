"""  
Ingestar toda la documentación descargada  
"""  
import subprocess  
import sys  
from pathlib import Path  
  
def ingest_all_documentation():  
    """Ingesta todos los directorios de documentación"""  
      
    base_dir = Path("data/raw")  
    doc_dirs = [  
        "oracle_java_docs",  
        "spring_official_docs",  
        "github_docs",  
        "stackoverflow_docs",  
        "baeldung_docs",  
        "spring_docs"  
    ]  
      
    print("="*60)  
    print("Ingesta Completa de Documentación")  
    print("="*60)  
      
    for doc_dir in doc_dirs:  
        dir_path = base_dir / doc_dir  
        if dir_path.exists():  
            print(f"\nIngiriendo: {doc_dir}")  
            subprocess.run([  
                sys.executable,  
                "scripts/ingest_documents.py",  
                str(dir_path)  
            ])  
        else:  
            print(f"\n⚠ Directorio no encontrado: {doc_dir}")  
      
    print("\n" + "="*60)  
    print("Ingesta completada")  
    print("="*60)  
  
if __name__ == "__main__":  
    ingest_all_documentation()