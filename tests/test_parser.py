"""Tests for OpenAPI parser."""

import pytest

from auto_mcp.core.parser import OpenAPIParser


def test_parse_simple_spec():
    """Test parsing a simple OpenAPI spec."""
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Test API",
            "version": "1.0.0",
        },
        "paths": {
            "/users": {
                "get": {
                    "operationId": "list_users",
                    "summary": "List all users",
                    "responses": {"200": {"description": "OK"}},
                }
            }
        },
    }

    parser = OpenAPIParser(spec)
    result = parser.parse()

    assert result["openapi"] == "3.0.0"
    assert result["info"]["title"] == "Test API"


def test_extract_endpoints():
    """Test extracting endpoints from spec."""
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Test", "version": "1.0.0"},
        "paths": {
            "/users": {
                "get": {
                    "operationId": "list_users",
                    "summary": "List users",
                    "responses": {"200": {"description": "OK"}},
                },
                "post": {
                    "operationId": "create_user",
                    "summary": "Create user",
                    "responses": {"201": {"description": "Created"}},
                },
            }
        },
    }

    parser = OpenAPIParser(spec)
    parser.parse()
    endpoints = parser.extract_endpoints()

    assert len(endpoints) == 2
    assert endpoints[0]["operation_id"] == "list_users"
    assert endpoints[0]["method"] == "get"
    assert endpoints[1]["operation_id"] == "create_user"
    assert endpoints[1]["method"] == "post"


def test_to_api_spec():
    """Test converting to API spec dict."""
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "My API",
            "version": "2.0.0",
            "description": "Test API",
        },
        "servers": [{"url": "https://api.example.com"}],
        "paths": {},
    }

    parser = OpenAPIParser(spec)
    parser.parse()
    api_spec = parser.to_api_spec()

    assert api_spec["title"] == "My API"
    assert api_spec["version"] == "2.0.0"
    assert api_spec["description"] == "Test API"
    assert api_spec["base_url"] == "https://api.example.com"


# Round 1: Complex nested structure test
def test_parse_nested_structure():
    """Test parsing API with nested schema structures."""
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Nested API", "version": "1.0.0"},
        "paths": {
            "/users/{userId}": {
                "get": {
                    "operationId": "get_user",
                    "parameters": [
                        {
                            "name": "userId",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        },
                        {
                            "name": "include",
                            "in": "query",
                            "schema": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "User found",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "name": {"type": "string"},
                                            "address": {
                                                "type": "object",
                                                "properties": {
                                                    "street": {"type": "string"},
                                                    "city": {"type": "string"}
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
    assert endpoints[0]["operation_id"] == "get_user"
    assert len(endpoints[0]["parameters"]) == 2
    assert endpoints[0]["parameters"][0]["location"] == "path"
    assert endpoints[0]["parameters"][0]["type"] == "integer"


# Round 2: Enum type test
def test_parse_enum_parameters():
    """Test parsing API with enum parameters."""
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Enum API", "version": "1.0.0"},
        "paths": {
            "/users": {
                "get": {
                    "operationId": "list_users",
                    "parameters": [
                        {
                            "name": "status",
                            "in": "query",
                            "schema": {
                                "type": "string",
                                "enum": ["active", "inactive", "pending"]
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
    assert endpoints[0]["parameters"][0]["enum"] == ["active", "inactive", "pending"]


# Round 3: Multiple HTTP methods test
def test_all_http_methods():
    """Test parsing all supported HTTP methods."""
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Methods API", "version": "1.0.0"},
        "paths": {
            "/resource": {
                "get": {
                    "operationId": "get_resource",
                    "responses": {"200": {"description": "OK"}}
                },
                "post": {
                    "operationId": "create_resource",
                    "responses": {"201": {"description": "Created"}}
                },
                "put": {
                    "operationId": "update_resource",
                    "responses": {"200": {"description": "Updated"}}
                },
                "patch": {
                    "operationId": "patch_resource",
                    "responses": {"200": {"description": "Patched"}}
                },
                "delete": {
                    "operationId": "delete_resource",
                    "responses": {"204": {"description": "Deleted"}}
                },
                "head": {
                    "operationId": "head_resource",
                    "responses": {"200": {"description": "Headers"}}
                },
                "options": {
                    "operationId": "options_resource",
                    "responses": {"200": {"description": "Options"}}
                }
            }
        }
    }

    parser = OpenAPIParser(spec)
    parser.parse()
    endpoints = parser.extract_endpoints()

    assert len(endpoints) == 7
    methods = {e["method"] for e in endpoints}
    assert methods == {"get", "post", "put", "patch", "delete", "head", "options"}


# Round 4: Request body test
def test_parse_request_body():
    """Test parsing endpoints with request bodies."""
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Body API", "version": "1.0.0"},
        "paths": {
            "/users": {
                "post": {
                    "operationId": "create_user",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "email": {"type": "string"}
                                    },
                                    "required": ["name", "email"]
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
    assert endpoints[0]["request_body"] is not None
    assert "content" in endpoints[0]["request_body"]


# Round 5: Authentication test
def test_parse_authentication():
    """Test parsing authentication schemes."""
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Auth API", "version": "1.0.0"},
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                },
                "apiKey": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key"
                }
            }
        },
        "paths": {}
    }

    parser = OpenAPIParser(spec)
    parser.parse()
    api_spec = parser.to_api_spec()

    assert "authentication" in api_spec
    assert "bearerAuth" in api_spec["authentication"]
    assert api_spec["authentication"]["bearerAuth"]["type"] == "http"
    assert api_spec["authentication"]["apiKey"]["type"] == "apiKey"


# Round 6: Tag extraction test
def test_parse_tags():
    """Test parsing endpoint tags."""
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Tags API", "version": "1.0.0"},
        "paths": {
            "/users": {
                "get": {
                    "operationId": "list_users",
                    "tags": ["users", "admin"],
                    "responses": {"200": {"description": "OK"}}
                }
            }
        }
    }

    parser = OpenAPIParser(spec)
    parser.parse()
    endpoints = parser.extract_endpoints()

    assert len(endpoints) == 1
    assert endpoints[0]["tags"] == ["users", "admin"]


# Round 7: Deprecated endpoint test
def test_parse_deprecated():
    """Test parsing deprecated endpoints."""
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Deprecated API", "version": "1.0.0"},
        "paths": {
            "/old": {
                "get": {
                    "operationId": "old_endpoint",
                    "deprecated": True,
                    "responses": {"200": {"description": "OK"}}
                }
            }
        }
    }

    parser = OpenAPIParser(spec)
    parser.parse()
    endpoints = parser.extract_endpoints()

    assert len(endpoints) == 1
    assert endpoints[0]["deprecated"] is True


# Round 8: Response schema test
def test_parse_response_schemas():
    """Test parsing response schemas."""
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Response API", "version": "1.0.0"},
        "paths": {
            "/data": {
                "get": {
                    "operationId": "get_data",
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "data": {"type": "string"}
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
    assert "200" in endpoints[0]["responses"]
    assert endpoints[0]["responses"]["200"]["schema"] is not None
