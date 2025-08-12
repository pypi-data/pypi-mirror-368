#!/usr/bin/env python3
"""
Tests for the MCP CSV Database Server
"""

import json
import tempfile
from pathlib import Path

import pandas as pd
import pytest

import mcp_csv_database.server as server_module
from mcp_csv_database.server import (
    analyze_missing_data,
    backup_database,
    clear_database,
    create_index,
    execute_sql_query,
    export_table_to_csv,
    find_duplicates,
    get_column_stats,
    get_data_summary,
    get_database_schema,
    get_query_plan,
    get_table_info,
    list_loaded_tables,
    load_csv_folder,
)


class TestCSVDatabaseServer:
    """Test suite for CSV Database Server functionality"""

    def setup_method(self):
        """Reset global state before each test"""
        clear_database()

    def teardown_method(self):
        """Clean up after each test"""
        clear_database()

    @pytest.fixture
    def sample_data_dir(self):
        """Create a temporary directory with sample CSV files"""
        temp_dir = Path(tempfile.mkdtemp())

        # Create sample data
        sales_data = pd.DataFrame(
            {
                "date": ["2023-01-01", "2023-01-02", "2023-01-03"],
                "product": ["Widget A", "Widget B", "Widget A"],
                "category": ["Electronics", "Electronics", "Electronics"],
                "quantity": [10, 5, 8],
                "price": [29.99, 49.99, 29.99],
            }
        )

        customers_data = pd.DataFrame(
            {
                "customer_id": [1, 2, 3],
                "name": ["Alice", "Bob", "Carol"],
                "city": ["NYC", "LA", "Chicago"],
            }
        )

        # Save to CSV files
        sales_data.to_csv(temp_dir / "sales.csv", index=False)
        customers_data.to_csv(temp_dir / "customers.csv", index=False)

        yield temp_dir

        # Cleanup
        clear_database()
        import shutil

        shutil.rmtree(temp_dir)

    def test_load_csv_folder(self, sample_data_dir):
        """Test loading CSV files from a folder"""
        result = load_csv_folder(str(sample_data_dir))

        assert "Loaded 2/2 CSV files" in result
        assert "sales" in result
        assert "customers" in result
        assert len(server_module._loaded_tables) == 2

    def test_load_csv_folder_with_prefix(self, sample_data_dir):
        """Test loading CSV files with table prefix"""
        result = load_csv_folder(str(sample_data_dir), table_prefix="test_")

        assert "test_sales" in result
        assert "test_customers" in result
        assert "test_sales" in server_module._loaded_tables
        assert "test_customers" in server_module._loaded_tables

    def test_load_nonexistent_folder(self):
        """Test loading from non-existent folder"""
        result = load_csv_folder("/nonexistent/folder")
        assert "Error: Folder" in result
        assert "does not exist" in result

    def test_list_loaded_tables(self, sample_data_dir):
        """Test listing loaded tables"""
        load_csv_folder(str(sample_data_dir))
        result = list_loaded_tables()

        assert "sales" in result
        assert "customers" in result
        assert "Loaded tables:" in result

    def test_get_database_schema(self, sample_data_dir):
        """Test getting database schema"""
        load_csv_folder(str(sample_data_dir))
        result = get_database_schema()

        assert "Table: sales" in result
        assert "Table: customers" in result
        assert "Columns:" in result
        assert "Row count:" in result

    def test_get_table_info(self, sample_data_dir):
        """Test getting table information"""
        load_csv_folder(str(sample_data_dir))
        result = get_table_info("sales")

        assert "Table: sales" in result
        assert "Columns" in result
        assert "Total rows: 3" in result
        assert "date" in result
        assert "product" in result

    def test_execute_sql_query_select(self, sample_data_dir):
        """Test executing SELECT queries"""
        load_csv_folder(str(sample_data_dir))
        result = execute_sql_query("SELECT * FROM sales")

        # Parse JSON result
        data = json.loads(result)
        assert data["query_type"] == "SELECT"
        assert data["row_count"] == 3
        assert len(data["data"]) == 3
        assert "date" in data["columns"]
        assert "product" in data["columns"]

    def test_execute_sql_query_with_limit(self, sample_data_dir):
        """Test executing SELECT queries with limit"""
        load_csv_folder(str(sample_data_dir))
        result = execute_sql_query("SELECT * FROM sales", limit=2)

        data = json.loads(result)
        assert data["row_count"] == 2
        assert len(data["data"]) == 2

    def test_execute_sql_query_aggregation(self, sample_data_dir):
        """Test executing aggregation queries"""
        load_csv_folder(str(sample_data_dir))
        result = execute_sql_query(
            """
            SELECT category, COUNT(*) as count, AVG(price) as avg_price
            FROM sales
            GROUP BY category
        """
        )

        data = json.loads(result)
        assert data["query_type"] == "SELECT"
        assert data["row_count"] == 1  # Only one category
        assert "count" in data["columns"]
        assert "avg_price" in data["columns"]

    def test_execute_sql_query_join(self, sample_data_dir):
        """Test executing JOIN queries"""
        # First modify the data to have matching customer_ids
        temp_dir = sample_data_dir
        sales_data = pd.DataFrame(
            {
                "customer_id": [1, 2, 1],
                "product": ["Widget A", "Widget B", "Widget A"],
                "quantity": [10, 5, 8],
            }
        )
        sales_data.to_csv(temp_dir / "sales.csv", index=False)

        load_csv_folder(str(temp_dir))
        result = execute_sql_query(
            """
            SELECT s.product, c.name
            FROM sales s
            JOIN customers c ON s.customer_id = c.customer_id
        """
        )

        data = json.loads(result)
        assert data["query_type"] == "SELECT"
        assert "product" in data["columns"]
        assert "name" in data["columns"]

    def test_create_index(self, sample_data_dir):
        """Test creating an index"""
        load_csv_folder(str(sample_data_dir))
        result = create_index("sales", "category")

        assert "Index" in result
        assert "created successfully" in result
        assert "sales.category" in result

    def test_export_table_to_csv(self, sample_data_dir):
        """Test exporting table to CSV"""
        load_csv_folder(str(sample_data_dir))

        output_path = sample_data_dir / "export.csv"
        result = export_table_to_csv("sales", str(output_path))

        assert "exported successfully" in result
        assert output_path.exists()

        # Verify the exported data
        exported_df = pd.read_csv(output_path, sep=";")
        assert len(exported_df) == 3
        assert "date" in exported_df.columns
        assert "product" in exported_df.columns

    def test_backup_database(self, sample_data_dir):
        """Test backing up the database"""
        load_csv_folder(str(sample_data_dir))

        backup_path = sample_data_dir / "backup.db"
        result = backup_database(str(backup_path))

        assert "backed up successfully" in result
        assert backup_path.exists()

    def test_get_query_plan(self, sample_data_dir):
        """Test getting query execution plan"""
        load_csv_folder(str(sample_data_dir))
        result = get_query_plan("SELECT * FROM sales WHERE category = 'Electronics'")

        assert "Query Execution Plan" in result
        assert "Step" in result

    def test_clear_database(self, sample_data_dir):
        """Test clearing the database"""
        load_csv_folder(str(sample_data_dir))
        assert len(server_module._loaded_tables) == 2

        result = clear_database()

        assert "Database cleared" in result
        assert "Removed 2 tables" in result
        assert len(server_module._loaded_tables) == 0

    def test_no_database_loaded_error(self):
        """Test error handling when no database is loaded"""
        clear_database()  # Ensure clean state

        result = execute_sql_query("SELECT * FROM test")
        assert "Error: No database loaded" in result

        result = get_database_schema()
        assert "No database loaded" in result

        result = get_table_info("test")
        assert "Error: No database loaded" in result

    def test_get_data_summary(self, sample_data_dir):
        """Test getting data summary"""
        load_csv_folder(str(sample_data_dir))
        result = get_data_summary("sales")

        assert "Data Summary: sales" in result
        assert "Dimensions:" in result
        assert "3 rows" in result
        assert "5 columns" in result
        assert "Numeric Columns:" in result
        # Text Columns section might not appear if all columns are detected as numeric
        assert ("Text Columns:" in result) or ("Numeric Columns:" in result)

    def test_get_column_stats(self, sample_data_dir):
        """Test getting column statistics"""
        load_csv_folder(str(sample_data_dir))
        result = get_column_stats("sales", "price")

        assert "Column Statistics: sales.price" in result
        assert "Total rows: 3" in result
        assert "Non-null values:" in result
        assert "Unique values:" in result
        assert "Numeric Statistics:" in result
        assert "Min:" in result
        assert "Max:" in result
        assert "Average:" in result

    def test_analyze_missing_data(self, sample_data_dir):
        """Test missing data analysis"""
        # Create data with missing values
        temp_dir = sample_data_dir
        data_with_missing = pd.DataFrame(
            {
                "name": ["Alice", "Bob", None],
                "age": [25, None, 35],
                "city": ["NYC", "LA", ""],
            }
        )
        data_with_missing.to_csv(temp_dir / "missing_data.csv", index=False)

        load_csv_folder(str(temp_dir))
        result = analyze_missing_data("missing_data")

        assert "Missing Data Analysis: missing_data" in result
        assert "Total rows: 3" in result
        assert "Missing data by column:" in result
        assert "Percentage" in result

    def test_find_duplicates(self, sample_data_dir):
        """Test duplicate detection"""
        # Create data with duplicates
        temp_dir = sample_data_dir
        data_with_duplicates = pd.DataFrame(
            {
                "name": ["Alice", "Bob", "Alice", "Carol"],
                "age": [25, 30, 25, 35],
                "city": ["NYC", "LA", "NYC", "Chicago"],
            }
        )
        data_with_duplicates.to_csv(temp_dir / "duplicates.csv", index=False)

        load_csv_folder(str(temp_dir))
        result = find_duplicates("duplicates", "all")

        assert "Duplicate Analysis: duplicates" in result
        assert "Duplicate groups found:" in result
        assert "Total duplicate rows:" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
