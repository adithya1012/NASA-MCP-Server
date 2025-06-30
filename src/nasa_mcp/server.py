# src/nasa_mcp/server.py
import asyncio
import sys
from typing import Any
from mcp.server.fastmcp import FastMCP
from .nasa_api import get_mars_image_definition, get_astronomy_picture_of_the_day_tool_defnition, get_neo_feed_definition

# Create FastMCP server instance
mcp = FastMCP("nasa-mcp-server")

@mcp.tool()
async def get_apod(date: Any = None, start_date: Any = None, end_date: Any = None, count: Any = None) -> str:
    """Gets the Astronomy Picture of the Day (APOD) from the NASA website.

    Parameters:
    date: (YYYY-MM-DD). Default is today. The date of the APOD image to retrieve
    start_date: (YYYY-MM-DD). Default is none. The start of a date range, when requesting date for a range of dates. Cannot be used with date.
    end_date: (YYYY-MM-DD).	Default is today.The end of the date range, when used with start_date.
    count: (int). Default is none. If this is specified then count randomly chosen images will be returned. Cannot be used with date or start_date and end_date.
    """
    return await get_astronomy_picture_of_the_day_tool_defnition(date, start_date, end_date, count)

@mcp.tool()
async def get_mars_image(earth_date: Any = None, sol: Any = None, camera: Any = None) -> str:
    """Request to Mars Rover Image. Fetch any images on Mars Rover. Each rover has its own set of photos stored in the database, which can be queried separately. There are several possible queries that can be made against the API.
    
    Parameters:
        - earth_date: (YYYY-MM-DD). Corresponding date on earth when the photo was taken. This should be in "YYYY-MM-DD" format. Default pass today's date
        - sol: (int). This is Martian sol of the Rover's mission. This is integer. Values can range from 0 to max found in endpoint. Default pass 1000.
        - camera: (string) Each camera has a unique function and perspective, and they are named as follows string:
            FHAZ: Front Hazard Avoidance Camera
            RHAZ: Rear Hazard Avoidance Camera
            MAST: Mast Camera
            CHEMCAM: Chemistry and Camera Complex
            MAHLI: Mars Hand Lens Imager
            MARDI: Mars Descent Imager
            NAVCAM: Navigation Camera
            PANCAM: Panoramic Camera
            MINITES: Miniature Thermal Emission Spectrometer (Mini-TES)
            You can use any one of the camera value at a time.
    """
    return await get_mars_image_definition(earth_date, sol, camera)


@mcp.tool()
async def get_neo_feed(start_date: Any = None, end_date: Any = None, limit_per_day: int = 2) -> str:
    """Gets Near Earth Objects (NEO) data from NASA's NeoWs API.
    Retrieves a list of asteroids based on their closest approach date to Earth.
    Maximum date range is 7 days. If no dates provided, returns next 7 days.
    
    Parameters:
    start_date: (YYYY-MM-DD). Default is today. The starting date for asteroid search
    end_date: (YYYY-MM-DD). Default is 7 days after start_date. The ending date for asteroid search
    limit_per_day: (int). Default is 2. Maximum number of asteroids to show per day to limit output size
    """
    return await get_neo_feed_definition(start_date, end_date, limit_per_day)

def main():
    """Main entry point for the server"""
    # Use stdio transport for standard MCP clients (Claude Desktop, VS Code)
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()