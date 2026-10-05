import unittest
from app.services.advisory_engine import (
    generate_agricultural_advisory,
    generate_aviation_briefing,
    generate_marine_advisory,
    generate_urban_smart_city_advisory
)

class TestAdvisoryEngine(unittest.TestCase):
    def setUp(self):
        self.mock_current = {
            "temperature": 32.0,
            "apparent_temperature": 34.0,
            "humidity": 65,
            "precipitation": 0.0,
            "weather_code": 1,
            "wind_speed": 12.0,
            "wind_direction": 270,
            "wind_gusts": 18.0,
            "pressure": 1012.0
        }
        self.mock_daily = [
            {"date": "2026-09-04", "precip_sum": 0.0, "precip_prob_max": 10, "temp_max": 34.0, "temp_min": 24.0},
            {"date": "2026-09-05", "precip_sum": 0.0, "precip_prob_max": 15, "temp_max": 35.0, "temp_min": 25.0}
        ]
        self.mock_aqi = {
            "us_aqi": 85,
            "category": "Moderate",
            "pm2_5": 28.5
        }

    def test_agricultural_advisory(self):
        advisory = generate_agricultural_advisory(self.mock_current, self.mock_daily, crop="Wheat")
        self.assertIn("irrigation", advisory)
        self.assertIn("spraying", advisory)
        self.assertIn("pest_disease", advisory)
        self.assertIn("livestock", advisory)
        self.assertEqual(advisory["crop"], "Wheat")

    def test_aviation_briefing(self):
        briefing = generate_aviation_briefing(self.mock_current, self.mock_daily, icao_code="VIDP")
        self.assertIn("flight_category", briefing)
        self.assertIn("metar", briefing)
        self.assertIn("taf", briefing)
        self.assertIn("crosswind_kt", briefing)

    def test_marine_advisory(self):
        marine = generate_marine_advisory(self.mock_current, location_name="Mumbai Port")
        self.assertIn("sea_state", marine)
        self.assertIn("safety_level", marine)
        self.assertIn("sig_wave_height_m", marine)

    def test_urban_advisory(self):
        urban = generate_urban_smart_city_advisory(self.mock_current, self.mock_aqi, location_name="New Delhi")
        self.assertIn("uhi_index", urban)
        self.assertIn("flood_risk_pct", urban)
        self.assertIn("labor_suitability", urban)

if __name__ == "__main__":
    unittest.main()
