"""
script para descargar documentación de repositorios github públicos
convierte markdown a texto plano para usar con documentloader existente
"""

import requests
import time
from pathlib import Path
import re
from urllib.parse import urljoin

def clean_markdown_to_text(markdown_content):
    """convertir markdown a texto plano limpio"""
    text = markdown_content
    
    # remuevo metadatos de front matter
    text = re.sub(r'^---.*?---\n', '', text, flags=re.DOTALL)
    
    # convierto headers (# ## ###) a texto simple
    text = re.sub(r'^#{1,6}\s*(.+)$', r'\1', text, flags=re.MULTILINE)
    
    # remuevo formateo de código inline
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # convierto bloques de código a texto simple
    text = re.sub(r'^```[\w]*\n(.*?)^```', r'\1', text, flags=re.MULTILINE | re.DOTALL)
    
    # remuevo enlaces pero mantengo el texto
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # remuevo imágenes
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', r'\1', text)
    
    # remuevo formateo bold/italic
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    
    # limpio listas
    text = re.sub(r'^\s*[-*+]\s+', '- ', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # limpio espacios extra
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    text = re.sub(r'^\s+|\s+$', '', text, flags=re.MULTILINE)
    
    return text.strip()

def download_github_docs():
    """descargar documentación de repositorios github públicos"""
    
    # agrego repositorios con documentación extensa y licencias abiertas
    repositories = [
        # spring ecosystem (apache 2.0)
        "spring-projects/spring-boot",
        "spring-projects/spring-framework", 
        "spring-projects/spring-data",
        "spring-projects/spring-security",
        "spring-projects/spring-cloud",
        "spring-projects/spring-batch",
        
        # tutoriales populares (mit/apache)
        "eugenp/tutorials",
        "in28minutes/spring-boot-examples",
        "RameshMF/spring-boot-tutorial",
        "khoubyari/spring-boot-rest-example",
        
        # patrones y arquitectura (mit)
        "iluwatar/java-design-patterns",
        "xurxodev/integration-testing-spring-boot",
        "fernandoabcampos/spring-netflix-oss-microservices",
        
        # apis y herramientas (apache/mit)
        "swagger-api/swagger-core",
        "OpenAPITools/openapi-generator",
        "spring-projects/spring-restdocs",
        
        # testing (mit/apache)
        "testcontainers/testcontainers-java",
        "rest-assured/rest-assured",
        
        # microservices examples
        "sqshq/piggymetrics",
        "yidongnan/spring-cloud-netflix-example"
    ]
    
    docs_dir = Path("data/raw/github_docs")
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    headers = {
        'User-Agent': 'Educational-Research-Project/1.0',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    total_files = 0
    
    for repo in repositories:
        print(f"procesando repositorio: {repo}")
        
        try:
            # obtengo información del repositorio
            repo_info_url = f"https://api.github.com/repos/{repo}"
            repo_response = requests.get(repo_info_url, headers=headers)
            
            if repo_response.status_code != 200:
                print(f"   no pude acceder al repositorio {repo}")
                continue
            
            repo_data = repo_response.json()
            license_name = repo_data.get('license', {}).get('name', 'Unknown') if repo_data.get('license') else 'Unknown'
            
            # obtengo contenido del repositorio
            contents_url = f"https://api.github.com/repos/{repo}/contents"
            response = requests.get(contents_url, headers=headers)
            
            if response.status_code == 200:
                contents = response.json()
                
                # busco archivos de documentación
                doc_files = []
                for item in contents:
                    if item['type'] == 'file':
                        filename = item['name'].lower()
                        if any(filename.startswith(prefix) for prefix in [
                            'readme', 'getting-started', 'quickstart', 'tutorial',
                            'guide', 'docs', 'documentation', 'api', 'reference'
                        ]) and filename.endswith(('.md', '.txt')):
                            doc_files.append(item)
                
                # también busco en carpeta docs/ si existe
                docs_folder_url = f"https://api.github.com/repos/{repo}/contents/docs"
                docs_response = requests.get(docs_folder_url, headers=headers)
                if docs_response.status_code == 200:
                    docs_contents = docs_response.json()
                    for item in docs_contents:
                        if item['type'] == 'file' and item['name'].endswith(('.md', '.txt')):
                            doc_files.append(item)
                
                # descargo archivos encontrados
                repo_files = 0
                for doc_file in doc_files[:10]:  # limito a 10 archivos por repo
                    if download_github_file(repo, doc_file, docs_dir, headers, license_name):
                        repo_files += 1
                        total_files += 1
                
                print(f"   descargados {repo_files} archivos de {repo}")
            
            else:
                print(f"   error accediendo a contenidos de {repo}: {response.status_code}")
        
        except Exception as e:
            print(f"   error procesando {repo}: {e}")
        
        # controlo el rate limiting de github (60 requests/hora sin autenticación)
        time.sleep(2)
    
    print(f"\ndescarga completa: {total_files} documentos obtenidos")
    print(f"guardados en: {docs_dir}")
    return docs_dir, total_files

def download_github_file(repo, file_info, output_dir, headers, license_name):
    """descargar un archivo específico de github y convertirlo a texto plano"""
    try:
        download_url = file_info.get('download_url')
        if not download_url:
            return False
        
        response = requests.get(download_url, headers=headers)
        
        if response.status_code == 200:
            # creo un nombre de archivo único
            repo_name = repo.replace('/', '_').replace('-', '_')
            original_name = file_info['name'].replace('.md', '').replace('.txt', '')
            filename = f"{repo_name}_{original_name}.txt"
            filepath = output_dir / filename
            
            # convierto contenido a texto plano
            content = response.text
            if file_info['name'].endswith('.md'):
                content = clean_markdown_to_text(content)
            
            # agrego metadatos al inicio
            metadata_header = f"""Source Repository: {repo}
License: {license_name}
Original File: {file_info['name']}
GitHub URL: https://github.com/{repo}
Download Date: {time.strftime('%Y-%m-%d %H:%M:%S')}

=== DOCUMENT CONTENT ===

"""
            
            # guardo el archivo
            with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(metadata_header + content)
            
            # verifico que el archivo tenga contenido útil
            if len(content.strip()) < 100:
                filepath.unlink()  # elimino archivos muy pequeños
                return False
            
            print(f"     {filename} ({len(content)} chars)")
            return True
        
        else:
            print(f"     error descargando {file_info['name']}: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"     error procesando {file_info['name']}: {e}")
        return False

def main():
    """función principal"""
    print("iniciando descarga de documentación desde github...")
    print("voy a descargar archivos readme, documentación y guías")
    print("solo repositorios con licencias abiertas (mit, apache, etc.)")
    print()
    
    docs_dir, total_files = download_github_docs()
    
    print("\n" + "="*50)
    print(f"resumen:")
    print(f"   documentos descargados: {total_files}")
    print(f"   directorio: {docs_dir}")
    print(f"   formato: texto plano (.txt)")
    print("\npara procesar con tu sistema existente:")
    print(f"   python scripts/ingest_documents.py {docs_dir} --batch-size 8")

if __name__ == "__main__":
    main()