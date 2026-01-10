import requests
from math import radians, cos, sin, asin, sqrt

def calculate_distance(lat1, lon1, lat2, lon2):
    """Haversine formula to calculate distance in km."""
    try:
        lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        r = 6371 
        return round(c * r, 2)
    except Exception:
        return 0.0

def find_labs_osm(lat, lng, test_names=[]):
    """
    1. Fetches OSM Data.
    2. Sorts by Distance to find the 'Nearest'.
    3. Generates a 'Navigate to Best' Google Maps Link.
    """
    
    # --- PART 1: FETCH RAW DATA (Nominatim) ---
    url = "https://nominatim.openstreetmap.org/search"
    osm_query = "hospital clinic medical"
    headers = { "User-Agent": "MedVision-Project/1.0" }
    
    params = {
        "q": osm_query,
        "lat": lat,
        "lon": lng,
        "format": "json",
        "limit": 10,
        "addressdetails": 1,
        "dedupe": 1
    }

    labs_list = []
    try:
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        
        for place in data:
            dist = calculate_distance(lat, lng, place.get("lat"), place.get("lon"))
            # Filter: Must be within 15km
            if dist <= 15.0:
                labs_list.append({
                    "name": place.get("display_name", "").split(",")[0],
                    "full_address": place.get("display_name"),
                    "lat": place.get("lat"),
                    "lon": place.get("lon"),
                    "distance_km": dist,
                    "type": place.get("type")
                })
        
        # Sort by distance (Index 0 is now the Nearest/Best)
        labs_list.sort(key=lambda x: x["distance_km"])

    except Exception as e:
        print(f"[OSM] Data Fetch Error: {e}")
        labs_list = []

    # --- PART 2: GENERATE LINKS ---
    
    # Link A: Visual Search (The "Explore" view)
    tests_str = " ".join(test_names).lower()
    if "x-ray" in tests_str or "scan" in tests_str:
        query_term = "Diagnostic+Centre"
    elif "blood" in tests_str:
        query_term = "Pathology+Lab"
    else:
        query_term = "Hospital"
        
    encoded_query = f"{query_term} near {lat},{lng}".replace(" ", "+").replace(",", "%2C")
    search_link = f"https://www.google.com/maps/search/{encoded_query}/@{lat},{lng},14z"

    # Link B: NAVIGATION (The "Go Now" view)
    # If we found at least one lab, we set the destination to the nearest one.
    directions_link = ""
    if len(labs_list) > 0:
        best_lab = labs_list[0]
        # Google Maps Direction Format: 
        # https://www.google.com/maps/dir/?api=1&origin={lat},{lng}&destination={lat},{lng}
        directions_link = (
            f"https://www.google.com/maps/dir/?api=1"
            f"&origin={lat},{lng}"
            f"&destination={best_lab['lat']},{best_lab['lon']}"
            f"&travelmode=driving"
        )

    return {
        "labs": labs_list[:5],        
        "map_search_link": search_link,    # View Area
        "map_directions_link": directions_link # Navigate to Nearest
    }