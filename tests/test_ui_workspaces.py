"""
Automated Streamlit AppTest for MY YOUTUBE CREATOR STUDIO.
Simulates end-to-end rendering across all 14 Studio workspaces.
"""

import unittest
from streamlit.testing.v1 import AppTest


class TestUIWorkspaces(unittest.TestCase):
    def test_all_14_workspaces_render_without_exception(self):
        at = AppTest.from_file("app.py", default_timeout=15)
        at.run()
        self.assertEqual(len(at.exception), 0, f"Exception on Dashboard: {at.exception}")

        workspaces = [
            "1. Dashboard",
            "2. My Channel",
            "3. Channel Audit",
            "4. Content",
            "5. Shorts Studio",
            "6. Long-Form Studio",
            "7. Video Analysis",
            "8. SEO and Metadata",
            "9. Thumbnail Lab",
            "10. Competitor Research",
            "11. Analytics",
            "12. Publishing Planner",
            "13. AI Creator Assistant",
            "14. Settings",
        ]

        for ws in workspaces:
            at.sidebar.radio[0].set_value(ws)
            at.run()
            self.assertEqual(len(at.exception), 0, f"Exception on workspace {ws}: {at.exception}")


if __name__ == "__main__":
    unittest.main()
