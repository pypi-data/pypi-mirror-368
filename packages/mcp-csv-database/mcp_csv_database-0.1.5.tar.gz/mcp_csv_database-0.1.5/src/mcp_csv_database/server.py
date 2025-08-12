#!/usr/bin/env python3
"""
MCP Server for CSV File Management
Loads CSV files from a folder into a temporary SQLite database and provides SQL query capabilities.
"""

import json
import os
import sqlite3
import tempfile
from pathlib import Path
from typing import Dict, Optional

import pandas as pd
from mcp.server.fastmcp import Context, FastMCP

# Initialize the MCP server
mcp = FastMCP("CSV Database Server")

# Global variables to store database connection and loaded tables
_db_connection: Optional[sqlite3.Connection] = None
_loaded_tables: Dict[str, str] = {}  # table_name -> csv_file_path
_db_path: Optional[str] = None


@mcp.tool()
def get_database_schema(ctx: Context | None = None) -> str:
    """Get the current database schema showing all loaded tables
    and their structure

    Args:
        ctx: Optional context object providing access to request ID
    """
    tool_call_id = getattr(ctx, "request_id", None) if ctx else None

    if not _db_connection:
        error_output = {
            "tool_call_id": tool_call_id,
            "error": "No database loaded. Use load_csv_folder tool first.",
        }
        return json.dumps(error_output, indent=2, default=str)

    try:
        cursor = _db_connection.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        if not tables:
            output = {
                "tool_call_id": tool_call_id,
                "message": "Database is empty. No tables loaded.",
            }
            return json.dumps(output, indent=2, default=str)

        schema_info = []
        for (table_name,) in tables:
            schema_info.append(f"\n=== Table: {table_name} ===")

            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            schema_info.append("Columns:")
            for col in columns:
                col_name, col_type, not_null, default, pk = (
                    col[1],
                    col[2],
                    col[3],
                    col[4],
                    col[5],
                )
                pk_indicator = " (PRIMARY KEY)" if pk else ""
                null_indicator = " NOT NULL" if not_null else ""
                default_indicator = f" DEFAULT {default}" if default else ""
                schema_info.append(
                    f"  - {col_name}: {col_type}{pk_indicator}{null_indicator}{default_indicator}"
                )

            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            schema_info.append(f"Row count: {count}")

            # Show sample data (first 3 rows)
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            sample_rows = cursor.fetchall()
            if sample_rows:
                schema_info.append("Sample data:")
                column_names = [desc[0] for desc in cursor.description]
                for row in sample_rows:
                    row_dict = dict(zip(column_names, row))
                    schema_info.append(f"  {row_dict}")

        output = {"tool_call_id": tool_call_id, "schema": "\n".join(schema_info)}
        return json.dumps(output, indent=2, default=str)

    except Exception as e:
        error_output = {"tool_call_id": tool_call_id, "error": f"Error retrieving schema: {str(e)}"}
        return json.dumps(error_output, indent=2, default=str)


@mcp.tool()
def list_loaded_tables(ctx: Context | None = None) -> str:
    """List all currently loaded tables with their source CSV files

    Args:
        ctx: Optional context object providing access to request ID
    """
    tool_call_id = getattr(ctx, "request_id", None) if ctx else None

    if not _loaded_tables:
        output = {"tool_call_id": tool_call_id, "message": "No tables loaded."}
        return json.dumps(output, indent=2, default=str)

    table_list = []
    for table_name, csv_path in _loaded_tables.items():
        table_list.append(f"- {table_name} (from {csv_path})")

    output = {"tool_call_id": tool_call_id, "tables": "Loaded tables:\n" + "\n".join(table_list)}
    return json.dumps(output, indent=2, default=str)


@mcp.tool()
def load_csv_folder(folder_path: str, table_prefix: str = "", ctx: Context | None = None) -> str:
    """
    Load all CSV files from a folder into a temporary SQLite database.

    Args:
        folder_path: Path to folder containing CSV files
        table_prefix: Optional prefix for table names
        ctx: Optional context object providing access to request ID

    Returns:
        Status message with details of loaded files
    """
    tool_call_id = getattr(ctx, "request_id", None) if ctx else None
    global _db_connection, _loaded_tables, _db_path

    try:
        # Validate folder path
        folder = Path(folder_path)
        if not folder.exists():
            error_output = {
                "tool_call_id": tool_call_id,
                "error": f"Folder '{folder_path}' does not exist.",
            }
            return json.dumps(error_output, indent=2, default=str)

        if not folder.is_dir():
            error_output = {
                "tool_call_id": tool_call_id,
                "error": f"'{folder_path}' is not a directory.",
            }
            return json.dumps(error_output, indent=2, default=str)

        # Find CSV files
        csv_files = list(folder.glob("*.csv"))
        if not csv_files:
            error_output = {
                "tool_call_id": tool_call_id,
                "error": f"No CSV files found in '{folder_path}'.",
            }
            return json.dumps(error_output, indent=2, default=str)

        # Create temporary database
        if _db_connection:
            _db_connection.close()

        # Create a temporary file for the database
        temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        _db_path = temp_db.name
        temp_db.close()

        _db_connection = sqlite3.connect(_db_path)
        _loaded_tables = {}

        results = []
        successful_loads = 0

        for csv_file in csv_files:
            try:
                # Generate table name
                table_name = table_prefix + csv_file.stem.replace("-", "_").replace(" ", "_")

                # Load CSV into pandas DataFrame - try different separators
                df = None
                separators = [";", ",", "\t"]
                for sep in separators:
                    try:
                        df = pd.read_csv(csv_file, sep=sep, encoding="utf-8")
                        # Check if we got meaningful columns
                        # (more than 1 column usually indicates
                        # correct separator)
                        if len(df.columns) > 1:
                            break
                    except Exception:
                        continue

                if df is None:
                    # Fallback to default pandas behavior
                    df = pd.read_csv(csv_file)

                # Load DataFrame into SQLite
                df.to_sql(
                    table_name,
                    _db_connection,
                    index=False,
                    if_exists="replace",
                )

                _loaded_tables[table_name] = str(csv_file)
                results.append(
                    f"✓ Loaded {csv_file.name} -> table '{table_name}' ({len(df)} rows, {len(df.columns)} columns)"
                )
                successful_loads += 1

            except Exception as e:
                results.append(f"✗ Failed to load {csv_file.name}: {str(e)}")

        summary = f"Loaded {successful_loads}/{len(csv_files)} CSV files into temporary database.\n"
        summary += f"Database path: {_db_path}\n\n"
        summary += "\n".join(results)

        output = {
            "tool_call_id": tool_call_id,
            "summary": summary,
            "successful_loads": successful_loads,
            "total_files": len(csv_files),
            "database_path": _db_path,
        }
        return json.dumps(output, indent=2, default=str)

    except Exception as e:
        error_output = {
            "tool_call_id": tool_call_id,
            "error": f"Error loading CSV folder: {str(e)}",
        }
        return json.dumps(error_output, indent=2, default=str)


@mcp.tool()
def execute_sql_query(query: str, limit: int = 100, ctx: Context | None = None) -> str:
    """
    Execute any SQL query on the loaded database.

    Args:
        query: Any SQL query to execute (SELECT, INSERT, UPDATE, DELETE, CREATE, etc.)
        limit: Maximum number of rows to return for SELECT queries (default: 100)
        ctx: Optional context object providing access to request ID

    Returns:
        Query results formatted as JSON or execution status
    """
    tool_call_id = getattr(ctx, "request_id", None) if ctx else None
    
    if not _db_connection:
        error_output = {
            "tool_call_id": tool_call_id,
            "error": "No database loaded. Use load_csv_folder tool first.",
        }
        return json.dumps(error_output, indent=2, default=str)

    try:
        cursor = _db_connection.cursor()
        query_upper = query.strip().upper()

        # Execute the query
        cursor.execute(query)

        # Handle different types of queries
        if query_upper.startswith("SELECT"):
            # For SELECT queries, return data
            column_names = (
                [description[0] for description in cursor.description] if cursor.description else []
            )
            rows = cursor.fetchall()

            if not rows:
                output = {
                    "tool_call_id": tool_call_id,
                    "message": "Query executed successfully. No results returned.",
                }
                return json.dumps(output, indent=2, default=str)

            # Apply limit for SELECT queries if not already present
            if "LIMIT" not in query_upper and len(rows) > limit:
                rows = rows[:limit]
                limited = True
            else:
                limited = False

            # Convert to list of dictionaries
            results = []
            for row in rows:
                row_dict = dict(zip(column_names, row))
                results.append(row_dict)

            # Format output
            output = {
                "tool_call_id": tool_call_id,
                "query": query,
                "query_type": "SELECT",
                "row_count": len(results),
                "limited": limited,
                "columns": column_names,
                "data": results,
            }

            return json.dumps(output, indent=2, default=str)

        else:
            # For non-SELECT queries (INSERT, UPDATE, DELETE, CREATE, etc.)
            _db_connection.commit()  # Commit changes
            rows_affected = cursor.rowcount

            # Determine query type
            query_type = query_upper.split()[0] if query_upper.split() else "UNKNOWN"

            output = {
                "tool_call_id": tool_call_id,
                "query": query,
                "query_type": query_type,
                "rows_affected": rows_affected,
                "status": "success",
                "message": f"{query_type} query executed successfully",
            }

            return json.dumps(output, indent=2, default=str)

    except Exception as e:
        error_output = {
            "tool_call_id": getattr(ctx, "request_id", None) if ctx else None,
            "error": f"Error executing query: {str(e)}",
        }
        return json.dumps(error_output, indent=2, default=str)


@mcp.tool()
def get_table_info(table_name: str, ctx: Context | None = None) -> str:
    """
    Get detailed information about a specific table.

    Args:
        table_name: Name of the table to inspect
        ctx: Optional context object providing access to request ID

    Returns:
        Detailed table information including schema and sample data
    """
    tool_call_id = getattr(ctx, "request_id", None) if ctx else None

    if not _db_connection:
        error_output = {
            "tool_call_id": tool_call_id,
            "error": "No database loaded. Use load_csv_folder tool first.",
        }
        return json.dumps(error_output, indent=2, default=str)

    try:
        cursor = _db_connection.cursor()

        # Check if table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        )
        if not cursor.fetchone():
            available_tables = list(_loaded_tables.keys())
            error_output = {
                "tool_call_id": tool_call_id,
                "error": f"Table '{table_name}' not found. Available tables: {available_tables}",
            }
            return json.dumps(error_output, indent=2, default=str)

        info = []
        info.append(f"=== Table: {table_name} ===")

        # Source file info
        if table_name in _loaded_tables:
            info.append(f"Source CSV: {_loaded_tables[table_name]}")

        # Column information
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        info.append(f"\nColumns ({len(columns)}):")
        for col in columns:
            col_name, col_type = col[1], col[2]
            info.append(f"  - {col_name}: {col_type}")

        # Row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        info.append(f"\nTotal rows: {count}")

        # Sample data
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
        sample_rows = cursor.fetchall()
        if sample_rows:
            info.append("\nSample data (first 5 rows):")
            column_names = [desc[0] for desc in cursor.description]
            for i, row in enumerate(sample_rows, 1):
                row_dict = dict(zip(column_names, row))
                info.append(f"  Row {i}: {row_dict}")

        output = {"tool_call_id": tool_call_id, "table_info": "\n".join(info)}
        return json.dumps(output, indent=2, default=str)

    except Exception as e:
        error_output = {
            "tool_call_id": tool_call_id,
            "error": f"Error getting table info: {str(e)}",
        }
        return json.dumps(error_output, indent=2, default=str)


@mcp.tool()
def create_index(
    table_name: str, column_name: str, index_name: str = "", ctx: Context | None = None
) -> str:
    """
    Create an index on a table column for better query performance.

    Args:
        table_name: Name of the table
        column_name: Name of the column to index
        index_name: Optional custom index name
        ctx: Optional context object providing access to request ID

    Returns:
        Status message
    """
    tool_call_id = getattr(ctx, "request_id", None) if ctx else None

    if not _db_connection:
        error_output = {
            "tool_call_id": tool_call_id,
            "error": "No database loaded. Use load_csv_folder tool first.",
        }
        return json.dumps(error_output, indent=2, default=str)

    try:
        if not index_name:
            index_name = f"idx_{table_name}_{column_name}"

        # Sanitize column name if it contains spaces or special characters
        if " " in column_name or any(char in column_name for char in ["-", ".", "(", ")"]):
            column_ref = f'"{column_name}"'
        else:
            column_ref = column_name

        query = f'CREATE INDEX IF NOT EXISTS "{index_name}" ON "{table_name}" ({column_ref})'

        cursor = _db_connection.cursor()
        cursor.execute(query)
        _db_connection.commit()

        output = {
            "tool_call_id": tool_call_id,
            "message": f"Index '{index_name}' created successfully on {table_name}.{column_name}",
            "index_name": index_name,
            "table_name": table_name,
            "column_name": column_name,
        }
        return json.dumps(output, indent=2, default=str)

    except Exception as e:
        error_output = {"tool_call_id": tool_call_id, "error": f"Error creating index: {str(e)}"}
        return json.dumps(error_output, indent=2, default=str)


@mcp.tool()
def backup_database(backup_path: str, ctx: Context | None = None) -> str:
    """
    Create a backup of the current database to a file.

    Args:
        backup_path: Path where to save the backup file
        ctx: Optional context object providing access to request ID

    Returns:
        Status message
    """
    tool_call_id = getattr(ctx, "request_id", None) if ctx else None

    if not _db_connection:
        error_output = {
            "tool_call_id": tool_call_id,
            "error": "No database loaded. Use load_csv_folder tool first.",
        }
        return json.dumps(error_output, indent=2, default=str)

    try:
        # Create backup using SQLite backup
        backup_conn = sqlite3.connect(backup_path)
        _db_connection.backup(backup_conn)
        backup_conn.close()

        output = {
            "tool_call_id": tool_call_id,
            "message": f"Database backed up successfully to: {backup_path}",
            "backup_path": backup_path,
        }
        return json.dumps(output, indent=2, default=str)

    except Exception as e:
        error_output = {"tool_call_id": tool_call_id, "error": f"Error creating backup: {str(e)}"}
        return json.dumps(error_output, indent=2, default=str)


@mcp.tool()
def export_table_to_csv(
    table_name: str, output_path: str, include_header: bool = True, ctx: Context | None = None
) -> str:
    """
    Export a table to a CSV file.

    Args:
        table_name: Name of the table to export
        output_path: Path for the output CSV file
        include_header: Whether to include column headers
        ctx: Optional context object providing access to request ID

    Returns:
        Status message
    """
    tool_call_id = getattr(ctx, "request_id", None) if ctx else None

    if not _db_connection:
        error_output = {
            "tool_call_id": tool_call_id,
            "error": "No database loaded. Use load_csv_folder tool first.",
        }
        return json.dumps(error_output, indent=2, default=str)

    try:
        # Read table into pandas DataFrame
        df = pd.read_sql_query(f'SELECT * FROM "{table_name}"', _db_connection)

        # Export to CSV
        df.to_csv(
            output_path,
            index=False,
            header=include_header,
            sep=";",
            encoding="utf-8",
        )

        output = {
            "tool_call_id": tool_call_id,
            "message": f"Table '{table_name}' exported successfully to: {output_path} ({len(df)} rows)",
            "table_name": table_name,
            "output_path": output_path,
            "row_count": len(df),
            "include_header": include_header,
        }
        return json.dumps(output, indent=2, default=str)

    except Exception as e:
        error_output = {"tool_call_id": tool_call_id, "error": f"Error exporting table: {str(e)}"}
        return json.dumps(error_output, indent=2, default=str)


@mcp.tool()
def get_query_plan(query: str, ctx: Context | None = None) -> str:
    """
    Get the execution plan for a query to understand performance.

    Args:
        query: SQL query to analyze
        ctx: Optional context object providing access to request ID

    Returns:
        Query execution plan
    """
    tool_call_id = getattr(ctx, "request_id", None) if ctx else None

    if not _db_connection:
        error_output = {
            "tool_call_id": tool_call_id,
            "error": "No database loaded. Use load_csv_folder tool first.",
        }
        return json.dumps(error_output, indent=2, default=str)

    try:
        cursor = _db_connection.cursor()
        explain_query = f"EXPLAIN QUERY PLAN {query}"
        cursor.execute(explain_query)

        plan_rows = cursor.fetchall()

        if not plan_rows:
            output = {
                "tool_call_id": tool_call_id,
                "message": "No execution plan available.",
                "query": query,
            }
            return json.dumps(output, indent=2, default=str)

        plan_info = ["Query Execution Plan:", "=" * 30]
        for row in plan_rows:
            plan_info.append(f"Step {row[0]}: {row[3]}")

        output = {
            "tool_call_id": tool_call_id,
            "query": query,
            "execution_plan": "\n".join(plan_info),
        }
        return json.dumps(output, indent=2, default=str)

    except Exception as e:
        error_output = {
            "tool_call_id": tool_call_id,
            "error": f"Error getting query plan: {str(e)}",
        }
        return json.dumps(error_output, indent=2, default=str)


@mcp.tool()
def clear_database(ctx: Context | None = None) -> str:
    """
    Clear the temporary database and remove all loaded tables.

    Args:
        ctx: Optional context object providing access to request ID

    Returns:
        Status message
    """
    tool_call_id = getattr(ctx, "request_id", None) if ctx else None
    global _db_connection, _loaded_tables, _db_path

    try:
        if _db_connection:
            _db_connection.close()
            _db_connection = None

        if _db_path and os.path.exists(_db_path):
            os.unlink(_db_path)
            _db_path = None

        table_count = len(_loaded_tables)
        _loaded_tables = {}

        output = {
            "tool_call_id": tool_call_id,
            "message": f"Database cleared. Removed {table_count} tables.",
            "tables_removed": table_count,
        }
        return json.dumps(output, indent=2, default=str)

    except Exception as e:
        error_output = {"tool_call_id": tool_call_id, "error": f"Error clearing database: {str(e)}"}
        return json.dumps(error_output, indent=2, default=str)


@mcp.tool()
def get_column_stats(table_name: str, column_name: str, ctx: Context | None = None) -> str:
    """
    Get statistical summary for a specific column.

    Args:
        table_name: Name of the table
        column_name: Name of the column to analyze
        ctx: Optional context object providing access to request ID

    Returns:
        Statistical summary including count, nulls, unique values, and distribution info
    """
    tool_call_id = getattr(ctx, "request_id", None) if ctx else None

    if not _db_connection:
        error_output = {
            "tool_call_id": tool_call_id,
            "error": "No database loaded. Use load_csv_folder tool first.",
        }
        return json.dumps(error_output, indent=2, default=str)

    try:
        cursor = _db_connection.cursor()

        # Check if table and column exist
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        if column_name not in columns:
            error_output = {
                "tool_call_id": tool_call_id,
                "error": f"Column '{column_name}' not found in table '{table_name}'. Available columns: {columns}",
            }
            return json.dumps(error_output, indent=2, default=str)

        stats = []
        stats.append(f"=== Column Statistics: {table_name}.{column_name} ===")

        # Basic counts
        cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
        total_rows = cursor.fetchone()[0]

        cursor.execute(
            f'SELECT COUNT("{column_name}") FROM "{table_name}" WHERE "{column_name}" IS NOT NULL'
        )
        non_null_count = cursor.fetchone()[0]
        null_count = total_rows - non_null_count

        cursor.execute(
            f'SELECT COUNT(DISTINCT "{column_name}") FROM "{table_name}" WHERE "{column_name}" IS NOT NULL'
        )
        unique_count = cursor.fetchone()[0]

        stats.append(f"Total rows: {total_rows}")
        stats.append(f"Non-null values: {non_null_count}")
        stats.append(f"Null values: {null_count} ({null_count / total_rows * 100:.1f}%)")
        stats.append(f"Unique values: {unique_count}")

        # Try numeric statistics
        try:
            cursor.execute(
                f"""
                SELECT
                    MIN(CAST("{column_name}" AS REAL)),
                    MAX(CAST("{column_name}" AS REAL)),
                    AVG(CAST("{column_name}" AS REAL))
                FROM "{table_name}"
                WHERE "{column_name}" IS NOT NULL
                AND "{column_name}" != ''
            """
            )
            min_val, max_val, avg_val = cursor.fetchone()
            if min_val is not None:
                stats.append("\nNumeric Statistics:")
                stats.append(f"Min: {min_val}")
                stats.append(f"Max: {max_val}")
                stats.append(f"Average: {avg_val:.2f}")
        except Exception:
            pass

        # Most common values
        cursor.execute(
            f"""
            SELECT "{column_name}", COUNT(*) as freq
            FROM "{table_name}"
            WHERE "{column_name}" IS NOT NULL
            GROUP BY "{column_name}"
            ORDER BY freq DESC
            LIMIT 5
        """
        )
        common_values = cursor.fetchall()

        if common_values:
            stats.append("\nMost Common Values:")
            for value, freq in common_values:
                percentage = freq / total_rows * 100
                stats.append(f"  '{value}': {freq} ({percentage:.1f}%)")

        output = {
            "tool_call_id": tool_call_id,
            "column_stats": "\n".join(stats),
            "table_name": table_name,
            "column_name": column_name,
        }
        return json.dumps(output, indent=2, default=str)

    except Exception as e:
        error_output = {"tool_call_id": tool_call_id, "error": f"Error analyzing column: {str(e)}"}
        return json.dumps(error_output, indent=2, default=str)


@mcp.tool()
def find_duplicates(table_name: str, columns: str = "all", ctx: Context | None = None) -> str:
    """
    Find duplicate rows in a table.

    Args:
        table_name: Name of the table to check
        columns: Comma-separated column names to check for duplicates, or "all" for all columns
        ctx: Optional context object providing access to request ID

    Returns:
        Information about duplicate rows found
    """
    tool_call_id = getattr(ctx, "request_id", None) if ctx else None

    if not _db_connection:
        error_output = {
            "tool_call_id": tool_call_id,
            "error": "No database loaded. Use load_csv_folder tool first.",
        }
        return json.dumps(error_output, indent=2, default=str)

    try:
        cursor = _db_connection.cursor()

        # Get table columns
        cursor.execute(f"PRAGMA table_info({table_name})")
        all_columns = [col[1] for col in cursor.fetchall()]

        if columns.lower() == "all":
            check_columns = all_columns
        else:
            check_columns = [col.strip() for col in columns.split(",")]
            # Validate columns exist
            invalid_cols = [col for col in check_columns if col not in all_columns]
            if invalid_cols:
                error_output = {
                    "tool_call_id": tool_call_id,
                    "error": f"Invalid columns: {invalid_cols}. Available columns: {all_columns}",
                }
                return json.dumps(error_output, indent=2, default=str)

        # Build query to find duplicates
        column_list = ", ".join([f'"{col}"' for col in check_columns])

        duplicate_query = f"""
            SELECT {column_list}, COUNT(*) as duplicate_count
            FROM "{table_name}"
            GROUP BY {column_list}
            HAVING COUNT(*) > 1
            ORDER BY duplicate_count DESC
        """

        cursor.execute(duplicate_query)
        duplicates = cursor.fetchall()

        if not duplicates:
            output = {
                "tool_call_id": tool_call_id,
                "message": f"No duplicate rows found in table '{table_name}' for columns: {check_columns}",
                "table_name": table_name,
                "columns_checked": check_columns,
            }
            return json.dumps(output, indent=2, default=str)

        # Count total duplicate rows
        cursor.execute(
            f"""
            SELECT SUM(duplicate_count - 1) FROM (
                SELECT COUNT(*) as duplicate_count
                FROM "{table_name}"
                GROUP BY {column_list}
                HAVING COUNT(*) > 1
            )
        """
        )
        total_duplicate_rows = cursor.fetchone()[0] or 0

        result = []
        result.append(f"=== Duplicate Analysis: {table_name} ===")
        result.append(f"Columns checked: {check_columns}")
        result.append(f"Duplicate groups found: {len(duplicates)}")
        result.append(f"Total duplicate rows: {total_duplicate_rows}")
        result.append("")

        # Show top duplicate groups
        result.append("Top duplicate groups:")
        column_names = [desc[0] for desc in cursor.description[:-1]]  # Exclude count column

        for i, row in enumerate(duplicates[:10]):  # Show top 10
            values = row[:-1]  # Exclude count
            count = row[-1]
            value_pairs = [f"{col}='{val}'" for col, val in zip(column_names, values)]
            result.append(f"  {i + 1}. {', '.join(value_pairs)} (appears {count} times)")

        if len(duplicates) > 10:
            result.append(f"  ... and {len(duplicates) - 10} more duplicate groups")

        output = {
            "tool_call_id": tool_call_id,
            "duplicate_analysis": "\n".join(result),
            "table_name": table_name,
            "columns_checked": check_columns,
            "duplicate_groups_found": len(duplicates),
            "total_duplicate_rows": total_duplicate_rows,
        }
        return json.dumps(output, indent=2, default=str)

    except Exception as e:
        error_output = {
            "tool_call_id": tool_call_id,
            "error": f"Error finding duplicates: {str(e)}",
        }
        return json.dumps(error_output, indent=2, default=str)


@mcp.tool()
def analyze_missing_data(table_name: str, ctx: Context | None = None) -> str:
    """
    Analyze missing data patterns in a table.

    Args:
        table_name: Name of the table to analyze
        ctx: Optional context object providing access to request ID

    Returns:
        Summary of missing data patterns across all columns
    """
    tool_call_id = getattr(ctx, "request_id", None) if ctx else None

    if not _db_connection:
        error_output = {
            "tool_call_id": tool_call_id,
            "error": "No database loaded. Use load_csv_folder tool first.",
        }
        return json.dumps(error_output, indent=2, default=str)

    try:
        cursor = _db_connection.cursor()

        # Get total row count
        cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
        total_rows = cursor.fetchone()[0]

        # Get all columns
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]

        result = []
        result.append(f"=== Missing Data Analysis: {table_name} ===")
        result.append(f"Total rows: {total_rows}")
        result.append("")

        missing_info = []
        for column in columns:
            # Count null and empty values
            cursor.execute(
                f"""
                SELECT
                    COUNT(*) - COUNT("{column}") as null_count,
                    SUM(CASE WHEN "{column}" = '' THEN 1 ELSE 0 END) as empty_count
                FROM "{table_name}"
            """
            )
            null_count, empty_count = cursor.fetchone()
            missing_count = null_count + empty_count
            missing_percentage = (missing_count / total_rows) * 100 if total_rows > 0 else 0

            missing_info.append(
                (
                    column,
                    missing_count,
                    missing_percentage,
                    null_count,
                    empty_count,
                )
            )

        # Sort by missing percentage (highest first)
        missing_info.sort(key=lambda x: x[2], reverse=True)

        result.append("Missing data by column:")
        result.append("Column | Missing | Percentage | Nulls | Empty")
        result.append("-" * 50)

        for (
            column,
            missing_count,
            missing_pct,
            null_count,
            empty_count,
        ) in missing_info:
            result.append(
                f"{column:<15} | {missing_count:>7} | {missing_pct:>8.1f}% | {null_count:>5} | {empty_count:>5}"
            )

        # Summary insights
        result.append("")
        high_missing = [info for info in missing_info if info[2] > 50]
        if high_missing:
            result.append("⚠️  Columns with >50% missing data:")
            for column, _, missing_pct, _, _ in high_missing:
                result.append(f"  - {column}: {missing_pct:.1f}%")

        no_missing = [info for info in missing_info if info[1] == 0]
        if no_missing:
            result.append("")
            result.append(f"✅ Complete columns (no missing data): {len(no_missing)}")
            if len(no_missing) <= 10:
                complete_cols = [info[0] for info in no_missing]
                result.append(f"  {', '.join(complete_cols)}")

        output = {
            "tool_call_id": tool_call_id,
            "missing_data_analysis": "\n".join(result),
            "table_name": table_name,
            "total_rows": total_rows,
        }
        return json.dumps(output, indent=2, default=str)

    except Exception as e:
        error_output = {
            "tool_call_id": tool_call_id,
            "error": f"Error analyzing missing data: {str(e)}",
        }
        return json.dumps(error_output, indent=2, default=str)


@mcp.tool()
def get_data_summary(table_name: str, ctx: Context | None = None) -> str:
    """
    Get a comprehensive summary of the table data.

    Args:
        table_name: Name of the table to summarize
        ctx: Optional context object providing access to request ID

    Returns:
        Quick overview with key insights about the data
    """
    tool_call_id = getattr(ctx, "request_id", None) if ctx else None

    if not _db_connection:
        error_output = {
            "tool_call_id": tool_call_id,
            "error": "No database loaded. Use load_csv_folder tool first.",
        }
        return json.dumps(error_output, indent=2, default=str)

    try:
        cursor = _db_connection.cursor()

        # Basic table info
        cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
        total_rows = cursor.fetchone()[0]

        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        total_columns = len(columns_info)

        result = []
        result.append(f"=== Data Summary: {table_name} ===")
        result.append(f"Dimensions: {total_rows:,} rows × {total_columns} columns")
        result.append("")

        # Analyze each column quickly
        numeric_cols = []
        text_cols = []

        for col_info in columns_info:
            column = col_info[1]

            # Check if column has numeric data
            try:
                cursor.execute(
                    f"""
                    SELECT COUNT(*)
                    FROM "{table_name}"
                    WHERE "{column}" IS NOT NULL
                    AND "{column}" != ''
                    AND CAST("{column}" AS REAL) = CAST("{column}" AS REAL)
                    LIMIT 1
                """
                )
                if cursor.fetchone()[0] > 0:
                    # Get some numeric stats
                    cursor.execute(
                        f"""
                        SELECT
                            MIN(CAST("{column}" AS REAL)),
                            MAX(CAST("{column}" AS REAL)),
                            COUNT(DISTINCT "{column}")
                        FROM "{table_name}"
                        WHERE "{column}" IS NOT NULL
                        AND "{column}" != ''
                    """
                    )
                    min_val, max_val, unique_count = cursor.fetchone()
                    numeric_cols.append((column, min_val, max_val, unique_count))
                else:
                    raise ValueError("Not numeric")
            except Exception:
                # Text column
                cursor.execute(
                    f"""
                    SELECT COUNT(DISTINCT "{column}")
                    FROM "{table_name}"
                    WHERE "{column}" IS NOT NULL
                    AND "{column}" != ''
                """
                )
                unique_count = cursor.fetchone()[0]
                text_cols.append((column, unique_count))

        # Report numeric columns
        if numeric_cols:
            result.append("Numeric Columns:")
            for column, min_val, max_val, unique_count in numeric_cols:
                result.append(
                    f"  • {column}: {min_val} to {max_val} ({unique_count:,} unique values)"
                )

        # Report text columns
        if text_cols:
            result.append("")
            result.append("Text Columns:")
            for column, unique_count in text_cols:
                if unique_count == total_rows:
                    result.append(f"  • {column}: All unique values (likely ID/identifier)")
                elif unique_count < 20:
                    result.append(f"  • {column}: {unique_count} categories (likely categorical)")
                else:
                    result.append(f"  • {column}: {unique_count:,} unique values")

        # Quick data quality check
        result.append("")
        cursor.execute(
            f"""
            SELECT
                SUM(CASE WHEN {' OR '.join([f'"{col[1]}" IS NULL OR "{col[1]}" = ""' for col in columns_info])}
                    THEN 1 ELSE 0 END) as rows_with_missing
            FROM "{table_name}"
        """
        )
        rows_with_missing = cursor.fetchone()[0]
        complete_rows = total_rows - rows_with_missing

        result.append("Data Quality:")
        result.append(
            f"  • Complete rows: {complete_rows:,} ({complete_rows / total_rows * 100:.1f}%)"
        )
        result.append(
            f"  • Rows with missing data: {rows_with_missing:,} ({rows_with_missing / total_rows * 100:.1f}%)"
        )

        output = {
            "tool_call_id": tool_call_id,
            "data_summary": "\n".join(result),
            "table_name": table_name,
            "total_rows": total_rows,
            "total_columns": total_columns,
        }
        return json.dumps(output, indent=2, default=str)

    except Exception as e:
        error_output = {
            "tool_call_id": tool_call_id,
            "error": f"Error generating data summary: {str(e)}",
        }
        return json.dumps(error_output, indent=2, default=str)


@mcp.prompt()
def analyze_data_prompt(table_name: str, analysis_type: str = "summary") -> str:
    """
    Generate a prompt for analyzing data in a specific table.

    Args:
        table_name: Name of the table to analyze
        analysis_type: Type of analysis (summary, trends, insights, etc.)
    """
    if table_name not in _loaded_tables:
        available_tables = list(_loaded_tables.keys())
        return f"Table '{table_name}' not found. Available tables: {available_tables}"

    return f"""Please analyze the data in table '{table_name}' and provide a {analysis_type}.

Available analysis types:
- summary: Basic statistics and data overview
- trends: Identify patterns and trends in the data
- insights: Generate business insights from the data
- quality: Assess data quality and identify issues

Use the execute_sql_query tool to explore the data and provide your analysis."""


# Cleanup function to be called on server shutdown
def cleanup() -> None:
    """Cleanup function to close database connection and remove temporary files"""
    global _db_connection, _db_path

    if _db_connection:
        _db_connection.close()

    if _db_path and os.path.exists(_db_path):
        try:
            os.unlink(_db_path)
        except Exception:
            pass  # Ignore errors during cleanup


def main() -> None:
    """Main entry point for the MCP server"""
    import argparse
    import atexit

    atexit.register(cleanup)

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="CSV Database MCP Server - Analyze CSV files with AI assistance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start server and immediately analyze CSV files in a folder
  mcp-csv-database --csv-folder /path/to/data

  # Start with custom table prefix
  mcp-csv-database --csv-folder ./sales_data --table-prefix sales_

  # Start with HTTP transport for remote access
  mcp-csv-database --csv-folder ./data --transport sse --port 8080

Available analysis tools once started:
  • get_data_summary(table_name) - Comprehensive data overview
  • get_column_stats(table_name, column_name) - Detailed column analysis
  • analyze_missing_data(table_name) - Data quality assessment
  • find_duplicates(table_name) - Duplicate detection
  • execute_sql_query(query) - Custom SQL analysis
        """,
    )
    parser.add_argument(
        "folder_path",
        nargs="?",
        help="Path to folder containing CSV files to analyze (recommended)",
    )
    parser.add_argument(
        "--csv-folder",
        type=str,
        help="Alternative way to specify CSV folder path",
    )
    parser.add_argument(
        "--table-prefix",
        type=str,
        default="",
        help="Optional prefix for table names (e.g., 'sales_')",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport type: stdio (local), sse or streamable-http (remote)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=3000,
        help="Port for HTTP transport (default: 3000)",
    )

    args = parser.parse_args()

    print("🗃️  CSV Database MCP Server - Analyze CSV files with AI assistance")

    # Determine CSV folder from positional argument or flag
    csv_folder_path = args.folder_path or args.csv_folder

    # Auto-load CSV files if folder specified
    if csv_folder_path:
        print(f"📁 Auto-loading CSV files from: {csv_folder_path}")
        result = load_csv_folder(csv_folder_path, args.table_prefix)
        print(result)
        print()
        print("✅ Ready for data analysis! Your CSV files are loaded and ready.")
    else:
        print("💡 Tip: For instant analysis, restart with a CSV folder:")
        print("   mcp-csv-database /path/to/your/csv/files")
        print()

    print("Ready to load CSV files and execute SQL queries!")
    print("\nAvailable tools:")
    print("- load_csv_folder: Load CSV files from a folder")
    print("- execute_sql_query: Run SQL queries on loaded data")
    print("- get_data_summary: Get comprehensive data overview")
    print("- get_column_stats: Statistical analysis for specific columns")
    print("- analyze_missing_data: Analyze missing data patterns")
    print("- find_duplicates: Find duplicate rows in tables")
    print("- get_table_info: Get detailed table information")
    print("- get_database_schema: View database schema")
    print("- list_loaded_tables: List loaded tables")
    print("- clear_database: Clear all loaded data")

    # Run the server with specified transport
    if args.transport == "stdio":
        mcp.run()
    elif args.transport == "sse":
        mcp.run(transport="sse")
    elif args.transport == "streamable-http":
        mcp.run(transport="streamable-http")


# Main execution
if __name__ == "__main__":
    main()
