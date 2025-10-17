"""  
script para descargar documentación oficial de Spring.io y Oracle  
"""  
import requests  
from pathlib import Path  
from bs4 import BeautifulSoup  
import time  
import re  
  
def clean_html_to_text(html_content):  
    """convierto HTML a texto plano limpio"""  
    soup = BeautifulSoup(html_content, 'html.parser')  
      
    for element in soup(['script', 'style', 'nav', 'header', 'footer']):  
        element.decompose()  
      
    text = soup.get_text(separator='\n')  
      
    lines = [line.strip() for line in text.splitlines() if line.strip()]  
    text = '\n'.join(lines)  
      
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  
      
    return text.strip()  
  
def download_spring_official_docs():  
    """descargo documentación oficial de Spring.io"""  
      
    spring_urls = {  
        "spring_boot_reference.txt": "https://docs.spring.io/spring-boot/docs/current/reference/html/getting-started.html",  
        "spring_boot_features.txt": "https://docs.spring.io/spring-boot/docs/current/reference/html/features.html",  
        "spring_web_mvc.txt": "https://docs.spring.io/spring-framework/reference/web/webmvc.html",  
        "spring_data_jpa.txt": "https://docs.spring.io/spring-data/jpa/docs/current/reference/html/#reference",  
        "spring_security.txt": "https://docs.spring.io/spring-security/reference/servlet/getting-started.html",  
    }  
      
    docs_dir = Path("data/raw/spring_official_docs")  
    docs_dir.mkdir(parents=True, exist_ok=True)  
      
    headers = {  
        'User-Agent': 'Educational-Research-Project/1.0',  
        'Accept': 'text/html'  
    }  
      
    print("descargando documentación oficial de Spring.io...")  
      
    for filename, url in spring_urls.items():  
        try:  
            print(f"  descargando: {url}")  
            response = requests.get(url, headers=headers, timeout=30)  
              
            if response.status_code == 200:  
                text_content = clean_html_to_text(response.text)  
                  
                metadata = f"""Source: Spring.io Official Documentation  
URL: {url}  
Download Date: {time.strftime('%Y-%m-%d %H:%M:%S')}  
License: Apache 2.0  
  
=== DOCUMENT CONTENT ===  
  
"""  
                  
                filepath = docs_dir / filename  
                with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:  
                    f.write(metadata + text_content)  
                  
                print(f"    guardado: {filename} ({len(text_content)} chars)")  
            else:  
                print(f"    error {response.status_code}: {url}")  
              
            time.sleep(2)  
              
        except Exception as e:  
            print(f"    error descargando {url}: {e}")  
      
    return docs_dir  
  
def download_oracle_java_docs():  
    """descargo tutoriales de Java de Oracle"""  
      
    java_urls = {  
        "java_getting_started.txt": "https://docs.oracle.com/javase/tutorial/getStarted/index.html",  
        "java_oop_concepts.txt": "https://docs.oracle.com/javase/tutorial/java/concepts/index.html",  
        "java_language_basics.txt": "https://docs.oracle.com/javase/tutorial/java/nutsandbolts/index.html",  
        "java_classes_objects.txt": "https://docs.oracle.com/javase/tutorial/java/javaOO/index.html",  
    }  
      
    docs_dir = Path("data/raw/oracle_java_docs")  
    docs_dir.mkdir(parents=True, exist_ok=True)  
      
    headers = {  
        'User-Agent': 'Educational-Research-Project/1.0',  
        'Accept': 'text/html'  
    }  
      
    print("\ndescargando tutoriales de Java de Oracle...")  
      
    for filename, url in java_urls.items():  
        try:  
            print(f"  descargando: {url}")  
            response = requests.get(url, headers=headers, timeout=30)  
              
            if response.status_code == 200:  
                text_content = clean_html_to_text(response.text)  
                  
                metadata = f"""Source: Oracle Java Tutorials  
URL: {url}  
Download Date: {time.strftime('%Y-%m-%d %H:%M:%S')}  
License: Oracle Technology Network License Agreement  
  
=== DOCUMENT CONTENT ===  
  
"""  
                  
                filepath = docs_dir / filename  
                with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:  
                    f.write(metadata + text_content)  
                  
                print(f"    guardado: {filename} ({len(text_content)} chars)")  
            else:  
                print(f"    error {response.status_code}: {url}")  
              
            time.sleep(2)  
              
        except Exception as e:  
            print(f"    error descargando {url}: {e}")  
      
    return docs_dir  
  
def main():  
    print("="*60)  
    print("descarga de documentación oficial")  
    print("="*60)  
      
    spring_dir = download_spring_official_docs()  
      
    java_dir = download_oracle_java_docs()  
      
    print("\n" + "="*60)  
    print("resumen:")  
    print(f"  Spring docs: {spring_dir}")  
    print(f"  Java docs: {java_dir}")  
    print("\npara procesar con tu sistema:")  
    print(f"  python scripts/ingest_documents.py {spring_dir}")  
    print(f"  python scripts/ingest_documents.py {java_dir}")  
    print("="*60)  
  
if __name__ == "__main__":  
    main()