import os
from typing import Dict, List

# Configuration settings for WeatherGPT
APP_TITLE = "WeatherGPT - Conversational AI for Weather Forecasting & Climate Intelligence"
APP_VERSION = "2.0.0"
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1")

# Default API endpoints
OPEN_METEO_BASE = "https://api.open-meteo.com/v1"
GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"
AIR_QUALITY_API = "https://air-quality-api.open-meteo.com/v1/air-quality"
HISTORICAL_API = "https://archive-api.open-meteo.com/v1/archive"

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEFAULT_GEMINI_MODEL = "gemini-3.6-flash"

# In-memory cache TTL (seconds)
CACHE_TTL = 300  # 5 minutes

# Supported Indian Languages
SUPPORTED_LANGUAGES: Dict[str, Dict[str, str]] = {
    "en": {"name": "English", "native": "English", "bcp47": "en-IN"},
    "hi": {"name": "Hindi", "native": "हिन्दी", "bcp47": "hi-IN"},
    "bn": {"name": "Bengali", "native": "বাংলা", "bcp47": "bn-IN"},
    "te": {"name": "Telugu", "native": "తెలుగు", "bcp47": "te-IN"},
    "ta": {"name": "Tamil", "native": "தமிழ்", "bcp47": "ta-IN"},
    "mr": {"name": "Marathi", "native": "मराठी", "bcp47": "mr-IN"},
    "gu": {"name": "Gujarati", "native": "ગુજરાતી", "bcp47": "gu-IN"},
    "kn": {"name": "Kannada", "native": "ಕನ್ನಡ", "bcp47": "kn-IN"},
}

# Pre-defined key agricultural & urban centers in India
DEFAULT_LOCATIONS: List[Dict[str, any]] = [
    {"name": "New Delhi", "state": "Delhi", "lat": 28.6139, "lon": 77.2090, "type": "Metropolitan"},
    {"name": "Mumbai", "state": "Maharashtra", "lat": 19.0760, "lon": 72.8777, "type": "Coastal / Urban"},
    {"name": "Bengaluru", "state": "Karnataka", "lat": 12.9716, "lon": 77.5946, "type": "Plateau / Tech"},
    {"name": "Kolkata", "state": "West Bengal", "lat": 22.5726, "lon": 88.3639, "type": "Delta / Urban"},
    {"name": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lon": 80.2707, "type": "Coastal"},
    {"name": "Ludhiana", "state": "Punjab", "lat": 30.9010, "lon": 75.8573, "type": "Agricultural (Wheat/Rice)"},
    {"name": "Nagpur", "state": "Maharashtra", "lat": 21.1458, "lon": 79.0882, "type": "Agricultural (Cotton/Citrus)"},
    {"name": "Bhubaneswar", "state": "Odisha", "lat": 20.2961, "lon": 85.8245, "type": "Cyclone Prone Coast"},
    {"name": "Shimla", "state": "Himachal Pradesh", "lat": 31.1048, "lon": 77.1734, "type": "Himalayan / Horticulture"},
    {"name": "Hyderabad", "state": "Telangana", "lat": 17.3850, "lon": 78.4867, "type": "Semi-Arid / Urban"}
]
