"""
KQL Schema Memory Module (Enhanced Unified Version)

This module provides intelligent schema discovery and memory management for KQL clusters.
It integrates with the unified memory system to provide AI-optimized context loading
with special tokens and cross-cluster support. Prevents context size issues through
intelligent compression and relevance-based loading.

Author: Arjun Trivedi
Email: arjuntrivedi42@yahoo.com
"""

import json
import os
import re
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.exceptions import KustoServiceError

# Import the new unified memory system
from .unified_memory import (
    get_unified_memory,
    load_query_relevant_context as unified_load_context,
    ensure_table_in_memory as unified_ensure_table,
    get_table_ai_token as unified_get_token,
    SPECIAL_TOKENS
)

logger = logging.getLogger(__name__)

def _normalize_cluster_uri(cluster_uri: str) -> str:
    """Normalize cluster URI to standard format."""
    if cluster_uri.startswith("https://"):
        return cluster_uri
    elif "." in cluster_uri:
        return f"https://{cluster_uri}"
    else:
        return f"https://{cluster_uri}.kusto.windows.net"

def _cluster_hash(cluster_uri: str) -> str:
    """Generate hash for cluster URI."""
    return hashlib.md5(cluster_uri.encode()).hexdigest()[:8]  # Shorter hash for cleaner paths

def _get_memory_base_path(memory_path: Optional[str] = None) -> Path:
    """Get base path for memory storage (legacy compatibility)."""
    if memory_path:
        return Path(memory_path)
    if os.name == 'nt':
        base_path = Path(os.environ.get('APPDATA', ''))
    else:
        base_path = Path.home() / '.local' / 'share'
    return base_path / 'KQL_MCP' / 'cluster_memory'

def _get_table_memory_path(cluster_uri: str, database: str, table: str, memory_path: Optional[str] = None) -> Path:
    """Get path for specific table memory file (legacy compatibility)."""
    base = _get_memory_base_path(memory_path)
    cluster_hash = _cluster_hash(_normalize_cluster_uri(cluster_uri))
    return base / cluster_hash / database / f"{table}.json"

def _create_ai_context_token(table: str, summary: str, columns: List[Dict[str, str]]) -> str:
    """Create AI context token using new special token system."""
    # Use the new unified memory system for token creation
    memory = get_unified_memory()
    
    # Convert columns to expected format
    formatted_columns = []
    for col in columns:
        formatted_columns.append({
            "name": col.get("name", "unknown"),
            "type": col.get("type", "string"),
            "ai_desc": col.get("ai_desc", col.get("description", "unknown_field"))
        })
    
    # Create token with special markers
    return memory._create_ai_friendly_token(table, "unknown", "unknown", formatted_columns)

def _get_column_ai_description(name: str, type_: str, table: str) -> str:
    """Generate ultra-compact AI descriptions for columns."""
    # Ultra-compact descriptions to save context space
    patterns = {
        "TimeGenerated": "event_timestamp_utc",
        "EventID": "event_type_id", 
        "UserName": "user_account",
        "Account": "account_name",
        "Computer": "hostname",
        "ComputerName": "hostname", 
        "LogonType": "logon_method_type",
        "SubjectUserName": "initiating_user",
        "TargetUserName": "target_user",
        "SourceIP": "source_ip_addr",
        "ClientIP": "client_ip_addr",
        "EventData": "event_details_json",
        "ProcessName": "executable_name",
        "CommandLine": "process_command",
        "WorkstationName": "client_workstation",
        "SessionID": "logon_session_id",
        "ActivityID": "activity_correlation_id"
    }
    
    if name in patterns:
        return patterns[name]
    
    # Fallback patterns for unknown columns
    name_lower = name.lower()
    if "time" in name_lower or "date" in name_lower:
        return "timestamp_field"
    elif "id" in name_lower:
        return "identifier_field"
    elif "name" in name_lower:
        return "name_field"
    elif "ip" in name_lower or "address" in name_lower:
        return "network_address"
    elif "count" in name_lower or "number" in name_lower:
        return "numeric_count"
    elif "status" in name_lower or "result" in name_lower:
        return "status_indicator"
    else:
        return f"{type_.lower()}_field"

def _get_table_ai_summary(table_name: str, columns: List[str]) -> str:
    """Generate ultra-compact AI summary for table."""
    table_lower = table_name.lower()
    
    # Security and authentication tables
    if any(keyword in table_lower for keyword in ["security", "auth", "logon", "login"]):
        return "security_audit_events"
    elif any(keyword in table_lower for keyword in ["event", "log"]):
        return "system_event_logs"
    elif any(keyword in table_lower for keyword in ["network", "conn", "traffic"]):
        return "network_activity_logs"
    elif any(keyword in table_lower for keyword in ["process", "exec"]):
        return "process_execution_logs"
    elif any(keyword in table_lower for keyword in ["file", "disk"]):
        return "file_system_activity"
    elif any(keyword in table_lower for keyword in ["user", "identity"]):
        return "user_identity_data"
    elif any(keyword in table_lower for keyword in ["alert", "incident"]):
        return "security_alerts"
    else:
        return f"data_table_{len(columns)}_cols"

def save_table_memory(cluster_uri: str, database: str, table: str, columns: List[Dict[str, Any]], memory_path: Optional[str] = None, example_queries: Optional[List[str]] = None):
    """Save per-table AI-optimized memory file."""
    path = _get_table_memory_path(cluster_uri, database, table, memory_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert columns to AI-friendly format
    ai_columns = []
    for col in columns:
        ai_desc = _get_column_ai_description(col['name'], col['type'], table)
        ai_columns.append({
            "name": col['name'],
            "type": col['type'], 
            "ai_desc": ai_desc
        })
    
    # Generate compact summary
    summary = _get_table_ai_summary(table, [col['name'] for col in columns])
    
    # Create ultra-compact AI context token
    ai_context_token = _create_ai_context_token(table, summary, ai_columns)
    
    # Create common example queries for the table
    if not example_queries:
        example_queries = [
            f"{table} | take 10",
            f"{table} | where TimeGenerated > ago(1h) | take 100",
            f"{table} | summarize count() by bin(TimeGenerated, 1h)",
            f"{table} | project TimeGenerated, * | order by TimeGenerated desc"
        ]
    
    data = {
        "table": table,
        "database": database,
        "cluster_uri": cluster_uri,
        "summary": summary,
        "ai_context_token": ai_context_token,  # Ultra-compact representation for AI
        "columns": ai_columns,
        "example_queries": example_queries,
        "last_updated": datetime.now().isoformat(),
        "column_count": len(ai_columns)
    }
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved AI-optimized table memory: {path}")
    return path

def load_table_memory(cluster_uri: str, database: str, table: str, memory_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Load per-table memory file."""
    path = _get_table_memory_path(cluster_uri, database, table, memory_path)
    if not path.exists():
        return None
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load table memory {path}: {e}")
        return None

def discover_and_save_table_schema(cluster_uri: str, database: str, table: str, memory_path: Optional[str] = None):
    """Discover schema for a table and save using unified memory system."""
    
    # Use the unified memory system for discovery
    memory = get_unified_memory(memory_path)
    return memory.discover_and_save_table_schema(cluster_uri, database, table)

def get_context_for_tables(cluster_uri: str, database: str, tables: List[str], memory_path: Optional[str] = None) -> List[str]:
    """Load AI context tokens for relevant tables using unified memory system."""
    
    # Use the unified memory system for optimized context loading
    memory = get_unified_memory(memory_path)
    context_tokens = []
    
    # Ensure all tables are in memory and get their tokens
    for table in tables:
        try:
            if memory.ensure_table_in_memory(cluster_uri, database, table):
                token = memory.get_table_ai_token(cluster_uri, database, table)
                if token:
                    context_tokens.append(token)
                else:
                    # Fallback token with special markers
                    fallback_token = f"{SPECIAL_TOKENS['TABLE']}{table}|{SPECIAL_TOKENS['DESCRIPTION']}discovery_needed"
                    context_tokens.append(fallback_token)
            else:
                # Discovery failed, add placeholder
                fallback_token = f"{SPECIAL_TOKENS['TABLE']}{table}|{SPECIAL_TOKENS['DESCRIPTION']}discovery_failed"
                context_tokens.append(fallback_token)
        except Exception as e:
            logger.warning(f"Failed to get context for {database}.{table}: {e}")
            fallback_token = f"{SPECIAL_TOKENS['TABLE']}{table}|{SPECIAL_TOKENS['DESCRIPTION']}error_occurred"
            context_tokens.append(fallback_token)
    
    # Apply context size management
    total_size = sum(len(token) for token in context_tokens)
    if total_size > 4000:  # Apply size limit
        logger.warning(f"Context size {total_size} exceeds limit, applying compression")
        compressed_tokens = []
        remaining_size = 4000
        
        for token in context_tokens:
            if len(token) <= remaining_size:
                compressed_tokens.append(token)
                remaining_size -= len(token)
            else:
                # Try to compress the token
                compressed = memory._compress_token(token, remaining_size)
                if compressed:
                    compressed_tokens.append(compressed)
                break
        
        context_tokens = compressed_tokens
    
    logger.info(f"Loaded {len(context_tokens)} context tokens for tables: {tables}")
    return context_tokens

def ensure_table_memory(cluster_uri: str, database: str, table: str, memory_path: Optional[str] = None):
    """Ensure table memory exists using unified memory system."""
    memory = get_unified_memory(memory_path)
    return unified_ensure_table(cluster_uri, database, table)

def update_memory_after_query(cluster_uri: str, database: str, tables: List[str], memory_path: Optional[str] = None):
    """After query execution, ensure all referenced tables are in memory."""
    memory = get_unified_memory(memory_path)
    
    for table in tables:
        try:
            memory.ensure_table_in_memory(cluster_uri, database, table)
        except Exception as e:
            logger.warning(f"Failed to update memory for {database}.{table}: {e}")

def extract_tables_from_query(query: str) -> List[str]:
    """Extract table names from a KQL query with support for complex union queries."""
    tables = []
    
    # Pattern 1: cluster('...').database('...').TableName
    pattern1 = r"\.database\('([^']+)'\)\.([A-Za-z_][A-Za-z0-9_]*)"
    matches1 = re.findall(pattern1, query)
    for _, table in matches1:
        tables.append(table)
    
    # Pattern 2: TableName | (table followed by pipe)
    pattern2 = r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\|"
    matches2 = re.findall(pattern2, query)
    kql_keywords = {
        'where', 'project', 'extend', 'summarize', 'join', 'union', 'order', 'top',
        'take', 'limit', 'distinct', 'count', 'render', 'sort', 'mv-expand',
        'mv-apply', 'parse', 'extract', 'split', 'bag_unpack', 'evaluate'
    }
    for table in matches2:
        if table.lower() not in kql_keywords:
            tables.append(table)
    
    # Pattern 3: FROM TableName (if any)
    pattern3 = r"\bfrom\s+([A-Za-z_][A-Za-z0-9_]*)"
    matches3 = re.findall(pattern3, query, re.IGNORECASE)
    tables.extend(matches3)
    
    # Pattern 4: Union queries - extract table names from union clauses
    # Handle: union cluster('...').database('...').Table1, cluster('...').database('...').Table2
    union_pattern = r'union\s+(.*?)(?:\||$|;)'
    union_matches = re.findall(union_pattern, query, re.IGNORECASE | re.DOTALL)
    for union_clause in union_matches:
        # Extract table references from union clause
        union_table_pattern = r"\.database\('([^']+)'\)\.([A-Za-z_][A-Za-z0-9_]*)"
        union_tables = re.findall(union_table_pattern, union_clause)
        for _, table in union_tables:
            tables.append(table)
    
    # Remove duplicates and return
    unique_tables = list(set(tables))
    logger.debug(f"Extracted tables from query: {unique_tables}")
    return unique_tables

def get_example_queries_for_table(cluster_uri: str, database: str, table: str, memory_path: Optional[str] = None) -> List[str]:
    """Get example queries for a specific table."""
    mem = load_table_memory(cluster_uri, database, table, memory_path)
    if mem:
        return mem.get("example_queries", [])
    return []

def list_discovered_tables(cluster_uri: str, memory_path: Optional[str] = None) -> List[Dict[str, str]]:
    """List all discovered tables for a cluster."""
    base_path = _get_memory_base_path(memory_path)
    cluster_hash = _cluster_hash(_normalize_cluster_uri(cluster_uri))
    cluster_path = base_path / cluster_hash
    
    tables = []
    if cluster_path.exists():
        for db_path in cluster_path.iterdir():
            if db_path.is_dir():
                for table_file in db_path.glob("*.json"):
                    tables.append({
                        "database": db_path.name,
                        "table": table_file.stem,
                        "path": str(table_file)
                    })
    
    return tables