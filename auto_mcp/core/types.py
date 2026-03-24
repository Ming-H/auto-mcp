"""
Type definitions for AutoMCP.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class HTTPMethod(str, Enum):
    """HTTP methods supported by OpenAPI."""
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    PATCH = "patch"
    HEAD = "head"
    OPTIONS = "options"


class ParamLocation(str, Enum):
    """Parameter location in HTTP request."""
    PATH = "path"
    QUERY = "query"
    HEADER = "header"
    COOKIE = "cookie"


class Language(str, Enum):
    """Supported programming languages for MCP server generation."""
    PYTHON = "python"
    TYPESCRIPT = "typescript"


@dataclass
class Parameter:
    """API parameter definition."""
    name: str
    type: str
    location: ParamLocation
    required: bool = True
    description: Optional[str] = None
    default: Any = None
    enum: Optional[list[Any]] = None
    schema: Optional[dict[str, Any]] = None


@dataclass
class Response:
    """API response definition."""
    status_code: int
    description: str
    content_type: str = "application/json"
    schema: Optional[dict[str, Any]] = None


@dataclass
class Endpoint:
    """API endpoint definition."""
    path: str
    method: HTTPMethod
    operation_id: str
    summary: Optional[str] = None
    description: Optional[str] = None
    parameters: list[Parameter] = field(default_factory=list)
    request_body: Optional[dict[str, Any]] = None
    responses: dict[int, Response] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    deprecated: bool = False


@dataclass
class Server:
    """API server definition."""
    url: str
    description: Optional[str] = None
    variables: dict[str, Any] = field(default_factory=dict)


@dataclass
class Authentication:
    """Authentication scheme definition."""
    type: str  # apiKey, http, oauth2, openIdConnect
    scheme: Optional[str] = None
    bearer_format: Optional[str] = None
    description: Optional[str] = None


@dataclass
class APISpec:
    """Complete API specification."""
    title: str
    version: str
    description: Optional[str] = None
    base_url: Optional[str] = None
    endpoints: list[Endpoint] = field(default_factory=list)
    servers: list[Server] = field(default_factory=list)
    authentication: dict[str, Authentication] = field(default_factory=dict)
    raw_spec: dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPServerConfig:
    """MCP Server configuration."""
    name: str
    version: str
    description: str
    language: Language
    api_spec: APISpec
    author: Optional[str] = None
    license: Optional[str] = None
    dependencies: dict[str, str] = field(default_factory=dict)
    dev_dependencies: dict[str, str] = field(default_factory=dict)
