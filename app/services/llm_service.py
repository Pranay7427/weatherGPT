import httpx
import json
from typing import Dict, Any, Optional
from app.config import GEMINI_API_KEY, DEFAULT_GEMINI_MODEL
from app.services.nlu_engine import WeatherNLUEngine

nlu = WeatherNLUEngine()

async def generate_conversational_response(
    query: str,
    weather_data: Dict[str, Any],
    location_name: str,
    lang: str = "en",
    api_key: Optional[str] = None,
    advisory_data: Optional[Dict[str, Any]] = None,
    alerts_data: Optional[list] = None,
    nwp_data: Optional[Dict[str, Any]] = None,
    climate_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Dual-Core AI query understanding engine:
    1. If a Gemini API key is configured, uses Gemini to craft a tailored,
       grounded conversational response.
    2. Otherwise, relies on the instant built-in Meteorological NLU Engine.
    """
    parsed = nlu.parse_query(query)
    intent = parsed["intent"]
    time_ref = parsed["time_horizon"]

    active_key = api_key or GEMINI_API_KEY

    # If Gemini API key is present, attempt live grounded generation
    if active_key and active_key.strip():
        models_to_try = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-flash-latest", DEFAULT_GEMINI_MODEL]
        last_error = None
        last_status = None

        try:
            curr = weather_data.get("current", {})
            grounding_context = {
                "location": location_name,
                "current_observation": curr,
                "daily_forecast": weather_data.get("daily", []),
                "hourly_forecast": weather_data.get("hourly", [])[:24],
                "air_quality": weather_data.get("aqi", {}),
                "advisories": advisory_data,
                "active_alerts": alerts_data,
                "nwp_consensus": nwp_data.get("consensus", {}) if nwp_data else None,
                "climate_trends": climate_data
            }

            system_instruction = (
                "You are WeatherGPT, an authoritative AI meteorologist and lifestyle/farming decision advisor. "
                "Always answer the user's specific question directly with a clear, authoritative verdict upfront "
                "(e.g. for picnics, travel, sports, farming, drying clothes, rain queries). "
                "Ground all your answers strictly in the provided real-time meteorological data and forecasts. "
                "For picnic and outdoor questions, explicitly assess rain probability, temperature comfort, wind, UV, "
                "and recommend the best time windows of the day along with practical tips. "
                f"Respond in language code '{lang}' (e.g. Hindi, Bengali, Telugu, Tamil, Marathi, Gujarati, Kannada, or English). "
                "Use clean markdown formatting with emojis, bold highlights, and bullet points."
            )

            prompt = (
                f"User Question: \"{query}\"\n\n"
                f"Meteorological Grounding Data:\n{json.dumps(grounding_context, default=str)}\n\n"
                f"Please generate an accurate, helpful response in {lang}."
            )

            payload = {
                "systemInstruction": {"parts": [{"text": system_instruction}]},
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 800
                }
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                for model_name in models_to_try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={active_key}"
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                            if text:
                                return {
                                    "source": f"Google {model_name} (Cloud AI Grounded)",
                                    "intent": intent,
                                    "location": location_name,
                                    "text": text,
                                    "temperature": curr.get("temperature"),
                                    "condition": curr.get("condition"),
                                    "language": lang
                                }
                    else:
                        last_status = resp.status_code
                        try:
                            err_json = resp.json()
                            last_error = err_json.get("error", {}).get("message", resp.text[:120])
                        except Exception:
                            last_error = resp.text[:120]
                        print(f"Gemini API attempt ({model_name}) HTTP {last_status}: {last_error}")

        except Exception as e:
            err_label = f"{type(e).__name__}: {e}" if str(e) else type(e).__name__
            print(f"Gemini API invocation fallback: {err_label}")
            last_error = err_label

    # Built-in Meteorological NLU Engine (Zero Latency, High Reliability)
    resp = nlu.generate_natural_response(
        intent=intent,
        weather_data=weather_data,
        location_name=location_name,
        lang=lang,
        time_ref=time_ref,
        advisory_data=advisory_data,
        alerts_data=alerts_data,
        nwp_data=nwp_data,
        climate_data=climate_data,
        raw_query=query
    )

    if active_key and active_key.strip() and (last_status or last_error):
        # User entered a key, but Google API call did not succeed
        err_msg = f"HTTP {last_status}: {last_error}" if last_status else str(last_error)
        resp["text"] += (
            f"\n\n---\n> ⚠️ **Gemini API Key Notice**: Google AI request did not complete "
            f"(`{err_msg}`). "
            f"Please verify your API key at [Google AI Studio](https://aistudio.google.com/) and ensure Generative Language API is enabled. "
            f"In the meantime, WeatherGPT's Meteorological Core provided the authoritative answer above."
        )
        resp["source"] = "WeatherGPT Core (Gemini Fallback)"
    else:
        resp["source"] = "WeatherGPT Meteorological Intelligence Engine (Built-in)"

    return resp
