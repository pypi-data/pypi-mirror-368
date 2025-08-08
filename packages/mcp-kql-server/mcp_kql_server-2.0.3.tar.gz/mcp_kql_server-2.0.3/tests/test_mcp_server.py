"""
Unit tests for the MCP server module.
"""

import unittest

from mcp_kql_server.mcp_server import (
    KQLInput,
    KQLOutput,
    KQLResult,
    SchemaMemoryInput,
    SchemaMemoryOutput,
    SchemaMemoryResult
)
from mcp_kql_server.constants import TEST_CONFIG


class TestMCPServerModels(unittest.TestCase):
    """Test cases for MCP server Pydantic models."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_query = f"cluster('{TEST_CONFIG['mock_cluster_uri']}').database('{TEST_CONFIG['mock_database']}').{TEST_CONFIG['mock_table']} | take 10"
        self.test_cluster_uri = TEST_CONFIG["mock_cluster_uri"]

    def test_kql_input_model(self):
        """Test KQL input model validation."""
        # Valid input with defaults
        input_data = KQLInput(query=self.valid_query)
        self.assertEqual(input_data.query, self.valid_query)
        self.assertFalse(input_data.visualize)  # Default value
        self.assertTrue(input_data.use_schema_context)  # Default value
        self.assertIsNone(input_data.cluster_memory_path)  # Default value

        # Valid input with all parameters
        input_data = KQLInput(
            query=self.valid_query,
            visualize=True,
            cluster_memory_path="/custom/path",
            use_schema_context=False
        )
        self.assertEqual(input_data.query, self.valid_query)
        self.assertTrue(input_data.visualize)
        self.assertEqual(input_data.cluster_memory_path, "/custom/path")
        self.assertFalse(input_data.use_schema_context)

    def test_kql_result_model(self):
        """Test KQL result model creation."""
        result = KQLResult(
            columns=["Column1", "Column2"],
            rows=[["value1", "value2"], ["value3", "value4"]],
            row_count=2,
            visualization="| Column1 | Column2 |",
            schema_context={"tables": ["TestTable"]}
        )
        
        self.assertEqual(len(result.columns), 2)
        self.assertEqual(len(result.rows), 2)
        self.assertEqual(result.row_count, 2)
        self.assertIsNotNone(result.visualization)
        self.assertIsNotNone(result.schema_context)

    def test_kql_output_model(self):
        """Test KQL output model creation."""
        # Success output
        result = KQLResult(
            columns=["TestColumn"],
            rows=[["test_value"]],
            row_count=1
        )
        output = KQLOutput(status="success", result=result)
        self.assertEqual(output.status, "success")
        self.assertIsNotNone(output.result)
        self.assertIsNone(output.error)

        # Error output
        output = KQLOutput(status="error", error="Test error")
        self.assertEqual(output.status, "error")
        self.assertEqual(output.error, "Test error")
        self.assertIsNone(output.result)

    def test_schema_memory_input_model(self):
        """Test schema memory input model validation."""
        # With defaults
        input_data = SchemaMemoryInput(cluster_uri=self.test_cluster_uri)
        self.assertEqual(input_data.cluster_uri, self.test_cluster_uri)
        self.assertFalse(input_data.force_refresh)  # Default value
        self.assertIsNone(input_data.memory_path)  # Default value

        # With all parameters
        input_data = SchemaMemoryInput(
            cluster_uri=self.test_cluster_uri,
            memory_path="/custom/memory/path",
            force_refresh=True
        )
        self.assertEqual(input_data.cluster_uri, self.test_cluster_uri)
        self.assertEqual(input_data.memory_path, "/custom/memory/path")
        self.assertTrue(input_data.force_refresh)

    def test_schema_memory_result_model(self):
        """Test schema memory result model creation."""
        discovery_summary = {
            "action": "discovered_new",
            "databases": ["TestDB"],
            "total_tables": 5,
            "message": "Successfully discovered schema"
        }
        
        result = SchemaMemoryResult(
            cluster_uri=self.test_cluster_uri,
            database_count=1,
            total_tables=5,
            memory_file_path="/path/to/schema.json",
            timestamp="2025-01-26T12:00:00Z",
            discovery_summary=discovery_summary
        )
        
        self.assertEqual(result.cluster_uri, self.test_cluster_uri)
        self.assertEqual(result.database_count, 1)
        self.assertEqual(result.total_tables, 5)
        self.assertEqual(result.memory_file_path, "/path/to/schema.json")
        self.assertEqual(result.timestamp, "2025-01-26T12:00:00Z")
        self.assertIsInstance(result.discovery_summary, dict)
        self.assertEqual(result.discovery_summary["action"], "discovered_new")

    def test_schema_memory_output_model(self):
        """Test schema memory output model creation."""
        # Success output
        result = SchemaMemoryResult(
            cluster_uri=self.test_cluster_uri,
            database_count=1,
            total_tables=5,
            memory_file_path="/path/to/schema.json",
            timestamp="2025-01-26T12:00:00Z",
            discovery_summary={"action": "discovered_new"}
        )
        
        output = SchemaMemoryOutput(status="success", result=result)
        self.assertEqual(output.status, "success")
        self.assertIsNotNone(output.result)
        self.assertIsNone(output.error)

        # Error output
        output = SchemaMemoryOutput(status="error", error="Discovery failed")
        self.assertEqual(output.status, "error")
        self.assertEqual(output.error, "Discovery failed")
        self.assertIsNone(output.result)

    def test_model_serialization(self):
        """Test model serialization to dict."""
        input_data = KQLInput(query=self.valid_query, visualize=True)
        data_dict = input_data.model_dump()
        
        self.assertIsInstance(data_dict, dict)
        self.assertEqual(data_dict["query"], self.valid_query)
        self.assertTrue(data_dict["visualize"])
        self.assertTrue(data_dict["use_schema_context"])

    def test_model_edge_cases(self):
        """Test model edge cases."""
        # Test with empty string query (still valid for Pydantic but will fail validation later)
        input_data = KQLInput(query="")
        self.assertEqual(input_data.query, "")
        
        # Test with whitespace-only cluster URI
        input_data = SchemaMemoryInput(cluster_uri="   ")
        self.assertEqual(input_data.cluster_uri, "   ")


if __name__ == '__main__':
    unittest.main()