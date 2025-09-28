"""
script cli para ingestar documentos al sistema
"""
import os
import sys
import logging
import argparse
from pathlib import Path
from dotenv import load_dotenv

# agrego src al path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from ingestion.document_loader import DocumentLoader
from embeddings.embedding_engine import EmbeddingEngine
from storage.vector_store import VectorStore

def setup_logging():
    """configuro logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/ingest.log')
        ]
    )

def main():
    """función principal del script"""
    # cargo variables de entorno
    load_dotenv()
    
    # preparo logging
    Path("logs").mkdir(exist_ok=True)
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # defino los argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="ingesto documentos en el sistema")
    parser.add_argument("input_dir", help="directorio que contiene los documentos a ingestar")
    parser.add_argument("--batch-size", type=int, default=16, help="tamaño de lote para generar embeddings")
    parser.add_argument("--clear", action="store_true", help="borro documentos existentes antes de ingestar")
    
    args = parser.parse_args()
    
    try:
        logger.info("inicio el pipeline de ingesta de documentos")
        
        # verifico que el directorio de entrada exista
        input_dir = Path(args.input_dir)
        if not input_dir.exists():
            logger.error(f"el directorio {input_dir} no existe")
            return 1
        
        # inicializo los componentes
        logger.info("inicializando componentes...")
        loader = DocumentLoader()
        embedding_engine = EmbeddingEngine(
            model_name=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v1"),
            device=os.getenv("EMBEDDING_DEVICE", "cpu")
        )
        vector_store = VectorStore(db_path=os.getenv("CHROMA_DB_PATH", "./data/vectordb"))
        
        # si me piden limpiar el store, lo hago
        if args.clear:
            logger.info("limpio documentos existentes...")
            vector_store.delete_all_documents()
        
        # cargo los documentos
        logger.info(f"cargo documentos desde {input_dir}")
        documents = loader.load_documents_from_directory(input_dir)
        
        if not documents:
            logger.warning("no encontré documentos para ingestar")
            return 0
        
        logger.info(f"cargué {len(documents)} documentos")
        
        # genero embeddings
        logger.info("generando embeddings...")
        embeddings = embedding_engine.encode_documents(documents, batch_size=args.batch_size)
        
        if not embeddings:
            logger.error("no se generaron embeddings")
            return 1
        
        logger.info(f"generé {len(embeddings)} embeddings")
        
        # guardo en el vector store
        logger.info("almaceno documentos y embeddings...")
        vector_store.add_documents(documents, embeddings)
        
        # muestro estadísticas finales
        final_count = vector_store.get_document_count()
        logger.info(f"ingesta completada. total de documentos en el store: {final_count}")
        
        return 0
        
    except Exception as e:
        logger.error(f"error en el pipeline de ingesta: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit(main())
