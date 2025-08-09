"""
DoorDash MCP Server

An MCP server that provides DoorDash food ordering functionality.
"""

__version__ = "2.4.0"

from .server import main, mcp

__all__ = ["main", "mcp"]