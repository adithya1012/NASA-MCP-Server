# src/nasa_mcp/nasa_api.py
import datetime
import os
from typing import Any
import httpx

# Get NASA API key from environment variable (set by MCP client)
NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")
MARS_API = "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?"
APOD_API = "https://api.nasa.gov/planetary/apod?"
NEOWS_API = "https://api.nasa.gov/neo/rest/v1/feed?"

async def get_mars_image_definition(earth_date: Any = None, sol: Any = None, camera: Any = None) -> str:
    """Request to Mars Rover Image. Fetch any images on Mars Rover. Each rover has its own set of photos stored in the database, which can be queried separately. There are several possible queries that can be made against the API."""
    
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
    api_url = MARS_API + param_url
    
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
    

async def get_astronomy_picture_of_the_day_tool_defnition(date: Any = None, start_date: Any = None, end_date: Any = None, count: Any = None) -> str:
    """Request to NASA Astronomy Picture of the Day API. Fetch astronomy pictures and their details."""
    
    # Build parameters dictionary
    params = {}
    
    # Validate mutually exclusive parameters
    if count is not None:
        if date and (start_date or end_date):
            return "Error: count cannot be used with date, start_date, or end_date"
        if count <= 0:
            return "Error: count must be a positive integer"
        params["count"] = str(count)
    elif start_date or end_date:
        if date:
            return "Error: date cannot be used with start_date or end_date"
        
        # Validate start_date
        if start_date:
            try:
                datetime.datetime.strptime(start_date, "%Y-%m-%d")
                params["start_date"] = start_date
            except ValueError:
                return "Error: start_date must be in YYYY-MM-DD format"
        
        # Validate end_date
        if end_date:
            try:
                datetime.datetime.strptime(end_date, "%Y-%m-%d")
                params["end_date"] = end_date
            except ValueError:
                return "Error: end_date must be in YYYY-MM-DD format"
    elif date:
        # Validate single date
        try:
            print(date)
            print(type(date))
            datetime.datetime.strptime(date, "%Y-%m-%d")
            params["date"] = date
        except ValueError:
            return "Error: date must be in YYYY-MM-DD format"
    
    # Build URL parameters string
    param_url = ""
    for param_key, param_value in params.items():
        param_url += f"{param_key}={param_value}&"
    
    # Add API key
    param_url += f"api_key={NASA_API_KEY}"
    
    # Complete URL
    api_url = APOD_API + param_url
    
    try:
        # Make API request
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, timeout=30.0)
            response.raise_for_status()
            
            data = response.json()
            
            # Handle both single image and multiple images response
            if isinstance(data, list):
                # Multiple images (from count or date range)
                if len(data) == 0:
                    return "No APOD images found for the specified parameters"
                
                result = f"Found {len(data)} APOD images:\n\n"
                for i, apod in enumerate(data, 1):
                    result += f"--- Image {i} ---\n"
                    result += f"Date: {apod.get('date', 'Unknown')}\n"
                    result += f"Title: {apod.get('title', 'No title')}\n"
                    
                    # Use hdurl if available, otherwise url
                    image_url = apod.get('hdurl') or apod.get('url', 'No image URL')
                    result += f"Image URL: {image_url}\n"
                    
                    explanation = apod.get('explanation', 'No explanation available')
                    result += f"Explanation: {explanation}\n\n"
                
                return result.strip()
            
            else:
                # Single image
                result = "NASA Astronomy Picture of the Day\n"
                result += f"Date: {data.get('date', 'Unknown')}\n"
                result += f"Title: {data.get('title', 'No title')}\n"
                
                # Use hdurl if available, otherwise url
                image_url = data.get('hdurl') or data.get('url', 'No image URL')
                result += f"Image URL: {image_url}\n"
                
                explanation = data.get('explanation', 'No explanation available')
                result += f"Explanation: {explanation}"
                
                return result
            
    except httpx.TimeoutException:
        return "Error: Request timed out. Please try again."
    except httpx.HTTPStatusError as e:
        return f"Error: HTTP {e.response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

async def get_neo_feed_definition(start_date: Any = None, end_date: Any = None, limit_per_day: int = 2) -> str:
    """Gets Near Earth Objects (NEO) data from NASA's NeoWs API.
    
    Retrieves a list of asteroids based on their closest approach date to Earth.
    Maximum date range is 7 days. If no dates provided, returns next 7 days.
    
    Parameters:
    start_date: (YYYY-MM-DD). Default is today. The starting date for asteroid search
    end_date: (YYYY-MM-DD). Default is 7 days after start_date. The ending date for asteroid search
    limit_per_day: (int). Default is 5. Maximum number of asteroids to show per day to limit output size
    """
    
    params = {}
    
    # Validate limit_per_day parameter
    if limit_per_day <= 0:
        return "Error: limit_per_day must be a positive integer"
    
    # Validate and process dates
    if start_date or end_date:
        # Validate start_date
        if start_date:
            try:
                start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                params["start_date"] = start_date
            except ValueError:
                return "Error: start_date must be in YYYY-MM-DD format"
            if end_date:
                try:
                    end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
                    params["end_date"] = end_date
                except ValueError:
                    return "Error: end_date must be in YYYY-MM-DD format"
                if (end_dt - start_dt).days > 7:
                    return "Error: Date range cannot exceed 7 days"
                elif end_dt < start_dt:
                    return "Error: end_date must be after start_date"
        else:
            return "Error: start_date must provided to use the end_date"
    
    # Build URL parameters string
    param_url = ""
    for param_key, param_value in params.items():
        param_url += f"{param_key}={param_value}&"
    
    # Add API key
    param_url += f"api_key={NASA_API_KEY}"
    
    # Complete URL
    api_url = NEOWS_API + param_url
    
    try:
        # Make API request
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, timeout=30.0)
            
            # Parse JSON response first to check for API error format
            data = response.json()
            
            # Check if the response contains an API error (even with HTTP 200)
            if "error_message" in data:
                return f"API Error: {data.get('error_message', 'Unknown error occurred')}"
            
            # Check for HTTP errors after parsing JSON
            response.raise_for_status()
            
            # Extract key information
            element_count = data.get('element_count', 0)
            near_earth_objects = data.get('near_earth_objects', {})
            
            if element_count == 0:
                return "No Near Earth Objects found for the specified date range"
            
            result = f"NASA Near Earth Objects (NEO) Feed\n"
            result += f"Total asteroids found: {element_count}\n"
            result += f"Showing up to {limit_per_day} asteroids per day\n"
            
            # Add date range info
            if params:
                date_range = f"Date range: {params.get('start_date', 'auto')} to {params.get('end_date', 'auto')}"
            else:
                date_range = "Date range: Next 7 days (default)"
            result += f"{date_range}\n\n"
            
            # Process each date's asteroids (limited per day)
            total_shown = 0
            for date_str, asteroids in near_earth_objects.items():
                # Limit asteroids per day
                limited_asteroids = asteroids[:limit_per_day]
                total_shown += len(limited_asteroids)
                
                result += f"=== {date_str} ({len(asteroids)} asteroids total, showing {len(limited_asteroids)}) ===\n"
                
                for i, asteroid in enumerate(limited_asteroids, 1):
                    result += f"\n--- Asteroid {i} ---\n"
                    result += f"Name: {asteroid.get('name', 'Unknown')}\n"
                    result += f"Absolute Magnitude: {asteroid.get('absolute_magnitude_h', 'Unknown')}\n"
                    
                    # Diameter estimates
                    diameter = asteroid.get('estimated_diameter', {})
                    km_diameter = diameter.get('kilometers', {})
                    if km_diameter:
                        min_km = km_diameter.get('estimated_diameter_min', 0)
                        max_km = km_diameter.get('estimated_diameter_max', 0)
                        result += f"Estimated Diameter: {min_km:.3f} - {max_km:.3f} km\n"
                    
                    # Hazard status
                    is_hazardous = asteroid.get('is_potentially_hazardous_asteroid', False)
                    result += f"Potentially Hazardous: {'Yes' if is_hazardous else 'No'}\n"
                    
                    # Close approach data
                    close_approach = asteroid.get('close_approach_data', [])
                    if close_approach:
                        approach = close_approach[0]  # Get the first (closest) approach
                        result += f"Close Approach Date: {approach.get('close_approach_date_full', 'Unknown')}\n"
                        
                        # Velocity
                        velocity = approach.get('relative_velocity', {})
                        if velocity:
                            km_per_hour = velocity.get('kilometers_per_hour', 'Unknown')
                            result += f"Relative Velocity: {km_per_hour} km/h\n"
                        
                        # Miss distance
                        miss_distance = approach.get('miss_distance', {})
                        if miss_distance:
                            km_distance = miss_distance.get('kilometers', 'Unknown')
                            lunar_distance = miss_distance.get('lunar', 'Unknown')
                            result += f"Miss Distance: {km_distance} km ({lunar_distance} lunar distances)\n"
                        
                        result += f"Orbiting Body: {approach.get('orbiting_body', 'Unknown')}\n"
                    
                    # NASA JPL URL for more details
                    jpl_url = asteroid.get('nasa_jpl_url', '')
                    if jpl_url:
                        result += f"More Details: {jpl_url}\n"
                
                result += "\n"
            
            # Add summary statistics
            hazardous_count = 0
            for asteroids in near_earth_objects.values():
                hazardous_count += sum(1 for ast in asteroids if ast.get('is_potentially_hazardous_asteroid', False))
            
            result += f"Summary:\n"
            result += f"Total asteroids in feed: {element_count}\n"
            result += f"Asteroids shown: {total_shown}\n"
            result += f"Potentially hazardous asteroids (total): {hazardous_count}\n"
            result += f"Non-hazardous asteroids (total): {element_count - hazardous_count}\n"
            
            return result.strip()
            
    except httpx.TimeoutException:
        return "Error: Request timed out. Please try again."
    except httpx.HTTPStatusError as e:
        try:
            # Try to parse JSON response for detailed error message
            error_data = e.response.json()
            if "error_message" in error_data:
                return f"API Error: {error_data.get('error_message', 'Unknown error occurred')}"
        except:
            # If JSON parsing fails, use generic HTTP error messages
            pass
        
        if e.response.status_code == 400:
            return "Error: Invalid date format or date range exceeds 7 days"
        elif e.response.status_code == 403:
            return "Error: Invalid API key"
        else:
            return f"Error: HTTP {e.response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"


async def get_earth_image_definition(earth_date: Any = None, type: Any = None, limit: int = 1) -> str:
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

    base_api = "https://epic.gsfc.nasa.gov/api/"
    
    # Validate limit parameter
    if limit < 1:
        return "Error: limit must be at least 1"
    if limit > 10:
        limit = 10  # Cap at 10 for reasonable response size
    
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
        # print(f"Calling EARTH API FUNCTION with URL: {param_url}")
        
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
            
            # Determine image type from URL
            image_type = "natural"
            if "enhanced" in param_url:
                image_type = "enhanced"
            elif "aerosol" in param_url:
                image_type = "aerosol"
            elif "cloud" in param_url:
                image_type = "cloud"
            
            # Get the requested number of images (or all available if less than limit)
            images_to_process = data[:limit]
            
            # Build result string
            result = f"Earth Image{'s' if len(images_to_process) > 1 else ''} Found!!!!!!\n"
            result += f"Image Type: {image_type.title()}\n"
            result += f"Images returned: {len(images_to_process)} of {len(data)} available\n\n"
            
            # Process each image
            for i, image_data in enumerate(images_to_process, 1):
                image_date = image_data["date"]
                image_name = image_data["image"]
                caption = image_data.get("caption", "No caption available")
                
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
                
                # Build final image URL
                final_image_url = f"https://epic.gsfc.nasa.gov/archive/{image_type}/{year}/{month}/{day}/png/{image_name}.png"
                
                # Add image information to result
                result += f"Image {i}:\n"
                result += f"  URL: {final_image_url}\n"
                result += f"  Date: {image_date}\n"
                result += f"  Caption: {caption}\n"
                
                # Add separator between images (except for the last one)
                if i < len(images_to_process):
                    result += "\n"
            
            return result + " " + param_url
            
    except httpx.TimeoutException:
        return "Error: Request timed out. Please try again."
    except httpx.HTTPStatusError as e:
        return f"Error: HTTP {e.response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"
    

async def get_gibs_image_definition(
    layer: str = "MODIS_Terra_CorrectedReflectance_TrueColor",
    bbox: str = "-180,-90,180,90",
    date = None,
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
    
    # Validate parameters
    valid_formats = ["image/png", "image/jpeg"]
    if format not in valid_formats:
        return f"Error: Invalid format '{format}'. Valid options: {', '.join(valid_formats)}"
    
    valid_projections = ["epsg4326", "epsg3857"]
    if projection.lower() not in valid_projections:
        return f"Error: Invalid projection '{projection}'. Valid options: {', '.join(valid_projections)}"
    
    # Validate dimensions
    if width < 1 or width > 2048:
        return "Error: width must be between 1 and 2048 pixels"
    if height < 1 or height > 2048:
        return "Error: height must be between 1 and 2048 pixels"
    
    # Validate bounding box format
    try:
        bbox_parts = bbox.split(",")
        if len(bbox_parts) != 4:
            return "Error: bbox must be in format 'min_lon,min_lat,max_lon,max_lat'"
        
        min_lon, min_lat, max_lon, max_lat = map(float, bbox_parts)
        
        # Basic validation
        if min_lon >= max_lon or min_lat >= max_lat:
            return "Error: Invalid bounding box coordinates"
        if min_lon < -180 or max_lon > 180 or min_lat < -90 or max_lat > 90:
            return "Error: Coordinates must be within valid ranges (lon: -180 to 180, lat: -90 to 90)"
            
    except ValueError:
        return "Error: bbox coordinates must be valid numbers"
    
    # Validate date format if provided
    if date:
        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return "Error: date must be in YYYY-MM-DD format"
    
    # Build API URL
    projection_lower = projection.lower()
    base_url = f"https://gibs.earthdata.nasa.gov/wms/{projection_lower}/best/wms.cgi"
    
    # Build parameters
    params = {
        "SERVICE": "WMS",
        "REQUEST": "GetMap",
        "VERSION": "1.3.0",
        "LAYERS": layer,
        "BBOX": bbox,
        "WIDTH": str(width),
        "HEIGHT": str(height),
        "FORMAT": format,
        "CRS": f"EPSG:{projection_lower[4:]}"  # Convert epsg4326 to EPSG:4326
    }
    
    # Add time parameter if date is provided
    if date:
        params["TIME"] = date
    
    # Build query string
    query_string = "&".join([f"{key}={value}" for key, value in params.items()])
    final_url = f"{base_url}?{query_string}"
    
    try:
        # Make API request to check if the image is available
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=30.0,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        ) as client:
            response = await client.get(final_url, timeout=30.0)
            response.raise_for_status()
            
            # Check if response is an image
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                # If not an image, it might be an error response
                error_text = response.text
                if 'ServiceException' in error_text or 'Error' in error_text:
                    return f"Error: GIBS service returned an error. Please check your parameters."
                return f"Error: Unexpected response type: {content_type}"
            
            # Calculate approximate area covered
            area_width = abs(max_lon - min_lon)
            area_height = abs(max_lat - min_lat)
            
            # Build result
            result = f"GIBS Satellite Image Retrieved!\n"
            result += f"Image URL: {final_url}\n"
            result += f"Layer: {layer}\n"
            result += f"Date: {date if date else 'Most recent available'}\n"
            result += f"Bounding Box: {bbox}\n"
            result += f"Coverage Area: {area_width:.2f}° longitude × {area_height:.2f}° latitude\n"
            result += f"Image Size: {width}×{height} pixels\n"
            result += f"Format: {format}\n"
            result += f"Projection: {projection.upper()}\n"
            result += f"Image Size: {len(response.content)} bytes"
            
            return result
            
    except httpx.TimeoutException:
        return "Error: Request timed out. Please try again."
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            return "Error: Bad request. Please check your parameters (layer name, bbox, date, etc.)"
        elif e.response.status_code == 404:
            return "Error: Layer not found or no data available for the specified date/area"
        else:
            return f"Error: HTTP {e.response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"


async def get_gibs_layers_definition() -> str:
    """Get information about available GIBS layers and their capabilities."""
    
    layers_info = {
        "True Color Imagery": [
            "MODIS_Terra_CorrectedReflectance_TrueColor",
            "MODIS_Aqua_CorrectedReflectance_TrueColor", 
            "VIIRS_SNPP_CorrectedReflectance_TrueColor",
            "VIIRS_NOAA20_CorrectedReflectance_TrueColor"
        ],
        "False Color Imagery": [
            "MODIS_Terra_CorrectedReflectance_Bands721",
            "MODIS_Aqua_CorrectedReflectance_Bands721",
            "VIIRS_SNPP_CorrectedReflectance_Bands_M11-I2-I1",
            "VIIRS_NOAA20_CorrectedReflectance_Bands_M11-I2-I1"
        ],
        "Environmental Data": [
            "MODIS_Terra_Aerosol",
            "MODIS_Aqua_Aerosol",
            "MODIS_Terra_Land_Surface_Temp_Day",
            "MODIS_Terra_Land_Surface_Temp_Night",
            "MODIS_Terra_Sea_Ice",
            "MODIS_Terra_Snow_Cover"
        ],
        "Reference Data": [
            "Reference_Labels_15m",
            "Reference_Features_15m",
            "Coastlines_15m",
            "SRTM_GL1_Hillshade"
        ]
    }
    
    result = "Available GIBS Layers:\n\n"
    
    for category, layers in layers_info.items():
        result += f"{category}:\n"
        for layer in layers:
            result += f"  - {layer}\n"
        result += "\n"
    
    result += "Popular Bounding Boxes:\n"
    result += "  - World: -180,-90,180,90\n"
    result += "  - North America: -170,15,-50,75\n"
    result += "  - Europe: -25,35,45,70\n"
    result += "  - Asia: 60,-10,150,55\n"
    result += "  - Australia: 110,-45,160,-10\n"
    result += "  - Africa: -25,-40,55,40\n"
    result += "  - South America: -85,-60,-30,15\n\n"
    
    result += "Usage Tips:\n"
    result += "- Use epsg4326 for geographic data, epsg3857 for web mapping\n"
    result += "- PNG format preserves transparency, JPEG is smaller file size\n"
    result += "- Date format: YYYY-MM-DD (not all layers support all dates)\n"
    result += "- Smaller bounding boxes provide higher detail\n"
    result += "- Maximum recommended image size: 2048x2048 pixels"
    
    return result