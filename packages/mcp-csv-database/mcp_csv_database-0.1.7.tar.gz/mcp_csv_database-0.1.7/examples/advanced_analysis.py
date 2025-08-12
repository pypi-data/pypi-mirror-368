#!/usr/bin/env python3
"""
Advanced Data Analysis Example for MCP CSV Database Server

This example demonstrates all the advanced data analysis capabilities
including data quality assessment, statistical analysis, and duplicate detection.
"""

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from mcp_csv_database.server import (
    analyze_missing_data,
    clear_database,
    create_index,
    execute_sql_query,
    find_duplicates,
    get_column_stats,
    get_data_summary,
    get_database_schema,
    get_query_plan,
    list_loaded_tables,
    load_csv_folder,
)


def create_realistic_dataset():
    """Create a realistic dataset with various data quality issues for demonstration"""
    temp_dir = Path(tempfile.mkdtemp())

    # Create customers data with missing values and duplicates
    np.random.seed(42)  # For reproducible results

    customers_data = pd.DataFrame(
        {
            "customer_id": list(range(1, 101)) + [1, 2, 3],  # Some duplicates
            "name": (
                ["Alice Johnson", "Bob Smith", "Carol Williams", "David Brown", "Eva Davis"] * 20
                + ["Missing Name", None, ""]  # Some missing names
            ),
            "email": (
                [f"user{i}@example.com" for i in range(1, 101)]
                + ["alice@example.com", "bob@example.com", ""]  # Duplicate emails and missing
            ),
            "age": (
                np.random.randint(18, 80, 100).tolist() + [None, 25, None]  # Some missing ages
            ),
            "city": (
                np.random.choice(
                    ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"], 100
                ).tolist()
                + ["New York", None, ""]  # Some missing cities
            ),
            "income": (
                np.random.normal(50000, 20000, 100).round(2).tolist()
                + [75000.0, None, 45000.0]  # Some missing income
            ),
            "signup_date": (
                pd.date_range("2020-01-01", periods=100, freq="3D").strftime("%Y-%m-%d").tolist()
                + ["2023-01-01", "2023-01-02", None]  # Some missing dates
            ),
        }
    )

    # Create sales data with various patterns
    sales_data = pd.DataFrame(
        {
            "sale_id": range(1, 201),
            "customer_id": np.random.choice(range(1, 101), 200),
            "product": np.random.choice(
                ["Laptop", "Phone", "Tablet", "Headphones", "Watch", "Camera"], 200
            ),
            "category": np.random.choice(["Electronics", "Accessories", "Computers"], 200),
            "quantity": np.random.randint(1, 5, 200),
            "unit_price": np.random.uniform(50, 2000, 200).round(2),
            "sale_date": pd.date_range("2023-01-01", periods=200, freq="1D").strftime("%Y-%m-%d"),
            "sales_rep": np.random.choice(
                ["John Doe", "Jane Smith", "Mike Johnson", None, ""], 200
            ),  # Some missing sales reps
        }
    )

    # Create product catalog
    product_data = pd.DataFrame(
        {
            "product_name": ["Laptop", "Phone", "Tablet", "Headphones", "Watch", "Camera"],
            "category": [
                "Computers",
                "Electronics",
                "Computers",
                "Accessories",
                "Accessories",
                "Electronics",
            ],
            "brand": ["TechCorp", "PhoneCo", "TechCorp", "AudioBrand", "TimeBrand", "PhotoCorp"],
            "launch_year": [2021, 2022, 2023, 2020, 2021, 2022],
            "warranty_months": [24, 12, 18, 6, 12, 24],
            "weight_kg": [2.1, 0.2, 0.8, 0.3, 0.1, 0.9],
        }
    )

    # Save to CSV files
    customers_data.to_csv(temp_dir / "customers.csv", index=False)
    sales_data.to_csv(temp_dir / "sales.csv", index=False)
    product_data.to_csv(temp_dir / "products.csv", index=False)

    return temp_dir


def demonstrate_advanced_analysis():
    """Demonstrate all advanced analysis capabilities"""
    print("🔬 MCP CSV Database Server - Advanced Data Analysis Demo")
    print("=" * 60)

    # Create realistic dataset
    temp_dir = create_realistic_dataset()
    print(f"📁 Created sample dataset in: {temp_dir}")

    try:
        # 1. Load data
        print("\n1️⃣ Loading CSV files...")
        load_result = load_csv_folder(str(temp_dir))
        print(load_result)

        print("\n📋 Loaded tables:")
        tables = list_loaded_tables()
        print(tables)

        # 2. Data Overview
        print("\n2️⃣ DATA OVERVIEW & SCHEMA")
        print("-" * 40)
        schema = get_database_schema()
        print(schema)

        # 3. Comprehensive Data Summary
        print("\n3️⃣ COMPREHENSIVE DATA SUMMARIES")
        print("-" * 40)

        for table in ["customers", "sales", "products"]:
            print(f"\n--- {table.upper()} TABLE SUMMARY ---")
            summary = get_data_summary(table)
            print(summary)

        # 4. Data Quality Assessment
        print("\n4️⃣ DATA QUALITY ASSESSMENT")
        print("-" * 40)

        print("\n--- MISSING DATA ANALYSIS ---")
        missing_customers = analyze_missing_data("customers")
        print(missing_customers)

        print("\n--- DUPLICATE DETECTION ---")
        duplicates_all = find_duplicates("customers", "all")
        print(duplicates_all)

        duplicates_email = find_duplicates("customers", "email")
        print("\n--- DUPLICATES BY EMAIL ---")
        print(duplicates_email)

        # 5. Statistical Analysis
        print("\n5️⃣ STATISTICAL ANALYSIS")
        print("-" * 40)

        print("\n--- AGE STATISTICS ---")
        age_stats = get_column_stats("customers", "age")
        print(age_stats)

        print("\n--- INCOME STATISTICS ---")
        income_stats = get_column_stats("customers", "income")
        print(income_stats)

        print("\n--- SALES QUANTITY STATISTICS ---")
        quantity_stats = get_column_stats("sales", "quantity")
        print(quantity_stats)

        # 6. Advanced Queries with Analysis
        print("\n6️⃣ ADVANCED ANALYTICAL QUERIES")
        print("-" * 40)

        print("\n--- CUSTOMER SEGMENTATION BY INCOME ---")
        segmentation = execute_sql_query(
            """
            SELECT
                CASE
                    WHEN income < 30000 THEN 'Low Income'
                    WHEN income < 60000 THEN 'Middle Income'
                    WHEN income >= 60000 THEN 'High Income'
                    ELSE 'Unknown'
                END as income_segment,
                COUNT(*) as customer_count,
                AVG(income) as avg_income,
                MIN(age) as min_age,
                MAX(age) as max_age
            FROM customers
            WHERE income IS NOT NULL
            GROUP BY income_segment
            ORDER BY avg_income DESC
        """
        )
        print(segmentation)

        print("\n--- SALES PERFORMANCE BY PRODUCT ---")
        sales_analysis = execute_sql_query(
            """
            SELECT
                s.product,
                s.category,
                COUNT(*) as total_sales,
                SUM(s.quantity) as total_quantity,
                AVG(s.unit_price) as avg_price,
                SUM(s.quantity * s.unit_price) as total_revenue,
                COUNT(DISTINCT s.customer_id) as unique_customers
            FROM sales s
            GROUP BY s.product, s.category
            ORDER BY total_revenue DESC
        """
        )
        print(sales_analysis)

        print("\n--- CUSTOMER LIFETIME VALUE ---")
        clv_analysis = execute_sql_query(
            """
            SELECT
                c.customer_id,
                c.name,
                c.city,
                COUNT(s.sale_id) as total_orders,
                SUM(s.quantity * s.unit_price) as lifetime_value,
                AVG(s.quantity * s.unit_price) as avg_order_value,
                MIN(s.sale_date) as first_purchase,
                MAX(s.sale_date) as last_purchase
            FROM customers c
            JOIN sales s ON c.customer_id = s.customer_id
            WHERE c.name IS NOT NULL
            GROUP BY c.customer_id, c.name, c.city
            ORDER BY lifetime_value DESC
            LIMIT 10
        """
        )
        print(clv_analysis)

        # 7. Performance Optimization
        print("\n7️⃣ PERFORMANCE OPTIMIZATION")
        print("-" * 40)

        print("\n--- CREATING INDEXES ---")
        index1 = create_index("sales", "customer_id")
        print(index1)

        index2 = create_index("sales", "product")
        print(index2)

        print("\n--- QUERY EXECUTION PLAN ---")
        plan = get_query_plan(
            """
            SELECT s.product, COUNT(*)
            FROM sales s
            WHERE s.customer_id = 1
            GROUP BY s.product
        """
        )
        print(plan)

        # 8. Data Quality Insights
        print("\n8️⃣ DATA QUALITY INSIGHTS & RECOMMENDATIONS")
        print("-" * 40)

        data_quality_report = execute_sql_query(
            """
            SELECT
                'Customers' as table_name,
                COUNT(*) as total_rows,
                COUNT(CASE WHEN name IS NULL OR name = '' THEN 1 END) as missing_names,
                COUNT(CASE WHEN email IS NULL OR email = '' THEN 1 END) as missing_emails,
                COUNT(CASE WHEN age IS NULL THEN 1 END) as missing_ages,
                COUNT(CASE WHEN income IS NULL THEN 1 END) as missing_income,
                COUNT(DISTINCT email) as unique_emails,
                ROUND(AVG(age), 1) as avg_age,
                ROUND(AVG(income), 2) as avg_income
            FROM customers

            UNION ALL

            SELECT
                'Sales' as table_name,
                COUNT(*) as total_rows,
                COUNT(CASE WHEN sales_rep IS NULL OR sales_rep = '' THEN 1 END) as missing_sales_rep,
                0 as missing_emails,
                0 as missing_ages,
                0 as missing_income,
                COUNT(DISTINCT product) as unique_products,
                ROUND(AVG(quantity), 1) as avg_quantity,
                ROUND(AVG(unit_price), 2) as avg_unit_price
            FROM sales
        """
        )
        print(data_quality_report)

        print("\n✨ ANALYSIS COMPLETE!")
        print("\nKey Insights:")
        print("• Use analyze_missing_data() to identify data quality issues")
        print("• Use find_duplicates() to detect and handle duplicate records")
        print("• Use get_column_stats() for detailed statistical analysis")
        print("• Use get_data_summary() for quick data overview")
        print("• Create indexes on frequently queried columns for better performance")
        print("• Combine tools for comprehensive data quality assessment")

    finally:
        # Clean up
        print("\n🧹 Cleaning up...")
        clear_result = clear_database()
        print(clear_result)

        # Remove temporary files
        import shutil

        shutil.rmtree(temp_dir)
        print(f"Removed temporary directory: {temp_dir}")


if __name__ == "__main__":
    demonstrate_advanced_analysis()
