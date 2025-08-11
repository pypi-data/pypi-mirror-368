import unittest
from unittest.mock import patch
from linsecure.checks.system import check_os_info

class TestSystem(unittest.TestCase):

    @patch("platform.system", return_value="Linux")
    @patch("platform.release", return_value="5.15.0")
    def test_os_info(self, _, __):
        result = check_os_info()
        self.assertIn("Linux", result)
        self.assertIn("5.15.0", result)
