import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("Modelos disponibles:\n")
for m in genai.list_models():
    print(m.name)

print("\n--- Probando el modelo ---\n")
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
response = model.generate_content("Hola, ¿puedes responderme?")
print(response.text)
