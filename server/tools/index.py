import datetime
import os
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from mars_img import get_mars_image_definition
from earth_img import get_earth_image_definition
from APOD_tool import  get_astronomy_picture_of_the_day_tool_defnition

mcp = FastMCP("weather")

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url):
    """Make request to NWS API with proper error handling"""
    header = {
        "User-agent" : USER_AGENT,
        "Accept" : "application/geo+json"
    }
    async with httpx.AsyncClient() as clint:
        try:
            response = await clint.get(url, headers=header, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return None

def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
    Event:{props.get ('event', 'Unknown')}
    Area: {props.get ('areaDes', 'Unknown')} 
    Severity: {props.get( 'severity', 'Unknown')}
    Description: {props.get('description', 'No description available')} 
    Instructions: {props.get('instruction', 'No specific instructions provided')}
    """

@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.
    Args:
    state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)
    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."
    if not data["features"]:
        return "No active alerts for this state."
    alerts = [format_alert(feature) for feature in data[ "features"]]
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_add(a, b) -> str:
    """Gives the addition is 2 numbers
    Args:
    a: Integer
    b: Integer
    """
    return int(a)+int(b)

@mcp.tool()
async def get_mars_image_tool(earth_date: Any = None, sol: Any = None, camera: Any = None) -> str:
    """Request to Mars Rover Image. Fetch any images on Mars Rover. Each rover has its own set of photos stored in the database, which can be queried separately. There are several possible queries that can be made against the API.\n
    Parameters:\n
        - earth_date: (optinal) Corresponding date on earth when the photo was taken. This should be in "YYYY-MM-DD" format. Default pass today's date\n
        - sol: (optinal) This is Martian sol of the Rover's mission. This is integer. Values can range from 0 to max found in endpoint. Default pass 1000.\n
        - camera: (optinal) Each camera has a unique function and perspective, and they are named as follows string:\n
            FHAZ: Front Hazard Avoidance Camera\n
            RHAZ: Rear Hazard Avoidance Camera\n
            MAST: Mast Camera\n
            CHEMCAM: Chemistry and Camera Complex\n
            MAHLI: Mars Hand Lens Imager\n
            MARDI: Mars Descent Imager\n
            NAVCAM: Navigation Camera\n
            PANCAM: Panoramic Camera\n
            MINITES: Miniature Thermal Emission Spectrometer (Mini-TES)\n
            You can use any one of the camera value at a time.\n
    """
    return await get_mars_image_definition(earth_date, sol, camera)

@mcp.tool()
async def get_earth_image_tool(earth_date: Any = None, type: Any = None) -> str:
    """Request to Earth Polychromatic Imaging Camera (EPIC) API. Fetch satellite images of Earth from NASA's DSCOVR satellite.\n
    Parameters:\n
        - earth_date: (optional) Date when the photo was taken. This should be in "YYYY-MM-DD" format. If not provided, will get latest available images.\n
        - type: (optional) Type of image to retrieve. Options are:\n
            "natural" - Natural color images (default)\n
            "enhanced" - Enhanced color images\n
            "cloud" - Cloud color images
    """
    # TODO: Update the earth image tool description from github

    return await get_earth_image_definition(earth_date, type)

@mcp.tool()
async def get_astronomy_picture_of_the_day_tool(date: Any = None, start_date: Any = None, end_date: Any = None, count: Any = None) -> str:
    """
    Gets the Astronomy Picture of the Day (APOD) from the NASA website.

    Parameters:
    date: (YYYY-MM-DD). Default is today. The date of the APOD image to retrieve
    start_date: (YYYY-MM-DD). Default is none. The start of a date range, when requesting date for a range of dates. Cannot be used with date.
    end_date: (YYYY-MM-DD).	Default is today.The end of the date range, when used with start_date.
    count:(int). Default is none. If this is specified then count randomly chosen images will be returned. Cannot be used with date or start_date and end_date.
    """
    return await get_astronomy_picture_of_the_day_tool_defnition(date, start_date, end_date, count)

if __name__ == "__main__":
    # mcp.run(transport="streamable-http")
    mcp.run(transport="studio")


# get_earth_image_tool(type="natural")
