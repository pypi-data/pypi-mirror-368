"""
Unit tests for the schema memory module.
"""

import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

from mcp_kql_server.schema_memory import (
    SchemaMemoryManager,
    ColumnInfo,
    TableInfo,
    DatabaseInfo,
    ClusterSchema,
    extract_cluster_uri_from_query
)
from mcp_kql_server.constants import TEST_CONFIG


class TestSchemaMemory(unittest.TestCase):
    """Test cases for schema memory functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.schema_manager = SchemaMemoryManager(self.temp_dir)
        
        # Sample test data
        self.test_cluster_uri = TEST_CONFIG["mock_cluster_uri"]
        self.test_database = TEST_CONFIG["mock_database"]
        self.test_table = TEST_CONFIG["mock_table"]

    def test_cluster_hash(self):
        """Test cluster URI hashing."""
        hash1 = self.schema_manager._cluster_hash(self.test_cluster_uri)
        hash2 = self.schema_manager._cluster_hash(self.test_cluster_uri)
        
        # Same URI should produce same hash
        self.assertEqual(hash1, hash2)
        
        # Different URI should produce different hash
        different_uri = "https://different-cluster.kusto.windows.net"
        hash3 = self.schema_manager._cluster_hash(different_uri)
        self.assertNotEqual(hash1, hash3)

    def test_generate_column_description(self):
        """Test AI-powered column description generation."""
        # Test common security patterns
        desc = self.schema_manager._generate_column_description(
            "TimeGenerated", "datetime", "SecurityEvents"
        )
        self.assertIn("timestamp", desc.lower())
        
        desc = self.schema_manager._generate_column_description(
            "EventID", "int", "SecurityEvents"
        )
        self.assertIn("identifier", desc.lower())
        
        desc = self.schema_manager._generate_column_description(
            "UserName", "string", "SecurityEvents"
        )
        self.assertIn("user", desc.lower())
        
        # Test fallback for unknown columns
        desc = self.schema_manager._generate_column_description(
            "CustomColumn", "string", "CustomTable"
        )
        self.assertIn("customcolumn", desc.lower())

    def test_generate_table_description(self):
        """Test table description generation."""
        # Test security table patterns
        desc = self.schema_manager._generate_table_description(
            "SecurityEvents", ["TimeGenerated", "EventID", "UserName"]
        )
        self.assertIn("security", desc.lower())
        
        # Test generic table
        desc = self.schema_manager._generate_table_description(
            "CustomData", ["Column1", "Column2"]
        )
        self.assertIn("data", desc.lower())

    def test_save_and_load_schema_memory(self):
        """Test schema memory persistence."""
        # Create test schema
        column_info = ColumnInfo(
            name="TestColumn",
            data_type="string",
            description="Test column description"
        )
        
        table_info = TableInfo(
            name=self.test_table,
            description="Test table description",
            columns={"TestColumn": column_info}
        )
        
        database_info = DatabaseInfo(
            name=self.test_database,
            description="Test database description",
            tables={self.test_table: table_info}
        )
        
        schema = ClusterSchema(
            cluster_uri=self.test_cluster_uri,
            timestamp="2025-01-26T12:00:00Z",
            databases={self.test_database: database_info}
        )
        
        # Save schema
        file_path = self.schema_manager.save_schema_memory(schema)
        self.assertTrue(Path(file_path).exists())
        
        # Load schema
        loaded_schema = self.schema_manager.load_schema_memory(self.test_cluster_uri)
        self.assertIsNotNone(loaded_schema)
        if loaded_schema is not None:
            self.assertEqual(loaded_schema.cluster_uri, self.test_cluster_uri)
            self.assertEqual(len(loaded_schema.databases), 1)
            self.assertIn(self.test_database, loaded_schema.databases)

    def test_load_nonexistent_schema(self):
        """Test loading schema that doesn't exist."""
        nonexistent_uri = "https://nonexistent.kusto.windows.net"
        schema = self.schema_manager.load_schema_memory(nonexistent_uri)
        self.assertIsNone(schema)

    @patch('mcp_kql_server.schema_memory.KustoClient')
    def test_discover_cluster_schema_mock(self, mock_kusto_client):
        """Test schema discovery with mocked Kusto client."""
        # Mock client and responses
        mock_client_instance = MagicMock()
        mock_kusto_client.return_value = mock_client_instance
        
        # Mock database response
        mock_db_response = MagicMock()
        mock_db_response.primary_results = [
            [{"DatabaseName": self.test_database}]
        ]
        
        # Mock table response
        mock_table_response = MagicMock()
        mock_table_response.primary_results = [
            [{"TableName": self.test_table}]
        ]
        
        # Mock schema response
        mock_schema_response = MagicMock()
        mock_schema_response.primary_results = [
            MagicMock(rows=[["schema", "TestColumn:string"]])
        ]
        
        # Configure mock to return different responses for different queries
        def mock_execute_mgmt(database, query):
            if ".show databases" in query:
                return mock_db_response
            elif ".show tables" in query:
                return mock_table_response
            elif ".show table" in query and "cslschema" in query:
                return mock_schema_response
            return MagicMock()
        
        mock_client_instance.execute_mgmt.side_effect = mock_execute_mgmt
        
        # Test discovery
        with patch('mcp_kql_server.schema_memory.KustoConnectionStringBuilder'):
            schema = self.schema_manager.discover_cluster_schema(self.test_cluster_uri)
            
            self.assertIsNotNone(schema)
            self.assertEqual(schema.cluster_uri, self.test_cluster_uri)
            self.assertIn(self.test_database, schema.databases)

    def test_get_schema_context_for_query(self):
        """Test schema context extraction for queries."""
        # Create and save test schema first
        column_info = ColumnInfo(
            name="TestColumn",
            data_type="string",
            description="Test column description"
        )
        
        table_info = TableInfo(
            name=self.test_table,
            description="Test table description",
            columns={"TestColumn": column_info}
        )
        
        database_info = DatabaseInfo(
            name=self.test_database,
            description="Test database description",
            tables={self.test_table: table_info}
        )
        
        schema = ClusterSchema(
            cluster_uri=self.test_cluster_uri,
            timestamp="2025-01-26T12:00:00Z",
            databases={self.test_database: database_info}
        )
        
        self.schema_manager.save_schema_memory(schema)
        
        # Test context extraction
        query = f"{self.test_table} | take 10"
        context = self.schema_manager.get_schema_context_for_query(query, self.test_cluster_uri)
        
        self.assertIsInstance(context, dict)
        self.assertEqual(context["cluster_uri"], self.test_cluster_uri)
        
        # Test with no schema available
        different_uri = "https://different.kusto.windows.net"
        context = self.schema_manager.get_schema_context_for_query(query, different_uri)
        self.assertEqual(context, {})

    def test_list_memory_files(self):
        """Test listing of memory files."""
        # Initially no files
        files = self.schema_manager.list_memory_files()
        self.assertEqual(len(files), 0)
        
        # Create and save a schema
        schema = ClusterSchema(
            cluster_uri=self.test_cluster_uri,
            timestamp="2025-01-26T12:00:00Z",
            databases={}
        )
        
        self.schema_manager.save_schema_memory(schema)
        
        # Should now have one file
        files = self.schema_manager.list_memory_files()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]["cluster_uri"], self.test_cluster_uri)

    def test_extract_cluster_uri_from_query(self):
        """Test cluster URI extraction from queries."""
        # Test with simple cluster name
        query = "cluster('mycluster').database('mydb').MyTable | take 10"
        uri = extract_cluster_uri_from_query(query)
        self.assertEqual(uri, "https://mycluster.kusto.windows.net")
        
        # Test with FQDN
        query = "cluster('mycluster.kusto.windows.net').database('mydb').MyTable | take 10"
        uri = extract_cluster_uri_from_query(query)
        self.assertEqual(uri, "https://mycluster.kusto.windows.net")
        
        # Test with full URI
        query = "cluster('https://mycluster.kusto.windows.net').database('mydb').MyTable | take 10"
        uri = extract_cluster_uri_from_query(query)
        self.assertEqual(uri, "https://mycluster.kusto.windows.net")
        
        # Test with no cluster
        query = "MyTable | take 10"
        uri = extract_cluster_uri_from_query(query)
        self.assertIsNone(uri)


if __name__ == '__main__':
    unittest.main()