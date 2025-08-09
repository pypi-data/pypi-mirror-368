"""
Unit tests for the unified schema memory module.
"""

import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from mcp_kql_server.memory import (
    UnifiedSchemaMemory,
    get_unified_memory,
    SPECIAL_TOKENS
)
from mcp_kql_server.constants import TEST_CONFIG

class TestUnifiedMemory(unittest.TestCase):
    """Test cases for unified memory functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.memory = UnifiedSchemaMemory(self.temp_dir)
        
        # Sample test data
        self.test_cluster_uri = TEST_CONFIG["mock_cluster_uri"]
        self.test_database = TEST_CONFIG["mock_database"]
        self.test_table = TEST_CONFIG["mock_table"]

    def test_initialization(self):
        """Test memory initialization and path creation."""
        # Trigger file creation by loading memory
        self.memory.load_memory()
        self.assertTrue(self.memory.memory_path.is_file())

    def test_save_and_load_memory(self):
        """Test saving and loading of the unified memory file."""
        # Create some data
        self.memory._memory_cache = {
            "version": "2.0",
            "clusters": {
                self.test_cluster_uri: {
                    "databases": {
                        self.test_database: {
                            "tables": {
                                self.test_table: {"ai_token": "test_token"}
                            }
                        }
                    }
                }
            }
        }
        
        # Save and reload
        self.memory.save_memory()
        self.memory._memory_cache = None  # Clear cache
        loaded_memory = self.memory.load_memory()
        
        self.assertIn(self.test_cluster_uri, loaded_memory["clusters"])
        self.assertIn(self.test_database, loaded_memory["clusters"][self.test_cluster_uri]["databases"])
        self.assertIn(self.test_table, loaded_memory["clusters"][self.test_cluster_uri]["databases"][self.test_database]["tables"])

    def test_table_exists_in_memory(self):
        """Test checking for table existence."""
        self.assertFalse(self.memory.table_exists_in_memory(self.test_cluster_uri, self.test_database, self.test_table))
        
        # Add table and re-check
        self.memory._memory_cache = {
            "version": "2.0",
            "clusters": {
                self.test_cluster_uri: {
                    "databases": {
                        self.test_database: {
                            "tables": {
                                self.test_table: {}
                            }
                        }
                    }
                }
            }
        }
        self.assertTrue(self.memory.table_exists_in_memory(self.test_cluster_uri, self.test_database, self.test_table))

    @patch('mcp_kql_server.memory.KustoClient')
    def test_discover_and_save_table_schema(self, mock_kusto_client):
        """Test schema discovery and saving."""
        mock_client_instance = MagicMock()
        mock_kusto_client.return_value = mock_client_instance
        
        mock_schema_response = MagicMock()
        mock_schema_response.primary_results = [
            MagicMock(rows=[["schema", "TestColumn:string, AnotherColumn:int"]])
        ]
        mock_client_instance.execute_mgmt.return_value = mock_schema_response
        
        with patch('mcp_kql_server.memory.KustoConnectionStringBuilder'):
            result = self.memory.discover_and_save_table_schema(self.test_cluster_uri, self.test_database, self.test_table)
            self.assertTrue(result)
            
            # Verify data was saved
            self.assertTrue(self.memory.table_exists_in_memory(self.test_cluster_uri, self.test_database, self.test_table))
            token = self.memory.get_table_ai_token(self.test_cluster_uri, self.test_database, self.test_table)
            self.assertIsNotNone(token)
            self.assertIn(SPECIAL_TOKENS["TABLE"] + self.test_table, token)
            self.assertIn(SPECIAL_TOKENS["COLUMN"] + "TestColumn", token)
            self.assertIn(SPECIAL_TOKENS["COLUMN"] + "AnotherColumn", token)

    def test_load_query_relevant_context(self):
        """Test loading context relevant to a query."""
        # Mock the discovery process
        with patch.object(self.memory, 'discover_and_save_table_schema', return_value=True):
            with patch.object(self.memory, 'get_table_ai_token', return_value="test_token"):
                query = f"cluster('{self.test_cluster_uri}').database('{self.test_database}').{self.test_table} | take 10"
                context = self.memory.load_query_relevant_context(query)
                self.assertEqual(context, ["test_token"])

    def test_get_memory_stats(self):
        """Test getting memory statistics."""
        stats = self.memory.get_memory_stats()
        self.assertEqual(stats["total_clusters"], 0)
        
        # Add data and re-check
        self.memory._memory_cache = {
            "version": "2.0",
            "clusters": {
                self.test_cluster_uri: {
                    "databases": {
                        self.test_database: {
                            "tables": {
                                self.test_table: {}
                            }
                        }
                    }
                }
            }
        }
        stats = self.memory.get_memory_stats()
        self.assertEqual(stats["total_clusters"], 1)
        self.assertEqual(stats["total_databases"], 1)
        self.assertEqual(stats["total_tables"], 1)

if __name__ == '__main__':
    unittest.main()