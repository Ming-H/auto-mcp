"""
AutoMCP - Automatic MCP Server Generator

Generate Model Context Protocol (MCP) servers from API documentation.
"""

__version__ = "0.1.0"

from auto_mcp.core.generator import PythonMCPGenerator, TypeScriptMCPGenerator
from auto_mcp.core.parser import OpenAPIParser
from auto_mcp.core.types import APISpec, Endpoint, MCPServerConfig

__all__ = [
    "__version__",
    "APISpec",
    "Endpoint",
    "MCPServerConfig",
    "OpenAPIParser",
    "PythonMCPGenerator",
    "TypeScriptMCPGenerator",
]
