import time
import uuid
from typing import Dict, Any, List

def evaluate_weather_alerts(current: Dict[str, Any], daily: List[Dict[str, Any]], aqi: Dict[str, Any], location_name: str) -> List[Dict[str, Any]]:
    """
    Evaluates meteorological thresholds according to IMD / WMO early warning criteria:
    - Red Alert: Take Action (Severe life/property threat)
    - Orange Alert: Be Prepared (Disruption likely)
    - Yellow Alert: Be Updated (Severe weather possible)
    - Green Alert: Normal weather
    Returns a list of structured CAP-compliant alert objects.
    """
    alerts: List[Dict[str, Any]] = []
    temp = current.get("temperature", 28.0)
    wind_speed = current.get("wind_speed", 10.0)
    wind_gusts = current.get("wind_gusts", 15.0)
    precip = current.get("precipitation", 0.0)
    w_code = current.get("weather_code", 0)
    us_aqi = aqi.get("us_aqi", 70)

    # 1. Extreme Heatwave Warning
    if temp >= 44.0:
        alerts.append({
            "id": f"CAP-HW-{uuid.uuid4().hex[:8].upper()}",
            "headline": f"Severe Heatwave Warning for {location_name}",
            "event": "Severe Heatwave (लू)",
            "severity": "Extreme",
            "urgency": "Immediate",
            "certainty": "Observed",
            "color": "#ef4444",
            "color_code": "RED",
            "action": "Take Action",
            "description": f"Maximum temperature has soared to {temp}°C with high solar insolation.",
            "instruction": "Avoid outdoor exposure between 11 AM and 4 PM. Keep hydrated with ORS, buttermilk, and lemon water. Ensure shade for livestock.",
            "target_sectors": ["Public Health", "Agriculture", "Labor", "Power Grid"],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })
    elif temp >= 40.0:
        alerts.append({
            "id": f"CAP-HW-{uuid.uuid4().hex[:8].upper()}",
            "headline": f"Heatwave Advisory for {location_name}",
            "event": "Heatwave",
            "severity": "Severe",
            "urgency": "Expected",
            "certainty": "Likely",
            "color": "#f97316",
            "color_code": "ORANGE",
            "action": "Be Prepared",
            "description": f"Daytime temperatures reaching {temp}°C. Vulnerable populations at risk of dehydration.",
            "instruction": "Wear loose cotton clothing, carry water bottles, schedule heavy fieldwork during early morning hours.",
            "target_sectors": ["Public Health", "Agriculture"],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })

    # 2. Heavy Rainfall / Urban Inundation Warning
    daily_precip_max = max([d.get("precip_sum", 0.0) for d in daily[:2]], default=0.0)
    if precip >= 15.0 or daily_precip_max >= 65.0 or w_code in (65, 82):
        alerts.append({
            "id": f"CAP-RAIN-{uuid.uuid4().hex[:8].upper()}",
            "headline": f"Very Heavy Rainfall & Waterlogging Alert for {location_name}",
            "event": "Heavy Rainfall / Urban Flood Risk",
            "severity": "Severe",
            "urgency": "Immediate",
            "certainty": "Observed",
            "color": "#ef4444",
            "color_code": "RED",
            "action": "Take Action",
            "description": f"Heavy to very heavy downpours ({precip} mm/hr; up to {daily_precip_max} mm cumulative) likely to cause inundation.",
            "instruction": "Avoid low-lying underpasses and drains. Farmers should clear field drainage channels immediately to prevent root submersion.",
            "target_sectors": ["Disaster Management", "Traffic", "Agriculture", "Municipalities"],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })
    elif precip >= 5.0 or daily_precip_max >= 25.0 or w_code in (63, 81):
        alerts.append({
            "id": f"CAP-RAIN-{uuid.uuid4().hex[:8].upper()}",
            "headline": f"Moderate to Heavy Rain Warning for {location_name}",
            "event": "Heavy Rain Watch",
            "severity": "Moderate",
            "urgency": "Expected",
            "certainty": "Likely",
            "color": "#eab308",
            "color_code": "YELLOW",
            "action": "Be Updated",
            "description": f"Continuous showers anticipated. Localized ponding of roads and slow traffic movement expected.",
            "instruction": "Check weather updates before traveling. Delay application of non-systemic agrochemicals.",
            "target_sectors": ["Traffic", "Agriculture"],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })

    # 3. Severe Thunderstorm & Squall / Lightning Warning
    if w_code in (95, 96, 99) or wind_gusts >= 50.0:
        alerts.append({
            "id": f"CAP-TS-{uuid.uuid4().hex[:8].upper()}",
            "headline": f"Severe Thunderstorm, Lightning & High Gusts in {location_name}",
            "event": "Thunderstorm & Lightning (वज्रपात)",
            "severity": "Severe",
            "urgency": "Immediate",
            "certainty": "Observed",
            "color": "#f97316",
            "color_code": "ORANGE",
            "action": "Be Prepared",
            "description": f"Convective cloud formation with high lightning frequency and surface squalls up to {wind_gusts} km/h.",
            "instruction": "Seek shelter in sturdy pucca structures immediately. DO NOT take shelter under tall isolated trees or electric poles.",
            "target_sectors": ["Public Safety", "Aviation", "Power Distribution"],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })

    # 4. Cyclone / Strong Coastal Wind Warning
    if wind_speed >= 45.0 or wind_gusts >= 65.0:
        alerts.append({
            "id": f"CAP-CYC-{uuid.uuid4().hex[:8].upper()}",
            "headline": f"Deep Gale & High Sea Surge Warning near {location_name}",
            "event": "Coastal Gale / Severe Storm Surge",
            "severity": "Extreme",
            "urgency": "Immediate",
            "certainty": "Observed",
            "color": "#ef4444",
            "color_code": "RED",
            "action": "Take Action",
            "description": f"Sustained gale winds of {wind_speed} km/h with gusts exceeding {wind_gusts} km/h.",
            "instruction": "Fishermen strictly advised not to venture into deep sea or coastal waters. Secure thatched roofs, boats, and coastal assets.",
            "target_sectors": ["Fisheries", "Marine / Ports", "Coast Guard", "Disaster Management"],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })

    # 5. Air Quality & Smog Emergency
    if us_aqi >= 250:
        alerts.append({
            "id": f"CAP-AQI-{uuid.uuid4().hex[:8].upper()}",
            "headline": f"Severe Air Quality Health Emergency in {location_name}",
            "event": "Toxic Air Pollution (AQI > 250)",
            "severity": "Severe",
            "urgency": "Immediate",
            "certainty": "Observed",
            "color": "#7f1d1d",
            "color_code": "RED",
            "action": "Take Action",
            "description": f"Current AQI is {us_aqi} ({aqi.get('category')}). Fine particulate matter poses acute respiratory hazard.",
            "instruction": "Wear N95 masks outdoors. Keep windows shut. Children, asthmatics, and elderly must restrict all outdoor physical activities.",
            "target_sectors": ["Public Health", "Schools", "Urban Transport"],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })

    # If no severe alerts triggered, return a standard Green advisory
    if not alerts:
        alerts.append({
            "id": f"CAP-NORM-{uuid.uuid4().hex[:8].upper()}",
            "headline": f"No Severe Weather Warnings for {location_name}",
            "event": "Normal Synoptic Conditions",
            "severity": "Minor",
            "urgency": "Future",
            "certainty": "Likely",
            "color": "#22c55e",
            "color_code": "GREEN",
            "action": "No Action Required",
            "description": f"Current weather is stable ({current.get('condition', 'Fair')}, {temp}°C). No meteorological hazard criteria met.",
            "instruction": "Routine outdoor agricultural and civic operations can proceed smoothly.",
            "target_sectors": ["General Public", "All Sectors"],
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })

    return alerts

def get_simulated_live_feed() -> List[Dict[str, Any]]:
    """Simulates active early warning bulletins across India (e.g. from IMD/CAP portal)."""
    return [
        {
            "region": "Coastal Odisha & West Bengal",
            "event": "Depression over Bay of Bengal (Low Pressure)",
            "color_code": "ORANGE",
            "severity": "Severe",
            "valid_until": "Next 48 Hours",
            "guidance": "Fishermen advised not to venture into southwest and westcentral Bay of Bengal. Squally wind speed 45-55 kmph gusting to 65 kmph."
        },
        {
            "region": "Northwest India (Punjab, Haryana, Delhi)",
            "event": "Heatwave Conditions in Isolated Pockets",
            "color_code": "YELLOW",
            "severity": "Moderate",
            "valid_until": "Next 72 Hours",
            "guidance": "Maximum temperatures likely to remain 2-3°C above normal. Adequate hydration advised for outdoor labor."
        },
        {
            "region": "Assam & Meghalaya",
            "event": "Heavy to Very Heavy Rainfall Activity",
            "color_code": "RED",
            "severity": "Extreme",
            "valid_until": "Next 24 Hours",
            "guidance": "Localized flooding in low-lying areas and landslide hazard in vulnerable hilly terrain. NDRF units on alert."
        },
        {
            "region": "Konkan & Goa Coast",
            "event": "High Swell Waves & Sea Surge Alert",
            "color_code": "YELLOW",
            "severity": "Moderate",
            "valid_until": "Next 36 Hours",
            "guidance": "Swell surge height 2.2 to 2.8 meters during spring high tide. Small harbor craft to stay moored."
        }
    ]
