import unittest
from unittest.mock import patch
from linsecure.checks.ports import check_open_ports

class TestPorts(unittest.TestCase):

    @patch("subprocess.check_output")
    def test_no_ports(self, mock_subproc):
        mock_subproc.return_value = b"Netid  State      Recv-Q Send-Q Local Address:Port  Peer Address:Port\n"
        result = check_open_ports()
        print("ACTUAL:", result)
        self.assertIn("No open ports found", result)

    @patch("subprocess.check_output")
    def test_with_open_ports(self, mock_subproc):
        mock_output = b"""Netid  State      Recv-Q Send-Q Local Address:Port  Peer Address:Port
tcp    LISTEN     0      128    0.0.0.0:22        0.0.0.0:*       
tcp    LISTEN     0      128    127.0.0.1:8000    0.0.0.0:*       
"""
        mock_subproc.return_value = mock_output
        result = check_open_ports()
        self.assertIn("Open ports detected", result)
        self.assertIn("0.0.0.0:22", result)
        self.assertIn("127.0.0.1:8000", result)

if __name__ == "__main__":
    unittest.main()
