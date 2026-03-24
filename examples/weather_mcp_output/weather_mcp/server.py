"""
weather-mcp MCP Server

MCP server for Weather API
"""

from typing import Any

import httpx
from fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP(name="weather-mcp")

# Configuration
BASE_URL = "https://api.weather.example.com"

# HTTP client for API requests
_client: httpx.AsyncClient | None = None


def get_client() -> httpx.AsyncClient:
    """Get or create the HTTP client."""
    global _client
    if _client is None:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "weather-mcp/1.0.0",
        }
        _client = httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=30.0)
    return _client


@mcp.tool()
async def get_current_weather(
    location: str,
    units: str = None
) -> dict[str, Any]:
    """
    Get current weather
    
    Retrieve current weather conditions for a location
    
    API Endpoint: GET /weather/current
    """
    client = get_client()
    
    # Build request parameters
    path_params = {}
    query_params = {}
    headers = {}
    
    if location is not None:
        query_params["location"] = location
    if units is not None:
        query_params["units"] = units
    
    # Build the URL path
    path = "/weather/current"
    
    # Make the API request
    response = await client.get(
        path,
        params=query_params if query_params else None,
    )
    response.raise_for_status()
    
    return response.json()


@mcp.tool()
async def get_weather_forecast(
    days: int,
    location: str
) -> dict[str, Any]:
    """
    Get weather forecast
    
    Retrieve weather forecast for a specified number of days
    
    API Endpoint: GET /weather/forecast/{days}
    """
    client = get_client()
    
    # Build request parameters
    path_params = {}
    query_params = {}
    headers = {}
    
    if days is not None:
        path_params["days"] = days
    if location is not None:
        query_params["location"] = location
    
    # Build the URL path
    path = "/weather/forecast/{days}"
    path = path.replace("{", "").replace("}", "").replace("days", str(path_params.get("days", "")))
    
    # Make the API request
    response = await client.get(
        path,
        params=query_params if query_params else None,
    )
    response.raise_for_status()
    
    return response.json()




if __name__ == "__main__":
    # Run the MCP server
    mcp.run()