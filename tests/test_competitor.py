"""
Unit tests for CompetitorService.
"""

import unittest
from services.competitor_service import CompetitorService


class TestCompetitorService(unittest.TestCase):
    def setUp(self):
        self.service = CompetitorService()

    def test_analyze_competitors(self):
        inputs = ["@creator_alpha", "@creator_beta"]
        results = self.service.analyze_competitors(inputs)

        self.assertEqual(len(results["channels"]), 2)
        self.assertGreater(len(results["comparison_table"]), 0)
        self.assertGreater(len(results["all_videos_ranked"]), 0)
        # Check views per day ranking is sorted descending
        vids = results["all_videos_ranked"]
        for i in range(len(vids) - 1):
            self.assertGreaterEqual(vids[i]["views_per_day"], vids[i + 1]["views_per_day"])

    def test_analyze_single_competitor(self):
        single_res = self.service.analyze_single_competitor("@creator_single")
        self.assertTrue(single_res["has_data"])
        self.assertIn("baseline", single_res)
        self.assertGreater(single_res["baseline"]["median_views"], 0)
        self.assertIn("format_analysis", single_res)
        self.assertIn("upload_cadence", single_res)
        self.assertIn("transfer_strategies", single_res)
        self.assertGreater(len(single_res["transfer_strategies"]), 0)
        # Verify measured fact vs hypothesis tagging
        strat = single_res["transfer_strategies"][0]
        self.assertIn("Measured Fact:", strat["evidence_measured_fact"])
        self.assertIn("Creator Hypothesis:", strat["creator_hypothesis"])
        self.assertIn("Actionable Test:", strat["actionable_test"])


if __name__ == "__main__":
    unittest.main()
