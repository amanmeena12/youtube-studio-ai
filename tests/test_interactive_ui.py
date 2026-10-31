"""
Automated interactive simulation test for MY YOUTUBE CREATOR STUDIO UI workflows.
Tests button clicks, session state updates, and rendering across key creator flows.
"""

import unittest
from streamlit.testing.v1 import AppTest


class TestInteractiveUI(unittest.TestCase):
    def test_interactive_dashboard_and_scan(self):
        at = AppTest.from_file("app.py", default_timeout=15)
        at.run()
        self.assertEqual(len(at.exception), 0)

        # 1. Switch to My Channel and scan
        at.sidebar.radio[0].set_value("2. My Channel")
        at.run()
        self.assertEqual(len(at.exception), 0)

        # Find scan button and click
        scan_buttons = [b for b in at.button if "Scan Channel" in b.label]
        if scan_buttons:
            scan_buttons[0].click()
            at.run()
            self.assertEqual(len(at.exception), 0)

        # 2. Switch to Competitor Research and run
        at.sidebar.radio[0].set_value("10. Competitor Research")
        at.run()
        self.assertEqual(len(at.exception), 0)

        comp_buttons = [b for b in at.button if "Audit Competitor" in b.label]
        if comp_buttons:
            comp_buttons[0].click()
            at.run()
            self.assertEqual(len(at.exception), 0)

        # 3. Switch to SEO Studio and generate
        at.sidebar.radio[0].set_value("8. SEO and Metadata")
        at.run()
        self.assertEqual(len(at.exception), 0)

        seo_buttons = [b for b in at.button if "Generate & Validate" in b.label]
        if seo_buttons:
            seo_buttons[0].click()
            at.run()
            self.assertEqual(len(at.exception), 0)

        # 4. Switch to Video Analysis
        at.sidebar.radio[0].set_value("7. Video Analysis")
        at.run()
        self.assertEqual(len(at.exception), 0)


if __name__ == "__main__":
    unittest.main()
