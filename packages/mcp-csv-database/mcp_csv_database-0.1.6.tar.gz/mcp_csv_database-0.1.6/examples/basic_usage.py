#!/usr/bin/env python3
"""
Basic usage example for MCP CSV Database Server
"""

import tempfile
from pathlib import Path

import pandas as pd

from mcp_csv_database.server import (
    clear_database,
    create_index,
    execute_sql_query,
    export_table_to_csv,
    get_database_schema,
    get_table_info,
    list_loaded_tables,
    load_csv_folder,
)


def create_sample_data():
    """Create sample CSV files for demonstration"""
    temp_dir = Path(tempfile.mkdtemp())

    # Create sample sales data
    sales_data = pd.DataFrame(
        {
            "date": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04"],
            "product": ["Widget A", "Widget B", "Widget A", "Widget C"],
            "category": ["Electronics", "Electronics", "Electronics", "Home"],
            "quantity": [10, 5, 8, 12],
            "price": [29.99, 49.99, 29.99, 15.99],
            "customer_id": [1, 2, 1, 3],
        }
    )

    # Create sample customer data
    customer_data = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
            "name": ["Alice Johnson", "Bob Smith", "Carol Williams"],
            "email": [
                "alice@example.com",
                "bob@example.com",
                "carol@example.com",
            ],
            "city": ["New York", "Los Angeles", "Chicago"],
        }
    )

    # Save to CSV files
    sales_csv = temp_dir / "sales.csv"
    customers_csv = temp_dir / "customers.csv"

    sales_data.to_csv(sales_csv, index=False)
    customer_data.to_csv(customers_csv, index=False)

    return temp_dir, sales_csv, customers_csv


def main():
    """Demonstrate basic usage of the CSV database server"""
    print("🗃️  MCP CSV Database Server - Basic Usage Example")
    print("=" * 50)

    # Create sample data
    temp_dir, sales_csv, customers_csv = create_sample_data()
    print(f"Created sample data in: {temp_dir}")

    try:
        # 1. Load CSV files
        print("\n1. Loading CSV files...")
        result = load_csv_folder(str(temp_dir))
        print(result)

        # 2. List loaded tables
        print("\n2. Listing loaded tables...")
        tables = list_loaded_tables()
        print(tables)

        # 3. View database schema
        print("\n3. Database schema...")
        schema = get_database_schema()
        print(schema)

        # 4. Get specific table info
        print("\n4. Sales table information...")
        info = get_table_info("sales")
        print(info)

        # 5. Execute some queries
        print("\n5. Sample queries...")

        # Basic SELECT
        print("\n--- All sales data ---")
        result = execute_sql_query("SELECT * FROM sales")
        print(result)

        # Aggregation query
        print("\n--- Sales by category ---")
        result = execute_sql_query(
            """
            SELECT
                category,
                COUNT(*) as num_sales,
                SUM(quantity) as total_quantity,
                AVG(price) as avg_price,
                SUM(quantity * price) as total_revenue
            FROM sales
            GROUP BY category
            ORDER BY total_revenue DESC
        """
        )
        print(result)

        # Join query
        print("\n--- Sales with customer names ---")
        result = execute_sql_query(
            """
            SELECT
                s.date,
                s.product,
                s.quantity,
                s.price,
                c.name as customer_name,
                c.city
            FROM sales s
            JOIN customers c ON s.customer_id = c.customer_id
            ORDER BY s.date
        """
        )
        print(result)

        # 6. Create an index for better performance
        print("\n6. Creating index...")
        index_result = create_index("sales", "category")
        print(index_result)

        # 7. Export table to CSV
        print("\n7. Exporting table...")
        export_path = temp_dir / "sales_export.csv"
        export_result = export_table_to_csv("sales", str(export_path))
        print(export_result)

        # 8. Advanced analysis
        print("\n8. Advanced analysis...")
        result = execute_sql_query(
            """
            SELECT
                c.city,
                COUNT(DISTINCT s.product) as unique_products,
                SUM(s.quantity * s.price) as total_spent
            FROM customers c
            JOIN sales s ON c.customer_id = s.customer_id
            GROUP BY c.city
            ORDER BY total_spent DESC
        """
        )
        print(result)

    finally:
        # Clean up
        print("\n9. Cleaning up...")
        clear_result = clear_database()
        print(clear_result)

        # Remove temporary files
        import shutil

        shutil.rmtree(temp_dir)
        print(f"Removed temporary directory: {temp_dir}")


if __name__ == "__main__":
    main()
