"""
Utility functions for the MCP KQL Server.

This module contains common utility functions used across the MCP KQL Server
for operations like path handling, validation, formatting, and error handling.

Author: Arjun Trivedi
Email: arjuntrivedi42@yahoo.com
"""

import os
import re
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def get_default_cluster_memory_path() -> Path:
    """Get the default path for cluster memory storage.
    
    Automatically creates the directory structure if it doesn't exist.
    No environment variables required - uses platform-appropriate defaults.
    
    Returns:
        Path object pointing to the default cluster memory directory
    """
    if os.name == 'nt':  # Windows
        # Use APPDATA if available, otherwise use fallback
        appdata = os.environ.get('APPDATA')
        if appdata:
            base_path = Path(appdata)
        else:
            # Fallback for Windows without APPDATA
            base_path = Path.home() / 'AppData' / 'Roaming'
    else:  # macOS/Linux
        base_path = Path.home() / '.local' / 'share'
    
    # Create the full path
    memory_path = base_path / 'KQL_MCP' / 'cluster_memory'
    
    # Automatically create the directory if it doesn't exist
    try:
        memory_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized KQL memory path: {memory_path}")
    except Exception as e:
        logger.warning(f"Could not create memory directory {memory_path}: {e}")
        # Use a temporary fallback in user's home directory
        fallback_path = Path.home() / '.kql_mcp_memory'
        fallback_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Using fallback memory path: {fallback_path}")
        return fallback_path
    
    return memory_path


def normalize_cluster_uri(cluster_input: str) -> str:
    """Normalize a cluster URI to a standard format.
    
    Args:
        cluster_input: Raw cluster input (can be name, FQDN, or full URI)
        
    Returns:
        Normalized HTTPS URI for the cluster
        
    Raises:
        ValueError: If the cluster input is invalid
    """
    if not cluster_input or not cluster_input.strip():
        raise ValueError("Cluster input cannot be empty")
    
    cluster_input = cluster_input.strip()
    
    # If already a full HTTPS URI
    if cluster_input.startswith("https://"):
        parsed = urlparse(cluster_input)
        if not parsed.netloc:
            raise ValueError(f"Invalid cluster URI: {cluster_input}")
        return cluster_input
    
    # If it's a full domain name
    if "." in cluster_input and not cluster_input.startswith("http"):
        return f"https://{cluster_input}"
    
    # If it's just a cluster name
    if re.match(r'^[a-zA-Z0-9\-_]+$', cluster_input):
        return f"https://{cluster_input}.kusto.windows.net"
    
    raise ValueError(f"Invalid cluster format: {cluster_input}")


def extract_cluster_and_database_from_query(query: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract cluster URI and database name from a KQL query.
    
    Args:
        query: KQL query string
        
    Returns:
        Tuple of (cluster_uri, database_name) or (None, None) if not found
    """
    try:
        # Extract cluster
        cluster_match = re.search(r"cluster\('([^']+)'\)", query)
        if not cluster_match:
            return None, None
        
        cluster_uri = normalize_cluster_uri(cluster_match.group(1))
        
        # Extract database
        database_match = re.search(r"database\('([^']+)'\)", query)
        if not database_match:
            return cluster_uri, None
        
        database_name = database_match.group(1)
        
        return cluster_uri, database_name
        
    except Exception as e:
        logger.warning(f"Failed to extract cluster/database from query: {str(e)}")
        return None, None


def clean_query_for_execution(query: str) -> str:
    """Clean a KQL query by removing cluster and database prefixes.
    
    Args:
        query: Original KQL query with cluster/database prefixes
        
    Returns:
        Cleaned query ready for execution
    """
    # Remove cluster('...').database('...').
    cleaned = re.sub(
        r"cluster\('([^']+)'\)\.database\('([^']+)'\)\.",
        "",
        query,
        count=1
    )
    
    return cleaned.strip()


def format_error_message(error: Exception, context: str = "") -> str:
    """Format an error message with context for user display.
    
    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred
        
    Returns:
        Formatted error message suitable for user display
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    if context:
        return f"{context}: {error_type} - {error_msg}"
    else:
        return f"{error_type}: {error_msg}"


def validate_kql_query_syntax(query: str) -> Tuple[bool, Optional[str]]:
    """Perform basic syntax validation on a KQL query.
    
    Args:
        query: KQL query to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not query or not query.strip():
        return False, "Query cannot be empty"
    
    query = query.strip()
    
    # Check for required cluster() function
    if not re.search(r"cluster\('([^']+)'\)", query):
        return False, "Query must include cluster('...') specification"
    
    # Check for required database() function
    if not re.search(r"database\('([^']+)'\)", query):
        return False, "Query must include database('...') specification"
    
    # Check for basic KQL structure
    # After removing cluster/db prefix, should have table name or other valid KQL
    cleaned = clean_query_for_execution(query)
    if not cleaned:
        return False, "Query contains no executable KQL after cluster/database specification"
    
    # Check for suspicious characters that might indicate injection
    # Temporarily disabled to allow complex KQL queries with regex patterns
    suspicious_patterns = [
        # r'[\x00-\x08\x0b-\x0c\x0e-\x1f]',  # Control characters (but allow \t, \n, \r)
        # r'--\s*$',        # SQL-style comments at end
        # r'/\*.*\*/',      # Block comments
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, query, re.MULTILINE | re.DOTALL):
            return False, "Query contains potentially unsafe characters"
    
    return True, None


def safe_get_env_var(var_name: str, default: str = "") -> str:
    """Safely get an environment variable with a default value.
    
    Args:
        var_name: Name of the environment variable
        default: Default value if the variable is not set
        
    Returns:
        Environment variable value or default
    """
    return os.environ.get(var_name, default).strip()


def ensure_directory_exists(path: Path) -> bool:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Path to the directory
        
    Returns:
        True if directory exists or was created successfully
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {str(e)}")
        return False


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate a string to a maximum length with an optional suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length (including suffix)
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    truncated_length = max_length - len(suffix)
    if truncated_length <= 0:
        return suffix[:max_length]
    
    return text[:truncated_length] + suffix


def is_debug_mode() -> bool:
    """Check if debug mode is enabled.
    
    Debug mode is automatically enabled for development and can be controlled
    by setting KQL_DEBUG environment variable if needed.
    
    Returns:
        True if debug mode is enabled
    """
    # Default to False for production use, but allow override via environment
    debug_env = os.environ.get('KQL_DEBUG', '').lower()
    if debug_env in ['1', 'true', 'yes', 'on']:
        return True
    
    # Auto-enable debug mode if running in development environment
    # This can be detected by checking if we're running from source
    try:
        import sys
        # If running from source (not installed package), enable debug
        if hasattr(sys, '_called_from_test') or 'pytest' in sys.modules:
            return True
    except:
        pass
    
    return False


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """Mask sensitive data for logging, showing only first/last few characters.
    
    Args:
        data: Sensitive data to mask
        mask_char: Character to use for masking
        visible_chars: Number of characters to show at start and end
        
    Returns:
        Masked string
    """
    if len(data) <= visible_chars * 2:
        return mask_char * len(data)
    
    start = data[:visible_chars]
    end = data[-visible_chars:]
    middle_length = len(data) - (visible_chars * 2)
    
    return f"{start}{mask_char * middle_length}{end}"


def parse_connection_string_params(connection_string: str) -> Dict[str, str]:
    """Parse connection string parameters into a dictionary.
    
    Args:
        connection_string: Connection string with key=value pairs
        
    Returns:
        Dictionary of parsed parameters
    """
    params = {}
    
    # Split by semicolon and parse key=value pairs
    for param in connection_string.split(';'):
        param = param.strip()
        if '=' in param:
            key, value = param.split('=', 1)
            params[key.strip().lower()] = value.strip()
    
    return params


def format_bytes(bytes_count: int) -> str:
    """Format bytes count into human-readable string.
    
    Args:
        bytes_count: Number of bytes
        
    Returns:
        Formatted string (e.g., "1.5 KB", "2.3 MB")
    """
    if bytes_count < 1024:
        return f"{bytes_count} B"
    elif bytes_count < 1024 ** 2:
        return f"{bytes_count / 1024:.1f} KB"
    elif bytes_count < 1024 ** 3:
        return f"{bytes_count / (1024 ** 2):.1f} MB"
    else:
        return f"{bytes_count / (1024 ** 3):.1f} GB"


def get_file_age_days(filepath: Path) -> Optional[float]:
    """Get the age of a file in days.
    
    Args:
        filepath: Path to the file
        
    Returns:
        Age in days or None if file doesn't exist
    """
    try:
        if not filepath.exists():
            return None
        
        import time
        file_time = filepath.stat().st_mtime
        current_time = time.time()
        age_seconds = current_time - file_time
        
        return age_seconds / (24 * 60 * 60)  # Convert to days
        
    except Exception as e:
        logger.warning(f"Failed to get file age for {filepath}: {str(e)}")
        return None