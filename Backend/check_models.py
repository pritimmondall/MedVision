import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: No API Key found. Check your .env file.")
else:
    genai.configure(api_key=api_key)
    print(f"Checking models for key ending in: ...{api_key[-4:]}")
    
    try:
        print("\n--- AVAILABLE MODELS ---")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
        print("------------------------")
    except Exception as e:
        print(f"Error connecting to Google: {e}")