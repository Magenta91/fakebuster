import google.generativeai as genai
from app.config.settings import get_settings

settings = get_settings()
genai.configure(api_key=settings.gemini_api_key)

print("Listing available Gemini models...")
try:
    for model in genai.list_models():
        if 'embed' in model.name.lower() or 'embedding' in model.name.lower():
            print(f"\nEmbedding Model: {model.name}")
            print(f"  Supported methods: {model.supported_generation_methods}")
        elif 'gemini' in model.name.lower() and 'generateContent' in model.supported_generation_methods:
            print(f"\nChat Model: {model.name}")
            print(f"  Supported methods: {model.supported_generation_methods}")
except Exception as e:
    print(f"Error: {e}")
