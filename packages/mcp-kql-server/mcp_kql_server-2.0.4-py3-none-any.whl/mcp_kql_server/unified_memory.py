"""
Unified Schema Memory System for MCP KQL Server

This module provides a unified schema memory system that:
- Stores schema at %APPDATA%/KQL_MCP/schema_memory.json
- Uses AI-friendly special tokens (@@CLUSTER@@, ##DATABASE##, ##TABLE##, ::COLUMN::, %%DESC%%)
- Includes ALL columns with summaries (no artificial limits)
- Supports cross-cluster table sharing
- Prevents context size bloat with intelligent compression

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
from typing import Dict, List, Optional, Any, Tuple, Set

from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.exceptions import KustoServiceError

logger = logging.getLogger(__name__)

# AI-Friendly Special Tokens
SPECIAL_TOKENS = {
    "CLUSTER": "@@CLUSTER@@",
    "DATABASE": "##DATABASE##", 
    "TABLE": "##TABLE##",
    "COLUMN": "::COLUMN::",
    "DESCRIPTION": "%%DESC%%",
    "TYPE": ">>TYPE<<",
    "SUMMARY": "**SUMMARY**"
}

class UnifiedSchemaMemory:
    """Unified schema memory manager with AI-optimized token system."""
    
    def __init__(self, custom_memory_path: Optional[str] = None):
        """Initialize unified schema memory.
        
        Args:
            custom_memory_path: Optional custom path for memory storage
        """
        self.memory_path = self._get_memory_path(custom_memory_path)
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self._memory_cache = None
        self._index_cache = None
        
    def _get_memory_path(self, custom_path: Optional[str] = None) -> Path:
        """Get the path for unified schema memory."""
        if custom_path:
            return Path(custom_path) / "schema_memory.json"
        
        if os.name == 'nt':  # Windows
            base_path = Path(os.environ.get('APPDATA', ''))
        else:  # macOS/Linux
            base_path = Path.home() / '.local' / 'share'
        
        return base_path / 'KQL_MCP' / 'schema_memory.json'
    
    def load_memory(self) -> Dict[str, Any]:
        """Load schema memory from disk with caching."""
        if self._memory_cache is not None:
            return self._memory_cache
        
        if not self.memory_path.exists():
            self._memory_cache = self._create_empty_memory()
            self.save_memory()
            return self._memory_cache
        
        try:
            with open(self.memory_path, 'r', encoding='utf-8') as f:
                self._memory_cache = json.load(f)
            
            # Ensure proper structure
            if "version" not in self._memory_cache:
                self._memory_cache = self._migrate_memory(self._memory_cache)
            
            return self._memory_cache
            
        except Exception as e:
            logger.warning(f"Failed to load memory from {self.memory_path}: {e}")
            self._memory_cache = self._create_empty_memory()
            return self._memory_cache
    
    def save_memory(self) -> bool:
        """Save schema memory to disk."""
        if self._memory_cache is None:
            return False
        
        try:
            # Update timestamp
            self._memory_cache["last_updated"] = datetime.now().isoformat()
            
            # Ensure directory exists
            self.memory_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to temporary file first, then rename for atomicity
            temp_path = self.memory_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(self._memory_cache, f, indent=2, ensure_ascii=False)
            
            temp_path.replace(self.memory_path)
            
            # Clear index cache to force rebuild
            self._index_cache = None
            
            logger.info(f"Saved unified schema memory to {self.memory_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save memory to {self.memory_path}: {e}")
            return False
    
    def _create_empty_memory(self) -> Dict[str, Any]:
        """Create empty memory structure."""
        return {
            "version": "2.0",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "clusters": {}
        }
    
    def _migrate_memory(self, old_memory: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate old memory format to new unified format."""
        logger.info("Migrating schema memory to unified format")
        
        new_memory = self._create_empty_memory()
        
        # If old memory has cluster-based structure, migrate it
        if "clusters" in old_memory:
            new_memory["clusters"] = old_memory["clusters"]
        
        return new_memory
    
    def table_exists_in_memory(self, cluster_uri: str, database: str, table: str) -> bool:
        """Check if table schema exists in memory."""
        memory = self.load_memory()
        normalized_cluster = self._normalize_cluster_uri(cluster_uri)
        
        return (normalized_cluster in memory["clusters"] and 
                database in memory["clusters"][normalized_cluster].get("databases", {}) and
                table in memory["clusters"][normalized_cluster]["databases"][database].get("tables", {}))
    
    def get_table_ai_token(self, cluster_uri: str, database: str, table: str) -> Optional[str]:
        """Get AI-friendly token for a specific table."""
        if not self.table_exists_in_memory(cluster_uri, database, table):
            return None
        
        memory = self.load_memory()
        normalized_cluster = self._normalize_cluster_uri(cluster_uri)
        
        try:
            table_data = memory["clusters"][normalized_cluster]["databases"][database]["tables"][table]
            return table_data.get("ai_token")
        except KeyError:
            return None
    
    def ensure_table_in_memory(self, cluster_uri: str, database: str, table: str) -> bool:
        """Ensure table schema exists in memory, discover if missing."""
        if self.table_exists_in_memory(cluster_uri, database, table):
            return True
        
        logger.info(f"Table {database}.{table} not in memory, discovering schema...")
        return self.discover_and_save_table_schema(cluster_uri, database, table)
    
    def discover_and_save_table_schema(self, cluster_uri: str, database: str, table: str) -> bool:
        """Discover schema for a table and save with AI-optimized tokens."""
        normalized_cluster = self._normalize_cluster_uri(cluster_uri)
        
        try:
            kcsb = KustoConnectionStringBuilder.with_az_cli_authentication(normalized_cluster)
            client = KustoClient(kcsb)
            
            try:
                # Get table schema
                schema_query = f".show table {table} cslschema"
                schema_response = client.execute_mgmt(database, schema_query)
                
                columns = []
                if schema_response.primary_results[0].rows:
                    schema_text = schema_response.primary_results[0].rows[0][1]
                    # Extract ALL column definitions (no limits as per requirement)
                    column_pattern = r'(\w+):(\w+)(?:\s*=\s*[^,\)]+)?'
                    matches = re.findall(column_pattern, schema_text)
                    
                    for col_name, col_type in matches:
                        ai_desc = self._generate_ai_description(col_name, col_type, table)
                        columns.append({
                            "name": col_name,
                            "type": col_type,
                            "description": f"Column {col_name} of type {col_type} in table {table}",
                            "ai_desc": ai_desc
                        })
                
                # Create AI-friendly token with special markers
                ai_token = self._create_ai_friendly_token(table, normalized_cluster, database, columns)
                
                # Save to unified memory
                self._update_memory_with_table(normalized_cluster, database, table, columns, ai_token)
                
                logger.info(f"Successfully discovered and saved schema for {database}.{table}")
                return True
                
            finally:
                client.close()
                
        except Exception as e:
            logger.error(f"Failed to discover schema for {database}.{table}: {e}")
            return False
    
    def _create_ai_friendly_token(self, table: str, cluster_uri: str, database: str, columns: List[Dict]) -> str:
        """Create AI-friendly token with special markers for efficient parsing."""
        
        # Start with cluster, database, table markers
        token_parts = [
            f"{SPECIAL_TOKENS['CLUSTER']}{self._extract_cluster_name(cluster_uri)}",
            f"{SPECIAL_TOKENS['DATABASE']}{database}",
            f"{SPECIAL_TOKENS['TABLE']}{table}"
        ]
        
        # Add table summary
        table_summary = self._generate_table_summary(table, columns)
        token_parts.append(f"{SPECIAL_TOKENS['SUMMARY']}{table_summary}")
        
        # Add ALL columns with AI-friendly descriptions (no limits)
        for col in columns:
            col_token = (f"{SPECIAL_TOKENS['COLUMN']}{col['name']}"
                        f"{SPECIAL_TOKENS['TYPE']}{col['type']}"
                        f"{SPECIAL_TOKENS['DESCRIPTION']}{col['ai_desc']}")
            token_parts.append(col_token)
        
        # Join with separator
        full_token = "|".join(token_parts)
        
        # Log token size for monitoring
        logger.debug(f"Generated AI token for {table}: {len(full_token)} characters")
        
        return full_token
    
    def _generate_ai_description(self, col_name: str, col_type: str, table: str) -> str:
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
            "ActivityID": "activity_correlation_id",
            "TenantId": "azure_tenant_id",
            "SubscriptionId": "azure_subscription_id",
            "ResourceGroup": "azure_resource_group",
            "ResourceId": "azure_resource_id"
        }
        
        if col_name in patterns:
            return patterns[col_name]
        
        # Fallback patterns for unknown columns
        name_lower = col_name.lower()
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
            return f"{col_type.lower()}_field"
    
    def _generate_table_summary(self, table_name: str, columns: List[Dict]) -> str:
        """Generate ultra-compact summary for table."""
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
    
    def _update_memory_with_table(self, cluster_uri: str, database: str, table: str, 
                                  columns: List[Dict], ai_token: str):
        """Update unified memory with table information."""
        memory = self.load_memory()
        
        # Ensure cluster exists
        if cluster_uri not in memory["clusters"]:
            memory["clusters"][cluster_uri] = {"databases": {}}
        
        # Ensure database exists
        if database not in memory["clusters"][cluster_uri]["databases"]:
            memory["clusters"][cluster_uri]["databases"][database] = {"tables": {}}
        
        # Prepare column data
        columns_dict = {}
        for col in columns:
            columns_dict[col["name"]] = {
                "type": col["type"],
                "description": col["description"],
                "ai_desc": col["ai_desc"]
            }
        
        # Update table data
        memory["clusters"][cluster_uri]["databases"][database]["tables"][table] = {
            "ai_token": ai_token,
            "columns": columns_dict,
            "column_count": len(columns),
            "last_discovered": datetime.now().isoformat(),
            "shared_with_clusters": []  # For cross-cluster sharing
        }
        
        self._memory_cache = memory
        self.save_memory()
    
    def load_query_relevant_context(self, query: str, max_context_size: int = 4000) -> List[str]:
        """Load context tokens relevant to a specific query with size management."""
        
        # Extract all cluster/database/table references
        cluster_table_refs = self._extract_all_cluster_table_refs(query)
        
        context_tokens = []
        total_size = 0
        
        for cluster_uri, database, table in cluster_table_refs:
            # Ensure table is in memory
            if self.ensure_table_in_memory(cluster_uri, database, table):
                token = self.get_table_ai_token(cluster_uri, database, table)
                if token:
                    # Check if adding this token would exceed size limit
                    if total_size + len(token) <= max_context_size:
                        context_tokens.append(token)
                        total_size += len(token)
                    else:
                        # Try to compress the token
                        compressed_token = self._compress_token(token, max_context_size - total_size)
                        if compressed_token:
                            context_tokens.append(compressed_token)
                            total_size += len(compressed_token)
                        break  # Stop adding more tokens
        
        logger.info(f"Loaded {len(context_tokens)} context tokens, total size: {total_size} chars")
        return context_tokens
    
    def _extract_all_cluster_table_refs(self, query: str) -> List[Tuple[str, str, str]]:
        """Extract all cluster/database/table references from a query."""
        refs = []
        
        # Pattern for cluster('...').database('...').table
        cluster_table_pattern = r"cluster\('([^']+)'\)\.database\('([^']+)'\)\.([A-Za-z_][A-Za-z0-9_]*)"
        matches = re.findall(cluster_table_pattern, query)
        
        for cluster_raw, database, table in matches:
            cluster_uri = self._normalize_cluster_uri(cluster_raw)
            refs.append((cluster_uri, database, table))
        
        return refs
    
    def _compress_token(self, token: str, max_size: int) -> Optional[str]:
        """Compress a token to fit within size limit."""
        if len(token) <= max_size:
            return token
        
        if max_size < 100:  # Too small to compress meaningfully
            return None
        
        # Try to keep the most important parts
        parts = token.split("|")
        if len(parts) < 4:  # Cluster, database, table, summary minimum
            return None
        
        # Keep cluster, database, table, summary and as many columns as fit
        essential_parts = parts[:4]  # cluster, database, table, summary
        essential_size = sum(len(part) + 1 for part in essential_parts)  # +1 for separators
        
        if essential_size >= max_size:
            return None
        
        # Add columns until size limit
        remaining_size = max_size - essential_size
        column_parts = []
        
        for part in parts[4:]:  # Skip essential parts
            if len(part) + 1 <= remaining_size:  # +1 for separator
                column_parts.append(part)
                remaining_size -= len(part) + 1
            else:
                break
        
        compressed_parts = essential_parts + column_parts
        if len(column_parts) < len(parts) - 4:
            # Add truncation indicator
            compressed_parts.append(f"::COLUMN::truncated_cols>>TYPE<<info%%DESC%%{len(parts) - 4 - len(column_parts)}_more_columns")
        
        return "|".join(compressed_parts)
    
    def _normalize_cluster_uri(self, cluster_input: str) -> str:
        """Normalize cluster URI to standard format."""
        if not cluster_input or not cluster_input.strip():
            raise ValueError("Cluster input cannot be empty")
        
        cluster_input = cluster_input.strip()
        
        # If already a full HTTPS URI
        if cluster_input.startswith("https://"):
            return cluster_input
        
        # If it's a full domain name
        if "." in cluster_input and not cluster_input.startswith("http"):
            return f"https://{cluster_input}"
        
        # If it's just a cluster name
        if re.match(r'^[a-zA-Z0-9\-_]+$', cluster_input):
            return f"https://{cluster_input}.kusto.windows.net"
        
        raise ValueError(f"Invalid cluster format: {cluster_input}")
    
    def _extract_cluster_name(self, cluster_uri: str) -> str:
        """Extract short cluster name from URI for tokens."""
        # Extract just the cluster name part for compact tokens
        if cluster_uri.startswith("https://"):
            hostname = cluster_uri[8:].split('.')[0]
            return hostname
        return cluster_uri
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about the schema memory."""
        memory = self.load_memory()
        
        stats = {
            "version": memory.get("version", "unknown"),
            "last_updated": memory.get("last_updated"),
            "total_clusters": len(memory.get("clusters", {})),
            "total_databases": 0,
            "total_tables": 0,
            "memory_file_size": 0
        }
        
        # Calculate totals
        for cluster_data in memory.get("clusters", {}).values():
            for database_data in cluster_data.get("databases", {}).values():
                stats["total_databases"] += 1
                stats["total_tables"] += len(database_data.get("tables", {}))
        
        # Get file size
        if self.memory_path.exists():
            stats["memory_file_size"] = self.memory_path.stat().st_size
        
        return stats
    
    def clear_memory(self) -> bool:
        """Clear all schema memory."""
        try:
            self._memory_cache = self._create_empty_memory()
            self.save_memory()
            logger.info("Schema memory cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")
            return False

# Global instance
_unified_memory = None

def get_unified_memory(custom_path: Optional[str] = None) -> UnifiedSchemaMemory:
    """Get global unified memory instance."""
    global _unified_memory
    if _unified_memory is None:
        _unified_memory = UnifiedSchemaMemory(custom_path)
    return _unified_memory

# Convenience functions for backward compatibility
def load_query_relevant_context(query: str, max_context_size: int = 4000) -> List[str]:
    """Load context tokens relevant to a query."""
    memory = get_unified_memory()
    return memory.load_query_relevant_context(query, max_context_size)

def ensure_table_in_memory(cluster_uri: str, database: str, table: str) -> bool:
    """Ensure table schema exists in memory."""
    memory = get_unified_memory()
    return memory.ensure_table_in_memory(cluster_uri, database, table)

def get_table_ai_token(cluster_uri: str, database: str, table: str) -> Optional[str]:
    """Get AI token for a table."""
    memory = get_unified_memory()
    return memory.get_table_ai_token(cluster_uri, database, table)