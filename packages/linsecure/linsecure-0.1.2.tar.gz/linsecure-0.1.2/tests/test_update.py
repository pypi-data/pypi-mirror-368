import unittest
from unittest.mock import patch
from linsecure.checks.updates import check_updates

class TestUpdateCheck(unittest.TestCase):

    @patch("subprocess.check_output")
    def test_no_updates(self, mock_subproc):
        # Simulate output when there are no packages to update
        mock_subproc.return_value = b"Listing...\n"
        result = check_updates()

        self.assertIn("No packages need updating", result)
        self.assertNotIn("System packages with available updates", result)

    @patch("subprocess.check_output")
    def test_updates_available(self, mock_subproc):
        # Simulate output when updates are available
        mock_output = b"""Listing...
bash/now 5.0-6ubuntu1.1 amd64 [installed,upgradable to: 5.0-6ubuntu1.2]
coreutils/now 8.30-3ubuntu2 amd64 [installed,upgradable to: 8.30-3ubuntu2.1]
"""
        mock_subproc.return_value = mock_output
        result = check_updates()

        self.assertIn("System packages with available updates", result)
        self.assertIn("bash", result)
        self.assertIn("coreutils", result)

    @patch("subprocess.check_output", side_effect=Exception("Simulated error"))
    def test_update_check_error(self, mock_subproc):
        # Simulate unexpected error during subprocess call
        result = check_updates()
        self.assertIn("Error checking updates", result)

if __name__ == "__main__":
    unittest.main()
