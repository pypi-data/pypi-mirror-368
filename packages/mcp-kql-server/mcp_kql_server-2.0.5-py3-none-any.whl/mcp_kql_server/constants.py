"""
Constants for the MCP KQL Server.

This module contains all the constants used throughout the MCP KQL Server,
including default values, configuration settings, error messages, and other
static values.

Author: Arjun Trivedi
Email: arjuntrivedi42@yahoo.com
"""

from typing import Dict, List

# Version information
__version__ = "2.0.5"
MCP_PROTOCOL_VERSION = "2024-11-05"

# Server configuration
SERVER_NAME = f"mcp-kql-server({__version__})"
SERVER_DESCRIPTION = """AI-Enhanced KQL Server for Cybersecurity Analytics

An intelligent Model Context Protocol (MCP) server that provides advanced KQL query execution
capabilities with AI-powered schema discovery and intelligent security analytics assistance.

Key Features:
- AI-powered schema memory with intelligent table/column descriptions
- Cross-cluster query execution with unified authentication
- Security-focused table and column pattern recognition
- Real-time query visualization and result formatting
- FastMCP implementation for optimal performance

Perfect for SOC analysts, threat hunters, and security researchers working with Azure Data Explorer."""

# Default paths and directories
DEFAULT_MEMORY_DIR_NAME = "KQL_MCP"
DEFAULT_CLUSTER_MEMORY_DIR = "cluster_memory"
SCHEMA_FILE_EXTENSION = ".json"

# Azure and KQL configuration
DEFAULT_KUSTO_DOMAIN = "kusto.windows.net"
SYSTEM_DATABASES = {"$systemdb"}
DEFAULT_CONNECTION_TIMEOUT = 60  # Increased from 30
DEFAULT_QUERY_TIMEOUT = 600  # Increased from 300

# Schema memory configuration
SCHEMA_CACHE_MAX_AGE_DAYS = 7
MAX_SCHEMA_FILE_SIZE_MB = 10
MAX_TABLES_PER_DATABASE = 1000
MAX_COLUMNS_PER_TABLE = 500

# Query validation
MAX_QUERY_LENGTH = 100000
MIN_QUERY_LENGTH = 10

# Default configuration (no environment variables required)
DEFAULT_CONFIG = {
    "DEBUG_MODE": False,  # Default to production mode
    "AZURE_ERRORS_ONLY": True,  # Hide verbose Azure logs by default
    "CONNECTION_TIMEOUT": DEFAULT_CONNECTION_TIMEOUT,
    "QUERY_TIMEOUT": DEFAULT_QUERY_TIMEOUT,
    "AUTO_CREATE_MEMORY_PATH": True,  # Automatically create memory directories
    "ENABLE_LOGGING": True,  # Enable basic logging
}

# Logging configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Error messages
ERROR_MESSAGES = {
    "auth_failed": "Authentication failed. Please run 'az login' and try again.",
    "empty_query": "Query cannot be empty.",
    "invalid_cluster": "Invalid cluster URI format.",
    "invalid_database": "Invalid database name format.",
    "connection_timeout": "Connection to cluster timed out.",
    "query_timeout": "Query execution timed out.",
    "permission_denied": "Permission denied. Check your access rights to the cluster.",
    "cluster_not_found": "Cluster not found or not accessible.",
    "database_not_found": "Database not found in the specified cluster.",
    "table_not_found": "Table not found in the specified database.",
    "schema_discovery_failed": "Failed to discover cluster schema.",
    "schema_save_failed": "Failed to save schema memory.",
    "schema_load_failed": "Failed to load schema memory.",
    "memory_path_error": "Error accessing cluster memory path.",
}

# Success messages
SUCCESS_MESSAGES = {
    "query_executed": "Query executed successfully.",
    "schema_discovered": "Cluster schema discovered successfully.",
    "schema_saved": "Schema memory saved successfully.",
    "schema_loaded": "Schema memory loaded successfully.",
    "auth_success": "Authentication successful.",
}

# KQL query patterns for validation
QUERY_PATTERNS = {
    "cluster_pattern": r"cluster\('([^']+)'\)",
    "database_pattern": r"database\('([^']+)'\)",
    "table_pattern": r'\b([A-Za-z_][A-Za-z0-9_]*)\s*\|',
    "from_pattern": r'\.([A-Za-z_][A-Za-z0-9_]*)\s*(?:\||$|;)',
    "comment_pattern": r'//.*$',
    "multiline_comment_pattern": r'/\*.*?\*/',
}

# Schema discovery queries
DISCOVERY_QUERIES = {
    "show_databases": ".show databases",
    "show_tables": ".show tables",
    "show_table_schema": ".show table {table_name} cslschema",
    "show_columns": ".show table {table_name} details",
}

# Column type mappings for better descriptions
COLUMN_TYPE_DESCRIPTIONS = {
    "string": "Text field",
    "int": "Integer number",
    "long": "Large integer number",
    "real": "Decimal number",
    "bool": "Boolean true/false flag",
    "datetime": "Date and time value",
    "timespan": "Time duration value",
    "guid": "Unique identifier (GUID)",
    "dynamic": "Dynamic JSON-like object",
}

# Common security table patterns and their descriptions with AI-relevant tokens
SECURITY_TABLE_PATTERNS = {
    # Core Windows Security
    "SecurityEvent": "Windows security audit events | analysis_keywords: logon, privilege_use, account_management, process_tracking | mitre_techniques: T1078, T1003, T1134",
    "Event": "Windows event log entries | analysis_keywords: system_events, application_logs, security_warnings | mitre_techniques: T1005, T1074, T1083",
    
    # Azure AD & Identity
    "SigninLogs": "Azure AD sign-in activity | analysis_keywords: authentication, mfa, conditional_access, risk_detection | mitre_techniques: T1078.004, T1110, T1556",
    "AuditLogs": "Azure AD audit activity | analysis_keywords: role_changes, app_registrations, policy_modifications | mitre_techniques: T1098, T1484, T1136",
    "Syslog": "Linux/Unix system logs | analysis_keywords: authentication, system_events, security_violations | mitre_techniques: T1078.003, T1059.004",
    # Network & Infrastructure
    "CommonSecurityLog": "CEF security logs | analysis_keywords: firewall, ids_ips, network_security_appliances | mitre_techniques: T1095, T1071, T1090",
    
    # Security Operations
    "SecurityAlert": "Security alerts and detections | analysis_keywords: incidents, threats, suspicious_activities | mitre_techniques: Multi-technique",
    "SecurityIncident": "Security incident records | analysis_keywords: case_management, investigation, response_tracking | mitre_techniques: Multi-technique",
    "ThreatIntelligenceIndicator": "Threat intelligence indicators | analysis_keywords: iocs, ttps, threat_attribution | mitre_techniques: Multi-technique",
    "IdentityInfo": "Identity and user information | analysis_keywords: user_profiles, group_memberships, role_assignments | mitre_techniques: T1087, T1069",
    
    # Microsoft Defender & Endpoint Security
    "DeviceEvents": "Endpoint device events | analysis_keywords: malware_detection, exploit_attempts, device_control | mitre_techniques: T1055, T1059, T1203",
    "DeviceProcessEvents": "Process execution events | analysis_keywords: process_creation, command_execution, parent_child_relationships | mitre_techniques: T1059, T1055, T1106",
    "DeviceNetworkEvents": "Network activity from devices | analysis_keywords: connections, dns_queries, network_protocols, c2_communication | mitre_techniques: T1071, T1090, T1095",
    "DeviceFileEvents": "File system activity | analysis_keywords: file_creation, modifications, deletions, ransomware_indicators | mitre_techniques: T1005, T1486, T1083",
    "DeviceRegistryEvents": "Registry modification events | analysis_keywords: persistence, privilege_escalation, defense_evasion | mitre_techniques: T1112, T1547, T1574",
    
    # Email & Communication Security
    "EmailEvents": "Email security events | analysis_keywords: phishing, malware_attachments, business_email_compromise | mitre_techniques: T1566, T1204, T1114",
    "UrlClickEvents": "URL click events | analysis_keywords: user_interaction, safe_links, threat_protection | mitre_techniques: T1204.001, T1566.002",
    "CloudAppEvents": "Cloud application activity | analysis_keywords: saas_security, oauth_abuse, data_exfiltration | mitre_techniques: T1530, T1567, T1087.004",
}

# Common column name patterns and their descriptions with AI-relevant tokens
COMMON_COLUMN_PATTERNS = {
    # Time-related columns
    "TimeGenerated": "Event generation timestamp in UTC | analysis_keywords: temporal_analysis, timeline_reconstruction, correlation_window | data_type: datetime",
    "TimeCreated": "Record creation timestamp | analysis_keywords: audit_trail, data_lineage, chronological_order | data_type: datetime",
    "Timestamp": "Universal event timestamp | analysis_keywords: time_series, sequence_analysis, dwell_time | data_type: datetime",
    "EventTime": "Precise event occurrence time | analysis_keywords: incident_timeline, attack_progression, forensics | data_type: datetime",
    "CreatedTime": "Initial creation timestamp | analysis_keywords: artifact_age, baseline_establishment, delta_analysis | data_type: datetime",
    "ModifiedTime": "Last modification timestamp | analysis_keywords: change_tracking, tampering_detection, version_control | data_type: datetime",
    
    # Identity columns
    "EventID": "Event type identifier | analysis_keywords: event_classification, pattern_matching, signature_detection | data_type: categorical",
    "ActivityID": "Activity session identifier | analysis_keywords: session_tracking, user_journey, behavior_chaining | data_type: guid",
    "SessionID": "User/system session ID | analysis_keywords: session_hijacking, lateral_movement, persistence | data_type: guid",
    "ProcessID": "OS process identifier | analysis_keywords: process_tree, parent_child, injection_detection | data_type: numeric",
    "ThreadID": "OS thread identifier | analysis_keywords: thread_injection, execution_flow, concurrency | data_type: numeric",
    
    # User and account columns
    "UserName": "User account name | analysis_keywords: identity_resolution, privilege_escalation, account_abuse | data_type: string",
    "AccountName": "Account name in event | analysis_keywords: account_enumeration, credential_theft, impersonation | data_type: string",
    "User": "User identifier/name | analysis_keywords: user_attribution, insider_threat, access_patterns | data_type: string",
    "Subject": "Security principal info | analysis_keywords: delegation, impersonation, token_manipulation | data_type: object",
    "TargetUserName": "Target user for operation | analysis_keywords: privilege_escalation, account_manipulation, delegation | data_type: string",
    
    # System and computer columns
    "ComputerName": "Computer/host system name | analysis_keywords: asset_identification, lateral_movement, inventory | data_type: string",
    "Computer": "Computer/device name | analysis_keywords: endpoint_tracking, device_inventory, location_mapping | data_type: string",
    "SourceSystem": "Log generation system | analysis_keywords: data_source, log_aggregation, telemetry_origin | data_type: string",
    "Source": "Source system/application | analysis_keywords: application_mapping, service_discovery, attack_surface | data_type: string",
    "DeviceName": "Device identifier name | analysis_keywords: mobile_security, iot_tracking, device_management | data_type: string",
    
    # Network columns
    "IPAddress": "Associated IP address | analysis_keywords: geolocation, threat_intel, network_mapping | data_type: ipv4/ipv6",
    "SourceIP": "Connection source IP | analysis_keywords: attack_origin, c2_detection, reputation_check | data_type: ipv4/ipv6",
    "DestinationIP": "Connection destination IP | analysis_keywords: data_exfiltration, lateral_movement, service_discovery | data_type: ipv4/ipv6",
    "ClientIP": "Client IP address | analysis_keywords: user_location, vpn_detection, anomaly_analysis | data_type: ipv4/ipv6",
    "ServerIP": "Server IP address | analysis_keywords: infrastructure_mapping, service_identification, attack_target | data_type: ipv4/ipv6",
    
    # Process columns
    "ProcessName": "Process/executable name | analysis_keywords: malware_detection, process_analysis, whitelist_validation | data_type: string",
    "Process": "Process information | analysis_keywords: execution_chain, process_tree, behavior_analysis | data_type: object",
    "CommandLine": "Process command line | analysis_keywords: attack_technique, script_analysis, parameter_extraction | data_type: string",
    "ExecutablePath": "Executable file path | analysis_keywords: file_analysis, persistence_detection, path_traversal | data_type: string",
    
    # Event data columns
    "EventData": "Structured event data | analysis_keywords: field_extraction, enrichment, correlation_keys | data_type: dynamic",
    "Message": "Human-readable message | analysis_keywords: text_analysis, keyword_extraction, sentiment | data_type: string",
    "Description": "Event description | analysis_keywords: context_understanding, categorization, nlp_processing | data_type: string",
    "Details": "Additional event details | analysis_keywords: deep_analysis, investigation_support, forensics | data_type: object",
    
    # Status and classification columns
    "Severity": "Event severity level | analysis_keywords: prioritization, alerting, risk_scoring | data_type: categorical",
    "Level": "Log importance level | analysis_keywords: noise_reduction, filtering, escalation | data_type: categorical",
    "Category": "Event category | analysis_keywords: taxonomic_classification, use_case_mapping, analytics | data_type: categorical",
    "Type": "Event type/class | analysis_keywords: signature_matching, rule_correlation, pattern_detection | data_type: categorical",
    
    # Azure-specific columns
    "ResourceId": "Azure resource ID | analysis_keywords: cloud_asset_tracking, rbac_analysis, resource_enumeration | data_type: string",
    "SubscriptionId": "Azure subscription ID | analysis_keywords: tenant_mapping, billing_analysis, scope_definition | data_type: guid",
    "ResourceGroup": "Azure resource group | analysis_keywords: organization_structure, deployment_tracking, access_control | data_type: string",
    "TenantId": "Azure tenant ID | analysis_keywords: multi_tenant_analysis, organization_mapping, cross_tenant_attacks | data_type: guid",
}

# File and directory permissions
FILE_PERMISSIONS = {
    "schema_file": 0o600,  # Read/write for owner only
    "memory_dir": 0o700,   # Read/write/execute for owner only
}

# Limits and constraints
LIMITS = {
    "max_concurrent_queries": 5,
    "max_result_rows": 10000,
    "max_visualization_rows": 1000,
    "max_column_description_length": 500,
    "max_table_description_length": 1000,
    "max_retry_attempts": 3,
    "retry_delay_seconds": 2,
    "max_connection_pool_size": 10,
}

# Supported MCP tools with enhanced AI-powered capabilities
MCP_TOOLS = {
    "kql_execute": {
        "name": "kql_execute",
        "description": """Execute KQL queries with AI-enhanced intelligence
        
        Advanced KQL query execution engine with intelligent schema context, automatic
        result visualization, and security-focused analytics. Leverages AI-powered
        schema memory to provide intelligent query suggestions and optimization.
        
        Perfect for: SOC investigations, threat hunting, data exploration, security analytics
        Security Features: IoC enrichment, behavioral analytics, pattern recognition
        Output: Structured results with optional Markdown tables and AI insights""",
        "required_params": ["query"],
        "optional_params": ["visualize", "cluster_memory_path", "use_schema_context"],
        "ai_capabilities": [
            "schema_context_injection",
            "security_table_recognition",
            "intelligent_result_formatting"
        ],
        "use_cases": [
            "incident_investigation",
            "threat_hunting",
            "compliance_reporting",
            "security_analytics",
            "data_exploration"
        ]
    },
}

# HTTP status codes for error mapping
HTTP_STATUS_CODES = {
    400: "Bad Request - Invalid query syntax",
    401: "Unauthorized - Authentication failed",
    403: "Forbidden - Access denied to resource",
    404: "Not Found - Cluster, database, or table not found",
    408: "Timeout - Request timed out",
    429: "Too Many Requests - Rate limit exceeded",
    500: "Internal Server Error - Server error occurred",
    503: "Service Unavailable - Service temporarily unavailable",
}

# Azure CLI configuration
AZURE_CLI_CONFIG = {
    "login_experience": "core.login_experience_v2=off",
    "output_format": "output=json",
    "only_show_errors": "AZURE_CORE_ONLY_SHOW_ERRORS=true",
}

# Performance monitoring thresholds
PERFORMANCE_THRESHOLDS = {
    "query_warning_time_seconds": 30,
    "query_error_time_seconds": 300,
    "schema_discovery_warning_time_seconds": 60,
    "schema_discovery_error_time_seconds": 600,
    "memory_usage_warning_mb": 100,
    "memory_usage_error_mb": 500,
}

# Default visualization settings
VISUALIZATION_CONFIG = {
    "max_rows": 1000,
    "max_columns": 20,
    "table_format": "pipe",  # For tabulate library
    "float_format": ".2f",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "truncate_cell_length": 50,
}

# AI Enhancement Tokens and Keywords
AI_RELEVANCE_TOKENS = {
    "security_indicators": ["security", "threat", "alert", "warning", "target", "analysis"],
    "data_types": ["data", "record", "file", "network", "process", "user"],
    "analysis_keywords": [
        "threat_hunting", "incident_investigation", "behavioral_analysis",
        "anomaly_detection", "correlation", "timeline_reconstruction"
    ],
    "query_enhancement": [
        "schema_context", "intelligent_filtering", "auto_correlation",
        "temporal_analysis", "pattern_matching", "risk_scoring"
    ]
}



# Query Enhancement Patterns
QUERY_ENHANCEMENT_PATTERNS = {
    "temporal_correlation": {
        "description": "Time-based event correlation and sequencing",
        "example": "| extend TimeBin = bin(TimeGenerated, 5m) | summarize by TimeBin",
        "use_cases": ["timeline_analysis", "session_analysis", "trend_tracking"]
    },
    "geospatial_analysis": {
        "description": "Location-based analysis",
        "example": "| extend GeoInfo = geo_info_from_ip_address(ClientIP)",
        "use_cases": ["location_tracking", "geo_anomalies", "regional_analysis"]
    },
    "statistical_analysis": {
        "description": "Statistical baseline establishment for anomaly detection",
        "example": "| summarize avg(Count), stdev(Count) by User | extend Threshold = avg_Count + 2*stdev_Count",
        "use_cases": ["user_behavior", "system_performance", "access_patterns"]
    }
}

# Testing and development constants
TEST_CONFIG = {
    "mock_cluster_uri": "https://test-cluster.kusto.windows.net",
    "mock_database": "TestDatabase",
    "mock_table": "TestTable",
    "sample_query": "TestTable | take 10",
    "test_memory_dir": "test_memory",
    "ai_test_scenarios": [
        "schema_discovery",
        "query_enhancement",
        "security_analytics"
    ]
}