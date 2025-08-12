# MCP CSV Database Server

A Model Context Protocol (MCP) server that provides comprehensive tools for loading CSV files into a temporary SQLite database and performing advanced data analysis with AI assistance.

## Features

- **Smart CSV Loading**: Automatically detect CSV separators and load multiple files from a folder
- **Advanced SQL Queries**: Execute any SQL query with automatic result formatting and pagination
- **Schema Inspection**: View database schema, table structures, and relationships
- **Data Quality Analysis**: Comprehensive missing data analysis, duplicate detection, and data profiling
- **Statistical Analysis**: Column statistics, data summaries, and distribution analysis
- **Export Capabilities**: Export query results or tables back to CSV with custom formatting
- **Performance Tools**: Create indexes, analyze query execution plans, and optimize performance
- **AI-Ready**: Designed for seamless integration with AI assistants for data analysis workflows

## Installation

### From PyPI

```bash
pip install mcp-csv-database
```

### From source

```bash
git clone https://github.com/Lasitha-Jayawardana/mcp-csv-database.git
cd mcp-csv-database
pip install -e .
```

## Usage

### Command Line

Start the server with stdio transport:

```bash
mcp-csv-database
```

**Recommended**: Auto-load CSV files from a folder using positional argument:

```bash
mcp-csv-database /path/to/csv/files
```

Alternative syntax with explicit flag:

```bash
mcp-csv-database --csv-folder /path/to/csv/files
```

With custom table prefix:

```bash
mcp-csv-database /path/to/csv/files --table-prefix sales_
```

For remote access with HTTP transport:

```bash
mcp-csv-database /path/to/csv/files --transport sse --port 8080
```

### Configuration

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "csv-database": {
      "command": "mcp-csv-database",
      "args": ["/path/to/your/csv/files"]
    }
  }
}
```

Alternative configuration with explicit options:

```json
{
  "mcpServers": {
    "csv-database": {
      "command": "mcp-csv-database",
      "args": ["--csv-folder", "/path/to/csv/files", "--table-prefix", "analytics_"]
    }
  }
}
```

## Available Tools

### Data Loading & Management
- `load_csv_folder(folder_path, table_prefix="")` - Load all CSV files from a folder with smart separator detection
- `list_loaded_tables()` - List currently loaded tables with source file information
- `clear_database()` - Clear all loaded data and temporary files
- `backup_database(backup_path)` - Create complete database backups

### Data Querying & Schema
- `execute_sql_query(query, limit=100)` - Execute any SQL query with automatic result formatting
- `get_database_schema()` - View complete database schema with column types and sample data
- `get_table_info(table_name)` - Get detailed information about specific tables
- `get_query_plan(query)` - Analyze query execution plans for performance optimization

### Data Quality & Analysis
- `get_data_summary(table_name)` - Comprehensive data overview with insights and data types
- `get_column_stats(table_name, column_name)` - Detailed statistical analysis for specific columns
- `analyze_missing_data(table_name)` - Complete missing data analysis across all columns
- `find_duplicates(table_name, columns="all")` - Advanced duplicate detection with configurable column sets

### Performance & Export
- `create_index(table_name, column_name, index_name="")` - Create indexes for query optimization
- `export_table_to_csv(table_name, output_path, include_header=True)` - Export tables with custom formatting

## Examples

### Basic Usage

```python
# Load CSV files
result = load_csv_folder("/path/to/csv/files")

# View what's loaded
schema = get_database_schema()

# Query the data
result = execute_sql_query("SELECT * FROM my_table LIMIT 10")

# Export results
export_table_to_csv("my_table", "/path/to/output.csv")
```

### Advanced Data Analysis

```python
# Get comprehensive data overview
summary = get_data_summary("sales_data")

# Detailed statistical analysis for specific columns
price_stats = get_column_stats("sales_data", "price")
quantity_stats = get_column_stats("sales_data", "quantity")

# Data quality assessment
missing_analysis = analyze_missing_data("sales_data")
duplicates = find_duplicates("sales_data", "customer_id,product")

# Complex analytical queries
result = execute_sql_query("""
    SELECT 
        category,
        COUNT(*) as count,
        AVG(price) as avg_price,
        SUM(quantity) as total_quantity,
        MIN(price) as min_price,
        MAX(price) as max_price,
        STDDEV(price) as price_stddev
    FROM sales_data 
    GROUP BY category
    ORDER BY total_quantity DESC
""")

# Performance optimization
create_index("sales_data", "category")
query_plan = get_query_plan("SELECT * FROM sales_data WHERE category = 'Electronics'")
```

### Data Quality Workflow

```python
# Step 1: Load and inspect data
load_csv_folder("/path/to/data")
schema = get_database_schema()

# Step 2: Data quality assessment
missing_data = analyze_missing_data("customers")
duplicates = find_duplicates("customers", "email")
summary = get_data_summary("customers")

# Step 3: Statistical analysis
age_stats = get_column_stats("customers", "age") 
income_stats = get_column_stats("customers", "income")

# Step 4: Clean and analyze
clean_data = execute_sql_query("""
    SELECT customer_id, name, email, city, age, income
    FROM customers 
    WHERE email IS NOT NULL 
    AND age BETWEEN 18 AND 100
    AND income > 0
""")
```

## Transport Options

The server supports multiple transport methods:

- `stdio` (default): Standard input/output
- `sse`: Server-sent events
- `streamable-http`: HTTP streaming

```bash
# SSE transport
mcp-csv-database --transport sse --port 8080

# HTTP transport  
mcp-csv-database --transport streamable-http --port 8080
```

## Requirements

- Python 3.10+ (required for MCP framework compatibility)
- pandas >= 1.3.0
- sqlite3 (built-in)
- mcp >= 1.0.0

## CLI Reference

```bash
mcp-csv-database [folder_path] [OPTIONS]

# Positional Arguments:
#   folder_path              Path to folder containing CSV files (recommended)

# Options:
#   --csv-folder PATH        Alternative way to specify CSV folder path
#   --table-prefix PREFIX    Optional prefix for table names (e.g., 'sales_')
#   --transport TYPE         Transport type: stdio (default), sse, streamable-http
#   --port PORT             Port for HTTP transport (default: 3000)
#   -h, --help              Show help message and exit

# Examples:
mcp-csv-database /data/sales                          # Load CSV files from /data/sales
mcp-csv-database --csv-folder /data --table-prefix t_ # Load with table prefix
mcp-csv-database /data --transport sse --port 8080    # HTTP transport on port 8080
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v0.1.3 (Latest)
- Enhanced CLI interface with positional argument support for CSV folder paths
- Improved command-line help with comprehensive examples and tool descriptions
- Fixed mypy type checking and added pandas-stubs for better development experience
- Resolved GitHub Actions CI/CD pipeline configuration issues
- Updated Python requirement to 3.10+ for MCP framework compatibility

### v0.1.2
- Added comprehensive data analysis tools: `get_data_summary()`, `get_column_stats()`, `analyze_missing_data()`, `find_duplicates()`
- Enhanced statistical analysis capabilities with numeric data detection
- Improved data quality assessment and missing data visualization
- Added advanced duplicate detection with configurable column sets
- Enhanced table information display with better formatting

### v0.1.1
- Improved CSV separator auto-detection (semicolon, comma, tab)
- Enhanced error handling and user feedback
- Better table naming with special character handling
- Added comprehensive test coverage
- Improved documentation and examples

### v0.1.0
- Initial release
- Basic CSV loading and SQL querying
- Schema inspection tools
- Data export capabilities
- Multiple transport support