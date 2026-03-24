"""Comprehensive tests for remaining edge cases and scenarios."""

import pytest
import tempfile
from pathlib import Path
import yaml
import json

from auto_mcp.core.parser import OpenAPIParser
from auto_mcp.core.generator import PythonMCPGenerator, TypeScriptMCPGenerator
from auto_mcp.core.types import (
    APISpec,
    Endpoint,
    Language,
    MCPServerConfig,
    Parameter,
    ParamLocation,
    HTTPMethod,
    Server,
    Authentication,
    Response,
)


# Round 91-100: Comprehensive data type tests
class TestDataTypes:
    """Test all OpenAPI data types."""

    def test_all_primitive_types(self):
        """Test all primitive types in parameters."""
        types_to_test = [
            ("string", "str"),
            ("integer", "int"),
            ("number", "float"),
            ("boolean", "bool"),
        ]

        for openapi_type, expected_python in types_to_test:
            spec = {
                "openapi": "3.0.0",
                "info": {"title": "Types API", "version": "1.0.0"},
                "paths": {
                    "/test": {
                        "get": {
                            "operationId": f"test_{openapi_type}",
                            "parameters": [
                                {
                                    "name": "param",
                                    "in": "query",
                                    "schema": {"type": openapi_type}
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

            assert endpoints[0]["parameters"][0]["type"] == openapi_type

    def test_format_variants(self):
        """Test various format variants."""
        formats_to_test = [
            ("string", "date"),
            ("string", "date-time"),
            ("string", "email"),
            ("string", "uuid"),
            ("string", "uri"),
            ("integer", "int32"),
            ("integer", "int64"),
            ("number", "float"),
            ("number", "double"),
        ]

        for type_name, format_name in formats_to_test:
            spec = {
                "openapi": "3.0.0",
                "info": {"title": "Format API", "version": "1.0.0"},
                "paths": {
                    "/test": {
                        "get": {
                            "operationId": f"test_{type_name}_{format_name}",
                            "parameters": [
                                {
                                    "name": "param",
                                    "in": "query",
                                    "schema": {"type": type_name, "format": format_name}
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

            assert endpoints[0]["parameters"][0]["type"] == type_name

    def test_number_constraints(self):
        """Test numeric constraints."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Constraints API", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "operationId": "test_constraints",
                        "parameters": [
                            {
                                "name": "value",
                                "in": "query",
                                "schema": {
                                    "type": "integer",
                                    "minimum": 0,
                                    "maximum": 100,
                                    "multipleOf": 5
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
        param_schema = endpoints[0]["parameters"][0].get("schema", {})
        assert param_schema is not None

    def test_string_constraints(self):
        """Test string constraints."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "String API", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "operationId": "test_string",
                        "parameters": [
                            {
                                "name": "text",
                                "in": "query",
                                "schema": {
                                    "type": "string",
                                    "minLength": 1,
                                    "maxLength": 100,
                                    "pattern": "^[a-zA-Z]+$"
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

    def test_array_with_items(self):
        """Test array parameter with various item types."""
        item_types = ["string", "integer", "number", "boolean"]

        for item_type in item_types:
            spec = {
                "openapi": "3.0.0",
                "info": {"title": "Array API", "version": "1.0.0"},
                "paths": {
                    "/test": {
                        "get": {
                            "operationId": f"test_array_{item_type}",
                            "parameters": [
                                {
                                    "name": "items",
                                    "in": "query",
                                    "schema": {
                                        "type": "array",
                                        "items": {"type": item_type}
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

            assert endpoints[0]["parameters"][0]["type"] == "array"

    def test_nullable_parameters(self):
        """Test nullable parameters."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Nullable API", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "operationId": "test_nullable",
                        "parameters": [
                            {
                                "name": "value",
                                "in": "query",
                                "schema": {
                                    "type": "string",
                                    "nullable": True
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

    def test_read_only_write_only(self):
        """Test readOnly and writeOnly properties."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "RO/WO API", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "operationId": "test_ro_wo",
                        "responses": {
                            "200": {
                                "description": "OK",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "id": {
                                                    "type": "string",
                                                    "readOnly": True
                                                },
                                                "password": {
                                                    "type": "string",
                                                    "writeOnly": True
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

    def test_default_values(self):
        """Test parameters with default values."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Default API", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "operationId": "test_default",
                        "parameters": [
                            {
                                "name": "limit",
                                "in": "query",
                                "schema": {
                                    "type": "integer",
                                    "default": 10
                                }
                            },
                            {
                                "name": "active",
                                "in": "query",
                                "schema": {
                                    "type": "boolean",
                                    "default": True
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
        assert endpoints[0]["parameters"][0]["default"] == 10
        assert endpoints[0]["parameters"][1]["default"] is True

    def test_all_http_methods_lowercase(self):
        """Test all HTTP methods are normalized to lowercase."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Methods API", "version": "1.0.0"},
            "paths": {
                "/resource": {
                    "GET": {
                        "operationId": "get_res",
                        "responses": {"200": {"description": "OK"}}
                    },
                    "Post": {
                        "operationId": "post_res",
                        "responses": {"201": {"description": "Created"}}
                    },
                    "PUT": {
                        "operationId": "put_res",
                        "responses": {"200": {"description": "Updated"}}
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        endpoints = parser.extract_endpoints()

        methods = {e["method"] for e in endpoints}
        assert methods == {"get", "post", "put"}

    def test_mixed_case_parameters(self):
        """Test parameters with mixed case names."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Mixed Case API", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "operationId": "test_mixed",
                        "parameters": [
                            {"name": "UserID", "in": "path", "required": True, "schema": {"type": "string"}},
                            {"name": "apiKey", "in": "header", "required": True, "schema": {"type": "string"}}
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
        param_names = {p["name"] for p in endpoints[0]["parameters"]}
        assert param_names == {"UserID", "apiKey"}


# Round 101-110: Type system tests
class TestTypeSystem:
    """Test dataclass types and conversions."""

    def test_http_method_enum(self):
        """Test HTTPMethod enum values."""
        assert HTTPMethod.GET.value == "get"
        assert HTTPMethod.POST.value == "post"
        assert HTTPMethod.PUT.value == "put"
        assert HTTPMethod.DELETE.value == "delete"
        assert HTTPMethod.PATCH.value == "patch"
        assert HTTPMethod.HEAD.value == "head"
        assert HTTPMethod.OPTIONS.value == "options"

    def test_param_location_enum(self):
        """Test ParamLocation enum values."""
        assert ParamLocation.PATH.value == "path"
        assert ParamLocation.QUERY.value == "query"
        assert ParamLocation.HEADER.value == "header"
        assert ParamLocation.COOKIE.value == "cookie"

    def test_language_enum(self):
        """Test Language enum values."""
        assert Language.PYTHON.value == "python"
        assert Language.TYPESCRIPT.value == "typescript"

    def test_endpoint_dataclass(self):
        """Test Endpoint dataclass with all fields."""
        endpoint = Endpoint(
            path="/users/{id}",
            method=HTTPMethod.GET,
            operation_id="get_user",
            summary="Get user by ID",
            description="Detailed description",
            parameters=[
                Parameter(
                    name="id",
                    type="string",
                    location=ParamLocation.PATH,
                    required=True,
                )
            ],
            request_body={"content": {"application/json": {"schema": {"type": "object"}}}},
            responses={
                200: Response(
                    status_code=200,
                    description="User found",
                    content_type="application/json",
                )
            },
            tags=["users"],
            deprecated=False,
        )

        assert endpoint.path == "/users/{id}"
        assert endpoint.method == "get"
        assert endpoint.operation_id == "get_user"
        assert len(endpoint.parameters) == 1
        assert len(endpoint.responses) == 1
        assert endpoint.tags == ["users"]
        assert endpoint.deprecated is False

    def test_parameter_dataclass(self):
        """Test Parameter dataclass with all fields."""
        param = Parameter(
            name="test",
            type="string",
            location=ParamLocation.QUERY,
            required=False,
            description="Test parameter",
            default="default_value",
            enum=["a", "b", "c"],
            schema={"type": "string"},
        )

        assert param.name == "test"
        assert param.type == "string"
        assert param.location == "query"
        assert param.required is False
        assert param.description == "Test parameter"
        assert param.default == "default_value"
        assert param.enum == ["a", "b", "c"]

    def test_response_dataclass(self):
        """Test Response dataclass with all fields."""
        response = Response(
            status_code=404,
            description="Not found",
            content_type="application/json",
            schema={"type": "object"},
        )

        assert response.status_code == 404
        assert response.description == "Not found"
        assert response.content_type == "application/json"
        assert response.schema is not None

    def test_server_dataclass(self):
        """Test Server dataclass."""
        server = Server(
            url="https://api.example.com",
            description="Production server",
            variables={"env": {"default": "prod"}},
        )

        assert server.url == "https://api.example.com"
        assert server.description == "Production server"
        assert server.variables == {"env": {"default": "prod"}}

    def test_authentication_dataclass(self):
        """Test Authentication dataclass."""
        auth = Authentication(
            type="http",
            scheme="bearer",
            bearer_format="JWT",
            description="Bearer token authentication",
        )

        assert auth.type == "http"
        assert auth.scheme == "bearer"
        assert auth.bearer_format == "JWT"

    def test_api_spec_dataclass(self):
        """Test APISpec dataclass."""
        spec = APISpec(
            title="Test API",
            version="1.0.0",
            description="Test API description",
            base_url="https://api.test.com",
            endpoints=[
                Endpoint(
                    path="/test",
                    method=HTTPMethod.GET,
                    operation_id="test",
                )
            ],
            servers=[
                Server(url="https://api.test.com"),
            ],
            authentication={
                "bearer": Authentication(type="http", scheme="bearer"),
            },
        )

        assert spec.title == "Test API"
        assert spec.version == "1.0.0"
        assert spec.base_url == "https://api.test.com"
        assert len(spec.endpoints) == 1
        assert len(spec.servers) == 1
        assert "bearer" in spec.authentication

    def test_mcp_config_dataclass(self):
        """Test MCPServerConfig dataclass."""
        api_spec = APISpec(
            title="API",
            version="1.0.0",
            endpoints=[],
        )

        config = MCPServerConfig(
            name="test-mcp",
            version="1.0.0",
            description="Test MCP Server",
            language=Language.PYTHON,
            api_spec=api_spec,
            author="Test Author",
            license="MIT",
            dependencies={"fastmcp": "^0.1.0"},
            dev_dependencies={"pytest": "^7.0.0"},
        )

        assert config.name == "test-mcp"
        assert config.language == Language.PYTHON
        assert config.author == "Test Author"
        assert config.license == "MIT"
        assert "fastmcp" in config.dependencies
        assert "pytest" in config.dev_dependencies


# Round 111-120: Real-world API patterns
class TestRealWorldPatterns:
    """Test common real-world API patterns."""

    def test_pagination_pattern(self):
        """Test pagination parameters pattern."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Pagination API", "version": "1.0.0"},
            "paths": {
                "/items": {
                    "get": {
                        "operationId": "list_items",
                        "parameters": [
                            {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                            {"name": "per_page", "in": "query", "schema": {"type": "integer", "default": 20}},
                            {"name": "sort", "in": "query", "schema": {"type": "string"}},
                            {"name": "order", "in": "query", "schema": {"type": "string", "enum": ["asc", "desc"]}},
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
        assert len(endpoints[0]["parameters"]) == 4

    def test_filtering_pattern(self):
        """Test filtering parameters pattern."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Filter API", "version": "1.0.0"},
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "filter_users",
                        "parameters": [
                            {"name": "status", "in": "query", "schema": {"type": "string", "enum": ["active", "inactive"]}},
                            {"name": "role", "in": "query", "schema": {"type": "string"}},
                            {"name": "created_after", "in": "query", "schema": {"type": "string", "format": "date-time"}},
                            {"name": "search", "in": "query", "schema": {"type": "string"}},
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
        assert len(endpoints[0]["parameters"]) == 4

    def test_crud_pattern(self):
        """Test CRUD operations pattern."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "CRUD API", "version": "1.0.0"},
            "paths": {
                "/resources": {
                    "get": {
                        "operationId": "list_resources",
                        "responses": {"200": {"description": "OK"}}
                    },
                    "post": {
                        "operationId": "create_resource",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        },
                        "responses": {"201": {"description": "Created"}}
                    }
                },
                "/resources/{id}": {
                    "get": {
                        "operationId": "get_resource",
                        "parameters": [
                            {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}
                        ],
                        "responses": {"200": {"description": "OK"}}
                    },
                    "put": {
                        "operationId": "update_resource",
                        "parameters": [
                            {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}
                        ],
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        },
                        "responses": {"200": {"description": "Updated"}}
                    },
                    "delete": {
                        "operationId": "delete_resource",
                        "parameters": [
                            {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}
                        ],
                        "responses": {"204": {"description": "Deleted"}}
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        endpoints = parser.extract_endpoints()

        assert len(endpoints) == 5
        operations = {e["operation_id"] for e in endpoints}
        assert operations == {"list_resources", "create_resource", "get_resource", "update_resource", "delete_resource"}

    def test_nested_resources_pattern(self):
        """Test nested resource pattern."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Nested API", "version": "1.0.0"},
            "paths": {
                "/users/{userId}/posts": {
                    "get": {
                        "operationId": "list_user_posts",
                        "parameters": [
                            {"name": "userId", "in": "path", "required": True, "schema": {"type": "string"}}
                        ],
                        "responses": {"200": {"description": "OK"}}
                    }
                },
                "/users/{userId}/posts/{postId}/comments": {
                    "get": {
                        "operationId": "list_post_comments",
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

        assert len(endpoints) == 2
        assert "/users/{userId}/posts" in endpoints[0]["path"]
        assert "/users/{userId}/posts/{postId}/comments" in endpoints[1]["path"]

    def test_batch_operations_pattern(self):
        """Test batch operations pattern."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Batch API", "version": "1.0.0"},
            "paths": {
                "/items/batch": {
                    "post": {
                        "operationId": "batch_create_items",
                        "summary": "Create multiple items",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"type": "object"}
                                    }
                                }
                            }
                        },
                        "responses": {"201": {"description": "Created"}}
                    }
                },
                "/items/batch-delete": {
                    "post": {
                        "operationId": "batch_delete_items",
                        "summary": "Delete multiple items",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    }
                                }
                            }
                        },
                        "responses": {"204": {"description": "Deleted"}}
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        endpoints = parser.extract_endpoints()

        assert len(endpoints) == 2

    def test_action_endpoints_pattern(self):
        """Test action endpoints pattern (not standard CRUD)."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Action API", "version": "1.0.0"},
            "paths": {
                "/orders/{id}/cancel": {
                    "post": {
                        "operationId": "cancel_order",
                        "parameters": [
                            {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}
                        ],
                        "responses": {"200": {"description": "Cancelled"}}
                    }
                },
                "/users/{id}/activate": {
                    "post": {
                        "operationId": "activate_user",
                        "parameters": [
                            {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}
                        ],
                        "responses": {"200": {"description": "Activated"}}
                    }
                },
                "/documents/{id}/publish": {
                    "post": {
                        "operationId": "publish_document",
                        "parameters": [
                            {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}
                        ],
                        "responses": {"200": {"description": "Published"}}
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        endpoints = parser.extract_endpoints()

        assert len(endpoints) == 3

    def test_search_endpoint_pattern(self):
        """Test search endpoint pattern."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Search API", "version": "1.0.0"},
            "paths": {
                "/search": {
                    "get": {
                        "operationId": "search",
                        "parameters": [
                            {"name": "q", "in": "query", "required": True, "description": "Search query", "schema": {"type": "string"}},
                            {"name": "type", "in": "query", "schema": {"type": "string", "enum": ["all", "users", "posts"]}},
                            {"name": "facets", "in": "query", "schema": {"type": "boolean", "default": False}},
                            {"name": "offset", "in": "query", "schema": {"type": "integer", "default": 0}},
                            {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 10}},
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
        assert len(endpoints[0]["parameters"]) == 5

    def test_webhook_pattern(self):
        """Test webhook configuration pattern."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Webhook API", "version": "1.0.0"},
            "paths": {
                "/webhooks": {
                    "post": {
                        "operationId": "create_webhook",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["url", "events"],
                                        "properties": {
                                            "url": {"type": "string", "format": "uri"},
                                            "events": {"type": "array", "items": {"type": "string"}},
                                            "secret": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {"201": {"description": "Created"}}
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        endpoints = parser.extract_endpoints()

        assert len(endpoints) == 1

    def test_versioned_api_pattern(self):
        """Test versioned API pattern."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Versioned API", "version": "2.0.0"},
            "paths": {
                "/v2/users": {
                    "get": {
                        "operationId": "list_users_v2",
                        "responses": {"200": {"description": "OK"}}
                    }
                },
                "/v2/posts": {
                    "get": {
                        "operationId": "list_posts_v2",
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        endpoints = parser.extract_endpoints()

        assert len(endpoints) == 2
        for endpoint in endpoints:
            assert endpoint["path"].startswith("/v2/")

    def test_multi_server_configuration(self):
        """Test multiple server configuration pattern."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Multi Server API", "version": "1.0.0"},
            "servers": [
                {
                    "url": "https://api.example.com/v1",
                    "description": "Production server"
                },
                {
                    "url": "https://staging-api.example.com/v1",
                    "description": "Staging server"
                },
                {
                    "url": "http://localhost:3000/v1",
                    "description": "Local development server"
                }
            ],
            "paths": {
                "/test": {
                    "get": {
                        "operationId": "test",
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        api_spec = parser.to_api_spec()

        assert api_spec["base_url"] == "https://api.example.com/v1"
        assert len(api_spec["servers"]) == 3
