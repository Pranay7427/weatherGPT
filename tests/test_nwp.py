import unittest
import asyncio
from app.services.nwp_service import get_nwp_comparison

class TestNWPService(unittest.TestCase):
    def test_nwp_models_present(self):
        nwp = asyncio.run(get_nwp_comparison(28.6139, 77.2090))
        self.assertIn("models", nwp)
        self.assertIn("GFS", nwp["models"])
        self.assertIn("ECMWF", nwp["models"])
        self.assertIn("ICON", nwp["models"])
        self.assertIn("WRF", nwp["models"])

    def test_nwp_consensus_metrics(self):
        nwp = asyncio.run(get_nwp_comparison(28.6139, 77.2090))
        consensus = nwp.get("consensus", {})
        self.assertIn("temperature_curve", consensus)
        self.assertIn("confidence_score", consensus)
        self.assertIn("confidence_level", consensus)
        self.assertGreaterEqual(consensus["confidence_score"], 0)
        self.assertLessEqual(consensus["confidence_score"], 100)

if __name__ == "__main__":
    unittest.main()
