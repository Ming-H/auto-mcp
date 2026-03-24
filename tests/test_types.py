"""Tests for type mapping and conversion."""

import pytest

from auto_mcp.core.generator import BaseGenerator
from auto_mcp.core.types import Language


# Round 9-15: Type mapping tests
class TestTypeMapping:
    """Test OpenAPI type to Python type mapping."""

    def test_python_type_string(self):
        """Test string type mapping."""
        assert BaseGenerator._python_type_filter("string") == "str"

    def test_python_type_integer(self):
        """Test integer type mapping."""
        assert BaseGenerator._python_type_filter("integer") == "int"

    def test_python_type_number(self):
        """Test number type mapping."""
        assert BaseGenerator._python_type_filter("number") == "float"

    def test_python_type_boolean(self):
        """Test boolean type mapping."""
        assert BaseGenerator._python_type_filter("boolean") == "bool"

    def test_python_type_array(self):
        """Test array type mapping."""
        assert BaseGenerator._python_type_filter("array") == "list"

    def test_python_type_object(self):
        """Test object type mapping."""
        assert BaseGenerator._python_type_filter("object") == "dict"

    def test_python_type_unknown(self):
        """Test unknown type mapping."""
        assert BaseGenerator._python_type_filter("custom") == "Any"


class TestParameterLocation:
    """Test parameter location enum."""

    def test_path_location(self):
        """Test path parameter location."""
        from auto_mcp.core.types import ParamLocation
        assert ParamLocation.PATH == "path"

    def test_query_location(self):
        """Test query parameter location."""
        from auto_mcp.core.types import ParamLocation
        assert ParamLocation.QUERY == "query"

    def test_header_location(self):
        """Test header parameter location."""
        from auto_mcp.core.types import ParamLocation
        assert ParamLocation.HEADER == "header"

    def test_cookie_location(self):
        """Test cookie parameter location."""
        from auto_mcp.core.types import ParamLocation
        assert ParamLocation.COOKIE == "cookie"


class TestEndpointTypes:
    """Test Endpoint dataclass."""

    def test_endpoint_creation(self):
        """Test creating an endpoint."""
        from auto_mcp.core.types import Endpoint, HTTPMethod

        endpoint = Endpoint(
            path="/test",
            method=HTTPMethod.GET,
            operation_id="test_endpoint",
            summary="Test endpoint",
        )

        assert endpoint.path == "/test"
        assert endpoint.method == "get"
        assert endpoint.operation_id == "test_endpoint"
        assert endpoint.summary == "Test endpoint"
        assert endpoint.parameters == []
        assert endpoint.deprecated is False

    def test_parameter_creation(self):
        """Test creating a parameter."""
        from auto_mcp.core.types import Parameter, ParamLocation

        param = Parameter(
            name="test",
            type="string",
            location=ParamLocation.QUERY,
            required=True,
            description="Test parameter",
        )

        assert param.name == "test"
        assert param.type == "string"
        assert param.location == "query"
        assert param.required is True
        assert param.description == "Test parameter"


class TestResponseTypes:
    """Test Response dataclass."""

    def test_response_creation(self):
        """Test creating a response."""
        from auto_mcp.core.types import Response

        response = Response(
            status_code=200,
            description="OK",
            content_type="application/json",
        )

        assert response.status_code == 200
        assert response.description == "OK"
        assert response.content_type == "application/json"


class TestLanguageEnum:
    """Test Language enum."""

    def test_python_language(self):
        """Test Python language."""
        assert Language.PYTHON == "python"

    def test_typescript_language(self):
        """Test TypeScript language."""
        assert Language.TYPESCRIPT == "typescript"
