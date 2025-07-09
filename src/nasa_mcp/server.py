# src/nasa_mcp/server.py
import asyncio
import sys
from typing import Any
from mcp.server.fastmcp import FastMCP
from .nasa_api import get_earth_image_definition, get_gibs_image_definition, get_gibs_layers_definition, get_mars_image_definition, get_astronomy_picture_of_the_day_tool_defnition, get_neo_feed_definition, mcp_analyze_image_tool_definition

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

@mcp.tool()
async def get_earth_image_tool(earth_date: Any = None, type: Any = None, limit: int = 1) -> str:
    """Request to Earth Polychromatic Imaging Camera (EPIC) API. Fetch satellite images of Earth from NASA's DSCOVR satellite.\n
    Parameters:\n
        - earth_date: (optional) Date when the photo was taken. This should be in "YYYY-MM-DD" format. If not provided, will get latest available images.\n
        - type: (optional) Type of image to retrieve. Options are:\n
            "natural" - Natural color images (default)\n
            "enhanced" - Enhanced color images\n
            "aerosol" - Aerosol images\n
            "cloud" - Cloud images\n
        - limit: (optional) Number of images to retrieve. Default is 1. Maximum recommended is 10.\n
    """
    return await get_earth_image_definition(earth_date, type, limit)

@mcp.tool()
async def get_gibs_image(
    layer: str = "MODIS_Terra_CorrectedReflectance_TrueColor",
    bbox: str = "-180,-90,180,90",
    date: Any = None,
    width: int = 512,
    height: int = 512,
    format: str = "image/png",
    projection: str = "epsg4326"
) -> str:
    """Request to NASA GIBS (Global Imagery Browse Services) API. Fetch satellite imagery of Earth.
    
    Parameters:
        - layer: (string) The imagery layer to fetch. Popular options:
            "MODIS_Terra_CorrectedReflectance_TrueColor" - Terra satellite true color (default)
            "MODIS_Aqua_CorrectedReflectance_TrueColor" - Aqua satellite true color
            "VIIRS_SNPP_CorrectedReflectance_TrueColor" - VIIRS satellite true color
            "MODIS_Terra_CorrectedReflectance_Bands721" - Terra false color
            "MODIS_Aqua_CorrectedReflectance_Bands721" - Aqua false color
            "Reference_Labels_15m" - Political boundaries and labels
            "Reference_Features_15m" - Coastlines and water bodies
            "MODIS_Terra_Aerosol" - Aerosol optical depth
            "MODIS_Terra_Land_Surface_Temp_Day" - Land surface temperature
        - bbox: (string) Bounding box as "min_lon,min_lat,max_lon,max_lat". 
            Examples: "-180,-90,180,90" (whole world), "-125,25,-65,50" (USA), "0,40,40,70" (Europe)
        - date: (YYYY-MM-DD) Date for the imagery. If not provided, uses most recent available.
        - width: (int) Image width in pixels. Default 512. Max recommended 2048.
        - height: (int) Image height in pixels. Default 512. Max recommended 2048.
        - format: (string) Image format. Options: "image/png", "image/jpeg". Default "image/png".
        - projection: (string) Coordinate system. Options: "epsg4326" (Geographic), "epsg3857" (Web Mercator). Default "epsg4326".
    """
    return await get_gibs_image_definition(layer, bbox, date, width, height, format, projection)

@mcp.tool()
async def get_gibs_layers() -> str:
    """Get information about available GIBS layers and their capabilities."""
    return await get_gibs_layers_definition()

@mcp.tool()
async def get_image_analyze(image_url: str, max_size: int = 1024, quality: int = 85) -> str:
    """Fetch an image from URL and convert it to base64 for LLM analysis.
    Args:
        image_url: The URL of the image to analyze. (str)
        max_size: Maximum image size in pixels (width or height). Default: 1024
        quality: JPEG quality for compression (1-100). Default: 85
    Returns:
        Dict containing base64 image data and metadata
    """
    return await mcp_analyze_image_tool_definition(image_url, max_size, quality)

def main():
    """Main entry point for the server"""
    # Use stdio transport for standard MCP clients (Claude Desktop, VS Code)
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()