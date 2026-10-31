"""
Unit tests for VideoAnalyzer.
"""

import struct
import unittest
from services.video_analyzer import VideoAnalyzer


class TestVideoAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = VideoAnalyzer()

    def _create_minimal_mp4_bytes(self, duration_s=15, width=1080, height=1920):
        """Constructs a synthetic valid ISOBMFF header with ftyp and moov/mvhd/trak boxes."""
        # 1. ftyp box
        ftyp_data = b"mp42" + b"\x00\x00\x00\x00" + b"isommp42"
        ftyp_box = struct.pack(">I4s", len(ftyp_data) + 8, b"ftyp") + ftyp_data

        # 2. mvhd box
        timescale = 1000
        duration_ticks = int(duration_s * timescale)
        # version 0, flags 0, create 0, mod 0, timescale, duration
        mvhd_payload = b"\x00\x00\x00\x00" + b"\x00\x00\x00\x00" + b"\x00\x00\x00\x00" + struct.pack(">II", timescale, duration_ticks)
        mvhd_box = struct.pack(">I4s", len(mvhd_payload) + 8, b"mvhd") + mvhd_payload

        # 3. tkhd box (width, height in fixed point 16.16)
        w_fixed = width << 16
        h_fixed = height << 16
        tkhd_payload = b"\x00" * 76 + struct.pack(">II", w_fixed, h_fixed)
        tkhd_box = struct.pack(">I4s", len(tkhd_payload) + 8, b"tkhd") + tkhd_payload

        # 4. trak box
        trak_box = struct.pack(">I4s", len(tkhd_box) + 8, b"trak") + tkhd_box

        # 5. moov box
        moov_payload = mvhd_box + trak_box
        moov_box = struct.pack(">I4s", len(moov_payload) + 8, b"moov") + moov_payload

        return ftyp_box + moov_box

    def test_inspect_video_file_parsing(self):
        fake_data = self._create_minimal_mp4_bytes(duration_s=25, width=1080, height=1920)
        meta = self.analyzer.inspect_video_file(fake_data, filename="vertical_short.mp4")

        self.assertEqual(meta["width"], 1080)
        self.assertEqual(meta["height"], 1920)
        self.assertEqual(meta["aspect_ratio"], "9:16")
        self.assertTrue(meta["is_short"])
        self.assertAlmostEqual(meta["duration_sec"], 25.0, delta=0.5)

    def test_analyze_content_hook_and_pacing(self):
        metadata = {
            "duration_sec": 30.0,
            "is_short": True,
            "width": 1080,
            "height": 1920,
            "resolution": "1080x1920",
            "aspect_ratio": "9:16",
            "has_audio": True,
            "audio_channels": 2,
            "audio_sample_rate": 44100,
        }
        transcript = (
            "Why do 90% of beginners make this fatal mistake? Never upload before checking your audio track. "
            "Today we reveal the exact three steps you need to get crystal clear audio on mobile."
        )
        analysis = self.analyzer.analyze_content(metadata, transcript_text=transcript, topic_hint="Audio Editing")

        self.assertGreater(analysis["hook_score"], 70)
        self.assertEqual(len(analysis["recommended_titles"]), 5)
        self.assertGreater(len(analysis["checklist"]), 0)
        # Verify 3-tier recommendation and component scores
        self.assertIn("readiness_recommendation", analysis)
        self.assertIn(analysis["readiness_recommendation"], ["READY TO UPLOAD", "NEEDS IMPROVEMENT", "MAJOR REVISION RECOMMENDED"])
        self.assertIn("component_scores", analysis)
        self.assertIn("technical_quality", analysis["component_scores"])
        self.assertIn("pacing_cadence", analysis["component_scores"])

    def test_different_videos_produce_different_scores(self):
        good_meta = {"duration_sec": 45.0, "is_short": True, "width": 1080, "height": 1920, "has_audio": True, "bitrate_kbps": 6000}
        good_transcript = "Why do all top creators use this rule? Stop making this mistake. Here is step 1. Next step 2. Subscribe for part 2."
        good_eval = self.analyzer.analyze_content(good_meta, good_transcript)

        poor_meta = {"duration_sec": 120.0, "is_short": True, "width": 640, "height": 480, "has_audio": False, "bitrate_kbps": 400}
        poor_transcript = "Hey guys, welcome back to my channel. Today I am going to talk about stuff."
        poor_eval = self.analyzer.analyze_content(poor_meta, poor_transcript)

        # Confirm scores vary appropriately based on actual data
        self.assertGreater(good_eval["overall_score"], poor_eval["overall_score"])
        self.assertGreater(good_eval["component_scores"]["technical_quality"], poor_eval["component_scores"]["technical_quality"])
        self.assertGreater(good_eval["component_scores"]["opening_hook"], poor_eval["component_scores"]["opening_hook"])

    def test_timestamped_cues_and_detected_problems(self):
        srt_data = (
            "1\n00:00:01,000 --> 00:00:04,500\nHey guys welcome back to another video.\n\n"
            "2\n00:00:10,000 --> 00:00:15,000\nNow we start the main tutorial content.\n"
        )
        sub = self.analyzer.parse_subtitle_file(srt_data)
        self.assertEqual(len(sub["cues"]), 2)
        self.assertEqual(sub["cues"][0]["start_sec"], 1.0)
        self.assertEqual(sub["cues"][0]["end_sec"], 4.5)

        meta = {"duration_sec": 60.0, "is_short": False, "width": 1920, "height": 1080, "has_audio": True, "cues": sub["cues"]}
        analysis = self.analyzer.analyze_content(meta, sub["full_text"])
        self.assertGreater(len(analysis["detected_problems"]), 0)
        prob = analysis["detected_problems"][0]
        self.assertIn("timestamp", prob)
        self.assertIn("00:00:01", prob["timestamp"])


if __name__ == "__main__":
    unittest.main()
