"""
Unit tests for the kql_auth module.
"""

import unittest
import subprocess
from unittest.mock import patch, MagicMock

from mcp_kql_server.kql_auth import (
    kql_auth,
    trigger_az_cli_auth,
    authenticate
)


class TestKQLAuth(unittest.TestCase):
    """Test cases for KQL authentication functionality."""

    @patch('mcp_kql_server.kql_auth.subprocess.run')
    def test_kql_auth_success(self, mock_run):
        """Test successful authentication check."""
        # Mock successful az command
        mock_run.return_value = MagicMock(returncode=0)
        
        result = kql_auth()
        
        self.assertTrue(result["authenticated"])
        self.assertIn("authenticated", result["message"].lower())

    @patch('mcp_kql_server.kql_auth.subprocess.run')
    def test_kql_auth_failure(self, mock_run):
        """Test failed authentication check."""
        # Mock failed az command
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "az", stderr="Authentication failed"
        )
        
        result = kql_auth()
        
        self.assertFalse(result["authenticated"])
        self.assertIn("not authenticated", result["message"].lower())

    @patch('mcp_kql_server.kql_auth.subprocess.run')
    def test_kql_auth_exception(self, mock_run):
        """Test authentication check with unexpected exception."""
        # Mock exception
        mock_run.side_effect = Exception("Unexpected error")
        
        result = kql_auth()
        
        self.assertFalse(result["authenticated"])
        self.assertIn("Unexpected error", result["message"])

    @patch('mcp_kql_server.kql_auth.subprocess.run')
    def test_trigger_az_cli_auth_success(self, mock_run):
        """Test successful Azure CLI authentication trigger."""
        # Mock successful login
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        
        result = trigger_az_cli_auth()
        
        self.assertTrue(result["authenticated"])
        self.assertIn("successful", result["message"].lower())

    @patch('mcp_kql_server.kql_auth.subprocess.run')
    def test_trigger_az_cli_auth_failure(self, mock_run):
        """Test failed Azure CLI authentication trigger."""
        # Mock failed login
        mock_run.return_value = MagicMock(returncode=1, stderr="Login failed")
        
        result = trigger_az_cli_auth()
        
        self.assertFalse(result["authenticated"])
        self.assertIn("Login failed", result["message"])

    @patch('mcp_kql_server.kql_auth.subprocess.run')
    def test_trigger_az_cli_auth_timeout(self, mock_run):
        """Test Azure CLI authentication timeout."""
        # Mock timeout
        mock_run.side_effect = subprocess.TimeoutExpired("az", 120)
        
        result = trigger_az_cli_auth()
        
        self.assertFalse(result["authenticated"])
        self.assertIn("timeout", result["message"].lower())

    @patch('mcp_kql_server.kql_auth.kql_auth')
    def test_authenticate_already_authenticated(self, mock_kql_auth):
        """Test authenticate when already authenticated."""
        # Mock already authenticated
        mock_kql_auth.return_value = {
            "authenticated": True,
            "message": "Already authenticated"
        }
        
        result = authenticate()
        
        self.assertTrue(result["authenticated"])
        self.assertIn("Already authenticated", result["message"])

    @patch('mcp_kql_server.kql_auth.trigger_az_cli_auth')
    @patch('mcp_kql_server.kql_auth.kql_auth')
    def test_authenticate_needs_login(self, mock_kql_auth, mock_trigger_auth):
        """Test authenticate when login is needed."""
        # Mock not authenticated initially
        mock_kql_auth.return_value = {
            "authenticated": False,
            "message": "Not authenticated"
        }
        
        # Mock successful login
        mock_trigger_auth.return_value = {
            "authenticated": True,
            "message": "Login successful"
        }
        
        result = authenticate()
        
        self.assertTrue(result["authenticated"])
        mock_trigger_auth.assert_called_once()

    @patch('mcp_kql_server.kql_auth.trigger_az_cli_auth')
    @patch('mcp_kql_server.kql_auth.kql_auth')
    def test_authenticate_login_fails(self, mock_kql_auth, mock_trigger_auth):
        """Test authenticate when login fails."""
        # Mock not authenticated initially
        mock_kql_auth.return_value = {
            "authenticated": False,
            "message": "Not authenticated"
        }
        
        # Mock failed login
        mock_trigger_auth.return_value = {
            "authenticated": False,
            "message": "Login failed"
        }
        
        result = authenticate()
        
        self.assertFalse(result["authenticated"])
        mock_trigger_auth.assert_called_once()

    @patch('mcp_kql_server.kql_auth.platform.system')
    @patch('mcp_kql_server.kql_auth.subprocess.run')
    def test_platform_specific_commands(self, mock_run, mock_platform):
        """Test platform-specific command selection."""
        # Test Windows
        mock_platform.return_value = "Windows"
        mock_run.return_value = MagicMock(returncode=0)
        
        kql_auth()
        
        # Check that az.cmd was used for Windows
        calls = mock_run.call_args_list
        self.assertTrue(any("az.cmd" in str(call) for call in calls))
        
        # Reset mock
        mock_run.reset_mock()
        
        # Test Linux/Mac
        mock_platform.return_value = "Linux"
        mock_run.return_value = MagicMock(returncode=0)
        
        kql_auth()
        
        # Check that az was used for Linux
        calls = mock_run.call_args_list
        self.assertTrue(any("az" in str(call) and "az.cmd" not in str(call) for call in calls))


if __name__ == '__main__':
    unittest.main()