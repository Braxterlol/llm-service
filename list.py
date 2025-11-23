"""
Script para ver qué modelos de Gemini están disponibles
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Cargar .env
load_dotenv()

# Configurar API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ GOOGLE_API_KEY no encontrada en .env")
    exit(1)

genai.configure(api_key=api_key)

print("🔍 Listando modelos disponibles de Gemini:\n")

# Listar todos los modelos
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✅ {model.name}")
        print(f"   Descripción: {model.display_name}")
        print(f"   Métodos: {model.supported_generation_methods}")
        print()

print("\n💡 Usa uno de estos nombres en tu código")
print("   Ejemplo: model_name = 'models/gemini-1.5-flash-latest'")