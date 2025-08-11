import unittest
from unittest.mock import mock_open, patch
from linsecure.checks.ssh import check_ssh_config

class TestSSHConfig(unittest.TestCase):

    @patch("os.path.exists", return_value=False)
    def test_ssh_config_not_found(self, _):
        result = check_ssh_config()
        self.assertIn("SSH config not found", result)

    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data="""
        PermitRootLogin yes
        PasswordAuthentication no
    """)
    def test_ssh_config_warnings(self, mock_file, _):
        result = check_ssh_config()
        self.assertIn("SSH allows root login", result)
        self.assertIn("SSH password login is disabled", result)

    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data="PermitRootLogin no\nPasswordAuthentication no")
    def test_ssh_config_all_good(self, mock_file, _):
        result = check_ssh_config()
        self.assertIn("SSH root login is disabled", result)
        self.assertIn("SSH password login is disabled", result)
