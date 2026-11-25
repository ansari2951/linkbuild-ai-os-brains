import unittest

from agents.linkbuilding.monitor.backlink_monitor import analyze_backlink, validate_url
from agents.niches.niche_intelligence import NicheIntelligence
from agents.publisher.research.brain import research_publisher
from core.brain import CentralBrain
from core.dashboard_sync import build_dashboard_data


class TestSystemIntegrity(unittest.TestCase):

    def test_central_brain_all_agent_files_present(self):
        summary = CentralBrain().get_system_summary()
        self.assertEqual(summary["missing_agents"], 0)
        self.assertGreaterEqual(summary["available_agents"], 13)

    def test_niche_intelligence_loads_cleanly(self):
        niche_intel = NicheIntelligence()
        self.assertIn("Marketing", niche_intel.get_categories())

    def test_backlink_monitor_validation(self):
        self.assertTrue(validate_url("https://example.com"))
        self.assertFalse(validate_url("ftp://example.com"))
        res = analyze_backlink(
            {"published_url": "https://example.com", "target_url": "https://iana.org"},
            check_live=False,
        )
        self.assertEqual(res["monitor_status"], "READY_FOR_LIVE_CHECK")

    def test_publisher_research_brain_returns_completed(self):
        res = research_publisher("Find publisher websites for home improvement in US")
        self.assertEqual(res["status"], "completed")

    def test_dashboard_sync_builds_payload(self):
        payload = build_dashboard_data()
        self.assertIn("metrics", payload)
        self.assertEqual(payload["system"]["connected_brains"], 6)


if __name__ == "__main__":
    unittest.main()
