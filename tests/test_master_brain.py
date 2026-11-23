import unittest

from core.master_brain.router import route_task
from core.master_brain.registry import list_agents


class TestMasterBrain(unittest.TestCase):

    def test_publisher_research(self):
        self.assertEqual(
            route_task("Find publisher websites"),
            "publisher_research"
        )

    def test_client_research(self):
        self.assertEqual(
            route_task("Find client leads"),
            "client_research"
        )

    def test_email_intelligence(self):
        self.assertEqual(
            route_task("Check email replies"),
            "email_intelligence"
        )

    def test_unknown_command(self):
        self.assertIsNone(
            route_task("Play music")
        )

    def test_agent_registry(self):
        self.assertGreaterEqual(len(list_agents()), 6)


if __name__ == "__main__":
    unittest.main()
