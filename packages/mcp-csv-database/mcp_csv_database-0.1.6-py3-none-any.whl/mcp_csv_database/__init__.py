"""
MCP CSV Database Server

A Model Context Protocol (MCP) server that provides tools for loading CSV files
into a temporary SQLite database and executing SQL queries on the data.
"""

__version__ = "0.1.3"
__author__ = "Lasitha"
__email__ = "lasitha.work@gmail.com"
__description__ = "MCP server for CSV files analysing and SQL querying"

from .server import main

__all__ = ["main"]
