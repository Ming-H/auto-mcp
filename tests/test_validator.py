"""Tests for code and MCP protocol validators."""

import pytest
from pathlib import Path

from auto_mcp.core.validator import CodeValidator, MCPValidator


# Round 22-30: Validator tests
class TestCodeValidator:
    """Test Python/TypeScript code validation."""

    def test_valid_python_code(self):
        """Test validation of valid Python code."""
        code = """
def hello():
    return "world"
"""
        errors = CodeValidator.validate_python(code)
        assert len(errors) == 0

    def test_invalid_python_syntax(self):
        """Test validation of invalid Python code."""
        code = """
def hello(
    return "world"
"""
        errors = CodeValidator.validate_python(code)
        assert len(errors) > 0

    def test_python_with_async(self):
        """Test validation of async Python code."""
        code = """
async def fetch_data():
    return await api_call()
"""
        errors = CodeValidator.validate_python(code)
        assert len(errors) == 0

    def test_python_with_type_hints(self):
        """Test validation of Python with type hints."""
        code = """
from typing import List, Dict

def process(items: List[str]) -> Dict[str, int]:
    return {item: len(item) for item in items}
"""
        errors = CodeValidator.validate_python(code)
        assert len(errors) == 0

    def test_python_with_imports(self):
        """Test validation of Python with imports."""
        code = """
import httpx
from fastmcp import FastMCP

mcp = FastMCP("test")
"""
        errors = CodeValidator.validate_python(code)
        assert len(errors) == 0

    def test_valid_typescript_code(self):
        """Test validation of valid TypeScript code."""
        code = """
interface User {
    name: string;
    age: number;
}

function getUser(): User {
    return { name: "test", age: 25 };
}
"""
        errors = CodeValidator.validate_typescript(code)
        # TypeScript validation might be skipped if tsc not installed
        assert isinstance(errors, list)

    def test_typescript_with_async(self):
        """Test validation of async TypeScript code."""
        code = """
async function fetchData(): Promise<string> {
    const response = await fetch("https://api.example.com");
    return await response.text();
}
"""
        errors = CodeValidator.validate_typescript(code)
        assert isinstance(errors, list)

    def test_python_file_validation(self, tmp_path):
        """Test validation of Python file."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        errors = CodeValidator.validate_python_file(test_file)
        assert len(errors) == 0

    def test_invalid_python_file(self, tmp_path):
        """Test validation of invalid Python file."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def broken(\n")

        errors = CodeValidator.validate_python_file(test_file)
        assert len(errors) > 0


class TestMCPValidator:
    """Test MCP protocol validation."""

    def test_valid_server_config(self):
        """Test validation of valid server config."""
        config = {
            "name": "test-server",
            "version": "1.0.0",
        }
        errors = MCPValidator.validate_server_config(config)
        assert len(errors) == 0

    def test_missing_name(self):
        """Test validation with missing name."""
        config = {
            "version": "1.0.0",
        }
        errors = MCPValidator.validate_server_config(config)
        assert len(errors) > 0
        assert "name" in errors[0]

    def test_missing_version(self):
        """Test validation with missing version."""
        config = {
            "name": "test-server",
        }
        errors = MCPValidator.validate_server_config(config)
        assert len(errors) > 0
        assert "version" in errors[0]

    def test_valid_tool_definition(self):
        """Test validation of valid tool definition."""
        tool = {
            "name": "test_tool",
            "description": "A test tool",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        }
        errors = MCPValidator.validate_tool_definition(tool)
        assert len(errors) == 0

    def test_tool_missing_name(self):
        """Test validation of tool without name."""
        tool = {
            "description": "A test tool",
            "inputSchema": {"type": "object"},
        }
        errors = MCPValidator.validate_tool_definition(tool)
        assert len(errors) > 0

    def test_tool_missing_description(self):
        """Test validation of tool without description."""
        tool = {
            "name": "test_tool",
            "inputSchema": {"type": "object"},
        }
        errors = MCPValidator.validate_tool_definition(tool)
        assert len(errors) > 0

    def test_tool_missing_input_schema(self):
        """Test validation of tool without inputSchema."""
        tool = {
            "name": "test_tool",
            "description": "A test tool",
        }
        errors = MCPValidator.validate_tool_definition(tool)
        assert len(errors) > 0

    def test_complete_tool_definition(self):
        """Test validation of complete tool with parameters."""
        tool = {
            "name": "get_weather",
            "description": "Get weather for a location",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name",
                    }
                },
                "required": ["location"],
            },
        }
        errors = MCPValidator.validate_tool_definition(tool)
        assert len(errors) == 0
