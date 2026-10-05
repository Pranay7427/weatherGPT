import math
from typing import Dict, Any, List

def generate_agricultural_advisory(current: Dict[str, Any], daily: List[Dict[str, Any]], crop: str = "General") -> Dict[str, Any]:
    """Generates precision agro-meteorological advisory for farmers."""
    temp = current.get("temperature", 28.0)
    humidity = current.get("humidity", 60)
    wind = current.get("wind_speed", 10.0)
    rain_next_48h = sum([d.get("precip_sum", 0.0) for d in daily[:2]])
    rain_prob_max = max([d.get("precip_prob_max", 0) for d in daily[:2]], default=0)

    # 1. Irrigation recommendation
    if rain_prob_max >= 50 or rain_next_48h >= 8.0:
        irrigation_status = "HOLD / POSTPONE"
        irrigation_color = "#eab308"
        irrigation_advice = (
            f"Significant rainfall ({rain_next_48h:.1f} mm, {rain_prob_max}% prob) expected within 48h. "
            f"Withhold tubewell/canal irrigation to prevent waterlogging and nitrogen leaching."
        )
    elif temp > 35.0:
        irrigation_status = "RECOMMENDED (EVENING)"
        irrigation_color = "#3b82f6"
        irrigation_advice = (
            f"High thermal stress (temp {temp}°C). Provide light irrigation during late evening or night "
            f"to moderate root-zone temperature and reduce evapotranspiration deficit."
        )
    else:
        irrigation_status = "NORMAL CYCLE"
        irrigation_color = "#22c55e"
        irrigation_advice = "Normal soil moisture regime. Carry out scheduled irrigation as per crop growth stage."

    # 2. Pesticide / Spraying suitability
    if wind >= 18.0:
        spray_suitability = "UNSUITABLE (HIGH WIND DRIFT)"
        spray_color = "#ef4444"
        spray_advice = f"Surface wind ({wind} km/h) exceeds safe drift threshold (15 km/h). Delay spray to prevent chemical drift and wastage."
    elif rain_prob_max >= 40:
        spray_suitability = "UNSUITABLE (WASH-OFF RISK)"
        spray_color = "#ef4444"
        spray_advice = f"Rain probability is {rain_prob_max}%. Rain wash-off will reduce pesticide/fungicide efficacy. Wait for a clear 6-hour window."
    else:
        spray_suitability = "OPTIMAL WINDOW"
        spray_color = "#22c55e"
        spray_advice = f"Calm winds ({wind} km/h) and clear skies. Ideal window for foliar insecticide/nutrient application."

    # 3. Pest & Disease risk index
    if humidity >= 75 and temp >= 22 and temp <= 30:
        pest_risk = "ELEVATED (Fungal & Bacterial Blight)"
        pest_color = "#f97316"
        pest_advice = "Warm and humid microclimate favors blast, rust, and leaf spot proliferation. Scout fields and inspect lower foliage."
    elif temp >= 38:
        pest_risk = "MODERATE (Sucking Pests / Aphids / Mites)"
        pest_color = "#eab308"
        pest_advice = "Dry heat fosters rapid reproduction of whiteflies and red spider mites. Inspect undersides of leaves."
    else:
        pest_risk = "LOW / NORMAL"
        pest_color = "#22c55e"
        pest_advice = "Favorable ambient conditions. Maintain regular field sanitation and trap monitoring."

    # 4. Livestock thermal index (THI)
    # Simplified Temperature-Humidity Index
    thi = 0.8 * temp + (humidity / 100.0) * (temp - 14.4) + 46.4
    if thi >= 80:
        livestock_status = "Severe Heat Stress"
        livestock_advice = "Keep cattle in well-ventilated shaded sheds, provide cold clean drinking water ad-libitum, and offer mineral licks."
    elif thi >= 72:
        livestock_status = "Mild Stress"
        livestock_advice = "Ensure adequate fan ventilation and fresh green fodder to maintain milk yield."
    else:
        livestock_status = "Comfort Zone"
        livestock_advice = "Animal comfort conditions are ideal."

    return {
        "crop": crop,
        "summary": f"48h Rain Forecast: {rain_next_48h:.1f} mm | Wind: {wind} km/h | Ambient: {temp}°C",
        "irrigation": {
            "status": irrigation_status,
            "color": irrigation_color,
            "advice": irrigation_advice
        },
        "spraying": {
            "status": spray_suitability,
            "color": spray_color,
            "advice": spray_advice
        },
        "pest_disease": {
            "risk_level": pest_risk,
            "color": pest_color,
            "advice": pest_advice
        },
        "livestock": {
            "thi_score": round(thi, 1),
            "status": livestock_status,
            "advice": livestock_advice
        }
    }

def generate_aviation_briefing(current: Dict[str, Any], daily: List[Dict[str, Any]], icao_code: str = "VIDP") -> Dict[str, Any]:
    """Generates synthetic METAR/TAF aviation meteorological briefing."""
    temp = current.get("temperature", 28.0)
    wind_dir = current.get("wind_direction", 270)
    wind_spd = current.get("wind_speed", 10.0)
    wind_kt = int(wind_spd * 0.539957)
    press = int(current.get("pressure", 1012.0))
    w_code = current.get("weather_code", 0)

    # Determine flight category
    # VFR: ceiling > 3000 ft and vis > 5 SM (8000m)
    # MVFR: ceiling 1000-3000 ft or vis 3-5 SM
    # IFR: ceiling 500-1000 ft or vis 1-3 SM
    # LIFR: ceiling < 500 ft or vis < 1 SM
    if w_code in (45, 48):  # Fog
        vis_meters = 400
        category = "LIFR (Low Instrument Flight Rules)"
        cat_color = "#dc2626"
        cloud_str = "VV002"
        weather_str = "FG"
    elif w_code in (65, 82, 95, 96, 99):  # Heavy rain / TS
        vis_meters = 2500
        category = "IFR (Instrument Flight Rules)"
        cat_color = "#ea580c"
        cloud_str = "BKN015CB"
        weather_str = "+TSRA" if w_code >= 95 else "+RA"
    elif w_code in (61, 63, 80, 81):  # Rain
        vis_meters = 4500
        category = "MVFR (Marginal VFR)"
        cat_color = "#ca8a04"
        cloud_str = "SCT025 BKN040"
        weather_str = "RA"
    elif w_code == 3:  # Overcast
        vis_meters = 8000
        category = "MVFR"
        cat_color = "#ca8a04"
        cloud_str = "OVC025"
        weather_str = "NSW"
    else:
        vis_meters = 9999
        category = "VFR (Visual Flight Rules)"
        cat_color = "#16a34a"
        cloud_str = "FEW040"
        weather_str = "NOSIG"

    # Synthetic METAR line
    # Format: VIDP 041200Z 27010KT 9999 FEW040 28/19 Q1012 NOSIG
    dew_point = int(temp - ((100 - current.get("humidity", 60)) / 5))
    metar = (
        f"{icao_code} 041200Z {wind_dir:03d}{wind_kt:02d}KT "
        f"{vis_meters:04d} {weather_str if weather_str != 'NOSIG' else ''} "
        f"{cloud_str} {int(temp):02d}/{dew_point:02d} Q{press} {weather_str}"
    ).replace("  ", " ")

    # TAF line
    taf = (
        f"TAF {icao_code} 041200Z 0412/0518 {wind_dir:03d}{wind_kt:02d}KT 9999 {cloud_str} "
        f"TEMPO 0418/0422 4000 SHRA SCT020CB BECMG 0502/0504 {wind_dir:03d}{max(4, wind_kt-2):02d}KT"
    )

    # Runway crosswind component for runway 09/27 (heading 090 / 270)
    runway_hdg = 270
    crosswind = round(abs(wind_kt * math.sin(math.radians(wind_dir - runway_hdg))), 1)
    headwind = round(wind_kt * math.cos(math.radians(wind_dir - runway_hdg)), 1)

    return {
        "icao_station": icao_code,
        "flight_category": category,
        "category_color": cat_color,
        "metar": metar,
        "taf": taf,
        "visibility_meters": vis_meters,
        "ceiling": "2,500 ft AGL" if category != "VFR" else "> 5,000 ft AGL",
        "wind": f"{wind_dir}° at {wind_kt} knots ({wind_spd} km/h)",
        "crosswind_kt": crosswind,
        "headwind_kt": headwind,
        "runway_recommendation": f"Runway 27 (Crosswind: {crosswind} kt, Headwind: {headwind} kt)",
        "hazards": [
            "Convective CB cloud clusters within 25nm" if w_code in (95, 96, 99) else None,
            "Low-level wind shear potential near frontal boundary" if wind_kt > 18 else None,
            "Reduced runway friction coefficient due to wet surface" if w_code in (61, 63, 65, 80, 81, 82) else None
        ]
    }

def generate_marine_advisory(current: Dict[str, Any], location_name: str) -> Dict[str, Any]:
    """Generates maritime and coastal safety advisories for fishermen and port authorities."""
    wind_kmh = current.get("wind_speed", 12.0)
    wind_gusts = current.get("wind_gusts", 18.0)
    wind_knots = round(wind_kmh * 0.539957, 1)

    # Wave height estimation via empirical coastal fetch formula
    # H_s ≈ 0.025 * (wind_kmh ** 1.3)
    sig_wave_height = round(0.022 * (wind_kmh ** 1.35), 2)
    sig_wave_height = max(0.4, min(6.5, sig_wave_height))

    # Swell period (seconds)
    swell_period = round(4.5 + (wind_knots * 0.2), 1)

    # Douglas Sea Scale
    if sig_wave_height < 0.5:
        sea_state = "Smooth (Wave 0.1 - 0.5 m)"
        safety = "SAFE FOR ALL VESSELS"
        safety_color = "#22c55e"
    elif sig_wave_height < 1.25:
        sea_state = "Slight (Wave 0.5 - 1.25 m)"
        safety = "SAFE FOR FISHING"
        safety_color = "#22c55e"
    elif sig_wave_height < 2.5:
        sea_state = "Moderate (Wave 1.25 - 2.5 m)"
        safety = "CAUTION FOR SMALL CRAFT"
        safety_color = "#eab308"
    elif sig_wave_height < 4.0:
        sea_state = "Rough (Wave 2.5 - 4.0 m)"
        safety = "RESTRICTED (FISHERMEN DO NOT VENTURE)"
        safety_color = "#f97316"
    else:
        sea_state = "Very Rough / High (Wave > 4.0 m)"
        safety = "STRICT PROHIBITION (HARBOR MOORING)"
        safety_color = "#ef4444"

    return {
        "location": location_name,
        "sea_state": sea_state,
        "safety_level": safety,
        "safety_color": safety_color,
        "sig_wave_height_m": sig_wave_height,
        "swell_period_sec": swell_period,
        "wind_knots": wind_knots,
        "wind_gusts_knots": round(wind_gusts * 0.539957, 1),
        "guidance": (
            f"Significant wave height estimated at {sig_wave_height} m with a swell period of {swell_period} s. "
            f"Wind speed {wind_knots} knots with gusts to {round(wind_gusts * 0.539957, 1)} knots. "
            f"{'Fishermen are advised to maintain offshore communication and stay within 10 nautical miles.' if 'CAUTION' in safety else 'Clear waters. Operations can proceed normally.' if 'SAFE' in safety else 'High seas alert. Cease all shoreline and deep-sea netting operations immediately.'}"
        )
    }

def generate_urban_smart_city_advisory(current: Dict[str, Any], aqi: Dict[str, Any], location_name: str) -> Dict[str, Any]:
    """Generates urban analytics: Urban Heat Island, Waterlogging Risk, and Construction Safety."""
    temp = current.get("temperature", 28.0)
    precip = current.get("precipitation", 0.0)
    wind = current.get("wind_speed", 10.0)
    us_aqi = aqi.get("us_aqi", 70)

    # Urban Heat Island (UHI) Index (0 to 10 scale)
    # High temp + low wind = intense urban heat trapping
    uhi_intensity = max(1.0, min(10.0, ((temp - 25.0) * 0.4) + (max(0, 15.0 - wind) * 0.2)))
    if uhi_intensity > 7.0:
        uhi_label = "Severe Urban Heat Trapping"
        uhi_color = "#ef4444"
    elif uhi_intensity > 4.0:
        uhi_label = "Moderate Heat Microclimate"
        uhi_color = "#f97316"
    else:
        uhi_label = "Low / Well Ventilated"
        uhi_color = "#22c55e"

    # Waterlogging & Drainage Inundation Risk (0 to 100%)
    if precip >= 20.0:
        flood_risk_pct = 90
        flood_status = "CRITICAL INUNDATION"
        flood_color = "#ef4444"
    elif precip >= 10.0:
        flood_risk_pct = 70
        flood_status = "MODERATE WATERLOGGING"
        flood_color = "#f97316"
    elif precip >= 3.0:
        flood_risk_pct = 40
        flood_status = "LOCALIZED PUDDLING"
        flood_color = "#eab308"
    else:
        flood_risk_pct = 10
        flood_status = "MINIMAL DRAINAGE LOAD"
        flood_color = "#22c55e"

    # Construction & Outdoor Labor Index
    if temp >= 42.0 or us_aqi >= 300:
        labor_suitability = "HALT / UNSAFE"
        labor_color = "#ef4444"
        labor_action = "Suspend high-altitude crane operations and exposed physical labor. Mandatory heat/pollution recess."
    elif temp >= 37.0 or us_aqi >= 150:
        labor_suitability = "RESTRICTED HOURS"
        labor_color = "#f97316"
        labor_action = "Rotate outdoor shifts; supply electrolyte hydration; deploy dust suppression water sprinklers."
    else:
        labor_suitability = "FAVORABLE"
        labor_color = "#22c55e"
        labor_action = "Civic construction and transit operations can proceed as scheduled."

    return {
        "location": location_name,
        "uhi_index": round(uhi_intensity, 1),
        "uhi_status": uhi_label,
        "uhi_color": uhi_color,
        "flood_risk_pct": flood_risk_pct,
        "flood_status": flood_status,
        "flood_color": flood_color,
        "labor_suitability": labor_suitability,
        "labor_color": labor_color,
        "labor_action": labor_action,
        "air_quality_summary": f"AQI {us_aqi} ({aqi.get('category', 'Moderate')}) - PM2.5: {aqi.get('pm2_5', 25)} µg/m³"
    }
