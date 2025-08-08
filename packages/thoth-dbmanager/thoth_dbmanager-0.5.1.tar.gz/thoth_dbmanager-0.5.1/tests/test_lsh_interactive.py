# Copyright (c) 2025 Marco Pancotti
# This file is part of Thoth and is released under the MIT License.
# See the LICENSE.md file in the project root for full license information.

"""
Interactive LSH search test utility.

This module provides utilities for testing LSH functionality interactively
and can be used in Jupyter notebooks or Python REPL.
"""

import pytest
from pathlib import Path
from typing import Dict, List, Optional
import logging

from thoth_dbmanager import ThothDbManager


class LshTestUtility:
    """Utility class for testing LSH functionality."""
    
    def __init__(self, db_root_path: str = "dev_databases"):
        """
        Initialize the LSH test utility.
        
        Args:
            db_root_path: Root path for databases
        """
        self.db_root_path = db_root_path
        self.db_manager = None
        
    def connect_database(self, database_name: str, db_type: str = "sqlite") -> bool:
        """
        Connect to a database.
        
        Args:
            database_name: Name of the database
            db_type: Type of database (default: sqlite)
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.db_manager = ThothDbManager.get_instance(
                db_type=db_type,
                db_root_path=self.db_root_path,
                db_id=database_name
            )
            return True
        except Exception as e:
            print(f"Failed to connect to database {database_name}: {e}")
            return False
    
    def get_lsh_status(self) -> Dict[str, any]:
        """
        Get LSH status and file paths information.
        
        Returns:
            Dictionary with LSH status and file paths
        """
        if not self.db_manager:
            return {"error": "No database connected"}
        
        status = {}
        
        if self.db_manager.lsh_manager:
            lsh_manager = self.db_manager.lsh_manager
            
            # Basic info
            status['db_id'] = lsh_manager.db_id
            status['storage_path'] = str(lsh_manager.storage_path)
            status['preprocessed_path'] = str(lsh_manager.preprocessed_path)
            
            # File paths
            db_id = lsh_manager.db_id
            lsh_file = lsh_manager.lsh_base_path.with_suffix('.pkl')
            minhashes_file = lsh_manager.preprocessed_path / f"{db_id}_minhashes.pkl"
            unique_values_file = lsh_manager.preprocessed_path / f"{db_id}_unique_values.pkl"
            
            status['files'] = {
                'lsh_file': {
                    'path': str(lsh_file),
                    'exists': lsh_file.exists()
                },
                'minhashes_file': {
                    'path': str(minhashes_file),
                    'exists': minhashes_file.exists()
                },
                'unique_values_file': {
                    'path': str(unique_values_file),
                    'exists': unique_values_file.exists()
                }
            }
            
            status['lsh_available'] = lsh_manager.is_available()
            status['lsh_loaded'] = lsh_manager.lsh is not None
            
        else:
            status['error'] = "LSH manager not available"
        
        return status
    
    def search_similar(
        self,
        search_string: str,
        signature_size: int = 30,
        n_gram: int = 3,
        top_n: int = 10
    ) -> Dict[str, any]:
        """
        Search for similar values using LSH.
        
        Args:
            search_string: String to search for
            signature_size: MinHash signature size
            n_gram: N-gram size
            top_n: Maximum results to return
            
        Returns:
            Dictionary with search results and metadata
        """
        if not self.db_manager:
            return {"error": "No database connected"}
        
        result = {
            'search_string': search_string,
            'parameters': {
                'signature_size': signature_size,
                'n_gram': n_gram,
                'top_n': top_n
            }
        }
        
        try:
            # Perform search
            search_results = self.db_manager.query_lsh(
                keyword=search_string,
                signature_size=signature_size,
                n_gram=n_gram,
                top_n=top_n
            )
            
            result['results'] = search_results
            result['success'] = True
            
            # Add summary statistics
            total_results = sum(
                sum(len(values) for values in table.values()) 
                for table in search_results.values()
            )
            result['summary'] = {
                'total_results': total_results,
                'tables_found': len(search_results),
                'columns_found': sum(len(table) for table in search_results.values())
            }
            
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
        
        return result
    
    def print_status(self) -> None:
        """Print LSH status in a readable format."""
        status = self.get_lsh_status()
        
        print("=== LSH Status ===")
        if 'error' in status:
            print(f"❌ Error: {status['error']}")
            return
        
        print(f"📁 Database ID: {status['db_id']}")
        print(f"📁 Storage Path: {status['storage_path']}")
        print(f"📁 Preprocessed Path: {status['preprocessed_path']}")
        print()
        
        print("📄 LSH Files:")
        for file_type, file_info in status['files'].items():
            status_icon = "✅" if file_info['exists'] else "❌"
            print(f"  {status_icon} {file_type}: {file_info['path']}")
        print()
        
        availability_icon = "✅" if status['lsh_available'] else "❌"
        loaded_icon = "✅" if status['lsh_loaded'] else "❌"
        print(f"{availability_icon} LSH Available: {status['lsh_available']}")
        print(f"{loaded_icon} LSH Loaded in Memory: {status['lsh_loaded']}")
    
    def print_search_results(self, results: Dict[str, any]) -> None:
        """
        Print search results in a readable format.
        
        Args:
            results: Results from search_similar method
        """
        print(f"=== LSH Search Results ===")
        print(f"🔍 Search String: '{results['search_string']}'")
        print(f"⚙️ Parameters: {results['parameters']}")
        print()
        
        if not results.get('success', False):
            print(f"❌ Error: {results.get('error', 'Unknown error')}")
            return
        
        summary = results['summary']
        print(f"📊 Summary:")
        print(f"  Total Results: {summary['total_results']}")
        print(f"  Tables Found: {summary['tables_found']}")
        print(f"  Columns Found: {summary['columns_found']}")
        print()
        
        if summary['total_results'] == 0:
            print("No similar values found.")
            return
        
        search_results = results['results']
        
        for table_name, columns in search_results.items():
            print(f"📋 Table: {table_name}")
            for column_name, values in columns.items():
                print(f"  📊 Column: {column_name} ({len(values)} values)")
                for value in values:
                    print(f"    • {value}")
            print()


# Convenience functions for quick testing
def quick_lsh_test(database_name: str, search_string: str, **kwargs) -> None:
    """
    Quick LSH test function for interactive use.
    
    Args:
        database_name: Name of the database
        search_string: String to search for
        **kwargs: Additional parameters for search_similar
    """
    utility = LshTestUtility()
    
    print(f"Connecting to database: {database_name}")
    if not utility.connect_database(database_name):
        return
    
    print("\nLSH Status:")
    utility.print_status()
    
    print(f"\nSearching for: '{search_string}'")
    results = utility.search_similar(search_string, **kwargs)
    utility.print_search_results(results)


# Pytest tests
@pytest.mark.integration
def test_lsh_utility_basic():
    """Test basic LSH utility functionality."""
    utility = LshTestUtility()
    
    # Test with a non-existent database (should fail gracefully)
    assert not utility.connect_database("nonexistent_db")
    
    status = utility.get_lsh_status()
    assert "error" in status


@pytest.mark.integration
@pytest.mark.sqlite
def test_lsh_search_functionality():
    """Test LSH search functionality if SQLite database exists."""
    utility = LshTestUtility()
    
    # This test will only pass if there's a test database available
    # You can modify the database name to match your test setup
    test_db_name = "demo"  # Change this to your test database name
    
    if utility.connect_database(test_db_name):
        status = utility.get_lsh_status()
        assert "db_id" in status
        
        # Try a search (will fail if LSH not preprocessed, but should not crash)
        results = utility.search_similar("test", top_n=5)
        assert "search_string" in results
        assert results["search_string"] == "test"


if __name__ == "__main__":
    # Interactive example
    print("LSH Test Utility - Interactive Example")
    print("======================================")
    
    # Example usage
    database_name = input("Enter database name (or press Enter for 'demo'): ").strip()
    if not database_name:
        database_name = "demo"
    
    search_string = input("Enter search string (or press Enter for 'apple'): ").strip()
    if not search_string:
        search_string = "apple"
    
    quick_lsh_test(database_name, search_string)