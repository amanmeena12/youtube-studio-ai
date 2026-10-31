"""
Unit tests for MetadataGenerator.
"""

import unittest
from services.metadata_generator import MetadataGenerator


class TestMetadataGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = MetadataGenerator()

    def test_generate_all(self):
        meta = self.generator.generate_all(
            topic="Python Machine Learning",
            niche="Programming",
            format_type="Long-form",
            target_audience="Data Science Students",
            target_country="United States",
        )
        self.assertEqual(len(meta["titles"]), 5)
        self.assertIn("description", meta)
        self.assertGreater(len(meta["tags"]), 5)
        self.assertGreater(len(meta["hashtags"]), 2)
        self.assertEqual(meta["validation"]["status"], "PASSED")

    def test_validation_limits(self):
        # Test excessively long title
        long_title = "A" * 105
        val = self.generator.validate_metadata(
            title=long_title,
            description="Good description with https://link.com",
            tags=["tag1", "tag2"],
            hashtags=["#Python", "#Coding"],
        )
        self.assertEqual(val["status"], "FAILED")
        self.assertTrue(any("exceeds 100 character limit" in e for e in val["errors"]))


if __name__ == "__main__":
    unittest.main()
