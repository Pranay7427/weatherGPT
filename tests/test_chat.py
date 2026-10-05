import unittest
from app.services.nlu_engine import WeatherNLUEngine

class TestNluEngine(unittest.TestCase):
    def setUp(self):
        self.nlu = WeatherNLUEngine()
        self.mock_weather = {
            "current": {
                "temperature": 29.5,
                "apparent_temperature": 31.0,
                "humidity": 58,
                "wind_speed": 11.0,
                "wind_direction": 270,
                "wind_gusts": 15.0,
                "pressure": 1012,
                "precipitation": 0.0,
                "condition": "Mainly clear",
                "weather_code": 1
            },
            "daily": [
                {"date": "2026-09-04", "condition": "Mainly clear", "temp_max": 33.0, "temp_min": 24.0, "precip_prob_max": 10, "precip_sum": 0.0},
                {"date": "2026-09-05", "condition": "Partly cloudy", "temp_max": 32.0, "temp_min": 23.0, "precip_prob_max": 20, "precip_sum": 0.0}
            ]
        }

    def test_query_parsing_intents(self):
        p1 = self.nlu.parse_query("What is the weather in Mumbai right now?")
        self.assertEqual(p1["intent"], "CURRENT_WEATHER")
        self.assertIn("Mumbai", p1["location"])

        p2 = self.nlu.parse_query("should i farm rice ?")
        self.assertEqual(p2["intent"], "CROP_SUITABILITY")
        self.assertEqual(p2["crop"], "rice")

        p3 = self.nlu.parse_query("Give me aviation briefing for Delhi airport")
        self.assertEqual(p3["intent"], "AVIATION")

        p4 = self.nlu.parse_query("Is there any cyclone warning in Odisha?")
        self.assertEqual(p4["intent"], "ALERTS")

    def test_rice_farming_direct_answer(self):
        resp = self.nlu.generate_natural_response(
            intent="CROP_SUITABILITY",
            weather_data=self.mock_weather,
            location_name="Indore",
            lang="en",
            raw_query="should i farm rice ?"
        )
        self.assertIn("Direct Verdict", resp["text"])
        self.assertIn("Rice / Paddy", resp["text"])
        self.assertIn("29.5°C", resp["text"])

    def test_multilingual_generation(self):
        resp_en = self.nlu.generate_natural_response(
            intent="CURRENT_WEATHER",
            weather_data=self.mock_weather,
            location_name="New Delhi",
            lang="en"
        )
        self.assertIn("Current Weather in New Delhi", resp_en["text"])

        resp_hi = self.nlu.generate_natural_response(
            intent="CURRENT_WEATHER",
            weather_data=self.mock_weather,
            location_name="New Delhi",
            lang="hi"
        )
        self.assertIn("वर्तमान मौसम स्थिति", resp_hi["text"])

        resp_bn = self.nlu.generate_natural_response(
            intent="CURRENT_WEATHER",
            weather_data=self.mock_weather,
            location_name="Kolkata",
            lang="bn"
        )
        self.assertIn("Kolkata", resp_bn["text"])

    def test_picnic_suitability_query(self):
        query = "whether it is suitable to plan a picnic tommorow ?"
        p = self.nlu.parse_query(query)
        self.assertEqual(p["intent"], "OUTDOOR_ACTIVITY")
        self.assertEqual(p["time_horizon"], "tomorrow")

        resp = self.nlu.generate_natural_response(
            intent=p["intent"],
            weather_data=self.mock_weather,
            location_name="Delhi",
            lang="en",
            time_ref=p["time_horizon"],
            raw_query=query
        )
        self.assertIn("Picnic & Outing Weather Suitability", resp["text"])
        self.assertIn("Direct Verdict", resp["text"])
        self.assertIn("SUITABLE", resp["text"])

    def test_clothing_and_umbrella_query(self):
        query = "do I need to carry an umbrella today?"
        p = self.nlu.parse_query(query)
        self.assertEqual(p["intent"], "CLOTHING_ADVICE")

        resp = self.nlu.generate_natural_response(
            intent=p["intent"],
            weather_data=self.mock_weather,
            location_name="Mumbai",
            lang="en",
            time_ref=p["time_horizon"],
            raw_query=query
        )
        self.assertIn("Clothing & Umbrella Guide", resp["text"])
        self.assertIn("Umbrella Recommendation", resp["text"])

    def test_health_air_quality_query(self):
        query = "is the air quality safe for morning running?"
        p = self.nlu.parse_query(query)
        self.assertEqual(p["intent"], "HEALTH_AIR_QUALITY")

        mock_weather_with_aqi = dict(self.mock_weather)
        mock_weather_with_aqi["aqi"] = {"aqi": 45, "category": "Good", "pm2_5": 12.0, "pm10": 25.0}

        resp = self.nlu.generate_natural_response(
            intent=p["intent"],
            weather_data=mock_weather_with_aqi,
            location_name="Shimla",
            lang="en",
            time_ref=p["time_horizon"],
            raw_query=query
        )
        self.assertIn("Air Quality & Respiratory Health", resp["text"])
        self.assertIn("EXCELLENT / GOOD", resp["text"])

    def test_greeting_query(self):
        query = "Hello, what can you do?"
        p = self.nlu.parse_query(query)
        self.assertEqual(p["intent"], "GENERAL_GREETING")

        resp = self.nlu.generate_natural_response(
            intent=p["intent"],
            weather_data=self.mock_weather,
            location_name="Bengaluru",
            lang="en",
            raw_query=query
        )
        self.assertIn("WeatherGPT", resp["text"])
        self.assertIn("Bengaluru", resp["text"])

if __name__ == "__main__":
    unittest.main()
