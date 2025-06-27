# src/nasa_mcp/nasa_api.py
import datetime
import os
from typing import Any
import httpx

# Get NASA API key from environment variable (set by MCP client)
NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")
base_api = "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?"

async def get_mars_image_definition(earth_date: Any = None, sol: Any = None, camera: Any = None) -> str:
    """Request to Mars Rover Image. Fetch any images on Mars Rover. Each rover has its own set of photos stored in the database, which can be queried separately. There are several possible queries that can be made against the API.
    
    Parameters:
        - earth_date: (optional) Corresponding date on earth when the photo was taken. This should be in "YYYY-MM-DD" format. Default pass today's date
        - sol: (optional) This is Martian sol of the Rover's mission. This is integer. Values can range from 0 to max found in endpoint. Default pass 1000.
        - camera: (optional) Each camera has a unique function and perspective, and they are named as follows string:
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
    
    # Build parameters dictionary
    params = {}
    
    # Handle mutually exclusive date/sol parameters
    if sol is not None:
        if sol < 0:
            return "Error: sol must be a non-negative integer"
        params["sol"] = str(sol)
    elif earth_date:
        # Validate date format
        try:
            datetime.datetime.strptime(earth_date, "%Y-%m-%d")
            params["earth_date"] = earth_date
        except ValueError:
            return "Error: earth_date must be in YYYY-MM-DD format"
    else:
        # Default: use sol=1000 if neither is provided
        params["sol"] = "1000"
    
    # Handle camera parameter
    if camera:
        valid_cameras = [
            "FHAZ", "RHAZ", "MAST", "CHEMCAM", "MAHLI", 
            "MARDI", "NAVCAM", "PANCAM", "MINITES"
        ]
        camera_upper = camera.upper()
        if camera_upper in valid_cameras:
            params["camera"] = camera_upper
        else:
            return f"Error: Invalid camera '{camera}'. Valid options: {', '.join(valid_cameras)}"
    
    # Build URL parameters string
    param_url = ""
    for param_key, param_value in params.items():
        param_url += f"{param_key}={param_value}&"
    
    # Add page and API key
    param_url += f"page=1&api_key={NASA_API_KEY}"
    
    # Complete URL
    api_url = base_api + param_url
    
    try:
        # Make API request
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, timeout=30.0)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if photos were found
            if not data.get("photos") or len(data["photos"]) == 0:
                return "No images are found for the specified parameters"
            
            # Return first image URL
            first_image_url = data["photos"][0]["img_src"]
            
            # Optional: return additional info
            photo_info = data["photos"][0]
            result = f"Mars Rover Image Found!\n"
            result += f"Image URL: {first_image_url}\n"
            result += f"Camera: {photo_info['camera']['full_name']} ({photo_info['camera']['name']})\n"
            result += f"Earth Date: {photo_info['earth_date']}\n"
            result += f"Sol: {photo_info['sol']}\n"
            result += f"Total photos available: {len(data['photos'])}"
            
            return result
            
    except httpx.TimeoutException:
        return "Error: Request timed out. Please try again."
    except httpx.HTTPStatusError as e:
        return f"Error: HTTP {e.response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"