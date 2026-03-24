"""
API documentation parser for AutoMCP.
"""

import json
from pathlib import Path
from typing import Any

import httpx
import yaml
from pydantic import BaseModel, Field


class OpenAPIParser:
    """Parser for OpenAPI 3.x specifications."""

    def __init__(self, spec_source: str | dict[str, Any]) -> None:
        """
        Initialize the parser with a spec source.

        Args:
            spec_source: URL, file path, or parsed dict
        """
        self.spec_source = spec_source
        self._raw_spec: dict[str, Any] = {}

    def parse(self) -> dict[str, Any]:
        """
        Parse the OpenAPI specification.

        Returns:
            Parsed specification as a dictionary
        """
        if isinstance(self.spec_source, dict):
            self._raw_spec = self.spec_source
        elif isinstance(self.spec_source, str):
            if self.spec_source.startswith(("http://", "https://")):
                self._raw_spec = self._load_from_url()
            else:
                self._raw_spec = self._load_from_file()

        self._validate_spec()
        return self._raw_spec

    def _load_from_url(self) -> dict[str, Any]:
        """Load OpenAPI spec from a URL."""
        response = httpx.get(self.spec_source, follow_redirects=True, timeout=30)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")

        if "application/json" in content_type:
            return response.json()
        else:
            return yaml.safe_load(response.text)

    def _load_from_file(self) -> dict[str, Any]:
        """Load OpenAPI spec from a file."""
        path = Path(self.spec_source)
        if not path.exists():
            raise FileNotFoundError(f"Spec file not found: {self.spec_source}")

        content = path.read_text()
        if path.suffix in (".yaml", ".yml"):
            return yaml.safe_load(content)
        elif path.suffix == ".json":
            return json.loads(content)
        else:
            # Try YAML first, then JSON
            try:
                return yaml.safe_load(content)
            except yaml.YAMLError:
                return json.loads(content)

    def _validate_spec(self) -> None:
        """Validate the loaded OpenAPI spec."""
        if not self._raw_spec:
            raise ValueError("Empty specification")

        if "openapi" not in self._raw_spec and "swagger" not in self._raw_spec:
            raise ValueError("Not a valid OpenAPI/Swagger specification")

        openapi_version = self._raw_spec.get("openapi", self._raw_spec.get("swagger", ""))
        if not openapi_version.startswith(("3.", "2.")):
            raise ValueError(f"Unsupported OpenAPI version: {openapi_version}")

        # Convert Swagger 2.0 to OpenAPI 3.0 format for internal processing
        if "swagger" in self._raw_spec and self._raw_spec["swagger"].startswith("2."):
            self._convert_swagger_to_openapi()

    def _convert_swagger_to_openapi(self) -> None:
        """Convert Swagger 2.0 spec to OpenAPI 3.0 format for unified processing."""
        spec = self._raw_spec

        # Convert host/basePath to servers
        if "host" in spec or "basePath" in spec:
            host = spec.pop("host", "localhost")
            base_path = spec.pop("basePath", "")
            schemes = spec.pop("schemes", ["https"])
            default_scheme = schemes[0] if schemes else "https"

            if "servers" not in spec:
                spec["servers"] = [{
                    "url": f"{default_scheme}://{host}{base_path}",
                    "description": "Default server (converted from Swagger 2.0)"
                }]

        # Convert definitions to components/schemas
        if "definitions" in spec:
            if "components" not in spec:
                spec["components"] = {}
            spec["components"]["schemas"] = spec.pop("definitions")

        # Convert parameters in body to requestBody
        for path, path_item in spec.get("paths", {}).items():
            for method, operation in path_item.items():
                if method.lower() not in ("get", "post", "put", "delete", "patch", "head", "options"):
                    continue

                # Find body parameter and convert to requestBody
                new_params = []
                body_param = None
                form_params = []

                for param in operation.get("parameters", []):
                    if param.get("in") == "body":
                        body_param = param
                    elif param.get("in") == "formData":
                        form_params.append(param)
                    else:
                        new_params.append(param)

                if body_param:
                    operation["requestBody"] = {
                        "description": body_param.get("description", ""),
                        "required": body_param.get("required", False),
                        "content": {
                            "application/json": {
                                "schema": body_param.get("schema", {"type": "object"})
                            }
                        }
                    }
                    operation["parameters"] = new_params

                # Convert formData to multipart/form-data
                if form_params:
                    properties = {}
                    required = []
                    for fp in form_params:
                        prop_name = fp.get("name")
                        properties[prop_name] = {
                            "type": fp.get("type", "string"),
                            "description": fp.get("description", "")
                        }
                        if fp.get("required"):
                            required.append(prop_name)
                        new_params.append({
                            "name": prop_name,
                            "in": "query",  # Fallback to query for MCP tools
                            "required": fp.get("required", False),
                            "schema": {"type": fp.get("type", "string")},
                            "description": fp.get("description", "")
                        })

                    operation["requestBody"] = {
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "properties": properties,
                                    "required": required if required else None
                                }
                            }
                        }
                    }
                    operation["parameters"] = new_params

        # Convert produces/consumes to content in responses
        produces = spec.pop("produces", ["application/json"])
        consumes = spec.pop("consumes", ["application/json"])

        for path, path_item in spec.get("paths", {}).items():
            for method, operation in path_item.items():
                if method.lower() not in ("get", "post", "put", "delete", "patch"):
                    continue

                # Convert response produces
                for status_code, response in operation.get("responses", {}).items():
                    if "schema" in response and "content" not in response:
                        schema = response.pop("schema")
                        response["content"] = {
                            produces[0] if produces else "application/json": {
                                "schema": schema
                            }
                        }

        # Mark as converted
        spec["_converted_from_swagger"] = True

    def extract_endpoints(self) -> list[dict[str, Any]]:
        """Extract all endpoints from the specification."""
        paths = self._raw_spec.get("paths", {})
        endpoints = []

        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.lower() not in ("get", "post", "put", "delete", "patch", "head", "options"):
                    continue

                endpoint = {
                    "path": path,
                    "method": method.lower(),
                    "operation_id": operation.get("operationId", f"{method}_{path.replace('/', '_')}"),
                    "summary": operation.get("summary"),
                    "description": operation.get("description"),
                    "parameters": self._extract_parameters(operation),
                    "request_body": operation.get("requestBody"),
                    "responses": self._extract_responses(operation),
                    "tags": operation.get("tags", []),
                    "deprecated": operation.get("deprecated", False),
                }
                endpoints.append(endpoint)

        return endpoints

    def _extract_parameters(self, operation: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract parameters from an operation."""
        parameters = []

        for param in operation.get("parameters", []):
            param_obj = {
                "name": param.get("name"),
                "type": self._get_parameter_type(param),
                "location": param.get("in"),
                "required": param.get("required", False),
                "description": param.get("description"),
                "default": param.get("schema", {}).get("default"),
                "enum": param.get("schema", {}).get("enum"),
                "schema": param.get("schema"),
            }
            parameters.append(param_obj)

        return parameters

    def _get_parameter_type(self, param: dict[str, Any]) -> str:
        """Get the type of a parameter."""
        schema = param.get("schema", {})
        if schema:
            return self._resolve_schema_type(schema)
        return param.get("type", "string")

    def _resolve_schema_type(self, schema: dict[str, Any]) -> str:
        """
        Resolve the type from a schema, handling complex schemas like allOf, anyOf, oneOf.

        Args:
            schema: OpenAPI schema dictionary

        Returns:
            Resolved type string
        """
        # Handle direct type
        if "type" in schema:
            return schema["type"]

        # Handle allOf - merge all schemas and use the first type found
        if "allOf" in schema:
            for sub_schema in schema["allOf"]:
                if "type" in sub_schema:
                    return sub_schema["type"]
                # Handle $ref in allOf
                if "$ref" in sub_schema:
                    ref_type = self._resolve_ref_type(sub_schema["$ref"])
                    if ref_type:
                        return ref_type
            return "object"  # Default for allOf

        # Handle anyOf/oneOf - use the first schema's type
        for key in ["anyOf", "oneOf"]:
            if key in schema and schema[key]:
                first_schema = schema[key][0]
                if "type" in first_schema:
                    return first_schema["type"]
                if "$ref" in first_schema:
                    ref_type = self._resolve_ref_type(first_schema["$ref"])
                    if ref_type:
                        return ref_type
            return "object"

        return "string"  # Default fallback

    def _resolve_ref_type(self, ref: str) -> str | None:
        """
        Resolve a $ref to its type.

        Args:
            ref: JSON reference string (e.g., "#/components/schemas/User")

        Returns:
            Type string or None
        """
        if not ref.startswith("#/"):
            return None

        parts = ref[2:].split("/")
        current = self._raw_spec
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        if isinstance(current, dict) and "type" in current:
            return current["type"]
        return None

    def _extract_responses(self, operation: dict[str, Any]) -> dict[str, dict[str, Any]]:
        """Extract responses from an operation."""
        responses = {}

        for status_code, response in operation.get("responses", {}).items():
            responses[status_code] = {
                "status_code": int(status_code) if status_code != "default" else 200,
                "description": response.get("description", ""),
                "content_type": self._get_response_content_type(response),
                "schema": self._get_response_schema(response),
            }

        return responses

    def _get_response_content_type(self, response: dict[str, Any]) -> str:
        """Get the content type of a response."""
        content = response.get("content", {})
        for content_type in ["application/json", "application/xml", "text/plain"]:
            if content_type in content:
                return content_type
        return "application/json"

    def _get_response_schema(self, response: dict[str, Any]) -> dict[str, Any] | None:
        """Get the schema of a response."""
        content = response.get("content", {})
        for content_type in ["application/json", "application/xml", "text/plain"]:
            if content_type in content and "schema" in content[content_type]:
                return content[content_type]["schema"]
        return None

    def to_api_spec(self) -> dict[str, Any]:
        """Convert the parsed spec to an API spec dictionary."""
        info = self._raw_spec.get("info", {})
        servers = self._raw_spec.get("servers", [])

        return {
            "title": info.get("title", "API"),
            "version": info.get("version", "1.0.0"),
            "description": info.get("description"),
            "base_url": servers[0]["url"] if servers else None,
            "endpoints": self.extract_endpoints(),
            "servers": servers,
            "authentication": self._extract_authentication(),
            "raw_spec": self._raw_spec,
        }

    def _extract_authentication(self) -> dict[str, Any]:
        """Extract authentication schemes from the spec."""
        components = self._raw_spec.get("components", {})
        security_schemes = components.get("securitySchemes", {})
        auth = {}

        for name, scheme in security_schemes.items():
            auth[name] = {
                "type": scheme.get("type"),
                "scheme": scheme.get("scheme"),
                "bearer_format": scheme.get("bearerFormat"),
                "description": scheme.get("description"),
            }

        return auth
