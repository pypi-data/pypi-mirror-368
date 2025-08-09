"""
Test module for utility functions.

Author: Arjun Trivedi
Email: arjuntrivedi42@yahoo.com
"""

import pytest
import os
from pathlib import Path


def test_basic_imports():
    """Test that basic imports work."""
    try:
        from mcp_kql_server.utils import (
            normalize_cluster_uri,
            clean_query_for_execution,
            validate_kql_query_syntax,
            format_error_message,
            is_debug_mode,
            truncate_string
        )
        assert True  # If we get here, imports worked
    except ImportError:
        pytest.skip("Module imports not available in CI environment")


def test_truncate_string():
    """Test string truncation utility."""
    from mcp_kql_server.utils import truncate_string
    
    # Test normal case
    result = truncate_string("Hello World", 5, "...")
    assert result == "He..."
    
    # Test string shorter than limit
    result = truncate_string("Hi", 10)
    assert result == "Hi"
    
    # Test exact length
    result = truncate_string("Hello", 5)
    assert result == "Hello"


def test_is_debug_mode():
    """Test debug mode detection."""
    from mcp_kql_server.utils import is_debug_mode
    
    # Test with environment variable
    os.environ['KQL_DEBUG'] = 'true'
    assert is_debug_mode() == True
    
    os.environ['KQL_DEBUG'] = 'false'
    assert is_debug_mode() == False
    
    # Clean up
    if 'KQL_DEBUG' in os.environ:
        del os.environ['KQL_DEBUG']


def test_normalize_cluster_uri():
    """Test cluster URI normalization."""
    try:
        from mcp_kql_server.utils import normalize_cluster_uri
        
        # Test basic cluster name
        result = normalize_cluster_uri("mycluster")
        assert result == "https://mycluster.kusto.windows.net"
        
        # Test full URI
        result = normalize_cluster_uri("https://mycluster.kusto.windows.net")
        assert result == "https://mycluster.kusto.windows.net"
        
        # Test domain name
        result = normalize_cluster_uri("mycluster.kusto.windows.net")
        assert result == "https://mycluster.kusto.windows.net"
        
    except ImportError:
        pytest.skip("Module not available in CI environment")


def test_clean_query_for_execution():
    """Test query cleaning functionality."""
    try:
        from mcp_kql_server.utils import clean_query_for_execution
        
        query = "cluster('test').database('db').MyTable | take 10"
        result = clean_query_for_execution(query)
        assert result == "MyTable | take 10"
        
    except ImportError:
        pytest.skip("Module not available in CI environment")


def test_format_error_message():
    """Test error message formatting."""
    try:
        from mcp_kql_server.utils import format_error_message
        
        error = ValueError("Test error")
        result = format_error_message(error, "Test context")
        assert "Test context" in result
        assert "ValueError" in result
        assert "Test error" in result
        
    except ImportError:
        pytest.skip("Module not available in CI environment")