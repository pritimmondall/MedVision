from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel 
import easyocr
import shutil
import google.generativeai as genai
import os
import json
import requests # <--- NEEDED FOR IP LOOKUP
from datetime import date 
from dotenv import load_dotenv

# Import your modules
from agent.bot import PharmaAgent 
from calendar_service import add_checkup_event 
from maps_service_osm import find_labs_osm 

load_dotenv()

app = FastAPI()

# --- 1. MODEL CONFIGURATION ---
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("CRITICAL: GEMINI_API_KEY is missing from .env file!")

genai.configure(api_key=api_key)

def get_working_model():
    print("Searching for available models...")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name:
                    return genai.GenerativeModel(m.name)
        return genai.GenerativeModel('gemini-pro')
    except Exception as e:
        return genai.GenerativeModel('gemini-1.5-flash')

model = get_working_model()
reader = easyocr.Reader(['en'])

def parse_with_ai(ocr_text_list):
    raw_text = " ".join(ocr_text_list)
    today_str = date.today().isoformat() 
    prompt = f"""
    You are a medical assistant. Today is {today_str}.
    Analyze this prescription text: "{raw_text}"
    Extract data into strict JSON format.
    Keys required:
    - medicines: list of objects with "name", "dosage", "frequency"
    - tests: list of strings (e.g. "X-Ray", "Blood Test"). If none, return [].
    - next_visit: "YYYY-MM-DD" or null
    """
    try:
        response = model.generate_content(prompt)
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except Exception as e:
        return {"error": str(e), "medicines": [], "tests": [], "next_visit": None}

# --- NEW HELPER: GET AUTO LOCATION ---
def get_auto_location():
    """
    Uses the Server's Public IP to guess location (City level accuracy).
    Perfect for localhost demos.
    """
    try:
        # This API returns the location of the internet connection running this script
        response = requests.get("http://ip-api.com/json")
        data = response.json()
        if data['status'] == 'success':
            print(f"📍 Auto-Detected Location: {data['city']}, {data['country']}")
            return float(data['lat']), float(data['lon'])
        else:
            return None, None
    except Exception as e:
        print(f"Auto-Location Failed: {e}")
        return None, None

# --- 2. MAIN PROCESSING ENDPOINT ---
@app.post("/process-prescription")
async def process_prescription(
    file: UploadFile = File(...),
    priority: str = Form("price") 
):
    temp_filename = f"temp_{file.filename}"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        print(f"Processing image: {file.filename}")
        ocr_result = reader.readtext(temp_filename, detail=0)
        structured_data = parse_with_ai(ocr_result)
        
        detected_tests = structured_data.get("tests", [])
        if detected_tests:
            print(f"🔬 Found Diagnostic Tests: {detected_tests}")

        calendar_status = None
        if structured_data.get("next_visit"):
            calendar_status = add_checkup_event(structured_data['next_visit'], "Doctor Follow-up")

        agent_report = []
        if structured_data.get("medicines"):
            try:
                bot = PharmaAgent()
                agent_report = bot.process_order(structured_data["medicines"], user_priority=priority)
                bot.close()
            except Exception:
                pass

        return {
            "status": "success",
            "tests_found": detected_tests, 
            "structured_data": structured_data,
            "calendar_event": calendar_status,
            "agent_report": agent_report
        }
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

# --- 3. LAB SEARCH ENDPOINT (UPDATED) ---
class LabSearchRequest(BaseModel):
    lat: float = 0.0
    lng: float = 0.0
    test_names: list[str]

@app.post("/find-labs")
async def find_labs_endpoint(request: LabSearchRequest):
    current_lat = request.lat
    current_lng = request.lng
    
    # Auto-Location
    if current_lat == 0.0 or current_lng == 0.0:
        print("🌍 Auto-detecting location...")
        detected_lat, detected_lng = get_auto_location()
        if detected_lat:
            current_lat = detected_lat
            current_lng = detected_lng
        else:
            return {"status": "error", "message": "Could not detect location."}

    print(f"Searching labs near {current_lat}, {current_lng}")
    
    # Call the Updated Service
    result_data = find_labs_osm(current_lat, current_lng, request.test_names)
    
    return {
        "status": "success",
        "location_used": {"lat": current_lat, "lng": current_lng},
        "nearest_lab_name": result_data["labs"][0]["name"] if result_data["labs"] else "None",
        
        # --- RETURN BOTH LINKS ---
        "view_map_url": result_data["map_search_link"],        # To Explore
        "navigate_now_url": result_data["map_directions_link"] # To Go (Directions)
    }