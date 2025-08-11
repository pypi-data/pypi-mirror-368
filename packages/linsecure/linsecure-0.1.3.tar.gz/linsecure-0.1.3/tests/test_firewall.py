import unittest
from unittest.mock import patch
from linsecure.checks.firewall import check_firewall

class TestFirewallCheck(unittest.TestCase):
    @patch("subprocess.check_output")
    def test_firewall_active(self, mock_output):
        mock_output.return_value = b"Status: active\n"
        result = check_firewall()
        self.assertIn("UFW firewall is active", result)

    @patch("subprocess.check_output")
    def test_firewall_inactive(self, mock_output):
        mock_output.return_value = b"Status: inactive\n"
        result = check_firewall()
        self.assertIn("UFW firewall is INACTIVE", result)

    @patch("subprocess.check_output", side_effect=FileNotFoundError)
    def test_ufw_not_installed(self, _):
        result = check_firewall()
        self.assertIn("UFW is not installed", result)
