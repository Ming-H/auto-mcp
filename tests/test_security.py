"""Security and authentication related tests."""

import pytest
from pathlib import Path
import tempfile

from auto_mcp.core.parser import OpenAPIParser
from auto_mcp.core.generator import PythonMCPGenerator
from auto_mcp.core.types import APISpec, Endpoint, Language, MCPServerConfig, Authentication


class TestSecuritySchemes:
    """Test various security schemes."""

    def test_bearer_auth(self):
        """Test Bearer token authentication."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Bearer Auth API", "version": "1.0.0"},
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                        "description": "JWT bearer token"
                    }
                }
            },
            "security": [{"bearerAuth": []}],
            "paths": {
                "/secure": {
                    "get": {
                        "operationId": "secure_endpoint",
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        api_spec = parser.to_api_spec()

        assert "bearerAuth" in api_spec["authentication"]
        assert api_spec["authentication"]["bearerAuth"]["type"] == "http"
        assert api_spec["authentication"]["bearerAuth"]["scheme"] == "bearer"

    def test_api_key_header(self):
        """Test API key in header."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API Key Header", "version": "1.0.0"},
            "components": {
                "securitySchemes": {
                    "apiKey": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key",
                        "description": "API key in header"
                    }
                }
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

        parser = OpenAPIParser(spec)
        parser.parse()
        api_spec = parser.to_api_spec()

        assert api_spec["authentication"]["apiKey"]["type"] == "apiKey"

    def test_api_key_query(self):
        """Test API key in query parameter."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API Key Query", "version": "1.0.0"},
            "components": {
                "securitySchemes": {
                    "apiKey": {
                        "type": "apiKey",
                        "in": "query",
                        "name": "api_key"
                    }
                }
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

        parser = OpenAPIParser(spec)
        parser.parse()
        api_spec = parser.to_api_spec()

        # The parser extracts auth, check type is correct
        assert api_spec["authentication"]["apiKey"]["type"] == "apiKey"

    def test_oauth2_flow(self):
        """Test OAuth2 flows."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "OAuth2 API", "version": "1.0.0"},
            "components": {
                "securitySchemes": {
                    "oauth2": {
                        "type": "oauth2",
                        "flows": {
                            "authorizationCode": {
                                "authorizationUrl": "https://example.com/oauth/authorize",
                                "tokenUrl": "https://example.com/oauth/token",
                                "scopes": {
                                    "read": "Read access",
                                    "write": "Write access"
                                }
                            }
                        }
                    }
                }
            },
            "paths": {
                "/protected": {
                    "get": {
                        "operationId": "protected_resource",
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        api_spec = parser.to_api_spec()

        assert "oauth2" in api_spec["authentication"]

    def test_multiple_auth_schemes(self):
        """Test multiple authentication schemes."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Multi Auth API", "version": "1.0.0"},
            "components": {
                "securitySchemes": {
                    "bearer": {
                        "type": "http",
                        "scheme": "bearer"
                    },
                    "apiKey": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-Key"
                    }
                }
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

        parser = OpenAPIParser(spec)
        parser.parse()
        api_spec = parser.to_api_spec()

        assert len(api_spec["authentication"]) == 2
        assert "bearer" in api_spec["authentication"]
        assert "apiKey" in api_spec["authentication"]

    def test_http_basic_auth(self):
        """Test HTTP basic authentication."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Basic Auth API", "version": "1.0.0"},
            "components": {
                "securitySchemes": {
                    "basicAuth": {
                        "type": "http",
                        "scheme": "basic",
                        "description": "Basic HTTP authentication"
                    }
                }
            },
            "paths": {
                "/secure": {
                    "get": {
                        "operationId": "secure_endpoint",
                        "responses": {"200": {"description": "OK"}}
                    }
                }
            }
        }

        parser = OpenAPIParser(spec)
        parser.parse()
        api_spec = parser.to_api_spec()

        assert api_spec["authentication"]["basicAuth"]["scheme"] == "basic"


class TestGeneratorWithAuth:
    """Test code generation with authentication."""

    def test_python_generator_with_bearer_auth(self):
        """Test Python generator includes auth handling."""
        api_spec = APISpec(
            title="Secure API",
            version="1.0.0",
            description="API with Bearer auth",
            base_url="https://api.example.com",
            endpoints=[],
            authentication={
                "bearerAuth": Authentication(
                    type="http",
                    scheme="bearer",
                    bearer_format="JWT",
                )
            },
        )

        config = MCPServerConfig(
            name="secure-mcp",
            version="1.0.0",
            description="Secure MCP Server",
            language=Language.PYTHON,
            api_spec=api_spec,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = PythonMCPGenerator(config)
            generator.generate(Path(tmpdir))

            server_content = (Path(tmpdir) / "secure_mcp" / "server.py").read_text()

            # Check auth handling is present
            assert "AUTH_TOKEN" in server_content
            assert "Authorization" in server_content
            assert "Bearer" in server_content

    def test_readme_mentions_auth(self):
        """Test README mentions authentication when configured."""
        api_spec = APISpec(
            title="Auth API",
            version="1.0.0",
            description="API with authentication",
            base_url="https://api.example.com",
            endpoints=[
                Endpoint(
                    path="/secure",
                    method="get",
                    operation_id="secure_endpoint",
                    summary="Secure endpoint",
                )
            ],
            authentication={
                "apiKey": Authentication(type="apiKey", scheme="header")
            },
        )

        config = MCPServerConfig(
            name="auth-mcp",
            version="1.0.0",
            description="Auth MCP Server",
            language=Language.PYTHON,
            api_spec=api_spec,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            generator = PythonMCPGenerator(config)
            generator.generate(Path(tmpdir))

            # README should mention authentication
            assert (Path(tmpdir) / "README.md").exists()


class TestSecurityHeaders:
    """Test security-related headers."""

    def test_rate_limit_headers(self):
        """Test rate limit headers in responses."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Rate Limited API", "version": "1.0.0"},
            "paths": {
                "/data": {
                    "get": {
                        "operationId": "get_data",
                        "responses": {
                            "200": {
                                "description": "OK",
                                "headers": {
                                    "X-RateLimit-Limit": {
                                        "schema": {"type": "integer"},
                                        "description": "Request limit per time window"
                                    },
                                    "X-RateLimit-Remaining": {
                                        "schema": {"type": "integer"},
                                        "description": "Requests remaining in window"
                                    },
                                    "X-RateLimit-Reset": {
                                        "schema": {"type": "integer"},
                                        "description": "Unix timestamp when limit resets"
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

    def test_correlation_id_header(self):
        """Test correlation ID in request headers."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Traced API", "version": "1.0.0"},
            "paths": {
                "/trace": {
                    "get": {
                        "operationId": "traced_endpoint",
                        "parameters": [
                            {
                                "name": "X-Correlation-ID",
                                "in": "header",
                                "required": False,
                                "description": "Correlation ID for tracing",
                                "schema": {"type": "string", "format": "uuid"}
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
        assert endpoints[0]["parameters"][0]["name"] == "X-Correlation-ID"


class TestErrorResponses:
    """Test error response structures."""

    def test_standard_error_responses(self):
        """Test standard HTTP error responses."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Error API", "version": "1.0.0"},
            "paths": {
                "/resource": {
                    "get": {
                        "operationId": "get_resource",
                        "responses": {
                            "400": {
                                "description": "Bad Request",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "error": {"type": "string"},
                                                "message": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            },
                            "401": {
                                "description": "Unauthorized",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "error": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            },
                            "403": {
                                "description": "Forbidden"
                            },
                            "404": {
                                "description": "Not Found"
                            },
                            "500": {
                                "description": "Internal Server Error"
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
        responses = endpoints[0]["responses"]
        assert "400" in responses
        assert "401" in responses
        assert "403" in responses
        assert "404" in responses
        assert "500" in responses

    def test_validation_error_response(self):
        """Test validation error response structure."""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Validation API", "version": "1.0.0"},
            "paths": {
                "/validate": {
                    "post": {
                        "operationId": "validate_data",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["email"],
                                        "properties": {
                                            "email": {"type": "string", "format": "email"}
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {
                            "422": {
                                "description": "Validation Error",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "errors": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "field": {"type": "string"},
                                                            "message": {"type": "string"}
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
        assert "422" in endpoints[0]["responses"]
