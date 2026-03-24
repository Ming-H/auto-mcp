"""
Example: Generate a Weather API MCP Server
"""

from pathlib import Path

from auto_mcp.core.generator import PythonMCPGenerator
from auto_mcp.core.parser import OpenAPIParser
from auto_mcp.core.types import APISpec, Language, MCPServerConfig

# Example OpenAPI spec for a weather API
WEATHER_API_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Weather API",
        "version": "1.0.0",
        "description": "A simple weather API for getting current weather and forecasts",
    },
    "servers": [
        {
            "url": "https://api.weather.example.com",
            "description": "Production server",
        }
    ],
    "paths": {
        "/weather/current": {
            "get": {
                "operationId": "get_current_weather",
                "summary": "Get current weather",
                "description": "Retrieve current weather conditions for a location",
                "tags": ["weather"],
                "parameters": [
                    {
                        "name": "location",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "City name or coordinates (lat,lon)",
                    },
                    {
                        "name": "units",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "string", "enum": ["metric", "imperial"]},
                        "description": "Unit system for measurements",
                    },
                ],
                "responses": {
                    "200": {
                        "description": "Weather data retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "location": {"type": "string"},
                                        "temperature": {"type": "number"},
                                        "condition": {"type": "string"},
                                        "humidity": {"type": "number"},
                                    }
                                }
                            }
                        }
                    }
                },
            }
        },
        "/weather/forecast/{days}": {
            "get": {
                "operationId": "get_weather_forecast",
                "summary": "Get weather forecast",
                "description": "Retrieve weather forecast for a specified number of days",
                "tags": ["weather"],
                "parameters": [
                    {
                        "name": "days",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer", "minimum": 1, "maximum": 7},
                        "description": "Number of days to forecast",
                    },
                    {
                        "name": "location",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "City name or coordinates (lat,lon)",
                    },
                ],
                "responses": {
                    "200": {
                        "description": "Forecast data retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "location": {"type": "string"},
                                        "forecast": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "date": {"type": "string"},
                                                    "high": {"type": "number"},
                                                    "low": {"type": "number"},
                                                    "condition": {"type": "string"},
                                                }
                                            },
                                        },
                                    }
                                }
                            }
                        }
                    }
                },
            }
        },
    },
}


def main() -> None:
    """Generate a Weather API MCP Server."""
    print("Generating Weather API MCP Server...")

    parser = OpenAPIParser(WEATHER_API_SPEC)
    parser.parse()
    spec_data = parser.to_api_spec()

    api_spec = APISpec(
        title=spec_data["title"],
        version=spec_data["version"],
        description=spec_data.get("description"),
        base_url=spec_data.get("base_url"),
        endpoints=spec_data["endpoints"],
    )

    config = MCPServerConfig(
        name="weather-mcp",
        version="1.0.0",
        description="MCP server for Weather API",
        language=Language.PYTHON,
        api_spec=api_spec,
        author="AutoMCP Example",
        license="MIT",
    )

    output_dir = Path("./examples/weather_mcp_output")
    generator = PythonMCPGenerator(config)
    generator.generate(output_dir)

    print(f"Generated MCP server at: {output_dir}")


if __name__ == "__main__":
    main()
