"""Undoom Uninstaller MCP - A Windows program uninstaller MCP server."""

__version__ = "0.1.5"
__author__ = "Undoom"
__email__ = "kaikaihuhu666@163.com"

from .server import main, cli_main

__all__ = ["main", "cli_main"]