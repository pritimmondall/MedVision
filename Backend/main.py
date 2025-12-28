from fastapi import FastAPI, UploadFile, File
import easyocr
import shutil
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# --- 1. ROBUST MODEL SELECTOR ---
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("CRITICAL: GEMINI_API_KEY is missing from .env file!")

genai.configure(api_key=api_key)

def get_working_model():
    """Automatically finds a model that actually works for this key."""
    print("Searching for available models...")
    try:
        # List all models available to your key
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # Prefer Flash, then Pro, then anything else
                if 'flash' in m.name:
                    print(f"--> SELECTED MODEL: {m.name}")
                    return genai.GenerativeModel(m.name)
        
        # Fallback if no specific 'flash' model found
        print("--> WARNING: No 'flash' model found, defaulting to 'gemini-pro'")
        return genai.GenerativeModel('gemini-pro')
    except Exception as e:
        print(f"--> ERROR listing models: {e}")
        # Last resort fallback
        return genai.GenerativeModel('gemini-1.5-flash')

# Initialize the model using the smart selector
model = get_working_model()

# Initialize OCR
print("Loading OCR Engine...")
reader = easyocr.Reader(['en'])

def parse_with_ai(ocr_text_list):
    raw_text = " ".join(ocr_text_list)
    prompt = f"""
    Extract medical data from this text into strict JSON:
    {{
        "medicines": [ {{ "name": "str", "dosage": "str", "frequency": "str" }} ],
        "tests": ["str"],
        "next_visit": "str or null"
    }}
    Text: {raw_text}
    """
    try:
        response = model.generate_content(prompt)
        # clean markdown
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except Exception as e:
        return {"error": "AI Parsing Failed", "details": str(e)}

@app.post("/process-prescription")
async def process_prescription(file: UploadFile = File(...)):
    temp_filename = f"temp_{file.filename}"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # OCR
        ocr_result = reader.readtext(temp_filename, detail=0)
        
        # AI Processing
        structured_data = parse_with_ai(ocr_result)

        return {
            "status": "success",
            "structured_data": structured_data,
            "raw_ocr": ocr_result
        }
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)