"""
Unit tests for AlgorithmOptimizer service.
Tests:
- Log-Normal Outlier Distribution & Z-score calculations
- Machine Learning TF-IDF & N-gram feature extraction
- Double-exponential Retention Curve Simulation (R(t))
- Bayesian Beta-Binomial Click-Through Rate predictor
- 7x24 Upload Timing Heatmap matrix
- Edge case handling (empty data, 1 video, division by zero)
"""

import unittest
from services.algorithm_optimizer import AlgorithmOptimizer


class TestAlgorithmOptimizer(unittest.TestCase):
    def setUp(self):
        self.optimizer = AlgorithmOptimizer()
        self.sample_videos = [
            {"video_id": "v1", "title": "Why Python is Taking Over AI in 2026", "views": 250000, "published_at": "2026-03-01T15:00:00Z"},
            {"video_id": "v2", "title": "Stop Doing This in Python (Top Mistakes)", "views": 180000, "published_at": "2026-03-05T16:00:00Z"},
            {"video_id": "v3", "title": "Python vs Rust: The Brutal Truth", "views": 420000, "published_at": "2026-03-10T14:30:00Z"},
            {"video_id": "v4", "title": "Beginner Python Tutorial Part 1", "views": 45000, "published_at": "2026-03-15T18:00:00Z"},
            {"video_id": "v5", "title": "How I Built an AI Agent in 24 Hours", "views": 310000, "published_at": "2026-03-20T15:30:00Z"},
            {"video_id": "v6", "title": "Weekly Tech News and Updates", "views": 22000, "published_at": "2026-03-25T11:00:00Z"},
        ]

    def test_outlier_distribution_calculation(self):
        result = self.optimizer.analyze_outlier_distribution(self.sample_videos)
        self.assertTrue(result["has_data"])
        self.assertEqual(result["sample_size"], 6)
        self.assertIn("metrics", result)
        self.assertGreater(result["metrics"]["mean_views"], 0)
        self.assertGreater(result["metrics"]["median_views"], 0)

        # Check that videos are enriched with Z-scores and tiers
        videos = result["videos"]
        self.assertEqual(len(videos), 6)
        # Highest views video (v3 with 420k views) should have highest positive z-score
        self.assertGreater(videos[0]["z_score"], 0.5)
        self.assertIn("percentile", videos[0])
        self.assertIn(videos[0]["badge"], ["BREAKOUT", "HIGH"])

    def test_outlier_distribution_empty_and_single(self):
        empty_res = self.optimizer.analyze_outlier_distribution([])
        self.assertFalse(empty_res["has_data"])

        single_res = self.optimizer.analyze_outlier_distribution([{"views": 100}])
        self.assertFalse(single_res["has_data"])

    def test_tfidf_ngram_extraction(self):
        result = self.optimizer.extract_winning_ngrams(self.sample_videos, top_k=5)
        self.assertTrue(result["has_data"])
        self.assertGreaterEqual(len(result["top_ngrams"]), 1)
        
        top_ngram = result["top_ngrams"][0]
        self.assertIn("phrase", top_ngram)
        self.assertIn("multiplier", top_ngram)
        self.assertIn("category", top_ngram)
        self.assertIn("impact_score", top_ngram)

    def test_retention_curve_simulation(self):
        # Test 10-minute long-form video
        res_long = self.optimizer.simulate_retention_curve(duration_sec=600.0, hook_score=85.0, pacing_wpm=150.0)
        self.assertIn("curve_points", res_long)
        self.assertGreater(len(res_long["curve_points"]), 10)
        
        # Point 0 must be 100%
        self.assertEqual(res_long["curve_points"][0]["retention_pct"], 100.0)
        # Last point must be lower than first point
        self.assertLess(res_long["curve_points"][-1]["retention_pct"], 100.0)
        
        # Check metrics
        metrics = res_long["metrics"]
        self.assertGreater(metrics["apv_pct"], 0.0)
        self.assertLessEqual(metrics["apv_pct"], 100.0)
        self.assertIn("retention_grade", metrics)

        # Test Short (45 seconds)
        res_short = self.optimizer.simulate_retention_curve(duration_sec=45.0, hook_score=90.0, is_short=True)
        self.assertTrue(res_short["is_short"])
        self.assertEqual(res_short["metrics"]["benchmark_apv_pct"], 80.0)

    def test_bayesian_ctr_prediction(self):
        # Optimal title with curiosity trigger & numerical specificity
        good_title = "Why Nobody Talks About This $1,000 AI Hack"
        res_good = self.optimizer.predict_bayesian_ctr(good_title)
        
        self.assertGreater(res_good["expected_ctr_pct"], 5.0)
        self.assertGreaterEqual(res_good["virality_index"], 50)
        self.assertGreater(len(res_good["strengths"]), 0)
        self.assertEqual(len(res_good["credible_interval"]), 2)

        # Weak title (short, no curiosity, no numbers)
        weak_title = "my video"
        res_weak = self.optimizer.predict_bayesian_ctr(weak_title)
        self.assertLessEqual(res_weak["expected_ctr_pct"], 5.0)

    def test_upload_timing_heatmap(self):
        res = self.optimizer.compute_upload_timing_heatmap(self.sample_videos)
        self.assertIn("heatmap", res)
        self.assertEqual(len(res["heatmap"]), 7)
        for day in res["heatmap"]:
            self.assertEqual(len(day["hourly_scores"]), 24)
        
        self.assertIn("golden_windows", res)
        self.assertGreaterEqual(len(res["golden_windows"]), 1)

    def test_algorithmic_audit_generation(self):
        channel = {"title": "Tech Mastery Channel", "videos": self.sample_videos}
        audit = self.optimizer.generate_algorithmic_audit(channel)
        
        self.assertIn("algorithmic_health_score", audit)
        self.assertIn("algorithmic_grade", audit)
        self.assertIn("title_hacks", audit)
        self.assertEqual(len(audit["title_hacks"]), 5)
        self.assertIn("core_algorithmic_bottleneck", audit)


if __name__ == "__main__":
    unittest.main()
