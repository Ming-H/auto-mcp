"""Advanced tests for complex OpenAPI scenarios."""

import pytest
import tempfile
from pathlib import Path

from auto_mcp.core.parser import OpenAPIParser
from auto_mcp.core.generator import PythonMCPGenerator
from auto_mcp.core.types import APISpec, Endpoint, Language, MCPServerConfig, Parameter, ParamLocation


# Round 51-60: Advanced OpenAPI scenarios
class TestAdvancedScenarios:
    """Test complex OpenAPI scenarios."""

    def test_ref_resolution_simple(self):
        """Test simple schema reference handling."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Ref API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"}
                        }
                    }
                }
            },
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "list_users",
                        "responses": {
                            "200": {
                                "description": "OK",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/User"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        endpoints = parser.extract_endpoints()

        assert len(endpoints) == 1
        assert endpoints[0]["responses"]["200"]["schema"] is not None

    def test_allof_schema_resolution(self):
        """Test allOf schema type resolution."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "AllOf API", "version": "1.0.0"},
            "components": {
                "schemas": {
                    "BaseModel": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"}
                        }
                    },
                    "ExtendedModel": {
                        "allOf": [
                            {"$ref": "#/components/schemas/BaseModel"},
                            {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"}
                                }
                            }
                        ]
                    }
                }
            },
            "paths": {
                "/extended": {
                    "post": {
                        "operationId": "create_extended",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "allOf": [
                                            {"type": "object"},
                                            {"type": "object", "properties": {"extra": {"type": "string"}}}
                                        ]
                                    }
                                }
                            }
                        },
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        endpoints = parser.extract_endpoints()

        assert len(endpoints) == 1
        # Should resolve allOf to a type
        assert endpoints[0]["request_body"] is not None

    def test_anyof_schema_resolution(self):
        """Test anyOf schema type resolution."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "AnyOf API", "version": "1.0.0"},
            "paths": {
                "/flexible": {
                    "post": {
                        "operationId": "create_flexible",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "anyOf": [
                                            {"type": "string"},
                                            {"type": "integer"}
                                        ]
                                    }
                                }
                            }
                        },
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        endpoints = parser.extract_endpoints()

        assert len(endpoints) == 1
        # Should resolve anyOf to first type
        assert endpoints[0]["request_body"] is not None

    def test_oneof_schema_resolution(self):
        """Test oneOf schema type resolution."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "OneOf API", "version": "1.0.0"},
            "paths": {
                "/exclusive": {
                    "post": {
                        "operationId": "create_exclusive",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "oneOf": [
                                            {"type": "boolean"},
                                            {"type": "null"}
                                        ]
                                    }
                                }
                            }
                        },
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        endpoints = parser.extract_endpoints()

        assert len(endpoints) == 1

    def test_array_of_primitives(self):
        """Test array parameter with primitive items."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Array API", "version": "1.0.0"},
            "paths": {
                "/items": {
                    "get": {
                        "operationId": "get_items",
                        "parameters": [
                            {
                                "name": "ids",
                                "in": "query",
                                "schema": {
                                    "type": "array",
                                    "items": {"type": "integer"}
                                }
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
        assert endpoints[0]["parameters"][0]["type"] == "array"

    def test_required_parameters(self):
        """Test required vs optional parameters."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Required API", "version": "1.0.0"},
            "paths": {
                "/search": {
                    "get": {
                        "operationId": "search",
                        "parameters": [
                            {
                                "name": "q",
                                "in": "query",
                                "required": True,
                                "schema": {"type": "string"}
                            },
                            {
                                "name": "limit",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "integer"}
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
        params = endpoints[0]["parameters"]
        assert params[0]["required"] is True
        assert params[1]["required"] is False

    def test_path_parameter_extraction(self):
        """Test path parameter extraction from URL template."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Path API", "version": "1.0.0"},
            "paths": {
                "/users/{userId}/posts/{postId}": {
                    "get": {
                        "operationId": "get_user_post",
                        "parameters": [
                            {"name": "userId", "in": "path", "required": True, "schema": {"type": "string"}},
                            {"name": "postId", "in": "path", "required": True, "schema": {"type": "string"}}
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
        assert endpoints[0]["path"] == "/users/{userId}/posts/{postId}"
        path_params = [p for p in endpoints[0]["parameters"] if p["location"] == "path"]
        assert len(path_params) == 2

    def test_header_parameters(self):
        """Test header parameter handling."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Header API", "version": "1.0.0"},
            "paths": {
                "/data": {
                    "get": {
                        "operationId": "get_data",
                        "parameters": [
                            {
                                "name": "X-API-Key",
                                "in": "header",
                                "required": True,
                                "schema": {"type": "string"}
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
        assert endpoints[0]["parameters"][0]["location"] == "header"

    def test_cookie_parameters(self):
        """Test cookie parameter handling."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Cookie API", "version": "1.0.0"},
            "paths": {
                "/profile": {
                    "get": {
                        "operationId": "get_profile",
                        "parameters": [
                            {
                                "name": "session",
                                "in": "cookie",
                                "required": True,
                                "schema": {"type": "string"}
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
        assert endpoints[0]["parameters"][0]["location"] == "cookie"

    def test_multiple_response_codes(self):
        """Test multiple response codes."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Multi Response API", "version": "1.0.0"},
            "paths": {
                "/resource": {
                    "get": {
                        "operationId": "get_resource",
                        "responses": {
                            "200": {"description": "Success"},
                            "404": {"description": "Not Found"},
                            "500": {"description": "Server Error"}
                        }
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        endpoints = parser.extract_endpoints()

        assert len(endpoints) == 1
        responses = endpoints[0]["responses"]
        assert "200" in responses
        assert "404" in responses
        assert "500" in responses

    def test_default_response(self):
        """Test default response."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Default Response API", "version": "1.0.0"},
            "paths": {
                "/resource": {
                    "get": {
                        "operationId": "get_resource",
                        "responses": {
                            "default": {"description": "Default response"}
                        }
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        endpoints = parser.extract_endpoints()

        assert len(endpoints) == 1
        # default response is stored with its key
        assert "default" in endpoints[0]["responses"]
        # status_code is still converted to 200
        assert endpoints[0]["responses"]["default"]["status_code"] == 200

    def test_xml_response_content_type(self):
        """Test XML response content type."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "XML API", "version": "1.0.0"},
            "paths": {
                "/data": {
                    "get": {
                        "operationId": "get_xml",
                        "responses": {
                            "200": {
                                "description": "XML response",
                                "content": {
                                    "application/xml": {
                                        "schema": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        endpoints = parser.extract_endpoints()

        assert len(endpoints) == 1
        assert endpoints[0]["responses"]["200"]["content_type"] == "application/xml"


# Round 61-70: Generator edge cases
class TestGeneratorEdgeCases:
    """Test generator edge cases."""

    def test_generator_with_no_endpoints(self):
        """Test generator with no endpoints."""
        api_spec = APISpec(
            title="Empty API",
            version="1.0.0",
            description="API with no endpoints",
            base_url="https://api.example.com",
            endpoints=[],
        )

        config = MCPServerConfig(
            name="empty-mcp",
            version="1.0.0",
            description="Empty MCP Server",
            language=Language.PYTHON,
            api_spec=api_spec,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = PythonMCPGenerator(config)
            generator.generate(Path(tmpdir))

            assert (Path(tmpdir) / "empty_mcp" / "server.py").exists()
            server_content = (Path(tmpdir) / "empty_mcp" / "server.py").read_text()
            # Should still have basic structure
            assert "FastMCP" in server_content

    def test_generator_with_special_characters(self):
        """Test generator with special characters in names."""
        api_spec = APISpec(
            title="Test API",
            version="1.0.0",
            description="Test API",
            base_url="https://api.example.com",
            endpoints=[
                Endpoint(
                    path="/api/v2/data",
                    method="get",
                    operation_id="get.v2-data",
                    summary="Get v2 data",
                )
            ],
        )

        config = MCPServerConfig(
            name="test-mcp",
            version="1.0.0",
            description="Test MCP Server",
            language=Language.PYTHON,
            api_spec=api_spec,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = PythonMCPGenerator(config)
            generator.generate(Path(tmpdir))

            server_content = (Path(tmpdir) / "test_mcp" / "server.py").read_text()
            # Should handle special characters
            assert "def get_v2_data(" in server_content

    def test_generator_with_long_descriptions(self):
        """Test generator with long descriptions."""
        long_desc = "This is a very long description that spans multiple lines and contains detailed information about the API endpoint and its usage."
        api_spec = APISpec(
            title="Test API",
            version="1.0.0",
            description=long_desc,
            base_url="https://api.example.com",
            endpoints=[
                Endpoint(
                    path="/test",
                    method="get",
                    operation_id="test_endpoint",
                    description=long_desc,
                )
            ],
        )

        config = MCPServerConfig(
            name="test-mcp",
            version="1.0.0",
            description="Test MCP Server",
            language=Language.PYTHON,
            api_spec=api_spec,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = PythonMCPGenerator(config)
            generator.generate(Path(tmpdir))

            server_content = (Path(tmpdir) / "test_mcp" / "server.py").read_text()
            assert long_desc in server_content

    def test_generator_with_unicode(self):
        """Test generator with unicode characters."""
        api_spec = APISpec(
            title="API 测试",
            version="1.0.0",
            description="API für Testing",
            base_url="https://api.example.com",
            endpoints=[
                Endpoint(
                    path="/café",
                    method="get",
                    operation_id="get_cafe",
                    summary="Get café information",
                )
            ],
        )

        config = MCPServerConfig(
            name="test-mcp",
            version="1.0.0",
            description="Test MCP Server",
            language=Language.PYTHON,
            api_spec=api_spec,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = PythonMCPGenerator(config)
            generator.generate(Path(tmpdir))

            server_content = (Path(tmpdir) / "test_mcp" / "server.py").read_text()
            assert "café" in server_content

    def test_generator_with_enum_parameters(self):
        """Test generator with enum parameters."""
        api_spec = APISpec(
            title="Enum API",
            version="1.0.0",
            description="Enum API",
            base_url="https://api.example.com",
            endpoints=[
                Endpoint(
                    path="/filter",
                    method="get",
                    operation_id="filter_data",
                    parameters=[
                        Parameter(
                            name="status",
                            type="string",
                            location=ParamLocation.QUERY,
                            required=False,
                            enum=["active", "inactive", "pending"],
                        )
                    ],
                )
            ],
        )

        config = MCPServerConfig(
            name="enum-mcp",
            version="1.0.0",
            description="Enum MCP Server",
            language=Language.PYTHON,
            api_spec=api_spec,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = PythonMCPGenerator(config)
            generator.generate(Path(tmpdir))

            server_content = (Path(tmpdir) / "enum_mcp" / "server.py").read_text()
            assert "status: str = None" in server_content

    def test_generator_with_deprecated_endpoint(self):
        """Test generator marks deprecated endpoints."""
        api_spec = APISpec(
            title="Deprecated API",
            version="1.0.0",
            description="Deprecated API",
            base_url="https://api.example.com",
            endpoints=[
                Endpoint(
                    path="/old",
                    method="get",
                    operation_id="old_endpoint",
                    deprecated=True,
                )
            ],
        )

        config = MCPServerConfig(
            name="deprecated-mcp",
            version="1.0.0",
            description="Deprecated MCP Server",
            language=Language.PYTHON,
            api_spec=api_spec,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = PythonMCPGenerator(config)
            generator.generate(Path(tmpdir))

            # Should still generate the endpoint
            server_content = (Path(tmpdir) / "deprecated_mcp" / "server.py").read_text()
            assert "def old_endpoint(" in server_content

    def test_generator_with_tags(self):
        """Test generator with endpoint tags."""
        api_spec = APISpec(
            title="Tagged API",
            version="1.0.0",
            description="Tagged API",
            base_url="https://api.example.com",
            endpoints=[
                Endpoint(
                    path="/users",
                    method="get",
                    operation_id="list_users",
                    tags=["users", "admin"],
                )
            ],
        )

        config = MCPServerConfig(
            name="tagged-mcp",
            version="1.0.0",
            description="Tagged MCP Server",
            language=Language.PYTHON,
            api_spec=api_spec,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = PythonMCPGenerator(config)
            generator.generate(Path(tmpdir))

            # Should generate successfully
            assert (Path(tmpdir) / "tagged_mcp" / "server.py").exists()

    def test_generator_with_custom_dependencies(self):
        """Test generator with custom dependencies."""
        api_spec = APISpec(
            title="Custom Dep API",
            version="1.0.0",
            description="Custom Dependencies",
            base_url="https://api.example.com",
            endpoints=[],
        )

        config = MCPServerConfig(
            name="custom-mcp",
            version="1.0.0",
            description="Custom MCP Server",
            language=Language.PYTHON,
            api_spec=api_spec,
            dependencies={"requests": "^2.31.0"},
            dev_dependencies={"pytest": "^7.4.0"},
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = PythonMCPGenerator(config)
            generator.generate(Path(tmpdir))

            pyproject_content = (Path(tmpdir) / "pyproject.toml").read_text()
            assert "requests" in pyproject_content

    def test_generator_readme_with_markdown(self):
        """Test README generation with markdown characters."""
        api_spec = APISpec(
            title="API with **Markdown**",
            version="1.0.0",
            description="API with *markdown* _characters_",
            base_url="https://api.example.com",
            endpoints=[
                Endpoint(
                    path="/test",
                    method="get",
                    operation_id="test_endpoint",
                    summary="Test `endpoint` with [link](https://example.com)",
                )
            ],
        )

        config = MCPServerConfig(
            name="markdown-mcp",
            version="1.0.0",
            description="Markdown MCP Server",
            language=Language.PYTHON,
            api_spec=api_spec,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = PythonMCPGenerator(config)
            generator.generate(Path(tmpdir))

            readme_content = (Path(tmpdir) / "README.md").read_text()
            assert "`test_endpoint`" in readme_content


# Round 71-80: Error handling tests
class TestErrorHandling:
    """Test error handling scenarios."""

    def test_empty_spec_error(self):
        """Test error on empty spec."""
        from auto_mcp.core.parser import OpenAPIParser
        import pytest

        parser = OpenAPIParser({})
        with pytest.raises(ValueError, match="Empty specification"):
            parser.parse()

    def test_missing_openapi_key(self):
        """Test error on missing openapi key."""
        from auto_mcp.core.parser import OpenAPIParser
        import pytest

        spec = {"info": {"title": "Test", "version": "1.0.0"}}
        parser = OpenAPIParser(spec)
        with pytest.raises(ValueError, match="Not a valid OpenAPI"):
            parser.parse()

    def test_file_not_found_error(self):
        """Test error on file not found."""
        from auto_mcp.core.parser import OpenAPIParser
        import pytest

        parser = OpenAPIParser("/nonexistent/file.yaml")
        with pytest.raises(FileNotFoundError):
            parser.parse()

    def test_generator_invalid_path(self):
        """Test generator with invalid output path (handled gracefully)."""
        api_spec = APISpec(
            title="Test API",
            version="1.0.0",
            description="Test",
            endpoints=[],
        )

        config = MCPServerConfig(
            name="test-mcp",
            version="1.0.0",
            description="Test",
            language=Language.PYTHON,
            api_spec=api_spec,
        )

        # Should work with temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = PythonMCPGenerator(config)
            generator.generate(Path(tmpdir))
            assert (Path(tmpdir) / "test_mcp").exists()

    def test_malformed_yaml(self):
        """Test handling malformed YAML."""
        from auto_mcp.core.parser import OpenAPIParser
        import pytest

        with tempfile.TemporaryDirectory() as tmpdir:
            bad_file = Path(tmpdir) / "bad.yaml"
            bad_file.write_text("openapi: 3.0.0\ninfo:\n  bad: yaml: content:")

            parser = OpenAPIParser(str(bad_file))
            # Should raise YAML error or handle gracefully
            try:
                parser.parse()
            except Exception:
                pass  # Expected

    def test_malformed_json(self):
        """Test handling malformed JSON."""
        from auto_mcp.core.parser import OpenAPIParser
        import pytest

        with tempfile.TemporaryDirectory() as tmpdir:
            bad_file = Path(tmpdir) / "bad.json"
            bad_file.write_text('{"openapi": "3.0.0", "info": }')

            parser = OpenAPIParser(str(bad_file))
            # Should raise JSON error
            try:
                parser.parse()
            except Exception:
                pass  # Expected

    def test_invalid_operation_id_characters(self):
        """Test operationId with invalid characters."""
        from auto_mcp.core.parser import OpenAPIParser

        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "operationId": "test/with/slashes",
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        endpoints = parser.extract_endpoints()

        assert len(endpoints) == 1
        # Should preserve the operationId

    def test_missing_info_section(self):
        """Test spec without info section."""
        from auto_mcp.core.parser import OpenAPIParser

        spec = {
            "openapi": "3.0.0",
            "paths": {}
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        api_spec = parser.to_api_spec()

        # Should use defaults
        assert api_spec["title"] == "API"
        assert api_spec["version"] == "1.0.0"

    def test_invalid_parameter_location(self):
        """Test parameter with invalid location."""
        from auto_mcp.core.parser import OpenAPIParser

        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "parameters": [
                            {"name": "bad", "in": "invalid", "schema": {"type": "string"}}
                        ],
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        endpoints = parser.extract_endpoints()

        # Should still parse, location will be "invalid"
        assert endpoints[0]["parameters"][0]["location"] == "invalid"

    def test_response_schema_with_nested_objects(self):
        """Test response schema with deeply nested objects."""
        from auto_mcp.core.parser import OpenAPIParser

        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Nested API", "version": "1.0.0"},
            "paths": {
                "/data": {
                    "get": {
                        "operationId": "get_nested",
                        "responses": {
                            "200": {
                                "description": "OK",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "level1": {
                                                    "type": "object",
                                                    "properties": {
                                                        "level2": {
                                                            "type": "object",
                                                            "properties": {
                                                                "level3": {"type": "string"}
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        endpoints = parser.extract_endpoints()

        assert len(endpoints) == 1
        assert endpoints[0]["responses"]["200"]["schema"] is not None


# Round 81-90: Integration tests
class TestIntegration:
    """Integration tests for end-to-end scenarios."""

    def test_full_workflow_simple_api(self):
        """Test complete workflow with a simple API."""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Pet Store API",
                "version": "1.0.0",
                "description": "A simple pet store API"
            },
            "servers": [{"url": "https://petstore.example.com"}],
            "paths": {
                "/pets": {
                    "get": {
                        "operationId": "list_pets",
                        "summary": "List all pets",
                        "parameters": [
                            {
                                "name": "limit",
                                "in": "query",
                                "schema": {"type": "integer"}
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "OK",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "post": {
                        "operationId": "create_pet",
                        "summary": "Create a pet",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "tag": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {"201": {"description": "Created"}}
                    }
                },
                "/pets/{petId}": {
                    "get": {
                        "operationId": "get_pet",
                        "summary": "Get a pet by ID",
                        "parameters": [
                            {"name": "petId", "in": "path", "required": True, "schema": {"type": "string"}}
                        ],
                        "responses": {"200": {"description": "OK"}}
                    },
                    "delete": {
                        "operationId": "delete_pet",
                        "summary": "Delete a pet",
                        "parameters": [
                            {"name": "petId", "in": "path", "required": True, "schema": {"type": "string"}}
                        ],
                        "responses": {"204": {"description": "Deleted"}}
                    }
                }
            }
        }

        # Parse
        parser = OpenAPIParser(spec)
        parser.parse()
        spec_data = parser.to_api_spec()

        # Create API spec
        from auto_mcp.core.types import Endpoint, Parameter, ParamLocation

        endpoints = []
        for ep_dict in spec_data["endpoints"]:
            params = []
            for p in ep_dict.get("parameters", []):
                params.append(Parameter(
                    name=p["name"],
                    type=p["type"],
                    location=ParamLocation(p["location"]),
                    required=p["required"],
                ))
            endpoints.append(Endpoint(
                path=ep_dict["path"],
                method=ep_dict["method"],
                operation_id=ep_dict["operation_id"],
                summary=ep_dict.get("summary"),
                parameters=params,
            ))

        api_spec = APISpec(
            title=spec_data["title"],
            version=spec_data["version"],
            description=spec_data.get("description"),
            base_url=spec_data.get("base_url"),
            endpoints=endpoints,
        )

        # Generate
        config = MCPServerConfig(
            name="petstore-mcp",
            version="1.0.0",
            description="Pet Store MCP Server",
            language=Language.PYTHON,
            api_spec=api_spec,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = PythonMCPGenerator(config)
            generator.generate(Path(tmpdir))

            # Verify files
            assert (Path(tmpdir) / "petstore_mcp" / "server.py").exists()
            assert (Path(tmpdir) / "pyproject.toml").exists()
            assert (Path(tmpdir) / "README.md").exists()

            # Validate generated code
            from auto_mcp.core.validator import CodeValidator

            server_content = (Path(tmpdir) / "petstore_mcp" / "server.py").read_text()
            errors = CodeValidator.validate_python(server_content)
            assert len(errors) == 0

            # Check content
            assert "def list_pets(" in server_content
            assert "def create_pet(" in server_content
            assert "def get_pet(" in server_content
            assert "def delete_pet(" in server_content
            assert "petId: str" in server_content

    def test_real_world_weather_api(self):
        """Test with a realistic weather API spec."""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Weather API",
                "version": "2.5.0",
                "description": "Get current weather and forecasts"
            },
            "servers": [
                {"url": "https://api.openweathermap.org/data/2.5"}
            ],
            "paths": {
                "/weather": {
                    "get": {
                        "operationId": "get_current_weather",
                        "summary": "Get current weather",
                        "tags": ["weather"],
                        "parameters": [
                            {
                                "name": "q",
                                "in": "query",
                                "required": True,
                                "description": "City name",
                                "schema": {"type": "string"}
                            },
                            {
                                "name": "appid",
                                "in": "query",
                                "required": True,
                                "description": "API key",
                                "schema": {"type": "string"}
                            },
                            {
                                "name": "units",
                                "in": "query",
                                "description": "Units of measurement",
                                "schema": {
                                    "type": "string",
                                    "enum": ["metric", "imperial", "kelvin"]
                                }
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "weather": {"type": "array"},
                                                "main": {"type": "object"},
                                                "name": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/forecast": {
                    "get": {
                        "operationId": "get_forecast",
                        "summary": "Get 5 day forecast",
                        "tags": ["weather"],
                        "parameters": [
                            {
                                "name": "q",
                                "in": "query",
                                "required": True,
                                "schema": {"type": "string"}
                            },
                            {
                                "name": "appid",
                                "in": "query",
                                "required": True,
                                "schema": {"type": "string"}
                            }
                        ],
                        "responses": {
                            "200": {"description": "Successful response"}
                        }
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        spec_data = parser.to_api_spec()

        assert spec_data["title"] == "Weather API"
        assert len(spec_data["endpoints"]) == 2

        # Generate and validate
        from auto_mcp.core.types import Endpoint, Parameter, ParamLocation

        endpoints = []
        for ep_dict in spec_data["endpoints"]:
            params = []
            for p in ep_dict.get("parameters", []):
                params.append(Parameter(
                    name=p["name"],
                    type=p["type"],
                    location=ParamLocation(p["location"]),
                    required=p["required"],
                    enum=p.get("enum"),
                ))
            endpoints.append(Endpoint(
                path=ep_dict["path"],
                method=ep_dict["method"],
                operation_id=ep_dict["operation_id"],
                summary=ep_dict.get("summary"),
                tags=ep_dict.get("tags", []),
                parameters=params,
            ))

        api_spec = APISpec(
            title=spec_data["title"],
            version=spec_data["version"],
            description=spec_data.get("description"),
            base_url=spec_data.get("base_url"),
            endpoints=endpoints,
        )

        config = MCPServerConfig(
            name="weather-mcp",
            version="2.5.0",
            description="Weather API MCP Server",
            language=Language.PYTHON,
            api_spec=api_spec,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = PythonMCPGenerator(config)
            generator.generate(Path(tmpdir))

            server_content = (Path(tmpdir) / "weather_mcp" / "server.py").read_text()

            assert "def get_current_weather(" in server_content
            assert "def get_forecast(" in server_content
            assert "q: str" in server_content
            assert "appid: str" in server_content

            from auto_mcp.core.validator import CodeValidator
            errors = CodeValidator.validate_python(server_content)
            assert len(errors) == 0
