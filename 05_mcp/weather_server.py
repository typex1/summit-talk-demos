"""Minimal MCP server: exposes the weather toolbox over the Model Context Protocol.

Run standalone:  python weather_server.py   (stdio transport — a client launches it)
"""
from mcp.server.fastmcp import FastMCP

server = FastMCP("weather")


@server.tool()
def list_cities_on_route(route: str) -> dict:
    """List the major cities along a cycling route, in order."""
    routes = {"berlin-munich": ["Berlin", "Leipzig", "Nuremberg", "Munich"]}
    return {"cities": routes.get(route.lower(), [])}


@server.tool()
def get_weather(city: str) -> dict:
    """Get current weather for a city."""
    fake_db = {
        "berlin": {"temp_c": 22, "condition": "sunny"},
        "leipzig": {"temp_c": 21, "condition": "cloudy"},
        "nuremberg": {"temp_c": 17, "condition": "rain"},
        "munich": {"temp_c": 18, "condition": "rain"},
    }
    return fake_db.get(city.lower(), {"temp_c": 20, "condition": "unknown"})


if __name__ == "__main__":
    server.run()  # stdio transport
