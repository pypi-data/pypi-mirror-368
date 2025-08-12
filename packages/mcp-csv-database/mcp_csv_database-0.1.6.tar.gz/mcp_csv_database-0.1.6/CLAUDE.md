# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server that provides tools for loading CSV files into a temporary SQLite database and executing SQL queries on the data. The server is built using FastMCP framework and provides a comprehensive set of tools for data analysis.

## Development Commands

### Installation and Setup
```bash
# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Install from source
pip install -e .
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/mcp_csv_database

# Run specific test file
pytest tests/test_server.py

# Run with verbose output
pytest -v
```

### Code Quality
```bash
# Format code with black (line length: 100)
black src/ tests/ examples/

# Sort imports with isort
isort src/ tests/ examples/

# Lint with flake8
flake8 src/ tests/ examples/

# Type checking with mypy
mypy src/
```

### Running the Server
```bash
# Basic stdio transport
mcp-csv-database

# With auto-loading CSV files
mcp-csv-database --csv-folder /path/to/csv/files

# With different transports
mcp-csv-database --transport sse --port 8080
mcp-csv-database --transport streamable-http --port 8080

# Run module directly for development
python -m mcp_csv_database.server --csv-folder ./examples/sample_data
```

## Code Architecture

### Core Components

**Main Server File** (`src/mcp_csv_database/server.py`):
- Single-file MCP server implementation using FastMCP framework
- Global state management with `_db_connection`, `_loaded_tables`, `_db_path`
- Automatic CSV separator detection (tries `;`, `,`, `\t`)
- Temporary SQLite database creation and management
- Built-in cleanup functionality with `atexit` handlers

**Key MCP Tools**:
- `load_csv_folder()`: Loads CSV files from directory into SQLite
- `execute_sql_query()`: Executes SQL queries with automatic JSON formatting
- `get_database_schema()`: Returns complete database schema information
- `get_table_info()`: Detailed information about specific tables
- `export_table_to_csv()`: Exports query results back to CSV
- `create_index()`: Creates database indexes for performance
- `backup_database()`: Creates SQLite database backups

### Data Flow Architecture

1. **CSV Loading**: Multi-separator detection → pandas DataFrame → SQLite tables
2. **Query Execution**: SQL input → sqlite3 cursor → JSON formatted results
3. **Schema Management**: PRAGMA queries → formatted schema information
4. **Export Pipeline**: SQLite → pandas → CSV with customizable separators

### Global State Management

The server maintains global state through module-level variables:
- `_db_connection`: Active SQLite connection
- `_loaded_tables`: Dictionary mapping table names to source CSV paths
- `_db_path`: Path to temporary database file

### Error Handling Patterns

- Graceful CSV loading with separator fallback
- Comprehensive SQL error reporting
- Database state validation before operations
- Automatic cleanup on server shutdown

## MCP Integration

**Transport Support**: stdio (default), sse, streamable-http
**Tool Registration**: Uses `@mcp.tool()` decorator for automatic registration
**Prompt Integration**: Includes `@mcp.prompt()` for data analysis prompts

## Testing Strategy

The test suite (`tests/test_server.py`) uses:
- `pytest` with fixtures for temporary data creation
- Comprehensive coverage of all MCP tools
- JSON parsing validation for query results
- Cleanup verification and state management testing

## Development Notes

- Line length limit: 100 characters (configured in pyproject.toml)
- Type hints required for all public functions
- Test coverage requirement: 80% minimum
- CSV separator detection supports European (`;`) and US (`,`) formats
- Database files are created in system temp directory with automatic cleanup