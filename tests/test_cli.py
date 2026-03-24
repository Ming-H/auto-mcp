"""Tests for CLI functionality."""

from pathlib import Path
import tempfile
import yaml
import json
from click.testing import CliRunner

from auto_mcp.cli import main


# Round 31-40: CLI tests
class TestCLI:
    """Test command-line interface."""

    def test_cli_version(self):
        """Test CLI version command."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_cli_help(self):
        """Test CLI help command."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "AutoMCP" in result.output
        assert "generate" in result.output
        assert "validate" in result.output
        assert "init" in result.output

    def test_init_command(self):
        """Test init command creates project structure."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir) / "test-project"
            result = runner.invoke(main, ["init", str(project_path)])

            assert result.exit_code == 0
            assert project_path.exists()
            assert (project_path / "spec.yaml").exists()
            assert (project_path / "README.md").exists()

    def test_generate_without_source(self):
        """Test generate command without spec or URL."""
        runner = CliRunner()
        result = runner.invoke(main, ["generate"])

        assert result.exit_code != 0
        assert "Error" in result.output

    def test_generate_with_yaml_spec(self):
        """Test generate command with YAML spec file."""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0",
                "description": "Test API for CLI"
            },
            "paths": {
                "/test": {
                    "get": {
                        "operationId": "test_endpoint",
                        "summary": "Test endpoint",
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }

        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            spec_file = Path(tmpdir) / "spec.yaml"
            spec_file.write_text(yaml.dump(spec))

            output_dir = Path(tmpdir) / "output"
            result = runner.invoke(main, [
                "generate",
                "--spec", str(spec_file),
                "--output", str(output_dir),
                "--lang", "python"
            ])

            assert result.exit_code == 0
            assert output_dir.exists()
            assert (output_dir / "test_api" / "server.py").exists()

    def test_generate_with_json_spec(self):
        """Test generate command with JSON spec file."""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "JSON Test API",
                "version": "1.0.0",
            },
            "paths": {
                "/data": {
                    "get": {
                        "operationId": "get_data",
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }

        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            spec_file = Path(tmpdir) / "spec.json"
            spec_file.write_text(json.dumps(spec))

            output_dir = Path(tmpdir) / "output"
            result = runner.invoke(main, [
                "generate",
                "--spec", str(spec_file),
                "--output", str(output_dir),
                "--lang", "python"
            ])

            assert result.exit_code == 0
            assert output_dir.exists()

    def test_generate_typescript(self):
        """Test generate command with TypeScript language."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "TS API", "version": "1.0.0"},
            "paths": {
                "/items": {
                    "get": {
                        "operationId": "list_items",
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }

        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            spec_file = Path(tmpdir) / "spec.yaml"
            spec_file.write_text(yaml.dump(spec))

            output_dir = Path(tmpdir) / "output"
            result = runner.invoke(main, [
                "generate",
                "--spec", str(spec_file),
                "--output", str(output_dir),
                "--lang", "typescript"
            ])

            assert result.exit_code == 0
            assert (output_dir / "src" / "index.ts").exists()

    def test_generate_custom_name(self):
        """Test generate command with custom name."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Original Name", "version": "1.0.0"},
            "paths": {}
        }

        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            spec_file = Path(tmpdir) / "spec.yaml"
            spec_file.write_text(yaml.dump(spec))

            output_dir = Path(tmpdir) / "output"
            result = runner.invoke(main, [
                "generate",
                "--spec", str(spec_file),
                "--output", str(output_dir),
                "--name", "custom-name"
            ])

            assert result.exit_code == 0
            assert (output_dir / "custom_name" / "server.py").exists()

    def test_validate_command_valid_python(self):
        """Test validate command with valid Python project."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a simple Python project
            project_dir = Path(tmpdir) / "test_project"
            project_dir.mkdir()
            (project_dir / "pyproject.toml").write_text("[tool.poetry]\nname = \"test\"\n")
            (project_dir / "test.py").write_text("def hello():\n    return 'world'")

            result = runner.invoke(main, ["validate", str(project_dir)])
            assert result.exit_code == 0
            assert "No validation errors" in result.output

    def test_validate_command_invalid_python(self):
        """Test validate command with invalid Python code."""
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a Python project with syntax error
            project_dir = Path(tmpdir) / "bad_project"
            project_dir.mkdir()
            (project_dir / "pyproject.toml").write_text("[tool.poetry]\nname = \"test\"\n")
            (project_dir / "test.py").write_text("def broken(\n")

            result = runner.invoke(main, ["validate", str(project_dir)])
            assert result.exit_code == 0
            assert "errors" in result.output.lower() or "error" in result.output.lower()


# Round 41-50: Edge case tests
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_paths(self):
        """Test parsing spec with empty paths."""
        from auto_mcp.core.parser import OpenAPIParser

        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Empty API", "version": "1.0.0"},
            "paths": {}
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        endpoints = parser.extract_endpoints()

        assert len(endpoints) == 0

    def test_missing_operation_id(self):
        """Test endpoints without operationId."""
        from auto_mcp.core.parser import OpenAPIParser

        spec = {
            "openapi": "3.0.0",
            "info": {"title": "No OpID API", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        endpoints = parser.extract_endpoints()

        assert len(endpoints) == 1
        assert "operation_id" in endpoints[0]

    def test_no_servers(self):
        """Test spec without servers section."""
        from auto_mcp.core.parser import OpenAPIParser

        spec = {
            "openapi": "3.0.0",
            "info": {"title": "No Servers API", "version": "1.0.0"},
            "paths": {}
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        api_spec = parser.to_api_spec()

        assert api_spec["base_url"] is None

    def test_multiple_servers(self):
        """Test spec with multiple servers."""
        from auto_mcp.core.parser import OpenAPIParser

        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Multi Server API", "version": "1.0.0"},
            "servers": [
                {"url": "https://api1.example.com"},
                {"url": "https://api2.example.com"}
            ],
            "paths": {}
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        api_spec = parser.to_api_spec()

        assert api_spec["base_url"] == "https://api1.example.com"

    def test_parameter_without_schema(self):
        """Test parameter without schema field."""
        from auto_mcp.core.parser import OpenAPIParser

        spec = {
            "openapi": "3.0.0",
            "info": {"title": "No Schema API", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "parameters": [
                            {
                                "name": "param1",
                                "in": "query"
                            }
                        ],
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        endpoints = parser.extract_endpoints()

        assert len(endpoints) == 1
        assert len(endpoints[0]["parameters"]) == 1
        assert endpoints[0]["parameters"][0]["type"] == "string"  # default

    def test_response_without_content(self):
        """Test response without content field."""
        from auto_mcp.core.parser import OpenAPIParser

        spec = {
            "openapi": "3.0.0",
            "info": {"title": "No Content API", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "responses": {
                            "204": {"description": "No Content"}
                        }
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        endpoints = parser.extract_endpoints()

        assert len(endpoints) == 1
        assert "204" in endpoints[0]["responses"]

    def test_endpoint_without_responses(self):
        """Test endpoint without responses."""
        from auto_mcp.core.parser import OpenAPIParser

        spec = {
            "openapi": "3.0.0",
            "info": {"title": "No Response API", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "operationId": "test_no_response"
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        endpoints = parser.extract_endpoints()

        assert len(endpoints) == 1
        assert endpoints[0]["operation_id"] == "test_no_response"

    def test_swagger_2_compatibility(self):
        """Test Swagger 2.0 spec compatibility."""
        from auto_mcp.core.parser import OpenAPIParser

        spec = {
            "swagger": "2.0",
            "info": {"title": "Swagger 2 API", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "operationId": "test_swagger",
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        # Should accept Swagger 2.0
        parser.parse()
        assert parser._raw_spec["swagger"] == "2.0"

    def test_unsupported_version(self):
        """Test rejection of unsupported OpenAPI version."""
        from auto_mcp.core.parser import OpenAPIParser
        import pytest

        spec = {
            "openapi": "1.0.0",
            "info": {"title": "Old API", "version": "1.0.0"},
            "paths": {}
        }

        parser = OpenAPIParser(spec)
        with pytest.raises(ValueError, match="Unsupported"):
            parser.parse()
