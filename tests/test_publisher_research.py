import unittest

from agents.publisher.research.researcher import (
    validate_url,
    calculate_relevance,
    PageParser
)


class TestPublisherResearch(unittest.TestCase):

    def test_url_normalization(self):
        self.assertEqual(
            validate_url("example.com"),
            "https://example.com"
        )

    def test_localhost_blocked(self):
        with self.assertRaises(ValueError):
            validate_url("http://localhost")

    def test_relevance_matching(self):
        score = calculate_relevance(
            "home improvement",
            "Home Improvement Ideas",
            "Home renovation and improvement",
            "Helpful home improvement articles"
        )

        self.assertGreater(score, 0)

    def test_html_extraction(self):
        parser = PageParser()

        parser.feed(
            '<html><title>Home Improvement</title>'
            '<meta name="description" content="Home renovation">'
            '<a href="/contact">Contact</a></html>'
        )

        self.assertIn("Home Improvement", parser.title)
        self.assertEqual(parser.description, "Home renovation")
        self.assertIn("/contact", parser.links)


if __name__ == "__main__":
    unittest.main()
