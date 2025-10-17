"""  
script para descargar preguntas y respuestas de Stack Overflow sobre Java  
"""  
import requests  
from pathlib import Path  
import time  
import json  
  
def download_stackoverflow_java_questions():  
    """descargo preguntas populares de Java desde Stack Overflow"""  
      
    docs_dir = Path("data/raw/stackoverflow_docs")  
    docs_dir.mkdir(parents=True, exist_ok=True)  
      
    base_url = "https://api.stackexchange.com/2.3/questions"  
      
    tags = [  
        "java",  
        "spring-boot",  
        "spring-framework",  
        "jpa",  
        "hibernate",  
        "rest-api",  
        "maven",  
        "gradle"  
    ]  
      
    total_downloaded = 0  
      
    for tag in tags:  
        print(f"\ndescargando preguntas de Stack Overflow con tag: {tag}")  
          
        params = {  
            'order': 'desc',  
            'sort': 'votes',  
            'tagged': tag,  
            'site': 'stackoverflow',  
            'filter': 'withbody',  
            'pagesize': 20  
        }  
          
        try:  
            response = requests.get(base_url, params=params)  
              
            if response.status_code == 200:  
                data = response.json()  
                  
                for item in data.get('items', []):  
                    question_id = item['question_id']  
                    answers = get_accepted_answer(question_id)  
                      
                    doc_content = format_stackoverflow_doc(item, answers)  
                      
                    filename = f"stackoverflow_{tag}_{question_id}.txt"  
                    filepath = docs_dir / filename  
                      
                    with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:  
                        f.write(doc_content)  
                      
                    total_downloaded += 1  
                    print(f"  descargado: {item['title'][:50]}...")  
                  
                time.sleep(1)  
            else:  
                print(f"  error {response.status_code} para tag {tag}")  
                  
        except Exception as e:  
            print(f"  error descargando {tag}: {e}")  
      
    print(f"\n{'='*60}")  
    print(f"total descargado: {total_downloaded} documentos")  
    print(f"ubicación: {docs_dir}")  
    print(f"\npara ingestar:")  
    print(f"  python scripts/ingest_documents.py {docs_dir}")  
    print(f"{'='*60}")  
      
    return docs_dir  
  
def get_accepted_answer(question_id):  
    """obtengo respuesta aceptada de una pregunta"""  
    url = f"https://api.stackexchange.com/2.3/questions/{question_id}/answers"  
    params = {  
        'order': 'desc',  
        'sort': 'votes',  
        'site': 'stackoverflow',  
        'filter': 'withbody'  
    }  
      
    try:  
        response = requests.get(url, params=params)  
        if response.status_code == 200:  
            data = response.json()  
            items = data.get('items', [])  
            return items[0] if items else None  
    except:  
        pass  
      
    return None  
  
def format_stackoverflow_doc(question, answer):  
    """formateo pregunta y respuesta como documento"""  
      
    content = f"""Source: Stack Overflow  
Question ID: {question['question_id']}  
URL: {question['link']}  
Tags: {', '.join(question.get('tags', []))}  
Score: {question.get('score', 0)} votes  
Views: {question.get('view_count', 0)}  
  
=== QUESTION ===  
  
{question['title']}  
  
{question.get('body', '')}  
  
"""  
      
    if answer:  
        content += f"""  
=== ACCEPTED ANSWER ===  
  
Score: {answer.get('score', 0)} votes  
  
{answer.get('body', '')}  
"""  
      
    return content  
  
if __name__ == "__main__":  
    download_stackoverflow_java_questions()