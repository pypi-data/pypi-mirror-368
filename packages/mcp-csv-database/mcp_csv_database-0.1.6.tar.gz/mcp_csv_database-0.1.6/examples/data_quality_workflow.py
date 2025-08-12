#!/usr/bin/env python3
"""
Data Quality Assessment Workflow Example

This example demonstrates a complete data quality assessment workflow
using the MCP CSV Database Server's analysis tools.
"""

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from mcp_csv_database.server import (
    analyze_missing_data,
    clear_database,
    execute_sql_query,
    find_duplicates,
    get_column_stats,
    get_data_summary,
    load_csv_folder,
)


def create_messy_dataset():
    """Create a dataset with common data quality issues"""
    temp_dir = Path(tempfile.mkdtemp())

    # Create customer data with various quality issues
    np.random.seed(123)

    # Base clean data
    clean_customers = pd.DataFrame(
        {
            "id": range(1, 951),
            "first_name": [f"User{i}" for i in range(1, 951)],
            "last_name": [f"Lastname{i}" for i in range(1, 951)],
            "email": [f"user{i}@example.com" for i in range(1, 951)],
            "phone": [f"555-{1000+i:04d}" for i in range(950)],
            "age": np.random.randint(18, 80, 950),
            "income": np.random.normal(55000, 25000, 950).round(2),
            "city": np.random.choice(
                [
                    "New York",
                    "Los Angeles",
                    "Chicago",
                    "Houston",
                    "Phoenix",
                    "Philadelphia",
                    "San Antonio",
                    "San Diego",
                    "Dallas",
                ],
                950,
            ),
            "signup_date": pd.date_range("2020-01-01", periods=950, freq="1D").strftime("%Y-%m-%d"),
        }
    )

    # Introduce data quality issues
    problematic_data = []

    # 1. Missing values (50 records)
    for i in range(50):
        record = {
            "id": 951 + i,
            "first_name": None if i % 5 == 0 else f"User{951+i}",
            "last_name": "" if i % 7 == 0 else f"Lastname{951+i}",
            "email": None if i % 3 == 0 else f"user{951+i}@example.com",
            "phone": None if i % 4 == 0 else f"555-{2000+i:04d}",
            "age": None if i % 6 == 0 else np.random.randint(18, 80),
            "income": None if i % 8 == 0 else np.random.normal(55000, 25000),
            "city": (
                ""
                if i % 9 == 0
                else np.random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"])
            ),
            "signup_date": None if i % 10 == 0 else pd.Timestamp("2023-01-01").strftime("%Y-%m-%d"),
        }
        problematic_data.append(record)

    # 2. Duplicate records (25 records - exact duplicates)
    for i in range(25):
        base_id = np.random.randint(1, 100)  # Duplicate existing IDs
        record = {
            "id": base_id,  # Duplicate ID
            "first_name": f"User{base_id}",
            "last_name": f"Lastname{base_id}",
            "email": f"user{base_id}@example.com",  # Duplicate email
            "phone": f"555-{1000+base_id:04d}",
            "age": np.random.randint(18, 80),
            "income": np.random.normal(55000, 25000),
            "city": np.random.choice(["New York", "Los Angeles", "Chicago"]),
            "signup_date": pd.Timestamp("2022-06-15").strftime("%Y-%m-%d"),
        }
        problematic_data.append(record)

    # 3. Inconsistent data (25 records)
    for i in range(25):
        record = {
            "id": 1026 + i,
            "first_name": f"User{1026+i}",
            "last_name": f"Lastname{1026+i}",
            "email": f"INVALID_EMAIL_{i}",  # Invalid email format
            "phone": f"INVALID_PHONE_{i}",  # Invalid phone format
            "age": np.random.choice([-5, 0, 150, 999]),  # Invalid ages
            "income": np.random.choice([-50000, 0, 10000000]),  # Outlier incomes
            "city": f"Unknown City {i}",  # Inconsistent city names
            "signup_date": "INVALID_DATE",  # Invalid date format
        }
        problematic_data.append(record)

    # Combine all data
    all_data = pd.concat([clean_customers, pd.DataFrame(problematic_data)], ignore_index=True)

    # Shuffle the data
    all_data = all_data.sample(frac=1, random_state=42).reset_index(drop=True)

    # Save to CSV
    all_data.to_csv(temp_dir / "customer_data.csv", index=False)

    # Create a second table for relationship analysis
    orders_data = pd.DataFrame(
        {
            "order_id": range(1, 501),
            "customer_id": np.random.choice(all_data["id"].dropna().astype(int), 500),
            "order_date": pd.date_range("2023-01-01", periods=500, freq="1D").strftime("%Y-%m-%d"),
            "amount": np.random.uniform(10, 1000, 500).round(2),
            "status": np.random.choice(["pending", "completed", "cancelled", None, ""], 500),
        }
    )

    orders_data.to_csv(temp_dir / "orders.csv", index=False)

    return temp_dir


def run_data_quality_workflow():
    """Execute a comprehensive data quality assessment workflow"""
    print("🔍 Data Quality Assessment Workflow")
    print("=" * 50)

    # Create messy dataset
    temp_dir = create_messy_dataset()
    print(f"📁 Created sample dataset with quality issues in: {temp_dir}")

    try:
        # Step 1: Load Data
        print("\n🚀 STEP 1: DATA LOADING")
        print("-" * 30)
        load_result = load_csv_folder(str(temp_dir))
        print(load_result)

        # Step 2: Initial Data Overview
        print("\n📊 STEP 2: INITIAL DATA OVERVIEW")
        print("-" * 30)

        customer_summary = get_data_summary("customer_data")
        print("CUSTOMER DATA SUMMARY:")
        print(customer_summary)

        orders_summary = get_data_summary("orders")
        print("\nORDERS DATA SUMMARY:")
        print(orders_summary)

        # Step 3: Missing Data Analysis
        print("\n❌ STEP 3: MISSING DATA ANALYSIS")
        print("-" * 30)

        customer_missing = analyze_missing_data("customer_data")
        print("CUSTOMER MISSING DATA:")
        print(customer_missing)

        orders_missing = analyze_missing_data("orders")
        print("\nORDERS MISSING DATA:")
        print(orders_missing)

        # Step 4: Duplicate Detection
        print("\n🔄 STEP 4: DUPLICATE DETECTION")
        print("-" * 30)

        # Check for exact duplicates
        all_duplicates = find_duplicates("customer_data", "all")
        print("EXACT DUPLICATES (ALL COLUMNS):")
        print(all_duplicates)

        # Check for ID duplicates
        id_duplicates = find_duplicates("customer_data", "id")
        print("\nID DUPLICATES:")
        print(id_duplicates)

        # Check for email duplicates
        email_duplicates = find_duplicates("customer_data", "email")
        print("\nEMAIL DUPLICATES:")
        print(email_duplicates)

        # Step 5: Statistical Analysis of Key Columns
        print("\n📈 STEP 5: STATISTICAL ANALYSIS")
        print("-" * 30)

        age_stats = get_column_stats("customer_data", "age")
        print("AGE STATISTICS:")
        print(age_stats)

        income_stats = get_column_stats("customer_data", "income")
        print("\nINCOME STATISTICS:")
        print(income_stats)

        # Step 6: Data Quality Rules Validation
        print("\n✅ STEP 6: DATA QUALITY RULES VALIDATION")
        print("-" * 30)

        # Email format validation
        email_issues = execute_sql_query(
            """
            SELECT
                COUNT(*) as total_records,
                COUNT(CASE WHEN email IS NULL OR email = '' THEN 1 END) as missing_emails,
                COUNT(CASE WHEN email NOT LIKE '%@%.%' AND email IS NOT NULL AND email != '' THEN 1 END) as invalid_email_format,
                COUNT(CASE WHEN email LIKE '%@%.%' THEN 1 END) as valid_emails
            FROM customer_data
        """
        )
        print("EMAIL VALIDATION:")
        print(email_issues)

        # Age validation
        age_issues = execute_sql_query(
            """
            SELECT
                COUNT(*) as total_records,
                COUNT(CASE WHEN age IS NULL THEN 1 END) as missing_age,
                COUNT(CASE WHEN age < 0 THEN 1 END) as negative_age,
                COUNT(CASE WHEN age > 120 THEN 1 END) as unrealistic_age,
                COUNT(CASE WHEN age BETWEEN 0 AND 120 THEN 1 END) as valid_age
            FROM customer_data
        """
        )
        print("\nAGE VALIDATION:")
        print(age_issues)

        # Income validation
        income_issues = execute_sql_query(
            """
            SELECT
                COUNT(*) as total_records,
                COUNT(CASE WHEN income IS NULL THEN 1 END) as missing_income,
                COUNT(CASE WHEN income < 0 THEN 1 END) as negative_income,
                COUNT(CASE WHEN income > 1000000 THEN 1 END) as unrealistic_income,
                COUNT(CASE WHEN income BETWEEN 0 AND 1000000 THEN 1 END) as reasonable_income,
                ROUND(AVG(CASE WHEN income BETWEEN 0 AND 1000000 THEN income END), 2) as avg_reasonable_income
            FROM customer_data
        """
        )
        print("\nINCOME VALIDATION:")
        print(income_issues)

        # Step 7: Referential Integrity Check
        print("\n🔗 STEP 7: REFERENTIAL INTEGRITY CHECK")
        print("-" * 30)

        orphaned_orders = execute_sql_query(
            """
            SELECT
                COUNT(*) as total_orders,
                COUNT(CASE WHEN c.id IS NULL THEN 1 END) as orphaned_orders,
                COUNT(CASE WHEN c.id IS NOT NULL THEN 1 END) as valid_orders
            FROM orders o
            LEFT JOIN customer_data c ON o.customer_id = c.id
        """
        )
        print("REFERENTIAL INTEGRITY (Orders -> Customers):")
        print(orphaned_orders)

        # Step 8: Data Quality Score & Recommendations
        print("\n🎯 STEP 8: DATA QUALITY SCORE & RECOMMENDATIONS")
        print("-" * 30)

        quality_metrics = execute_sql_query(
            """
            SELECT
                'Overall Data Quality' as metric,
                COUNT(*) as total_records,
                ROUND(
                    (COUNT(CASE WHEN
                        id IS NOT NULL AND
                        first_name IS NOT NULL AND first_name != '' AND
                        last_name IS NOT NULL AND last_name != '' AND
                        email LIKE '%@%.%' AND
                        age BETWEEN 18 AND 120 AND
                        income > 0 AND income < 1000000
                    THEN 1 END) * 100.0 / COUNT(*)), 2
                ) as quality_score_percentage
            FROM customer_data
        """
        )
        print("DATA QUALITY METRICS:")
        print(quality_metrics)

        print("\n📋 DATA QUALITY RECOMMENDATIONS:")
        print("1. 🔧 FIX MISSING DATA:")
        print("   - Implement data validation at entry point")
        print("   - Set up alerts for records with missing critical fields")
        print("   - Consider default values or data imputation strategies")

        print("\n2. 🗑️  HANDLE DUPLICATES:")
        print("   - Implement unique constraints on ID and email fields")
        print("   - Set up duplicate detection processes")
        print("   - Create data deduplication workflows")

        print("\n3. ✏️  STANDARDIZE DATA:")
        print("   - Implement email format validation")
        print("   - Add age range constraints (18-120)")
        print("   - Set reasonable income limits")
        print("   - Standardize city names using a reference list")

        print("\n4. 🔒 ENSURE REFERENTIAL INTEGRITY:")
        print("   - Add foreign key constraints")
        print("   - Implement cascading updates/deletes")
        print("   - Regular orphaned record cleanup")

        print("\n✨ WORKFLOW COMPLETE!")
        print("Use these insights to improve your data collection and validation processes.")

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
    run_data_quality_workflow()
