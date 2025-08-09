"""
Unit tests for the MCP server module.
"""

import unittest

from mcp_kql_server.mcp_server import (
    KQLInput,
    KQLOutput,
    KQLResult
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
            schema_context=["TestTable"]
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
        


if __name__ == '__main__':
    unittest.main()