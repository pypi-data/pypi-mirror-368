"""
Unit tests for the execute_kql module.
"""

import unittest
from unittest.mock import patch, MagicMock
from azure.kusto.data.exceptions import KustoServiceError

from mcp_kql_server.execute_kql import (
    validate_query,
    execute_kql_query
)
from mcp_kql_server.constants import TEST_CONFIG, ERROR_MESSAGES


class TestExecuteKQL(unittest.TestCase):
    """Test cases for KQL execution functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_query = f"cluster('{TEST_CONFIG['mock_cluster_uri']}').database('{TEST_CONFIG['mock_database']}').{TEST_CONFIG['mock_table']} | take 10"
        self.test_cluster_uri = TEST_CONFIG["mock_cluster_uri"]
        self.test_database = TEST_CONFIG["mock_database"]

    def test_validate_query_success(self):
        """Test successful query validation."""
        cluster_uri, database = validate_query(self.valid_query)
        self.assertEqual(cluster_uri, self.test_cluster_uri)
        self.assertEqual(database, self.test_database)

    def test_validate_query_missing_cluster(self):
        """Test query validation with missing cluster."""
        invalid_query = f"database('{self.test_database}').TestTable | take 10"
        with self.assertRaises(ValueError) as context:
            validate_query(invalid_query)
        self.assertIn("cluster", str(context.exception).lower())

    def test_validate_query_missing_database(self):
        """Test query validation with missing database."""
        invalid_query = f"cluster('{self.test_cluster_uri}').TestTable | take 10"
        with self.assertRaises(ValueError) as context:
            validate_query(invalid_query)
        self.assertIn("database", str(context.exception).lower())

    def test_validate_query_empty(self):
        """Test query validation with empty query."""
        with self.assertRaises(ValueError) as context:
            validate_query("")
        self.assertIn("empty", str(context.exception).lower())

    def test_validate_query_suspicious_content(self):
        """Test query validation with suspicious content."""
        suspicious_query = f"cluster('{self.test_cluster_uri}').database('{self.test_database}').TestTable; DROP TABLE TestTable"
        with self.assertRaises(ValueError) as context:
            validate_query(suspicious_query)
        self.assertIn("unsafe", str(context.exception).lower())

    @patch('mcp_kql_server.execute_kql.KustoClient')
    @patch('mcp_kql_server.execute_kql.KustoConnectionStringBuilder')
    @patch('mcp_kql_server.execute_kql.SchemaMemoryManager')
    def test_execute_kql_query_success(self, mock_schema_manager, mock_connection_builder, mock_kusto_client):
        """Test successful KQL query execution."""
        # Mock Kusto client
        mock_client_instance = MagicMock()
        mock_kusto_client.return_value = mock_client_instance
        
        # Mock query response
        mock_response = MagicMock()
        mock_response.primary_results = [MagicMock()]
        
        # Mock table columns and data
        mock_column = MagicMock()
        mock_column.column_name = "TestColumn"
        mock_response.primary_results[0].columns = [mock_column]
        mock_response.primary_results[0].__iter__ = lambda x: iter([["test_value"]])
        
        mock_client_instance.execute.return_value = mock_response
        
        # Mock schema manager
        mock_schema_instance = MagicMock()
        mock_schema_manager.return_value = mock_schema_instance
        mock_schema_instance.get_schema_context_for_query.return_value = {}
        
        # Execute query
        result = execute_kql_query(self.valid_query, visualize=False, use_schema_context=False)
        
        # Verify results
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("TestColumn", result[0])
        self.assertEqual(result[0]["TestColumn"], "test_value")

    @patch('mcp_kql_server.execute_kql.KustoClient')
    @patch('mcp_kql_server.execute_kql.KustoConnectionStringBuilder')
    @patch('mcp_kql_server.execute_kql.SchemaMemoryManager')
    def test_execute_kql_query_with_visualization(self, mock_schema_manager, mock_connection_builder, mock_kusto_client):
        """Test KQL query execution with visualization."""
        # Mock Kusto client
        mock_client_instance = MagicMock()
        mock_kusto_client.return_value = mock_client_instance
        
        # Mock query response
        mock_response = MagicMock()
        mock_response.primary_results = [MagicMock()]
        
        # Mock table columns and data
        mock_column = MagicMock()
        mock_column.column_name = "TestColumn"
        mock_response.primary_results[0].columns = [mock_column]
        mock_response.primary_results[0].__iter__ = lambda x: iter([["test_value"]])
        
        mock_client_instance.execute.return_value = mock_response
        
        # Mock schema manager
        mock_schema_instance = MagicMock()
        mock_schema_manager.return_value = mock_schema_instance
        mock_schema_instance.get_schema_context_for_query.return_value = {}
        
        # Execute query with visualization
        result = execute_kql_query(self.valid_query, visualize=True, use_schema_context=False)
        
        # Verify results include visualization
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 1)  # Should have data + visualization
        
        # Check for visualization in results
        has_visualization = any("visualization" in row for row in result)
        self.assertTrue(has_visualization)

    @patch('mcp_kql_server.execute_kql.KustoClient')
    @patch('mcp_kql_server.execute_kql.KustoConnectionStringBuilder')
    def test_execute_kql_query_kusto_error(self, mock_connection_builder, mock_kusto_client):
        """Test KQL query execution with Kusto service error."""
        # Mock Kusto client to raise error
        mock_client_instance = MagicMock()
        mock_kusto_client.return_value = mock_client_instance
        mock_client_instance.execute.side_effect = KustoServiceError("Test Kusto error")
        
        # Execute query and expect exception
        with self.assertRaises(KustoServiceError):
            execute_kql_query(self.valid_query, use_schema_context=False)

    @patch('mcp_kql_server.execute_kql.KustoClient')
    @patch('mcp_kql_server.execute_kql.KustoConnectionStringBuilder')
    @patch('mcp_kql_server.execute_kql.SchemaMemoryManager')
    def test_execute_kql_query_with_schema_context(self, mock_schema_manager, mock_connection_builder, mock_kusto_client):
        """Test KQL query execution with schema context."""
        # Mock Kusto client
        mock_client_instance = MagicMock()
        mock_kusto_client.return_value = mock_client_instance
        
        # Mock query response
        mock_response = MagicMock()
        mock_response.primary_results = [MagicMock()]
        
        # Mock table columns and data
        mock_column = MagicMock()
        mock_column.column_name = "TestColumn"
        mock_response.primary_results[0].columns = [mock_column]
        mock_response.primary_results[0].__iter__ = lambda x: iter([["test_value"]])
        
        mock_client_instance.execute.return_value = mock_response
        
        # Mock schema manager with context
        mock_schema_instance = MagicMock()
        mock_schema_manager.return_value = mock_schema_instance
        mock_schema_instance.get_schema_context_for_query.return_value = {
            "relevant_tables": {"TestDB.TestTable": {"description": "Test table"}},
            "schema_timestamp": "2025-01-26T12:00:00Z"
        }
        
        # Execute query with schema context
        result = execute_kql_query(self.valid_query, visualize=True, use_schema_context=True)
        
        # Verify schema context was loaded
        mock_schema_instance.get_schema_context_for_query.assert_called_once()
        
        # Verify results
        self.assertIsInstance(result, list)

    @patch('mcp_kql_server.execute_kql.KustoClient')
    @patch('mcp_kql_server.execute_kql.KustoConnectionStringBuilder')
    @patch('mcp_kql_server.execute_kql.SchemaMemoryManager')
    def test_execute_kql_query_empty_results(self, mock_schema_manager, mock_connection_builder, mock_kusto_client):
        """Test KQL query execution with empty results."""
        # Mock Kusto client
        mock_client_instance = MagicMock()
        mock_kusto_client.return_value = mock_client_instance
        
        # Mock empty response
        mock_response = MagicMock()
        mock_response.primary_results = []
        mock_client_instance.execute.return_value = mock_response
        
        # Mock schema manager
        mock_schema_instance = MagicMock()
        mock_schema_manager.return_value = mock_schema_instance
        mock_schema_instance.get_schema_context_for_query.return_value = {}
        
        # Execute query
        result = execute_kql_query(self.valid_query, use_schema_context=False)
        
        # Verify empty results
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_execute_kql_query_invalid_query(self):
        """Test KQL query execution with invalid query."""
        invalid_query = "invalid query without cluster or database"
        
        with self.assertRaises(ValueError):
            execute_kql_query(invalid_query, use_schema_context=False)


if __name__ == '__main__':
    unittest.main()