import unittest
from unittest.mock import patch
from linsecure.checks.permissions import check_file_permissions

class TestPermissions(unittest.TestCase):

    @patch("subprocess.check_output")
    def test_world_writable_dirs_found(self, mock_subproc):
        mock_subproc.return_value = b"/tmp\n/var/tmp\n"
        result = check_file_permissions()
        self.assertIn("/tmp", result)
        self.assertIn("[!]", result)

    @patch("subprocess.check_output", return_value=b"")
    def test_no_world_writable_dirs(self, _):
        result = check_file_permissions()
        self.assertIn("No world-writable directories found", result)
