"""
Unit tests for YouTubeService.
"""

import unittest
from services.youtube_service import YouTubeService


class TestYouTubeService(unittest.TestCase):
    def setUp(self):
        self.service = YouTubeService()

    def test_parse_channel_identifier(self):
        cases = [
            ("UC1234567890123456789012", ("channel_id", "UC1234567890123456789012")),
            ("@MrBeast", ("handle", "MrBeast")),
            ("https://www.youtube.com/@veritasium", ("handle", "veritasium")),
            ("https://youtube.com/channel/UCq-Fj5jknLsUf-MWSy4_brA", ("channel_id", "UCq-Fj5jknLsUf-MWSy4_brA")),
            ("mkbhd", ("handle", "mkbhd")),
        ]
        for inp, expected in cases:
            res = self.service.parse_channel_identifier(inp)
            self.assertEqual(res, expected, f"Failed on input {inp}")

    def test_parse_video_id(self):
        cases = [
            ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ]
        for inp, expected in cases:
            res = self.service.parse_video_id(inp)
            self.assertEqual(res, expected, f"Failed on input {inp}")

    def test_fetch_channel_fallback(self):
        data = self.service.fetch_channel_data("@testcreator")
        self.assertIn("channel_id", data)
        self.assertIn("title", data)
        self.assertIn("videos", data)
        self.assertGreater(len(data["videos"]), 0)

    def test_audit_channel(self):
        channel_data = self.service.fetch_channel_data("@testcreator")
        audit = self.service.audit_channel(channel_data)
        self.assertIn("overall_score", audit)
        self.assertIn("grade", audit)
        self.assertIn("recommendations", audit)
        self.assertGreaterEqual(audit["overall_score"], 20)
        self.assertLessEqual(audit["overall_score"], 100)


if __name__ == "__main__":
    unittest.main()
