import os
import asyncio
from typing import Optional, List
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.config import APP_TITLE, APP_VERSION, SUPPORTED_LANGUAGES, DEFAULT_LOCATIONS
from app.services.weather_service import search_location, get_current_and_forecast, get_air_quality
from app.services.nwp_service import get_nwp_comparison
from app.services.alert_service import evaluate_weather_alerts, get_simulated_live_feed
from app.services.advisory_engine import (
    generate_agricultural_advisory,
    generate_aviation_briefing,
    generate_marine_advisory,
    generate_urban_smart_city_advisory
)
from app.services.climate_service import get_climate_analytics
from app.services.llm_service import generate_conversational_response

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description="Conversational AI for Weather Forecasting, Early Warnings, NWP & Climate Decision Support"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active WebSocket connections for alert broadcast
active_websockets: List[WebSocket] = []

# Pydantic models for API requests
class ChatRequest(BaseModel):
    query: str
    latitude: float = 28.6139
    longitude: float = 77.2090
    location_name: str = "New Delhi"
    language: str = "en"
    gemini_api_key: Optional[str] = None
    sector: Optional[str] = None

# --- API Endpoints ---

@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "app": APP_TITLE,
        "version": APP_VERSION,
        "supported_languages_count": len(SUPPORTED_LANGUAGES)
    }

@app.get("/api/languages")
async def list_languages():
    return {"languages": SUPPORTED_LANGUAGES}

@app.get("/api/locations")
async def list_default_locations():
    return {"locations": DEFAULT_LOCATIONS}

@app.get("/api/search")
async def search_city(q: str = Query(..., min_length=1)):
    results = await search_location(q)
    return {"results": results}

@app.get("/api/weather")
async def get_weather(
    lat: float = Query(28.6139),
    lon: float = Query(77.2090),
    name: str = Query("New Delhi")
):
    """Retrieve combined real-time weather, forecasts, AQI, and CAP early warnings."""
    weather = await get_current_and_forecast(lat, lon)
    aqi = await get_air_quality(lat, lon)
    weather["aqi"] = aqi

    # Evaluate early warning alerts based on thresholds
    alerts = evaluate_weather_alerts(
        current=weather.get("current", {}),
        daily=weather.get("daily", []),
        aqi=aqi,
        location_name=name
    )
    weather["alerts"] = alerts
    weather["location_name"] = name
    return weather

@app.get("/api/nwp")
async def get_nwp(
    lat: float = Query(28.6139),
    lon: float = Query(77.2090)
):
    """Retrieve multi-model Numerical Weather Prediction comparison (GFS, ECMWF, ICON, WRF)."""
    return await get_nwp_comparison(lat, lon)

@app.get("/api/alerts")
async def get_alerts(
    lat: float = Query(28.6139),
    lon: float = Query(77.2090),
    name: str = Query("New Delhi")
):
    """Retrieve active meteorological early warnings and national bulletin feed."""
    weather = await get_current_and_forecast(lat, lon)
    aqi = await get_air_quality(lat, lon)
    local_alerts = evaluate_weather_alerts(weather.get("current", {}), weather.get("daily", []), aqi, name)
    national_feed = get_simulated_live_feed()

    return {
        "location": name,
        "local_alerts": local_alerts,
        "national_feed": national_feed
    }

@app.get("/api/advisory")
async def get_sector_advisory(
    sector: str = Query("agriculture", description="agriculture | aviation | marine | urban"),
    lat: float = Query(28.6139),
    lon: float = Query(77.2090),
    name: str = Query("New Delhi"),
    crop: str = Query("Wheat")
):
    """Retrieve specialized decision support advisories."""
    weather = await get_current_and_forecast(lat, lon)
    aqi = await get_air_quality(lat, lon)
    curr = weather.get("current", {})
    daily = weather.get("daily", [])

    sector_lower = sector.lower()
    if sector_lower == "agriculture":
        return {
            "sector": "agriculture",
            "data": generate_agricultural_advisory(curr, daily, crop=crop)
        }
    elif sector_lower == "aviation":
        return {
            "sector": "aviation",
            "data": generate_aviation_briefing(curr, daily, icao_code="VIDP" if "Delhi" in name else "VABB")
        }
    elif sector_lower == "marine":
        return {
            "sector": "marine",
            "data": generate_marine_advisory(curr, location_name=name)
        }
    elif sector_lower == "urban":
        return {
            "sector": "urban",
            "data": generate_urban_smart_city_advisory(curr, aqi, location_name=name)
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid sector. Supported: agriculture, aviation, marine, urban")

@app.get("/api/climate")
async def get_climate(
    lat: float = Query(28.6139),
    lon: float = Query(77.2090),
    name: str = Query("New Delhi")
):
    """Retrieve historical reanalysis and climate trend analytics."""
    return await get_climate_analytics(lat, lon, name)

@app.post("/api/chat")
async def chat_interaction(req: ChatRequest):
    """Conversational AI meteorological query endpoint."""
    weather = await get_current_and_forecast(req.latitude, req.longitude)
    aqi = await get_air_quality(req.latitude, req.longitude)
    weather["aqi"] = aqi

    # Detect specific crop in query if present
    q_lower = req.query.lower()
    crop_selected = "Wheat"
    if "rice" in q_lower or "paddy" in q_lower or "धान" in q_lower:
        crop_selected = "Rice"
    elif "cotton" in q_lower or "कपास" in q_lower:
        crop_selected = "Cotton"
    elif "mustard" in q_lower or "सरसों" in q_lower:
        crop_selected = "Mustard"
    elif "corn" in q_lower or "maize" in q_lower or "मक्का" in q_lower:
        crop_selected = "Maize"

    # Pre-generate advisories & alerts to ground the response
    advisory_data = None
    if req.sector == "aviation":
        advisory_data = generate_aviation_briefing(weather.get("current", {}), weather.get("daily", []))
    elif req.sector == "marine":
        advisory_data = generate_marine_advisory(weather.get("current", {}), req.location_name)
    elif req.sector == "urban":
        advisory_data = generate_urban_smart_city_advisory(weather.get("current", {}), aqi, req.location_name)
    else:
        advisory_data = generate_agricultural_advisory(weather.get("current", {}), weather.get("daily", []), crop=crop_selected)

    alerts_data = evaluate_weather_alerts(
        weather.get("current", {}), weather.get("daily", []), aqi, req.location_name
    )
    nwp_data = await get_nwp_comparison(req.latitude, req.longitude)
    climate_data = await get_climate_analytics(req.latitude, req.longitude, req.location_name)

    response = await generate_conversational_response(
        query=req.query,
        weather_data=weather,
        location_name=req.location_name,
        lang=req.language,
        api_key=req.gemini_api_key,
        advisory_data=advisory_data,
        alerts_data=alerts_data,
        nwp_data=nwp_data,
        climate_data=climate_data
    )
    return response

# --- WebSocket for Real-time Alert Dissemination ---
@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await websocket.accept()
    active_websockets.append(websocket)
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "CONNECTED",
            "message": "Connected to WeatherGPT Real-Time Early Warning Dissemination Network"
        })
        while True:
            # Heartbeat / receive incoming client messages
            data = await websocket.receive_text()
            # Echo or acknowledge
            await websocket.send_json({"type": "ACK", "received": data})
    except WebSocketDisconnect:
        active_websockets.remove(websocket)
    except Exception as e:
        if websocket in active_websockets:
            active_websockets.remove(websocket)

# Serve static files and single page app
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
@app.get("/api")
@app.get("/api/index.py")
async def root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "WeatherGPT API is running. UI initializing..."}

