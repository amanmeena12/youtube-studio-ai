"""
Automated Test Runner for MY YOUTUBE CREATOR STUDIO.
Executes all unit and comprehensive end-to-end tests across all 20 required scenarios.
"""

import sys
import unittest

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.discover("tests", pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
