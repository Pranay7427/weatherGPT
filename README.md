# WeatherGPT: Conversational AI for Weather Forecasting, Alerts & Climate Information

[![Live Demo](https://img.shields.io/badge/Live_Demo-weathergpt--olive--gamma.vercel.app-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://weathergpt-olive-gamma.vercel.app)
![WeatherGPT Banner](https://img.shields.io/badge/WeatherGPT-v2.0-blue?style=for-the-badge&logo=fastapi)
![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Zero GPU Required](https://img.shields.io/badge/Compute-Zero%20GPU%20Required-success?style=for-the-badge)
![Supported Languages](https://img.shields.io/badge/Languages-8%20Indian%20Languages-orange?style=for-the-badge)

> 🌐 **Live Web Application:** [https://weathergpt-olive-gamma.vercel.app](https://weathergpt-olive-gamma.vercel.app)

<div align="center">
  <br/>
  <a href="https://weathergpt-olive-gamma.vercel.app" target="_blank">
    <img src="https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=https%3A%2F%2Fweathergpt-olive-gamma.vercel.app&margin=10" alt="WeatherGPT Live QR Code" width="180" height="180"/>
  </a>
  <p><b>📱 Scan or click the QR code to open WeatherGPT on mobile/desktop</b></p>
  <br/>
</div>

WeatherGPT is an intelligent meteorological conversational platform engineered to unify fragmented weather bulletins, numerical weather predictions (NWP), disaster early warning systems, and climate reanalysis into an accessible, actionable natural language interface.

---

## Key Features

1. **Real-Time Meteorological Ingestion:**
   - Live surface observation: Temperature, feels-like, relative humidity, precipitation rate, barometric pressure, wind vector/gusts, cloud cover, visibility.
   - Comprehensive Air Quality Index (AQI): US AQI, European AQI, PM2.5, PM10, NO2, SO2, CO, and O3 with health impact advisories.

2. **Conversational AI Query Understanding Engine:**
   - Intent classifier recognizing agricultural inquiries, aviation briefings, maritime conditions, early warnings, climate trends, and general forecasts.
   - Grounded Dual-Core AI Architecture: Instant zero-latency built-in meteorological reasoning engine + optional Gemini 2.5 Flash cloud adapter.

3. **Numerical Weather Prediction (NWP) Multi-Model Comparison:**
   - Direct integration comparing **NOAA GFS (13 km)**, **ECMWF IFS (9 km)**, **DWD ICON (13 km)**, and downscaled **Mesoscale WRF (3 km)**.
   - Computes multi-model ensemble consensus mean, inter-model spread (standard deviation), and synoptic forecast confidence percentage.

4. **Extreme Weather Alerts & Early Warning Dissemination:**
   - Conforms to the standard **Common Alerting Protocol (CAP - ITU/WMO)** and **IMD 4-Stage Warning System** (Red, Orange, Yellow, Green).
   - Real-time early warnings for Cyclones, Heatwaves, Cloudbursts/Urban Floods, Severe Thunderstorms, and Toxic Smog emergencies.
   - WebSocket streaming channel (`/ws/alerts`) for instant notification pushes.

5. **Sector-Specific Decision Support Systems:**
   - **🌾 Agriculture & Farmers:** Precision crop-weather advisories for Wheat, Rice/Paddy, Cotton, Mustard, and Vegetables covering irrigation holds, pesticide spray windows, pest/disease risk, and livestock thermal humidity comfort (THI).
   - **✈️ Aviation:** Automated METAR and TAF generation, flight categories (VFR, MVFR, IFR, LIFR), runway crosswind calculation, and convective hazard warnings.
   - **🚢 Maritime & Fishermen:** Coastal Douglas sea state, significant wave height ($H_s$), swell periods, wind knots, and fishing vessel safety clearance.
   - **🏙️ Smart Cities:** Urban Heat Island (UHI) intensity index, drainage inundation risk, and outdoor labor safety thresholds.

6. **Multilingual Indian Language Support:**
   - Complete localized UI and conversational response generation across 8 languages:
     - English
     - हिन्दी (Hindi)
     - বাংলা (Bengali)
     - తెలుగు (Telugu)
     - தமிழ் (Tamil)
     - मराठी (Marathi)
     - ગુજરાતી (Gujarati)
     - ಕನ್ನಡ (Kannada)

7. **Voice-Enabled Rural Accessibility:**
   - Speech-to-Text (STT) voice querying with dialect recognition (`hi-IN`, `bn-IN`, `te-IN`, etc.).
   - Text-to-Speech (TTS) audio response playback for farmers and rural accessibility.

8. **Interactive GIS Radar & Climate Analytics:**
   - Interactive Leaflet map featuring real-time RainViewer Doppler precipitation radar tiles with timeline animation.
   - 30-year climate reanalysis (1995–2024), decadal warming rates, and extreme heat day frequency analysis.

---

## Architecture Diagram

```
                 USER (Mobile / Web Client)
                            │
               Voice (STT) / Text Question
                            │
                            ▼
               WeatherGPT Modern Web UI
    (Glassmorphic, Responsive, Leaflet Radar, Chart.js)
                            │
                  REST / WebSocket Protocol
                            │
                            ▼
          FastAPI Backend & WeatherGPT Agent Core
                            │
              Understands User Intent & Sector
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
    Weather API         Alert Engine      Climate Archive
 (Open-Meteo / WMO)   (CAP / IMD feeds)  (ERA5 Reanalysis)
         │                  │                  │
         └──────────────────┼──────────────────┘
                            │
                            ▼
           Numerical Weather Prediction (NWP)
               (GFS vs ECMWF vs ICON vs WRF)
                            │
                            ▼
             Sector-Specific Advisory Generator
       (🌾 Agriculture | ✈️ Aviation | 🚢 Marine | 🏙️ City)
                            │
                            ▼
         Dual AI Engine (Built-in + Gemini Adapter)
                            │
                            ▼
             Natural Language & Multilingual
             Response + TTS Voice Synthesis
```

---

## Getting Started

### Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- No GPU required!

### Installation
```bash
# Clone or navigate to the directory
cd c:\Users\prana\OneDrive\Desktop\Project

# Install lightweight dependencies
pip install -r requirements.txt
```

### Running Locally
```bash
python run.py
```
Open your browser and navigate to: **`http://127.0.0.1:8000`**

### Running with Docker
```bash
docker-compose up --build
```

---

## Running Automated Tests
The repository includes automated unit tests covering weather observation retrieval, NWP multi-model consensus, decision support rules, and multilingual conversational NLU.

```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## REST API Documentation

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Serves the WeatherGPT Single Page Web Application |
| `/api/health` | `GET` | Service status, app version, and language stats |
| `/api/search` | `GET` | Geocoding search by city or district name |
| `/api/weather` | `GET` | Current weather, 24h hourly, 7-day daily, AQI, and alerts |
| `/api/nwp` | `GET` | Multi-model NWP forecast (GFS, ECMWF, ICON, WRF) & consensus |
| `/api/alerts` | `GET` | CAP-compliant early warnings & national disaster bulletin feed |
| `/api/advisory` | `GET` | Specialized decision support (Agriculture, Aviation, Marine, Urban) |
| `/api/climate` | `GET` | 30-year decadal temperature and precipitation trend reanalysis |
| `/api/chat` | `POST` | Conversational query understanding and multilingual response generation |
| `/ws/alerts` | `WS` | WebSocket channel for real-time hazard broadcast |
