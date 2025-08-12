# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure for open source distribution
- Comprehensive test suite with pytest
- Development tools configuration (black, isort, flake8, mypy)
- Example usage scripts
- Contributing guidelines

## [0.1.0] - 2024-01-XX

### Added
- Initial release of MCP CSV Database Server
- CSV file loading with automatic separator detection
- SQLite database creation and management
- SQL query execution with JSON-formatted results
- Database schema inspection tools
- Table information and statistics
- Index creation for query performance
- Database backup functionality
- CSV export capabilities
- Query execution plan analysis
- Multiple transport support (stdio, SSE, HTTP)
- Command-line interface with configurable options
- Automatic cleanup of temporary files
- Support for table name prefixes
- Comprehensive error handling
- Data analysis prompt template

### Features
- **File Loading**: Load multiple CSV files from a folder with automatic separator detection
- **SQL Queries**: Execute any SQL query (SELECT, INSERT, UPDATE, DELETE, CREATE, etc.)
- **Schema Tools**: View database schema, table information, and column details
- **Performance**: Create indexes and analyze query execution plans
- **Export**: Export tables back to CSV format
- **Transport**: Support for stdio, SSE, and HTTP transports
- **CLI**: Command-line interface with auto-loading capabilities

### Technical Details
- Built with FastMCP framework
- Uses pandas for CSV processing
- SQLite for in-memory database operations
- Temporary file management with automatic cleanup
- JSON-formatted query results
- Comprehensive error handling and validation