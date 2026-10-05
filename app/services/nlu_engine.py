import re
import datetime
from typing import Dict, Any, Tuple, Optional, List

class WeatherNLUEngine:
    """
    Intelligent Meteorological Conversational Reasoning Engine for WeatherGPT.
    Directly answers user queries with agronomic science, meteorological criteria,
    and multilingual explanations.
    """

    CROP_KNOWLEDGE_BASE = {
        "rice": {
            "names": ["rice", "paddy", "धान", "चावल", "ধান", "వరి", "அரிசி", "भात", "ચોખા", "ಅಕ್ಕಿ"],
            "optimal_temp_min": 20.0,
            "optimal_temp_max": 35.0,
            "critical_cold_temp": 18.0,
            "water_need": "Very High (1,200 - 1,500 mm; requires 5 cm continuous standing water during vegetative & reproductive stages)",
            "soil_type": "Heavy clay or clay-loam with low percolation and high water retention capacity",
            "primary_season": "Kharif (Sowing: June-July; Harvesting: October-November) and Boro/Summer (Nov-May in WB/Odisha/Assam)",
            "sowing_months": [5, 6, 7],  # May, June, July
            "harvest_months": [10, 11, 12],
            "advisory_notes": (
                "Rice requires assured water supply or heavy monsoon rains. "
                "Temperatures dropping below 18°C during flowering trigger spikelet sterility. "
                "If sowing new crop late in the year, cold winter winds can severely damage yield."
            )
        },
        "wheat": {
            "names": ["wheat", "गेहूं", "গম", "గోధుమ", "கோதுமை", "गहू", "ઘઉં", "ಗೋಧಿ"],
            "optimal_temp_min": 12.0,
            "optimal_temp_max": 24.0,
            "critical_cold_temp": 4.0,
            "water_need": "Moderate (450 - 650 mm across 4 to 6 scheduled irrigations)",
            "soil_type": "Well-drained fertile loamy to clay-loamy soils",
            "primary_season": "Rabi (Sowing: late October to November; Harvesting: March-April)",
            "sowing_months": [10, 11],
            "harvest_months": [3, 4],
            "advisory_notes": "Requires cool winter climate for tillering. Crown Root Initiation (CRI) at 21 days after sowing is critical for first irrigation."
        },
        "cotton": {
            "names": ["cotton", "कपास", "তুলা", "పత్తి", "பருத்தி", "कापूस", "કપાસ", "ಹತ್ತಿ"],
            "optimal_temp_min": 21.0,
            "optimal_temp_max": 32.0,
            "critical_cold_temp": 16.0,
            "water_need": "Moderate (500 - 700 mm). Highly sensitive to waterlogging and root rot.",
            "soil_type": "Deep black soils (Regur) with good drainage",
            "primary_season": "Kharif (Sowing: April-June; Harvesting: October-December)",
            "sowing_months": [4, 5, 6],
            "harvest_months": [10, 11, 12],
            "advisory_notes": "Needs warm days and frost-free season (at least 180-200 frost-free days). Dry sunny weather is required during boll bursting."
        },
        "mustard": {
            "names": ["mustard", "sarson", "सरसों", "সরিষা", "ఆవాలు", "கடுகு", "मोहरी", "રાઈ", "ಸಾಸಿವೆ"],
            "optimal_temp_min": 15.0,
            "optimal_temp_max": 25.0,
            "critical_cold_temp": 5.0,
            "water_need": "Low (250 - 400 mm; 2-3 light irrigations at flowering and pod formation)",
            "soil_type": "Sandy loam to clay loam with good drainage",
            "primary_season": "Rabi (Sowing: October; Harvesting: February-March)",
            "sowing_months": [9, 10],
            "harvest_months": [2, 3],
            "advisory_notes": "Ideal low-water cash crop. Susceptible to aphid infestations if temperatures rise too early in spring."
        },
        "sugarcane": {
            "names": ["sugarcane", "cane", "गन्ना", "আখ", "చెరకు", "கரும்பு", "ऊस", "શેરડી", "ಕಬ್ಬು"],
            "optimal_temp_min": 22.0,
            "optimal_temp_max": 36.0,
            "critical_cold_temp": 15.0,
            "water_need": "Very High (1,500 - 2,500 mm perennial water requirement)",
            "soil_type": "Deep rich loamy soil with neutral pH (6.5 - 7.5)",
            "primary_season": "Annual / Perennial (Sowing: Oct-Nov Autumn or Feb-March Spring)",
            "sowing_months": [2, 3, 10, 11],
            "harvest_months": [1, 2, 11, 12],
            "advisory_notes": "Needs continuous hot sunny days with assured canal or tubewell irrigation."
        },
        "maize": {
            "names": ["maize", "corn", "मक्का", "ভুট্টা", "మొక్కజొన్న", "மக்காச்சோளம்", "मका", "મકાઈ", "ಮೆಕ್ಕೆಜೋಳ"],
            "optimal_temp_min": 20.0,
            "optimal_temp_max": 30.0,
            "critical_cold_temp": 10.0,
            "water_need": "Moderate (500 - 800 mm). Very sensitive to water stagnation at seedling stage.",
            "soil_type": "Well-drained sandy loam to silt loam rich in organic matter",
            "primary_season": "Kharif and Rabi (Versatile crop)",
            "sowing_months": [6, 7, 10, 11],
            "harvest_months": [9, 10, 2, 3],
            "advisory_notes": "Ensure field has drainage gradient. Water ponding for > 24 hours destroys maize root hair."
        }
    }

    LOCATION_PATTERNS = [
        r"(?:in|at|for|near|of|around)\s+([A-Za-z\s]+?)(?:\s+(?:today|tomorrow|yesterday|now|this|next)|\?|\.|\,|$)",
        r"([A-Za-z]+)\s+(?:weather|forecast|temperature|rain|alerts|climate)",
        r"(?:दिल्ली|मुंबई|बेंगलुरु|कोलकाता|चेन्नई|पुणे|पटना|शिमला|हैदराबाद|अहमदाबाद|लुधियाना|भुवनेश्वर)"
    ]

    def parse_query(self, query: str) -> Dict[str, Any]:
        """Deep intent and entity classification of user query."""
        q_lower = query.lower().strip()

        # 1. Detect Crop entity if any
        detected_crop = None
        for crop_key, crop_info in self.CROP_KNOWLEDGE_BASE.items():
            if any(name in q_lower for name in crop_info["names"]):
                detected_crop = crop_key
                break

        # 2. Detect Specific Question Intent
        detected_intent = "CURRENT_WEATHER"

        # Check for Crop Suitability / Farming Decision
        suitability_keywords = [
            "should i farm", "should i grow", "should i plant", "should i sow",
            "can i farm", "can i grow", "can i plant", "can i cultivate",
            "is it good to grow", "is it good to farm", "is rice suitable", "is wheat suitable",
            "farming of", "cultivation of", "खेती करूँ", "खेती कर सकते हैं", "लगाना चाहिए",
            "বোনা যাবে", "చాగు చేయవచ్చా", "பயிரிடலாமா", "લાગવડ કરવી"
        ]
        irrigation_keywords = [
            "irrigate", "irrigation", "water the crop", "watering", "should i water", "पानी देना", "सिंचाई", "সেচ", "నీరు పెట్టాలా"
        ]
        spray_keywords = [
            "spray", "spraying", "pesticide", "fungicide", "insecticide", "कीटनाशक", "छिड़काव", "স্প্রে", "పిచికారీ"
        ]
        rain_keywords = [
            "will it rain", "is it raining", "chance of rain", "rain tomorrow", "rainfall", "baarish", "बारिश", "বৃষ্টি", "వర్షం", "மழை", "पाऊस", "વરસાદ"
        ]
        aviation_keywords = [
            "aviation", "flight", "metar", "taf", "pilot", "runway", "crosswind", "takeoff", "landing", "विमान", "उड़ान"
        ]
        marine_keywords = [
            "marine", "sea", "ocean", "wave", "swell", "fisherman", "fishermen", "coast", "tide", "मछुआरे", "समुद्र", "लहरें"
        ]
        alerts_keywords = [
            "alert", "warning", "cyclone", "flood", "heatwave", "storm", "thunderstorm", "lightning", "चेतावनी", "अलर्ट", "तूफान"
        ]
        climate_keywords = [
            "climate", "historical", "trend", "global warming", "decadal", "anomaly", "past weather", "30 years", "जलवायु"
        ]

        outdoor_keywords = [
            "picnic", "outing", "outings", "day trip", "sightseeing", "hangout",
            "hiking", "hike", "trek", "trekking", "camping", "camp", "barbecue", "bbq",
            "outdoor party", "outdoor event", "garden party", "gather outside", "visit park",
            "पिकनिक", "घूमने", "सैर", "भ्रमण", "ভ্রমণ", "విహారయాత్ర", "சுற்றுலா", "सहलीला", "પિકનિક"
        ]
        sports_keywords = [
            "cricket", "football", "soccer", "badminton", "tennis", "running", "jogging", "cycling", "marathon", "मैच", "खेल", "दौड़ना"
        ]
        travel_keywords = [
            "travel", "trip", "drive", "driving", "road trip", "highway", "journey", "safe to travel", "यात्रा", "सफर", "गाड़ी चलाना"
        ]
        drying_keywords = [
            "dry clothes", "drying clothes", "wash clothes", "laundry", "कपड़े सुखाना", "कपड़े धोना"
        ]
        carwash_keywords = [
            "wash car", "car wash", "wash my car", "bike wash"
        ]
        clothing_keywords = [
            "what should i wear", "what to wear", "wear today", "wear tomorrow",
            "need a jacket", "need a coat", "need a sweater", "need an umbrella",
            "take an umbrella", "carry an umbrella", "raincoat", "warm clothes",
            "कपड़े पहनूं", "छाता ले जाऊं", "जैकेट चाहिए"
        ]
        health_keywords = [
            "air quality", "aqi", "safe to breathe", "pollution", "smog", "asthma", "allergy",
            "run outside", "jog outside", "safe for health", "वायु गुणवत्ता", "प्रदूषण"
        ]
        greeting_keywords = [
            "hi", "hello", "hey", "namaste", "who are you", "what can you do", "help", "नमस्ते"
        ]

        is_greeting = (
            any(kw in q_lower for kw in ["who are you", "what can you do", "what do you do", "help me", "namaste", "नमस्ते"])
            or any(q_lower.startswith(prefix) for prefix in ["hi ", "hello ", "hey ", "hi,", "hello,", "hey,"])
            or q_lower.strip("!?., ") in ["hi", "hello", "hey", "namaste", "help"]
        )

        if is_greeting:
            detected_intent = "GENERAL_GREETING"
        elif any(kw in q_lower for kw in clothing_keywords) or (("umbrella" in q_lower or "jacket" in q_lower or "sweater" in q_lower) and any(w in q_lower for w in ["need", "carry", "take", "should i", "wear", "require"])):
            detected_intent = "CLOTHING_ADVICE"
        elif any(kw in q_lower for kw in health_keywords) and any(w in q_lower for w in ["safe", "good", "bad", "level", "pollution", "health", "exercise", "jog", "outside", "today"]):
            detected_intent = "HEALTH_AIR_QUALITY"
        elif any(kw in q_lower for kw in outdoor_keywords) or (("picnic" in q_lower or "outing" in q_lower) and any(w in q_lower for w in ["suitable", "plan", "can i", "should i", "good", "go", "weather", "tomorrow", "tommorow"])):
            detected_intent = "OUTDOOR_ACTIVITY"
        elif any(kw in q_lower for kw in sports_keywords) and any(w in q_lower for w in ["play", "match", "can i", "should i", "good", "suitable", "weather", "tomorrow"]):
            detected_intent = "SPORTS_ACTIVITY"
        elif any(kw in q_lower for kw in travel_keywords) and any(w in q_lower for w in ["safe", "can i", "should i", "good", "weather", "condition", "road"]):
            detected_intent = "TRAVEL_ROAD"
        elif any(kw in q_lower for kw in drying_keywords):
            detected_intent = "DRYING_CLOTHES"
        elif any(kw in q_lower for kw in carwash_keywords):
            detected_intent = "CAR_WASH"
        elif any(kw in q_lower for kw in suitability_keywords) or (detected_crop and ("farm" in q_lower or "grow" in q_lower or "sow" in q_lower or "plant" in q_lower or "cultivate" in q_lower or "should i" in q_lower or "can i" in q_lower)):
            detected_intent = "CROP_SUITABILITY"
        elif any(kw in q_lower for kw in spray_keywords):
            detected_intent = "SPRAYING_DECISION"
        elif any(kw in q_lower for kw in irrigation_keywords):
            detected_intent = "IRRIGATION_DECISION"
        elif detected_crop or any(kw in q_lower for kw in ["crop", "farmer", "farming", "kisan", "krishi", "khet", "fertilizer", "urea"]):
            detected_intent = "AGRICULTURE"
        elif any(kw in q_lower for kw in aviation_keywords):
            detected_intent = "AVIATION"
        elif any(kw in q_lower for kw in marine_keywords):
            detected_intent = "MARINE"
        elif any(kw in q_lower for kw in alerts_keywords):
            detected_intent = "ALERTS"
        elif any(kw in q_lower for kw in climate_keywords):
            detected_intent = "CLIMATE"
        elif any(kw in q_lower for kw in rain_keywords):
            detected_intent = "RAIN_QUERY"
        elif any(kw in q_lower for kw in ["forecast", "tomorrow", "weekend", "next week", "7 days", "कल", "पूर्वानुमान"]):
            detected_intent = "FORECAST"

        # 3. Location Extraction
        extracted_location = None
        for pattern in self.LOCATION_PATTERNS:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                loc = match.group(1).strip() if match.groups() else match.group(0).strip()
                if loc.lower() not in ("today", "tomorrow", "now", "weather", "forecast", "the", "rice", "wheat", "crop", "picnic", "outing"):
                    extracted_location = loc
                    break

        known_cities = [
            "delhi", "new delhi", "mumbai", "bengaluru", "bangalore", "kolkata", "chennai",
            "hyderabad", "pune", "ahmedabad", "jaipur", "lucknow", "ludhiana", "shimla",
            "patna", "bhubaneswar", "guwahati", "chandigarh", "kochi", "goa", "odisha", "punjab", "bihar"
        ]
        for c in known_cities:
            if c in q_lower:
                extracted_location = c.title()
                break

        # 4. Time reference (handles common typos like tommorow)
        time_ref = "current"
        if any(w in q_lower for w in ["tomorrow", "tommorow", "tommorrow", "kal", "कल", "আগামীকাল", "రేపు", "நாளை", "उद्या", "આવતીકાલે", "ನಾಳೆ"]):
            time_ref = "tomorrow"
        elif any(w in q_lower for w in ["weekend", "saturday", "sunday", "शनिवार", "रविवार"]):
            time_ref = "weekend"
        elif any(w in q_lower for w in ["today", "aaj", "आज", "আজ", "ఈ రోజు", "இன்று"]):
            time_ref = "today"
        elif any(w in q_lower for w in ["week", "weekly", "next 7 days"]):
            time_ref = "week"

        return {
            "intent": detected_intent,
            "crop": detected_crop or "rice" if "rice" in q_lower or "paddy" in q_lower else None,
            "location": extracted_location,
            "time_horizon": time_ref,
            "raw_query": query
        }

    def generate_natural_response(
        self,
        intent: str,
        weather_data: Dict[str, Any],
        location_name: str,
        lang: str = "en",
        time_ref: str = "current",
        advisory_data: Optional[Dict[str, Any]] = None,
        alerts_data: Optional[List[Dict[str, Any]]] = None,
        nwp_data: Optional[Dict[str, Any]] = None,
        climate_data: Optional[Dict[str, Any]] = None,
        raw_query: str = ""
    ) -> Dict[str, Any]:
        """Synthesizes rich, direct, authoritative answers to user's exact questions."""
        curr = weather_data.get("current", {})
        temp = curr.get("temperature", 28.0)
        cond = curr.get("condition", "Partly cloudy")
        humidity = curr.get("humidity", 60)
        wind = curr.get("wind_speed", 10.0)
        rain = curr.get("precipitation", 0.0)
        daily = weather_data.get("daily", [])

        # -------------------------------------------------------------
        # CASE 1: CROP SUITABILITY / "SHOULD I FARM [CROP]?"
        # -------------------------------------------------------------
        parsed = self.parse_query(raw_query or "")
        crop_name = parsed.get("crop")
        if not crop_name and ("rice" in (raw_query or "").lower() or "paddy" in (raw_query or "").lower()):
            crop_name = "rice"
        elif not crop_name and "wheat" in (raw_query or "").lower():
            crop_name = "wheat"
        elif not crop_name and "cotton" in (raw_query or "").lower():
            crop_name = "cotton"
        elif not crop_name and "mustard" in (raw_query or "").lower():
            crop_name = "mustard"

        if intent == "CROP_SUITABILITY" or (crop_name and any(w in (raw_query or "").lower() for w in ["farm", "grow", "sow", "plant", "cultivate", "should i", "can i"])):
            return self._answer_crop_suitability(crop_name or "rice", temp, humidity, wind, rain, daily, location_name, lang)

        # -------------------------------------------------------------
        # CASE 1B: OUTDOOR ACTIVITY & PICNIC SUITABILITY
        # -------------------------------------------------------------
        if intent == "OUTDOOR_ACTIVITY" or any(w in (raw_query or "").lower() for w in ["picnic", "outing", "hangout", "पिकनिक", "घूमने"]):
            return self._answer_outdoor_activity(weather_data, location_name, lang, time_ref, raw_query)

        # -------------------------------------------------------------
        # CASE 1C: SPORTS & OUTDOOR GAMES SUITABILITY
        # -------------------------------------------------------------
        if intent == "SPORTS_ACTIVITY":
            return self._answer_sports_activity(weather_data, location_name, lang, time_ref, raw_query)

        # -------------------------------------------------------------
        # CASE 1D: TRAVEL & HIGHWAY DRIVING CONDITIONS
        # -------------------------------------------------------------
        if intent == "TRAVEL_ROAD":
            return self._answer_travel_road(weather_data, location_name, lang, time_ref, raw_query)

        # -------------------------------------------------------------
        # CASE 1E: DRYING CLOTHES / LAUNDRY DECISION
        # -------------------------------------------------------------
        if intent == "DRYING_CLOTHES":
            return self._answer_drying_clothes(weather_data, location_name, lang, time_ref, raw_query)

        # -------------------------------------------------------------
        # CASE 1F: CAR WASH DECISION
        # -------------------------------------------------------------
        if intent == "CAR_WASH":
            return self._answer_car_wash(weather_data, location_name, lang, time_ref, raw_query)

        # -------------------------------------------------------------
        # CASE 1G: CLOTHING & UMBRELLA ADVICE
        # -------------------------------------------------------------
        if intent == "CLOTHING_ADVICE":
            return self._answer_clothing_advice(weather_data, location_name, lang, time_ref, raw_query)

        # -------------------------------------------------------------
        # CASE 1H: HEALTH & AIR QUALITY / SMOG
        # -------------------------------------------------------------
        if intent == "HEALTH_AIR_QUALITY":
            return self._answer_health_air_quality(weather_data, location_name, lang, time_ref, raw_query)

        # -------------------------------------------------------------
        # CASE 1I: GENERAL GREETING & ASSISTANCE
        # -------------------------------------------------------------
        if intent == "GENERAL_GREETING":
            return self._answer_greeting(weather_data, location_name, lang, raw_query)

        # -------------------------------------------------------------
        # CASE 2: SPRAYING SUITABILITY DECISION
        # -------------------------------------------------------------
        if intent == "SPRAYING_DECISION":
            return self._answer_spraying_decision(temp, wind, humidity, daily, location_name, lang)

        # -------------------------------------------------------------
        # CASE 3: IRRIGATION DECISION
        # -------------------------------------------------------------
        if intent == "IRRIGATION_DECISION":
            return self._answer_irrigation_decision(temp, rain, daily, location_name, lang)

        # -------------------------------------------------------------
        # CASE 4: RAIN QUESTION ("Will it rain tomorrow / today?")
        # -------------------------------------------------------------
        if intent == "RAIN_QUERY":
            return self._answer_rain_query(curr, daily, location_name, lang, time_ref)

        # -------------------------------------------------------------
        # CASE 5: GENERAL AGRICULTURE ADVISORY
        # -------------------------------------------------------------
        if intent == "AGRICULTURE":
            agri = advisory_data or {}
            irr = agri.get("irrigation", {})
            spray = agri.get("spraying", {})
            pest = agri.get("pest_disease", {})

            if lang == "hi":
                text = (
                    f"🌾 **{location_name} के लिए कृषि मौसम सलाह (Kisan Advisory):**\n\n"
                    f"• **वर्तमान मौसम स्थिति:** तापमान {temp}°C, हवा {wind} km/h, आर्द्रता {humidity}%\n"
                    f"• **सिंचाई निर्णय:** {irr.get('advice', 'सामान्य चक्र बनाए रखें।')}\n"
                    f"• **कीटनाशक छिड़काव स्थिति:** {spray.get('advice', 'मौसम अनुकूल है।')}\n"
                    f"• **कीट व रोग चेतावनी:** {pest.get('advice', 'नियमित निगरानी रखें।')}\n\n"
                    f"💡 *टिप: आप किसी विशिष्ट फसल के बारे में भी पूछ सकते हैं, जैसे: 'क्या मुझे धान की खेती करनी चाहिए?' या 'गेहूं की बुवाई कब करें?'*"
                )
            else:
                text = (
                    f"🌾 **Agricultural Weather Decision Support for {location_name}:**\n\n"
                    f"• **Current Microclimate:** {temp}°C, {cond}, Wind: {wind} km/h, Humidity: {humidity}%\n"
                    f"• **Irrigation Action:** {irr.get('advice', 'Normal soil moisture regime.')}\n"
                    f"• **Spraying Window ({spray.get('status', 'Optimal')}):** {spray.get('advice')}\n"
                    f"• **Pest & Disease Outlook ({pest.get('risk_level', 'Low')}):** {pest.get('advice')}\n\n"
                    f"💡 *Pro-Tip: Ask specific crop questions like 'Should I farm rice?', 'Can I spray pesticide on wheat?', or 'When to harvest?'*"
                )
            return {"intent": intent, "location": location_name, "text": text, "temperature": temp, "condition": cond, "language": lang}

        # -------------------------------------------------------------
        # CASE 6: AVIATION BRIEFING
        # -------------------------------------------------------------
        if intent == "AVIATION":
            av = advisory_data or {}
            text = (
                f"✈️ **Aviation Weather Briefing for {location_name} ({av.get('icao_station', 'ICAO')}):**\n\n"
                f"• **Flight Category:** **{av.get('flight_category', 'VFR')}**\n"
                f"• **METAR:** `{av.get('metar', '')}`\n"
                f"• **TAF:** `{av.get('taf', '')}`\n"
                f"• **Surface Wind:** {av.get('wind', '')} | **Ceiling:** {av.get('ceiling', '')}\n"
                f"• **Active Runway:** {av.get('runway_recommendation', 'Runway 27')}\n"
                f"• **Hazards Identified:** {', '.join([h for h in av.get('hazards', []) if h]) or 'No significant convective or turbulence hazards reported.'}"
            )
            return {"intent": intent, "location": location_name, "text": text, "temperature": temp, "condition": cond, "language": lang}

        # -------------------------------------------------------------
        # CASE 7: MARINE & COASTAL
        # -------------------------------------------------------------
        if intent == "MARINE":
            mar = advisory_data or {}
            text = (
                f"🚢 **Maritime & Coastal Safety Bulletin for {location_name}:**\n\n"
                f"• **Sea State:** {mar.get('sea_state', 'Moderate')}\n"
                f"• **Safety Rating:** **{mar.get('safety_level', 'CAUTION')}**\n"
                f"• **Significant Wave Height:** {mar.get('sig_wave_height_m', 1.2)} meters\n"
                f"• **Swell Period:** {mar.get('swell_period_sec', 6.0)} seconds\n"
                f"• **Wind Speed:** {mar.get('wind_knots', 10.0)} knots (Gusts: {mar.get('wind_gusts_knots', 15.0)} kt)\n"
                f"• **Operational Advisory:** {mar.get('guidance', 'Navigate with standard coastal precautions.')}"
            )
            return {"intent": intent, "location": location_name, "text": text, "temperature": temp, "condition": cond, "language": lang}

        # -------------------------------------------------------------
        # CASE 8: DISASTER ALERTS
        # -------------------------------------------------------------
        if intent == "ALERTS":
            active_alerts = alerts_data or []
            first_alert = active_alerts[0] if active_alerts else {}
            if lang == "hi":
                text = (
                    f"🚨 **{location_name} के लिए आपदा व मौसम चेतावनी बुलेटिन (IMD/CAP Feed):**\n\n"
                    f"• **चेतावनी स्तर:** **{first_alert.get('color_code', 'GREEN')} ALERT** ({first_alert.get('action', 'अपडेट रहें')})\n"
                    f"• **घटना:** {first_alert.get('event', 'सामान्य मौसम')}\n"
                    f"• **विवरण:** {first_alert.get('description', 'कोई गंभीर मौसम खतरा दर्ज नहीं है।')}\n"
                    f"• **सुरक्षा निर्देश:** {first_alert.get('instruction', 'सामान्य गतिविधियां जारी रख सकते हैं।')}"
                )
            else:
                text = (
                    f"🚨 **Early Warning & Disaster Bulletin for {location_name}:**\n\n"
                    f"• **Alert Status:** **{first_alert.get('color_code', 'GREEN')} ALERT** — {first_alert.get('action', 'No Action Needed')}\n"
                    f"• **Hazard Event:** {first_alert.get('event', 'Stable Weather')}\n"
                    f"• **Meteorological Description:** {first_alert.get('description', 'No active extreme weather alerts.')}\n"
                    f"• **Recommended Protection Action:** {first_alert.get('instruction', 'Maintain standard weather awareness.')}\n"
                    f"• **Target Sectors:** {', '.join(first_alert.get('target_sectors', ['General Public']))}"
                )
            return {"intent": intent, "location": location_name, "text": text, "temperature": temp, "condition": cond, "language": lang}

        # -------------------------------------------------------------
        # CASE 9: CLIMATE TRENDS
        # -------------------------------------------------------------
        if intent == "CLIMATE":
            clim = climate_data or {}
            text = (
                f"📈 **Climate Trend & Historical Reanalysis for {location_name}:**\n\n"
                f"• **Baseline Reference Period:** {clim.get('baseline_period', '1991-2020')}\n"
                f"• **Regional Decadal Warming Rate:** +{clim.get('decadal_warming_rate_c', 0.22)}°C / decade\n"
                f"• **Cumulative Warming Since 1995:** +{clim.get('net_warming_since_1995_c', 1.29)}°C\n"
                f"• **Key Climatological Findings:**\n"
                + "\n".join([f"  - {insight}" for insight in clim.get("research_insights", [])[:3]])
            )
            return {"intent": intent, "location": location_name, "text": text, "temperature": temp, "condition": cond, "language": lang}

        # -------------------------------------------------------------
        # CASE 10: MULTI-DAY FORECAST
        # -------------------------------------------------------------
        if intent == "FORECAST":
            if time_ref == "tomorrow" and len(daily) > 1:
                tm = daily[1]
                if lang == "hi":
                    text = (
                        f"📅 **{location_name} में कल का मौसम पूर्वानुमान:**\n\n"
                        f"• **मौसम स्थिति:** {tm.get('condition')} ({tm.get('temp_max')}°C / {tm.get('temp_min')}°C)\n"
                        f"• **बारिश की संभावना:** {tm.get('precip_prob_max')}% (संभावित मात्रा: {tm.get('precip_sum')} mm)\n"
                        f"• **हवा की अधिकतम गति:** {tm.get('wind_max')} km/h | **यूवी इंडेक्स:** {tm.get('uv_index_max')}\n"
                        f"• **सूर्योदय / सूर्यास्त:** {tm.get('sunrise')} / {tm.get('sunset')}"
                    )
                else:
                    text = (
                        f"📅 **Tomorrow's Weather Forecast for {location_name}:**\n\n"
                        f"• **Condition:** {tm.get('condition')}\n"
                        f"• **Temperature:** High: {tm.get('temp_max')}°C | Low: {tm.get('temp_min')}°C\n"
                        f"• **Precipitation:** {tm.get('precip_prob_max')}% chance ({tm.get('precip_sum')} mm)\n"
                        f"• **Wind & UV:** Max wind {tm.get('wind_max')} km/h, Peak UV {tm.get('uv_index_max')}\n"
                        f"• **Sunrise / Sunset:** {tm.get('sunrise')} AM / {tm.get('sunset')} PM"
                    )
            else:
                days_summary = [f"• **{d.get('date')}**: {d.get('condition')}, {d.get('temp_max')}°C / {d.get('temp_min')}°C (Rain: {d.get('precip_prob_max')}%)" for d in daily[:5]]
                text = f"📅 **5-Day Weather Outlook for {location_name}:**\n\n" + "\n".join(days_summary)
            return {"intent": intent, "location": location_name, "text": text, "temperature": temp, "condition": cond, "language": lang}

        # -------------------------------------------------------------
        # DEFAULT: CURRENT WEATHER
        # -------------------------------------------------------------
        if lang == "hi":
            text = (
                f"🌤️ **{location_name} में वर्तमान मौसम स्थिति:**\n\n"
                f"• **स्थिति:** {cond}\n"
                f"• **तापमान:** {temp}°C (महसूस: {curr.get('apparent_temperature')}°C)\n"
                f"• **हवा:** {wind} km/h (दिशा: {curr.get('wind_direction')}°)\n"
                f"• **नमी:** {humidity}% | **वर्षा:** {rain} mm\n"
                f"• **वायुमंडलीय दबाव:** {curr.get('pressure')} hPa"
            )
        else:
            text = (
                f"🌤️ **Current Weather in {location_name}:**\n\n"
                f"• **Condition:** {cond}\n"
                f"• **Temperature:** {temp}°C (Feels like: {curr.get('apparent_temperature')}°C)\n"
                f"• **Wind:** {wind} km/h from {curr.get('wind_direction')}° (Gusts: {curr.get('wind_gusts')} km/h)\n"
                f"• **Relative Humidity:** {humidity}% | Precipitation: {rain} mm\n"
                f"• **Barometric Pressure:** {curr.get('pressure')} hPa"
            )

        return {"intent": intent, "location": location_name, "text": text, "temperature": temp, "condition": cond, "language": lang}

    # =================================================================
    # SPECIALIZED QUESTION-ANSWERING REASONING METHODS
    # =================================================================

    def _answer_crop_suitability(
        self,
        crop_key: str,
        current_temp: float,
        humidity: int,
        wind_speed: float,
        rain: float,
        daily: List[Dict[str, Any]],
        location_name: str,
        lang: str
    ) -> Dict[str, Any]:
        """Provides an authoritative agronomic assessment for planting/farming a specific crop."""
        crop_info = self.CROP_KNOWLEDGE_BASE.get(crop_key, self.CROP_KNOWLEDGE_BASE["rice"])
        current_month = datetime.datetime.now().month  # e.g., 9 for September

        is_sowing_season = current_month in crop_info["sowing_months"]
        is_harvest_season = current_month in crop_info["harvest_months"]
        temp_suitable = crop_info["optimal_temp_min"] <= current_temp <= crop_info["optimal_temp_max"]
        cold_threat = current_temp < crop_info["critical_cold_temp"]

        # Formulate Verdict
        if crop_key == "rice":
            if current_month in [5, 6, 7]:  # Kharif onset
                verdict = "YES - OPTIMAL SEASON FOR KHARIF RICE"
                verdict_status = "✅ Favorable"
                action_advice = "The monsoon window is ideal. Ensure nursery transplantation into puddled fields with 5 cm standing water."
            elif current_month in [8, 9]:  # Late Kharif
                verdict = "CAUTION - LATE FOR NEW SOWING; SUITABLE FOR STANDING CROP"
                verdict_status = "⚠️ Late Sowing Not Recommended"
                action_advice = (
                    "If you already have a **standing rice crop**, current conditions (temp "
                    f"{current_temp}°C) are good for panicle heading and grain filling. Maintain shallow water (2-3 cm).\n\n"
                    "However, **sowing a NEW rice nursery now is NOT recommended** in North/Central India because upcoming "
                    "winter cold (< 18°C) will cause spikelet sterility and major yield loss. Instead, start preparing your fields "
                    "for **Rabi crops (Wheat, Mustard, Chickpea/Gram)** starting October."
                )
            elif current_month in [11, 12, 1]:  # Winter (Boro season in East/South)
                verdict = "CONDITIONAL (BORO RICE ONLY IN EASTERN/SOUTHERN DELTAS)"
                verdict_status = "⚠️ Requires Assured Tubewell Irrigation"
                action_advice = "Winter/Boro rice is viable only in areas with guaranteed tubewell irrigation (West Bengal, Assam, Odisha, AP). Not viable in North/Western plains due to frost."
            else:
                verdict = "OFF-SEASON FOR RICE"
                verdict_status = "❌ Off-Season"
                action_advice = "Wait for the onset of the South-West monsoon (June-July). Consider short-duration Zaid crops (Moong, Urad, Cucumber) instead."

        elif crop_key == "wheat":
            if current_month in [10, 11]:
                verdict = "YES - IDEAL SOWING WINDOW FOR WHEAT"
                verdict_status = "✅ Highly Recommended"
                action_advice = "Optimal temperatures (15-22°C). Sow treated seed with seed drill at 4-5 cm depth."
            elif current_month in [12]:
                verdict = "LATE SOWING (USE LATE-SOWN VARIETIES)"
                verdict_status = "⚠️ Late Sown Varieties Needed"
                action_advice = "Use thermotolerant late-sown wheat varieties (e.g. PBW-373, HD-3059) to prevent terminal heat stress in March."
            else:
                verdict = "NOT RECOMMENDED (WRONG SEASON FOR WHEAT)"
                verdict_status = "❌ High Temperatures"
                action_advice = f"Wheat requires a cool winter growing regime (12-22°C). Current temperature ({current_temp}°C) is too warm. Prepare land for October sowing."

        elif crop_key == "cotton":
            if current_month in [4, 5, 6]:
                verdict = "YES - OPTIMAL SOWING PERIOD FOR COTTON"
                verdict_status = "✅ Favorable"
                action_advice = "Ensure deep plowing and well-drained black soil. Avoid waterlogged fields."
            else:
                verdict = "NOT RECOMMENDED FOR NEW SOWING"
                verdict_status = "⚠️ Not Sowing Season"
                action_advice = "Cotton needs a long warm season (180-200 frost-free days). If you have standing cotton, prepare for boll picking in dry weather."

        elif crop_key == "mustard":
            if current_month in [9, 10]:
                verdict = "YES - PRIME SOWING WINDOW FOR MUSTARD"
                verdict_status = "✅ Highly Recommended"
                action_advice = f"Mustard requires mild cool weather (15-25°C). Current ambient temp of {current_temp}°C is suitable for early Rabi seedbed preparation."
            else:
                verdict = "WAIT FOR RABI ONSET (OCTOBER)"
                verdict_status = "⚠️ Wait for October"
                action_advice = "Mustard is a Rabi oilseed crop. Wait until average temperatures dip below 25°C in October."

        else:
            verdict = "EVALUATE LOCAL MICROCLIMATE & IRRIGATION"
            verdict_status = "ℹ️ Evaluation Needed"
            action_advice = f"Ensure current temperature ({current_temp}°C) aligns with crop thermal window."

        crop_display_name = crop_key.title()
        if crop_key == "rice":
            crop_display_name = "Rice / Paddy (धान)"
        elif crop_key == "wheat":
            crop_display_name = "Wheat (गेहूं)"

        if lang == "hi":
            text = (
                f"🌾 **क्या आपको {crop_display_name} की खेती करनी चाहिए? ({location_name})**\n\n"
                f"### निर्णय (Direct Verdict): **{verdict_status}**\n\n"
                f"**विस्तृत कृषि सलाह:**\n{action_advice}\n\n"
                f"📊 **मौसम एवं आवश्यकता विश्लेषण:**\n"
                f"• **स्थानीय तापमान:** वर्तमान {current_temp}°C (फसल अनुकूलतम सीमा: {crop_info['optimal_temp_min']}°C – {crop_info['optimal_temp_max']}°C)\n"
                f"• **पानी की आवश्यकता:** {crop_info['water_need']}\n"
                f"• **उपयुक्त मिट्टी:** {crop_info['soil_type']}\n"
                f"• **मुख्य कृषि चक्र:** {crop_info['primary_season']}\n\n"
                f"💡 **विशेषज्ञ सुझाव:** {crop_info['advisory_notes']}"
            )
        else:
            text = (
                f"🌾 **Should you farm {crop_display_name} in {location_name}?**\n\n"
                f"### **Direct Verdict: {verdict_status}**\n\n"
                f"{action_advice}\n\n"
                f"📊 **Agronomic & Meteorological Feasibility Breakdown:**\n"
                f"• **Temperature Check:** Current ambient is **{current_temp}°C** (Crop Ideal Range: **{crop_info['optimal_temp_min']}°C – {crop_info['optimal_temp_max']}°C**).\n"
                f"• **Water Requirement:** {crop_info['water_need']}.\n"
                f"• **Soil Compatibility:** {crop_info['soil_type']}.\n"
                f"• **Standard Seasonal Cycle:** {crop_info['primary_season']}.\n\n"
                f"💡 **Scientific Guidance:** {crop_info['advisory_notes']}"
            )

        return {
            "intent": "CROP_SUITABILITY",
            "location": location_name,
            "crop": crop_key,
            "text": text,
            "verdict": verdict,
            "temperature": current_temp,
            "language": lang
        }

    def _answer_spraying_decision(
        self,
        temp: float,
        wind: float,
        humidity: int,
        daily: List[Dict[str, Any]],
        location_name: str,
        lang: str
    ) -> Dict[str, Any]:
        """Provides direct yes/no evaluation for pesticide or fertilizer spraying."""
        rain_prob = daily[0].get("precip_prob_max", 0) if daily else 0
        rain_sum = daily[0].get("precip_sum", 0.0) if daily else 0.0

        if wind >= 16.0:
            verdict = "❌ NO — DO NOT SPRAY TODAY (HIGH WIND DRIFT RISK)"
            reason = f"Wind speed is {wind} km/h (safe limit is < 15 km/h). High winds cause droplet drift away from targets, wasting expensive chemicals and risking bystander crops."
        elif rain_prob >= 45 or rain_sum >= 2.5:
            verdict = "❌ NO — POSTPONE SPRAY (RAIN WASH-OFF HAZARD)"
            reason = f"Rain probability is {rain_prob}% (expected {rain_sum} mm). Rainfall within 4-6 hours will wash off the active chemical before absorption."
        elif temp >= 36.0:
            verdict = "⚠️ CONDITIONAL — SPRAY ONLY IN EARLY MORNING OR LATE EVENING"
            reason = f"Midday temperature ({temp}°C) is high. High heat accelerates chemical evaporation and can cause phytotoxic foliar scorching on leaves."
        else:
            verdict = "✅ YES — OPTIMAL WEATHER WINDOW FOR SPRAYING"
            reason = f"Winds are gentle ({wind} km/h), rain risk is low ({rain_prob}%), and temperature ({temp}°C) supports excellent foliar uptake."

        if lang == "hi":
            text = (
                f"🧪 **क्या आज कीटनाशक/उर्वरक का छिड़काव करना चाहिए? ({location_name})**\n\n"
                f"### **निर्णय:** **{verdict}**\n\n"
                f"• **कारण:** {reason}\n"
                f"• **हवा की गति:** {wind} km/h (सुरक्षित सीमा: < 15 km/h)\n"
                f"• **बारिश की संभावना:** {rain_prob}%\n"
                f"• **तापमान:** {temp}°C\n\n"
                f"💡 **सलाह:** छिड़काव हमेशा सुबह 7-10 बजे या शाम 4-6 बजे के बीच करें। सुरक्षात्मक मास्क और दस्ताने अवश्य पहनें।"
            )
        else:
            text = (
                f"🧪 **Can you spray pesticide/fertilizer today in {location_name}?**\n\n"
                f"### **Direct Verdict: {verdict}**\n\n"
                f"• **Rationale:** {reason}\n"
                f"• **Wind Velocity:** {wind} km/h (Recommended threshold: < 15 km/h)\n"
                f"• **Rainwash Risk:** {rain_prob}% probability\n"
                f"• **Ambient Temperature:** {temp}°C\n\n"
                f"💡 **Application Advice:** Carry out foliar applications during early morning (07:00–10:00) or late afternoon (16:00–18:00) with uniform nozzle pressure."
            )

        return {"intent": "SPRAYING_DECISION", "location": location_name, "text": text, "language": lang}

    def _answer_irrigation_decision(
        self,
        temp: float,
        rain: float,
        daily: List[Dict[str, Any]],
        location_name: str,
        lang: str
    ) -> Dict[str, Any]:
        """Provides direct yes/no evaluation for watering/irrigating fields."""
        rain_48h = sum([d.get("precip_sum", 0.0) for d in daily[:2]])
        max_prob = max([d.get("precip_prob_max", 0) for d in daily[:2]], default=0)

        if max_prob >= 50 or rain_48h >= 6.0:
            verdict = "❌ HOLD / STOP IRRIGATION (SIGNIFICANT RAIN EXPECTED)"
            reason = f"Forecast shows {rain_48h:.1f} mm rain ({max_prob}% chance) over next 48h. Artificial irrigation now risks waterlogging, root suffocation, and nutrient leaching."
        elif temp >= 35.0:
            verdict = "✅ YES — IRRIGATE LIGHTLY DURING EVENING / NIGHT"
            reason = f"High ambient temperature ({temp}°C) causes high evapotranspiration deficit. Night watering cools the root zone without midday evaporation loss."
        else:
            verdict = "ℹ️ MAINTAIN REGULAR CROP-STAGE CYCLE"
            reason = f"No imminent heavy rainfall. Proceed with regular moisture scheduling as per your crop's vegetative or flowering stage."

        if lang == "hi":
            text = (
                f"💧 **क्या आज खेत में सिंचाई करनी चाहिए? ({location_name})**\n\n"
                f"### **निर्णय:** **{verdict}**\n\n"
                f"• **वैज्ञानिक कारण:** {reason}\n"
                f"• **अगले 48 घंटे में बारिश का पूर्वानुमान:** {rain_48h:.1f} mm ({max_prob}% संभावना)\n"
                f"• **वर्तमान तापमान:** {temp}°C"
            )
        else:
            text = (
                f"💧 **Should you irrigate your fields today in {location_name}?**\n\n"
                f"### **Direct Verdict: {verdict}**\n\n"
                f"• **Agronomic Rationale:** {reason}\n"
                f"• **48-Hour Rainfall Forecast:** {rain_48h:.1f} mm ({max_prob}% rain probability)\n"
                f"• **Current Ambient:** {temp}°C"
            )

        return {"intent": "IRRIGATION_DECISION", "location": location_name, "text": text, "language": lang}

    def _answer_rain_query(
        self,
        curr: Dict[str, Any],
        daily: List[Dict[str, Any]],
        location_name: str,
        lang: str,
        time_ref: str
    ) -> Dict[str, Any]:
        """Provides direct yes/no answers for precipitation queries."""
        if time_ref == "tomorrow" and len(daily) > 1:
            target_day = daily[1]
            day_label = "tomorrow"
            day_hi = "कल"
        else:
            target_day = daily[0] if daily else {}
            day_label = "today"
            day_hi = "आज"

        prob = target_day.get("precip_prob_max", 0)
        sum_mm = target_day.get("precip_sum", 0.0)
        cond = target_day.get("condition", "Partly cloudy")

        if prob >= 70 or sum_mm >= 10.0:
            verdict = f"🌧️ YES — HEAVY RAIN HIGHLY LIKELY ({prob}% CHANCE)"
            guidance = f"Expect substantial showers totaling approximately {sum_mm} mm. Carry umbrellas and prepare for localized traffic slowdowns."
        elif prob >= 40 or sum_mm >= 2.0:
            verdict = f"🌦️ SCATTERED RAIN / SHOWERS LIKELY ({prob}% CHANCE)"
            guidance = f"Intermittent light to moderate rain showers ({sum_mm} mm) are expected. Postpone non-essential outdoor painting or drying."
        else:
            verdict = f"☀️ NO — MAINLY DRY & CLEAR ({prob}% CHANCE)"
            guidance = "No significant rainfall is expected. Dry conditions will prevail."

        if lang == "hi":
            text = (
                f"🌧️ **क्या {location_name} में {day_hi} बारिश होगी?**\n\n"
                f"### **उत्तर (Direct Answer):** **{verdict}**\n\n"
                f"• **बारिश की संभावना:** {prob}%\n"
                f"• **अनुमानित वर्षा मात्रा:** {sum_mm} mm\n"
                f"• **संभावित मौसम स्थिति:** {cond}\n"
                f"• **मार्गदर्शन:** {guidance}"
            )
        else:
            text = (
                f"🌧️ **Will it rain {day_label} in {location_name}?**\n\n"
                f"### **Direct Answer: {verdict}**\n\n"
                f"• **Precipitation Probability:** **{prob}%**\n"
                f"• **Expected Volume:** {sum_mm} mm\n"
                f"• **Expected Sky Condition:** {cond}\n"
                f"• **Practical Guidance:** {guidance}"
            )

        return {"intent": "RAIN_QUERY", "location": location_name, "text": text, "language": lang}

    def _answer_outdoor_activity(
        self,
        weather_data: Dict[str, Any],
        location_name: str,
        lang: str = "en",
        time_ref: str = "current",
        raw_query: str = ""
    ) -> Dict[str, Any]:
        """Provides an authoritative yes/no suitability verdict and briefing for picnics, outings, and outdoor events."""
        curr = weather_data.get("current", {})
        daily = weather_data.get("daily", [])
        aqi = weather_data.get("aqi", {})

        # Resolve target day
        if time_ref == "tomorrow" and len(daily) > 1:
            target = daily[1]
            day_title_en = "Tomorrow"
            day_title_hi = "कल"
        elif time_ref == "weekend" and len(daily) > 2:
            target = daily[2]
            day_title_en = "This Weekend"
            day_title_hi = "इस वीकेंड"
        else:
            target = daily[0] if daily else {}
            day_title_en = "Today"
            day_title_hi = "आज"

        temp_max = target.get("temp_max", curr.get("temperature", 28.0))
        temp_min = target.get("temp_min", curr.get("temperature", 22.0) - 5.0)
        precip_prob = target.get("precip_prob_max", 0)
        precip_sum = target.get("precip_sum", 0.0)
        cond = target.get("condition", "Partly cloudy")
        wind_max = target.get("wind_max", curr.get("wind_speed", 12.0))
        uv_max = target.get("uv_index_max", 5.0)
        aqi_val = aqi.get("us_aqi", 75)
        aqi_cat = aqi.get("category", "Moderate")

        # Evaluate suitability
        if precip_prob >= 55 or precip_sum >= 4.0:
            verdict_en = "❌ NOT RECOMMENDED / UNFAVORABLE (High Rain & Wet Ground Threat)"
            verdict_hi = "❌ पिकनिक के लिए अनुशंसित नहीं (भारी बारिश व भीगी जमीन का खतरा)"
            rationale_en = (
                f"High chance of rainfall ({precip_prob}% probability, ~{precip_sum} mm expected) "
                "will disrupt open-air seating, dining, and lawn activities. "
                "Strongly recommend postponing or choosing an indoor recreational venue."
            )
            rationale_hi = (
                f"बारिश की बहुत अधिक संभावना ({precip_prob}%, लगभग {precip_sum} mm वर्षा) है। "
                "खुले मैदान में पिकनिक या भोजन करना भीगने के कारण मुश्किल होगा। पिकनिक को किसी अन्य दिन के लिए टालें।"
            )
            time_window_en = "🚫 Open lawn activities discouraged. If proceeding, pick a park with sheltered waterproof gazebos."
            time_window_hi = "🚫 खुले मैदान में गतिविधियां टालें। यदि आवश्यक हो तो शेड या वाटरप्रूफ गज़ेबो वाली जगह चुनें।"
        elif precip_prob >= 35 or precip_sum >= 1.5:
            verdict_en = "⚠️ MARGINALLY SUITABLE (Proceed with Caution & Rain Backup)"
            verdict_hi = "⚠️ मध्यम अनुकूल (छाता व शेड का बैकअप प्रबंध रखें)"
            rationale_en = (
                f"Scattered light to moderate showers are possible ({precip_prob}% chance, ~{precip_sum} mm). "
                "Picnic is feasible if you choose a park equipped with covered pavilions, and carry umbrellas and waterproof mats."
            )
            rationale_hi = (
                f"रुक-रुक कर फुहारें ({precip_prob}% संभावना) पड़ने की संभावना है। "
                "पिकनिक संभव है यदि आप किसी शेड या कवर्ड पवेलियन के पास बैठें और वाटरप्रूफ मैट व छाते साथ रखें।"
            )
            time_window_en = "🌅 **Morning window (8:30 AM – 11:30 AM)** is usually safest before afternoon rain clouds build."
            time_window_hi = "🌅 **सुबह का समय (8:30 AM – 11:30 AM)** दोपहर की बारिश से पहले सबसे सुरक्षित रहेगा।"
        elif temp_max >= 38.0:
            verdict_en = "⚠️ HEAT CAUTION: AVOID MIDDAY PICNICS"
            verdict_hi = "⚠️ अत्यधिक गर्मी: केवल सुबह या शाम को ही जाएं"
            rationale_en = (
                f"Sunny but dangerously hot ({temp_max}°C peak). Midday outdoor stay exposes you to heat exhaustion and dehydration."
            )
            rationale_hi = (
                f"धूप खिली रहेगी परंतु तापमान अत्यधिक गर्म ({temp_max}°C) रहेगा। दोपहर 12:00 से 4:00 के बीच लू का खतरा रहेगा।"
            )
            time_window_en = "🌅 **8:00 AM – 10:30 AM** (morning breeze) or 🌇 **5:00 PM – 6:45 PM** (sunset). Avoid 12:00 PM – 4:00 PM."
            time_window_hi = "🌅 **सुबह 8:00 से 10:30** या 🌇 **शाम 5:00 से 6:45** ही अनुकूल रहेगा।"
        elif temp_max >= 33.0:
            verdict_en = "✅ SUITABLE WITH WARM-WEATHER PRECAUTIONS"
            verdict_hi = "✅ पिकनिक के लिए अनुकूल (धूप से बचाव रखें)"
            rationale_en = (
                f"Clear/dry weather with low rain chance ({precip_prob}%). Afternoons are warm ({temp_max}°C), so locate under dense tree shade."
            )
            rationale_hi = (
                f"मौसम सूखा है और बारिश की संभावना केवल {precip_prob}% है। दोपहर में तापमान ({temp_max}°C) रहेगा, अतः घने पेड़ों की छांव चुनें।"
            )
            time_window_en = "🌅 **Morning (9:00 AM – 11:30 AM)** or 🌇 **Afternoon/Sunset (4:00 PM – 6:30 PM)**."
            time_window_hi = "🌅 **सुबह 9:00 से 11:30** या 🌇 **शाम 4:00 से 6:30** सबसे सुखद रहेगा।"
        elif 18.0 <= temp_max < 33.0:
            verdict_en = "✅ HIGHLY SUITABLE & IDEAL FOR A PICNIC!"
            verdict_hi = "✅ बिल्कुल उत्तम व सुखद मौसम — पिकनिक के लिए सर्वश्रेष्ठ!"
            rationale_en = (
                f"Superb meteorological conditions! Pleasant temperature ({temp_max}°C high, {temp_min}°C low), "
                f"mild sky ({cond}), gentle breeze ({wind_max} km/h), and very low rain risk ({precip_prob}%). "
                "Perfect for outdoor dining, sports, and family leisure all day long."
            )
            rationale_hi = (
                f"बेहद सुहावना और उत्तम मौसम! तापमान {temp_max}°C / {temp_min}°C, "
                f"हल्की हवा ({wind_max} km/h), और बारिश की संभावना न के बराबर ({precip_prob}%) है। "
                "पूरे दिन पिकनिक और आउटडोर गतिविधियों के लिए मौसम एकदम अनुकूल है।"
            )
            time_window_en = "⏰ **All day from 10:00 AM to 5:30 PM** (Thermal comfort is optimal throughout the day)."
            time_window_hi = "⏰ **सुबह 10:00 बजे से शाम 5:30 बजे तक कभी भी** (दिनभर मौसम सुखद रहेगा)।"
        else:
            verdict_en = "✅ SUITABLE BUT COOL / CHILLY (Dress Warmly)"
            verdict_hi = "✅ अनुकूल परंतु ठंडा मौसम (गर्म कपड़े पहनें)"
            rationale_en = (
                f"Dry skies ({cond}) with crisp cool temperatures ({temp_max}°C / {temp_min}°C). "
                "Enjoyable in sunny spots with warm sweaters and hot beverages."
            )
            rationale_hi = (
                f"मौसम साफ है परंतु ठंड रहेगी ({temp_max}°C / {temp_min}°C)। "
                "धूप वाली जगह पर बैठें और गर्म चाय/कॉफी व ऊनी कपड़े साथ रखें।"
            )
            time_window_en = "☀️ **11:00 AM – 3:30 PM** (Warmest sunny hours of the day)."
            time_window_hi = "☀️ **दोपहर 11:00 से 3:30** (धूप का आनंद लेने का सबसे अच्छा समय)।"

        if lang == "hi":
            text = (
                f"🧺 **{location_name} में {day_title_hi} पिकनिक की योजना (Picnic Suitability):**\n\n"
                f"### **🎯 सीधा निर्णय (Verdict):** **{verdict_hi}**\n\n"
                f"• **मौसम का विश्लेषण:** {rationale_hi}\n"
                f"• **अनुमानित तापमान:** अधिकतम **{temp_max}°C** | न्यूनतम **{temp_min}°C**\n"
                f"• **बारिश की संभावना:** **{precip_prob}%** (मात्रा: {precip_sum} mm)\n"
                f"• **हवा व यूवी:** हवा **{wind_max} km/h**, यूवी इंडेक्स **{uv_max}**\n"
                f"• **वायु गुणवत्ता (AQI):** {aqi_val} ({aqi_cat})\n\n"
                f"⏰ **सर्वश्रेष्ठ समय (Best Time Window):**\n{time_window_hi}\n\n"
                f"🎒 **पिकनिक चेकलिस्ट व व्यावहारिक सुझाव:**\n"
                f"1. **बैठने की चादर/मैट:** वाटरप्रूफ चटाई साथ रखें ताकि जमीन की नमी से बचाव हो सके।\n"
                f"2. **पेयजल:** कम से कम 2 लीटर प्रति व्यक्ति स्वच्छ पानी व ताजे फल रखें।\n"
                f"3. **धूप से सुरक्षा:** धूप का चश्मा व सनस्क्रीन (UV इंडेक्स {uv_max} है)।\n"
                f"4. **खेल सामग्री:** बैडमिंटन, फ्रिसबी या फुटबॉल (हवा {wind_max} km/h अनुकूल है)।"
            )
        else:
            text = (
                f"🧺 **Picnic & Outing Weather Suitability for {location_name} ({day_title_en}):**\n\n"
                f"### **🎯 Direct Verdict:** **{verdict_en}**\n\n"
                f"• **Meteorological Assessment:** {rationale_en}\n"
                f"• **Expected Temperature:** High: **{temp_max}°C** | Low: **{temp_min}°C**\n"
                f"• **Rainfall Probability:** **{precip_prob}%** (Estimated Volume: {precip_sum} mm)\n"
                f"• **Atmosphere & Breeze:** {cond}, Max wind **{wind_max} km/h**\n"
                f"• **Air Quality & UV:** AQI **{aqi_val}** ({aqi_cat}), Peak UV Index **{uv_max}** / 10\n\n"
                f"⏰ **Recommended Picnic Time Window:**\n{time_window_en}\n\n"
                f"🎒 **Picnic Essentials & Practical Checklist:**\n"
                f"1. **Ground Mat:** Bring a waterproof picnic sheet (lawns frequently retain moisture).\n"
                f"2. **Hydration & Fresh Food:** Carry adequate drinking water (2 L/person) and securely sealed food.\n"
                f"3. **Sun & Skin Protection:** Apply SPF 30+ sunscreen, wear hats/sunglasses (UV index: {uv_max}).\n"
                f"4. **Recreation & Sports:** Wind velocity ({wind_max} km/h) is gentle and safe for badminton and frisbee."
            )

        return {
            "intent": "OUTDOOR_ACTIVITY",
            "location": location_name,
            "text": text,
            "temperature": temp_max,
            "condition": cond,
            "language": lang
        }

    def _answer_sports_activity(
        self,
        weather_data: Dict[str, Any],
        location_name: str,
        lang: str = "en",
        time_ref: str = "current",
        raw_query: str = ""
    ) -> Dict[str, Any]:
        """Evaluates ground and weather conditions for outdoor sports like cricket, football, running, cycling."""
        curr = weather_data.get("current", {})
        daily = weather_data.get("daily", [])
        target = daily[1] if (time_ref == "tomorrow" and len(daily) > 1) else (daily[0] if daily else {})

        temp_max = target.get("temp_max", curr.get("temperature", 28.0))
        precip_prob = target.get("precip_prob_max", 0)
        wind_max = target.get("wind_max", curr.get("wind_speed", 12.0))
        cond = target.get("condition", "Partly cloudy")

        if precip_prob >= 50:
            verdict = "❌ NOT RECOMMENDED (High Rain & Slippery Pitch/Ground Risk)"
            note = f"Rain probability is {precip_prob}%. Soggy turf increases injury risk and will disrupt the match."
        elif temp_max >= 36.0:
            verdict = "⚠️ CAUTION: PLAY EARLY MORNING ONLY (High Heat Strain)"
            note = f"Daytime high reaches {temp_max}°C. Limit strenuous play to 6:30 AM – 9:30 AM or under evening floodlights."
        else:
            verdict = "✅ HIGHLY SUITABLE FOR OUTDOOR SPORTS & CRICKET!"
            note = f"Dry surface, pleasant winds ({wind_max} km/h), and mild temperatures ({temp_max}°C)."

        text = (
            f"🏏 **Sports & Outdoor Games Briefing for {location_name}:**\n\n"
            f"### **🎯 Direct Verdict: {verdict}**\n\n"
            f"• **Ground & Weather State:** {note}\n"
            f"• **Rain Stoppage Risk:** {precip_prob}%\n"
            f"• **Wind Effect on Ball Flight:** {wind_max} km/h ({'calm/controllable' if wind_max < 20 else 'gusty drift'})\n"
            f"• **Best Playing Slot:** 7:00 AM – 10:30 AM or 4:30 PM – 6:30 PM."
        )
        return {"intent": "SPORTS_ACTIVITY", "location": location_name, "text": text, "language": lang}

    def _answer_travel_road(
        self,
        weather_data: Dict[str, Any],
        location_name: str,
        lang: str = "en",
        time_ref: str = "current",
        raw_query: str = ""
    ) -> Dict[str, Any]:
        """Evaluates driving, highway, and road trip safety."""
        curr = weather_data.get("current", {})
        daily = weather_data.get("daily", [])
        target = daily[1] if (time_ref == "tomorrow" and len(daily) > 1) else (daily[0] if daily else {})

        precip_prob = target.get("precip_prob_max", 0)
        precip_sum = target.get("precip_sum", 0.0)
        wind_max = target.get("wind_max", curr.get("wind_speed", 12.0))

        if precip_prob >= 70 or precip_sum >= 15.0:
            verdict = "⚠️ TRAVEL CAUTION: WET HIGHWAYS & HYDROPLANING HAZARD"
            tips = "Heavy downpours expected. Reduce speed by 20-30%, increase following distance, and avoid flooded underpasses."
        elif wind_max >= 45:
            verdict = "⚠️ HIGH WIND WARNING: CROSSWINDS ON BRIDGES & FLYOVERS"
            tips = "Strong wind gusts. Grip steering wheel firmly, especially when driving high-sided SUVs or motorbikes."
        else:
            verdict = "✅ SAFE & FAVORABLE FOR ROAD TRAVEL / DRIVING"
            tips = "Good visibility, dry asphalt conditions, and normal atmospheric pressure across highway routes."

        text = (
            f"🚗 **Travel & Highway Driving Advisory for {location_name}:**\n\n"
            f"### **🎯 Road Safety Verdict: {verdict}**\n\n"
            f"• **Highway Precipitation:** {precip_prob}% chance ({precip_sum} mm)\n"
            f"• **Wind Speed:** {wind_max} km/h\n"
            f"• **Driving Guidance:** {tips}"
        )
        return {"intent": "TRAVEL_ROAD", "location": location_name, "text": text, "language": lang}

    def _answer_drying_clothes(
        self,
        weather_data: Dict[str, Any],
        location_name: str,
        lang: str = "en",
        time_ref: str = "current",
        raw_query: str = ""
    ) -> Dict[str, Any]:
        """Evaluates outdoor laundry drying conditions."""
        curr = weather_data.get("current", {})
        daily = weather_data.get("daily", [])
        target = daily[1] if (time_ref == "tomorrow" and len(daily) > 1) else (daily[0] if daily else {})

        precip_prob = target.get("precip_prob_max", 0)
        temp_max = target.get("temp_max", curr.get("temperature", 28.0))
        wind_max = target.get("wind_max", curr.get("wind_speed", 12.0))

        if precip_prob >= 40:
            verdict = "❌ NO — AVOID DRYING OUTSIDE (High Rain Risk)"
            speed = "Rain will soak clothes. Use indoor drying racks or covered balconies."
        elif temp_max >= 30 and wind_max >= 10:
            verdict = "✅ YES — EXCELLENT FAST DRYING WEATHER"
            speed = "Clothes will dry rapidly in approximately 1.5 – 2.5 hours."
        else:
            verdict = "✅ YES — NORMAL OUTDOOR DRYING"
            speed = "Expected drying time is approximately 3 – 4 hours."

        text = (
            f"👕 **Outdoor Laundry & Drying Advisory for {location_name}:**\n\n"
            f"### **🎯 Direct Verdict: {verdict}**\n\n"
            f"• **Drying Speed Estimate:** {speed}\n"
            f"• **Rain Threat:** {precip_prob}%\n"
            f"• **Ambient Heat & Breeze:** High of {temp_max}°C, Wind {wind_max} km/h."
        )
        return {"intent": "DRYING_CLOTHES", "location": location_name, "text": text, "language": lang}

    def _answer_car_wash(
        self,
        weather_data: Dict[str, Any],
        location_name: str,
        lang: str = "en",
        time_ref: str = "current",
        raw_query: str = ""
    ) -> Dict[str, Any]:
        """Evaluates car wash decision based on 48h rain forecast."""
        daily = weather_data.get("daily", [])
        rain_soon = any(d.get("precip_prob_max", 0) >= 35 for d in daily[:3])

        if rain_soon:
            verdict = "⚠️ POSTPONE CAR WASH (Rain Expected within 48-72h)"
            advice = "Showers are predicted in the next 2-3 days, which will splash dirt and leave water spots on freshly cleaned cars."
        else:
            verdict = "✅ GREAT TIME TO WASH YOUR CAR!"
            advice = "Dry, rain-free conditions will persist for the next 3-5 days. Your car will stay clean and shiny."

        text = (
            f"🚙 **Car Wash Weather Decision for {location_name}:**\n\n"
            f"### **🎯 Verdict: {verdict}**\n\n"
            f"• **Meteorological Advice:** {advice}"
        )
        return {"intent": "CAR_WASH", "location": location_name, "text": text, "language": lang}

    def _answer_clothing_advice(
        self,
        weather_data: Dict[str, Any],
        location_name: str,
        lang: str = "en",
        time_ref: str = "current",
        raw_query: str = ""
    ) -> Dict[str, Any]:
        """Advises on attire, jackets, sweaters, and umbrella necessity."""
        curr = weather_data.get("current", {})
        daily = weather_data.get("daily", [])
        target = daily[1] if (time_ref == "tomorrow" and len(daily) > 1) else (daily[0] if daily else {})

        temp = target.get("temp_max", curr.get("temperature", 28.0))
        temp_min = target.get("temp_min", curr.get("apparent_temperature", 22.0))
        precip_prob = target.get("precip_prob_max", 0)
        cond = target.get("condition", curr.get("condition", "Partly cloudy"))
        wind = target.get("wind_max", curr.get("wind_speed", 10.0))
        q_lower = (raw_query or "").lower()

        # Umbrella decision
        need_umbrella = precip_prob >= 35 or "rain" in cond.lower() or "drizzle" in cond.lower() or "shower" in cond.lower()
        if need_umbrella:
            umbrella_verdict = f"☔ **YES, CARRY AN UMBRELLA** ({precip_prob}% chance of rain/showers)."
        else:
            umbrella_verdict = f"🌂 **NO UMBRELLA NEEDED** (Precipitation chance is low at {precip_prob}%)."

        # Attire selection based on thermal profile
        if temp < 12:
            attire = "🧥 **Heavy Winter Layers**: Wear a thick jacket or coat, warm inner thermals, and woolen socks/gloves."
        elif temp < 18:
            attire = "🧥 **Light Jacket or Warm Sweater**: A light windbreaker, fleece, or pullover is strongly recommended, especially in morning/evening."
        elif temp < 25:
            attire = "👕 **Comfortable Smart Casuals**: Long-sleeve cotton shirts, t-shirts, light jeans or trousers. Weather is mild and pleasant."
        elif temp < 33:
            attire = "🎽 **Light & Breathable Clothing**: Pure cotton fabrics, loose fitting t-shirts, cap, and sunglasses for daylight hours."
        else:
            attire = "☀️ **Hot Weather Protection**: Ultra-light breathable linen/cotton wear, UV-blocking sunglasses, wide-brim hat, and carry hydration."

        if lang == "hi":
            text = (
                f"👔 **{location_name} के लिए पोशाक व छाता सलाह ({'कल' if time_ref == 'tomorrow' else 'आज'}):**\n\n"
                f"### **🎯 छाता निर्णय:**\n"
                f"• {'☔ **हाँ, छाता साथ रखें** — बारिश की संभावना ' + str(precip_prob) + '% है।' if need_umbrella else '🌂 **छाते की जरूरत नहीं** — बारिश की संभावना मात्र ' + str(precip_prob) + '% है।'}\n\n"
                f"### **👕 कपड़ों की सिफारिश:**\n"
                f"• {attire}\n\n"
                f"• **मौसम संदर्भ:** तापमान {temp}°C (न्यूनतम {temp_min}°C), स्थिति '{cond}', हवा {wind} km/h."
            )
        else:
            text = (
                f"👔 **Clothing & Umbrella Guide for {location_name} ({'Tomorrow' if time_ref == 'tomorrow' else 'Today'}):**\n\n"
                f"### **🎯 Umbrella Recommendation:**\n"
                f"• {umbrella_verdict}\n\n"
                f"### **👕 Recommended Attire:**\n"
                f"• {attire}\n\n"
                f"• **Meteorological Context:** Temperature expected around **{temp}°C** (low: **{temp_min}°C**), Condition: *{cond}*, Wind: {wind} km/h."
            )

        return {"intent": "CLOTHING_ADVICE", "location": location_name, "text": text, "language": lang}

    def _answer_health_air_quality(
        self,
        weather_data: Dict[str, Any],
        location_name: str,
        lang: str = "en",
        time_ref: str = "current",
        raw_query: str = ""
    ) -> Dict[str, Any]:
        """Provides air quality, respiratory recommendations, and exercise safety."""
        aqi_info = weather_data.get("aqi", {})
        aqi_val = aqi_info.get("aqi", 85)
        category = aqi_info.get("category", "Moderate")
        pm25 = aqi_info.get("pm2_5", 28.0)
        pm10 = aqi_info.get("pm10", 55.0)

        if aqi_val <= 50:
            status = "🟢 **EXCELLENT / GOOD (AQI 0-50)**"
            exercise = "✅ Safe and ideal for all outdoor activities, vigorous jogging, and sports."
            masks = "No face masks or air purifiers necessary."
        elif aqi_val <= 100:
            status = "🟡 **MODERATE (AQI 51-100)**"
            exercise = "✅ Safe for most people. Unusually sensitive individuals may experience slight throat irritation during intense exercise."
            masks = "Not required for the general public."
        elif aqi_val <= 200:
            status = "🟠 **POOR / UNHEALTHY FOR SENSITIVE GROUPS (AQI 101-200)**"
            exercise = "⚠️ Limit prolonged intense outdoor exertion. Shift morning cardio or brisk runs indoors or to early dawn."
            masks = "Sensitive individuals (asthma, children, elderly) should consider wearing an N95 mask outdoors."
        elif aqi_val <= 300:
            status = "🔴 **VERY POOR / UNHEALTHY (AQI 201-300)**"
            exercise = "❌ Avoid strenuous outdoor workouts. Keep windows closed and operate indoor HEPA purifiers."
            masks = "N95/FFP2 masks strongly recommended if stepping outdoors."
        else:
            status = "🟣 **HAZARDOUS / SEVERE (AQI 300+)**"
            exercise = "⛔ EMERGENCY AIR HAZARD: Cease all outdoor activities. Remain in sealed indoor environments."
            masks = "High-filtration respirators mandatory for essential outdoor transit."

        text = (
            f"🫁 **Air Quality & Respiratory Health Advisory for {location_name}:**\n\n"
            f"### **🎯 Air Quality Level: {status}**\n\n"
            f"• **Current AQI Index:** **{aqi_val}** ({category})\n"
            f"• **Particulate Matter:** PM2.5: **{pm25} µg/m³** | PM10: **{pm10} µg/m³**\n"
            f"• **Outdoor Exercise & Jogging:** {exercise}\n"
            f"• **Protection Guidelines:** {masks}"
        )
        return {"intent": "HEALTH_AIR_QUALITY", "location": location_name, "text": text, "language": lang}

    def _answer_greeting(
        self,
        weather_data: Dict[str, Any],
        location_name: str,
        lang: str = "en",
        raw_query: str = ""
    ) -> Dict[str, Any]:
        """Provides a helpful, conversational welcome with actionable questions."""
        curr = weather_data.get("current", {})
        temp = curr.get("temperature", 28.0)
        cond = curr.get("condition", "Partly cloudy")

        text = (
            f"👋 **Hello! I'm WeatherGPT — Your Meteorological & Decision AI.**\n\n"
            f"Currently monitoring **{location_name}**: **{temp}°C**, *{cond}*.\n\n"
            f"**Here are popular questions you can ask me right now:**\n"
            f"• *\"Is it suitable to plan a picnic tomorrow?\"*\n"
            f"• *\"Do I need to carry an umbrella or jacket today?\"*\n"
            f"• *\"Should I farm rice in Punjab this season?\"*\n"
            f"• *\"Is the air quality safe for a morning jog?\"*\n"
            f"• *\"Can I play cricket or wash my car today?\"*\n"
            f"• *\"Will it rain in Delhi over the weekend?\"*\n\n"
            f"Feel free to ask in English, Hindi, or your preferred language!"
        )
        return {"intent": "GENERAL_GREETING", "location": location_name, "text": text, "language": lang}
