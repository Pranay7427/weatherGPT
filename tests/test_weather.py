import unittest
import asyncio
from app.services.weather_service import search_location, get_current_and_forecast, get_air_quality, get_weather_desc

class TestWeatherService(unittest.TestCase):
    def test_weather_codes(self):
        desc0 = get_weather_desc(0)
        self.assertEqual(desc0["desc"], "Clear sky")
        desc95 = get_weather_desc(95)
        self.assertEqual(desc95["desc"], "Thunderstorm")
        self.assertEqual(desc95["severity"], "severe")

    def test_geocoding_fallback(self):
        results = asyncio.run(search_location("Delhi"))
        self.assertGreaterEqual(len(results), 1)
        self.assertIn("Delhi", results[0]["display_name"])

    def test_weather_retrieval(self):
        data = asyncio.run(get_current_and_forecast(28.6139, 77.2090))
        self.assertIn("current", data)
        self.assertIn("temperature", data["current"])
        self.assertIn("hourly", data)
        self.assertIn("daily", data)
        self.assertGreater(len(data["daily"]), 0)

    def test_air_quality(self):
        aqi = asyncio.run(get_air_quality(28.6139, 77.2090))
        self.assertIn("us_aqi", aqi)
        self.assertIn("category", aqi)
        self.assertIn("pm2_5", aqi)

if __name__ == "__main__":
    unittest.main()
