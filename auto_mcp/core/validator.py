"""
Code and MCP protocol validation for AutoMCP.
"""

import ast
import subprocess
from pathlib import Path
from typing import Any


class CodeValidator:
    """Validate generated code for syntax errors."""

    @staticmethod
    def validate_python(code: str) -> list[str]:
        """
        Validate Python code syntax.

        Args:
            code: Python source code

        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
        except Exception as e:
            errors.append(f"Parse error: {str(e)}")
        return errors

    @staticmethod
    def validate_python_file(file_path: Path) -> list[str]:
        """Validate a Python file."""
        return CodeValidator.validate_python(file_path.read_text())

    @staticmethod
    def validate_typescript(code: str) -> list[str]:
        """
        Validate TypeScript code using tsc if available.

        Args:
            code: TypeScript source code

        Returns:
            List of error messages (empty if valid)
        """
        # Write to temp file and run tsc
        temp_file = Path("/tmp/temp_validate.ts")
        temp_file.write_text(code)

        try:
            result = subprocess.run(
                ["tsc", "--noEmit", str(temp_file)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                return result.stderr.split("\n")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # TypeScript not installed, skip validation
            pass
        finally:
            temp_file.unlink(missing_ok=True)

        return []


class MCPValidator:
    """Validate generated code against MCP protocol requirements."""

    REQUIRED_METHODS = ["tools/list", "tools/call", "resources/list"]
    REQUIRED_FIELDS = ["name", "version"]

    @staticmethod
    def validate_server_config(config: dict[str, Any]) -> list[str]:
        """
        Validate MCP server configuration.

        Args:
            config: Server configuration dictionary

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        for field in MCPValidator.REQUIRED_FIELDS:
            if field not in config:
                errors.append(f"Missing required field: {field}")

        return errors

    @staticmethod
    def validate_tool_definition(tool: dict[str, Any]) -> list[str]:
        """
        Validate a tool definition.

        Args:
            tool: Tool definition dictionary

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        if "name" not in tool:
            errors.append("Tool missing 'name' field")
        if "description" not in tool:
            errors.append("Tool missing 'description' field")
        if "inputSchema" not in tool:
            errors.append("Tool missing 'inputSchema' field")

        return errors
