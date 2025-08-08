# coffy/sql/__init__.py
# author: nsarathy

from .engine import execute_query, initialize, close_connection


def init(path: str = None):
    """Initialize the SQL engine with the given path."""
    initialize(path)


def query(sql: str):
    """Execute a SQL query and return the results."""
    return execute_query(sql)


def close():
    """Close the database connection."""
    close_connection()


__all__ = ["init", "query", "close"]
