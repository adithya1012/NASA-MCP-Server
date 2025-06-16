import datetime
import os
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from mars_img import get_mars_image_definition
mcp = FastMCP("weather")

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

MARS_BASE_API = "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?"
NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")

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
    # TODO: Update the earth image tool description from github
    # TODO: Move this function definition to different file for organized code. 
    """Request to Earth Polychromatic Imaging Camera (EPIC) API. Fetch satellite images of Earth from NASA's DSCOVR satellite.\n
    Parameters:\n
        - earth_date: (optional) Date when the photo was taken. This should be in "YYYY-MM-DD" format. If not provided, will get latest available images.\n
        - type: (optional) Type of image to retrieve. Options are:\n
            "natural" - Natural color images (default)\n
            "enhanced" - Enhanced color images\n
    """
    
    base_api = "https://epic.gsfc.nasa.gov/api/"
    
    # Build URL
    param_url = base_api
    
    # Handle image type
    if type:
        if type.lower() in ["natural", "enhanced", "aerosol", "cloud"]:
            param_url += f"{type.lower()}/"
        else:
            return f"Error: Invalid type '{type}'. Valid options: 'natural', 'enhanced','aerosol', 'cloud'"
    else:
        param_url += "natural/"
        
    
    # Handle date parameter
    if earth_date:
        try:
            datetime.datetime.strptime(earth_date, "%Y-%m-%d")
            year, month, day = earth_date.split("-")
            param_url += f"date/{year}-{month}-{day}"
        except ValueError:
            return "Error: earth_date must be in YYYY-MM-DD format"
    
    try:
        print(f"Calling EARTH API FUNCTION with URL: {param_url}")
        
        # Make API request
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=30.0,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
        ) as client:
            response = await client.get(param_url, timeout=30.0)
            # return param_url
            response.raise_for_status()
            
            data = response.json()
            
            # Check if images were found
            if not data or len(data) == 0:
                return "No images found for the specified parameters"
            
            # Extract image information from first result
            first_image = data[0]
            image_date = first_image["date"]
            image_name = first_image["image"]
            caption = first_image.get("caption", "No caption available")
            
            # Parse date to build archive URL
            # Date format is typically "2015-10-31 00:36:33" or "2015-10-31"
            date_parts = image_date.split("-")
            year = date_parts[0]
            month = date_parts[1]
            
            # Handle day extraction (might have time component)
            day_part = date_parts[2]
            if " " in day_part:
                day = day_part.split(" ")[0]
            else:
                day = day_part
            
            # Use the type from URL (natural or enhanced)
            image_type = "natural"
            if "enhanced" in param_url:
                image_type = "enhanced"
            elif "aerosol" in param_url:
                image_type = "aerosol"
            elif "cloud" in param_url:
                image_type = "cloud"
            
            
            # Build final image URL
            final_image_url = f"https://epic.gsfc.nasa.gov/archive/{image_type}/{year}/{month}/{day}/png/{image_name}.png"
            
            # Build result string
            result = f"Earth Image Found!\n"
            result += f"Image URL: {final_image_url}\n"
            result += f"Caption: {caption}\n"
            result += f"Date: {image_date}\n"
            result += f"Image Type: {image_type.title()}\n"
            result += f"Total images available: {len(data)}"
            
            return result+" "+ param_url
            # return param_url
            
    except httpx.TimeoutException:
        return "Error: Request timed out. Please try again."
    except httpx.HTTPStatusError as e:
        return f"Error: HTTP {e.response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"
    
if __name__ == "__main__":
    mcp.run()


# get_earth_image_tool(type="natural")