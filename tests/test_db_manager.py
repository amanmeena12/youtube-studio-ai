"""
Unit tests for DatabaseManager.
"""

import os
import tempfile
import unittest
from database.db_manager import DatabaseManager


class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db = DatabaseManager(db_path=self.temp_db.name)

    def tearDown(self):
        if os.path.exists(self.temp_db.name):
            os.remove(self.temp_db.name)

    def test_save_and_get_channel(self):
        ch_data = {
            "channel_id": "UC_TEST_12345678901234",
            "title": "Unit Test Creator",
            "custom_url": "@unittestcreator",
            "description": "A channel for testing.",
            "subscriber_count": 50000,
            "view_count": 1200000,
            "video_count": 45,
            "profile_image": "https://example.com/pfp.jpg",
            "raw_data": {"test_key": "test_val"},
        }
        row_id = self.db.save_channel(ch_data)
        self.assertGreater(row_id, 0)

        retrieved = self.db.get_channel("UC_TEST_12345678901234")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["title"], "Unit Test Creator")
        self.assertEqual(retrieved["subscriber_count"], 50000)
        self.assertEqual(retrieved["raw_data"]["test_key"], "test_val")

    def test_save_and_get_channel_audit(self):
        audit_data = {"recommendations": [{"what": "Improve title"}]}
        audit_id = self.db.save_channel_audit("UC_TEST_12345678901234", 85, audit_data)
        self.assertGreater(audit_id, 0)

        latest = self.db.get_latest_channel_audit("UC_TEST_12345678901234")
        self.assertIsNotNone(latest)
        self.assertEqual(latest["audit_score"], 85)
        self.assertEqual(latest["audit_data"]["recommendations"][0]["what"], "Improve title")

    def test_save_and_get_video_analysis(self):
        vid_data = {
            "title": "How to Code",
            "source_type": "upload",
            "file_name": "sample.mp4",
            "file_size": 1048576,
            "duration": 60.5,
            "aspect_ratio": "16:9",
            "resolution": "1920x1080",
            "fps": 30.0,
            "bitrate": 138000,
            "audio_channels": 2,
            "sample_rate": 44100,
            "hook_score": 88.0,
            "pacing_score": 90.0,
            "details": {"summary": "Great video"},
        }
        vid_id = self.db.save_video_analysis(vid_data)
        self.assertGreater(vid_id, 0)

        recent = self.db.get_recent_video_analyses(limit=5)
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0]["title"], "How to Code")
        self.assertEqual(recent[0]["details"]["summary"], "Great video")

    def test_competitor_crud(self):
        comp = {
            "channel_id": "UC_COMP_1",
            "channel_title": "Rival Channel",
            "handle": "@rival",
            "subscriber_count": 100000,
            "video_count": 200,
            "view_count": 5000000,
            "upload_frequency": 2.5,
            "raw_data": {},
        }
        self.db.save_competitor(comp)
        comps = self.db.get_competitors()
        self.assertEqual(len(comps), 1)
        self.assertEqual(comps[0]["channel_title"], "Rival Channel")

        self.db.delete_competitor("UC_COMP_1")
        comps_after = self.db.get_competitors()
        self.assertEqual(len(comps_after), 0)

    def test_chat_history(self):
        self.db.save_chat_message("sess_1", "user", "Hello assistant")
        self.db.save_chat_message("sess_1", "assistant", "Hello creator")

        history = self.db.get_chat_history("sess_1")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[1]["role"], "assistant")


if __name__ == "__main__":
    unittest.main()
