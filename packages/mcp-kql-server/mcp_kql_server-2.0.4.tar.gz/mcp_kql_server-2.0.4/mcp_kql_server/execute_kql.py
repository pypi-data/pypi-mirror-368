"""
Enhanced KQL Query Execution Module (AI-Optimized Per-Table Memory)

This module provides robust KQL query execution with Azure authentication,
AI-optimized per-table schema context integration, and intelligent error handling.

Author: Arjun Trivedi
Email: arjuntrivedi42@yahoo.com
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.exceptions import KustoServiceError
from tabulate import tabulate

from .schema_memory import (
    extract_tables_from_query,
    get_context_for_tables,
    update_memory_after_query,
    _normalize_cluster_uri,
    ensure_table_memory
)
from .unified_memory import (
    get_unified_memory,
    load_query_relevant_context
)
from .utils import (
    extract_cluster_and_database_from_query,
    clean_query_for_execution,
    validate_kql_query_syntax,
    format_error_message,
    is_debug_mode
)
from .constants import (
    DEFAULT_CONNECTION_TIMEOUT,
    DEFAULT_QUERY_TIMEOUT,
    LIMITS,
    ERROR_MESSAGES,
    SUCCESS_MESSAGES,
    VISUALIZATION_CONFIG
)

logger = logging.getLogger(__name__)

def validate_query(query: str) -> Tuple[str, str]:
    """
    Validate and extract cluster and database from KQL query.
    """
    logger.info("Validating KQL query...")
    is_valid, error_msg = validate_kql_query_syntax(query)
    if not is_valid:
        raise ValueError(error_msg)
    
    cluster_uri, database = extract_cluster_and_database_from_query(query)
    if not cluster_uri:
        raise ValueError(ERROR_MESSAGES["invalid_cluster"])
    if not database:
        raise ValueError(ERROR_MESSAGES["invalid_database"])
    
    logger.info(f"Validated: cluster_uri={cluster_uri}, database={database}")
    return cluster_uri, database

def pre_query_table_discovery(cluster_uri: str, database: str, tables: List[str], memory_path: Optional[str] = None):
    """
    Discover and cache table schemas BEFORE query execution using unified memory.
    This prevents the context size issue by ensuring we have compact context ready.
    """
    logger.info(f"Pre-discovering schemas for tables: {tables}")
    
    memory = get_unified_memory(memory_path)
    
    for table in tables:
        try:
            memory.ensure_table_in_memory(cluster_uri, database, table)
        except Exception as e:
            logger.warning(f"Failed to pre-discover {database}.{table}: {e}")

def execute_kql_query(
    query: str,
    visualize: bool = False,
    cluster_memory_path: Optional[str] = None,
    use_schema_context: bool = True
) -> List[Dict[str, Any]]:
    """
    Execute a KQL query with AI-optimized per-table schema context and visualization.
    
    Key improvements:
    1. Pre-query table discovery to ensure compact context is available
    2. Ultra-compact AI tokens to prevent context overflow
    3. Smart table extraction and memory management
    4. Optimized error handling
    """
    if is_debug_mode():
        logger.debug(f"Executing KQL query with params: visualize={visualize}, use_schema_context={use_schema_context}")
    
    logger.info("Preparing to execute KQL query")
    
    try:
        # Step 1: Validate and extract cluster/database info
        cluster_uri, database = validate_query(query)
        
        # Step 2: Enhanced table extraction with cross-cluster support
        tables = extract_tables_from_query(query)
        logger.info(f"Extracted tables from query: {tables}")
        
        # Step 3: Use unified memory system for context loading with size management
        schema_context = []
        if use_schema_context:
            try:
                # Use unified memory system for intelligent context loading
                memory = get_unified_memory(cluster_memory_path)
                
                # Load query-relevant context with automatic size management
                schema_context = memory.load_query_relevant_context(query, max_context_size=4000)
                
                if schema_context:
                    total_size = sum(len(token) for token in schema_context)
                    logger.info(f"Loaded {len(schema_context)} context tokens: {total_size} chars")
                else:
                    logger.info("No schema context available for query")
                    
            except Exception as e:
                logger.warning(f"Failed to load schema context: {e}")
                schema_context = []
                
                # Fallback to legacy method for discovered tables
                if tables:
                    try:
                        pre_query_table_discovery(cluster_uri, database, tables, cluster_memory_path)
                        schema_context = get_context_for_tables(cluster_uri, database, tables, cluster_memory_path)
                    except Exception as fallback_e:
                        logger.warning(f"Fallback context loading also failed: {fallback_e}")
        
        # Step 4: Clean the query for execution
        cleaned_query = clean_query_for_execution(query)
        if is_debug_mode():
            logger.debug(f"Cleaned KQL query:\n{cleaned_query}")
        
        # Step 5: Execute query with optimized settings
        normalized_cluster_uri = _normalize_cluster_uri(cluster_uri)
        kcsb = KustoConnectionStringBuilder.with_az_cli_authentication(normalized_cluster_uri)
        client = KustoClient(kcsb)
        
        try:
            # Execute with timeout protection
            response = client.execute(database, cleaned_query)
            
            if not response.primary_results:
                logger.warning("Query returned no results")
                return []
            
            # Process results with memory limits
            table = response.primary_results[0]
            columns = [col.column_name for col in table.columns]
            results = []
            max_rows = LIMITS["max_result_rows"]
            row_count = 0
            
            for row in table:
                if row_count >= max_rows:
                    logger.warning(f"Result set truncated to {max_rows} rows")
                    break
                results.append(dict(zip(columns, row)))
                row_count += 1
            
            logger.info(f"Query executed successfully. Returned {len(results)} rows.")
            
            # Step 6: Add visualization if requested
            if visualize and results:
                try:
                    viz_rows = min(len(results), VISUALIZATION_CONFIG["max_rows"])
                    viz_data = results[:viz_rows]
                    
                    # Truncate long cell content for better display
                    truncated_data = []
                    for row in viz_data:
                        truncated_row = {}
                        for key, value in row.items():
                            if isinstance(value, str) and len(value) > VISUALIZATION_CONFIG["truncate_cell_length"]:
                                truncated_row[key] = value[:VISUALIZATION_CONFIG["truncate_cell_length"]] + "..."
                            else:
                                truncated_row[key] = value
                        truncated_data.append(truncated_row)
                    
                    markdown_table = tabulate(
                        [list(row.values()) for row in truncated_data],
                        headers=columns,
                        tablefmt=VISUALIZATION_CONFIG["table_format"],
                        floatfmt=VISUALIZATION_CONFIG["float_format"]
                    )
                    
                    # Create visualization result with compact schema context
                    viz_result: Dict[str, Any] = {"visualization": markdown_table}
                    
                    if schema_context:
                        viz_result["schema_context"] = {
                            "tables_analyzed": tables,
                            "context_tokens": schema_context,  # Ultra-compact AI tokens
                            "context_summary": f"AI schema context for {len(tables)} tables ({len(''.join(schema_context))} chars)"
                        }
                    
                    results.append(viz_result)
                    
                except Exception as viz_error:
                    logger.warning(f"Failed to generate visualization: {viz_error}")
                    # Continue without visualization
            
            # Step 7: Update memory after successful query (async in background)
            try:
                update_memory_after_query(cluster_uri, database, tables, cluster_memory_path)
            except Exception as e:
                logger.warning(f"Failed to update memory after query: {e}")
            
            return results
            
        finally:
            client.close()
            
    except KustoServiceError as ke:
        error_msg = format_error_message(ke, "Kusto service error")
        logger.error(error_msg)
        raise KustoServiceError(error_msg) from ke
    except ValueError as ve:
        error_msg = format_error_message(ve, "Query validation error")
        logger.error(error_msg)
        raise ValueError(error_msg) from ve
    except Exception as e:
        error_msg = format_error_message(e, "Query execution error")
        logger.error(error_msg)
        raise Exception(error_msg) from e

# Example usage and testing
if __name__ == "__main__":
    # Test with sample query
    sample_query = "cluster('help.kusto.windows.net').database('SecurityLogs').AuthenticationEvents | take 20"
    try:
        results = execute_kql_query(sample_query, visualize=True, use_schema_context=True)
        print("Query Results:")
        for i, row in enumerate(results):
            if "visualization" in row:
                print(f"Visualization:\n{row['visualization']}")
                if "schema_context" in row:
                    print(f"Schema Context: {row['schema_context']['context_summary']}")
            else:
                print(f"Row {i+1}: {row}")
    except Exception as e:
        print(f"Error: {str(e)}")
