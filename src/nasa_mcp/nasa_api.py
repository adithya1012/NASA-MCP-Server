# src/nasa_mcp/nasa_api.py
import datetime
import os
from typing import Any, Dict, Union
import httpx
import base64
import requests
import io
from PIL import Image
import mcp.types as types

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
            
            # Return first image URL and info
            first_image_url = data["photos"][0]["img_src"]
            photo_info = data["photos"][0]
            
            # Build consistent response format
            result = {
                "description": f"Mars Rover Image Found!\nCamera: {photo_info['camera']['full_name']} ({photo_info['camera']['name']})\nEarth Date: {photo_info['earth_date']}\nSol: {photo_info['sol']}\nTotal photos available: {len(data['photos'])}",
                "resource": {
                    "uri": first_image_url,
                    "mimeType": "image/jpeg",
                    "name": f"Mars_Rover_{photo_info['camera']['name']}_{photo_info['earth_date']}_Sol{photo_info['sol']}"
                }
            }
            
            return str(result)
            
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
                
                # For multiple images, return the first one with info about others
                first_apod = data[0]
                image_url = first_apod.get('hdurl') or first_apod.get('url', '')
                
                # Determine mime type based on URL
                mime_type = "image/jpeg"
                if image_url.lower().endswith('.png'):
                    mime_type = "image/png"
                elif image_url.lower().endswith('.gif'):
                    mime_type = "image/gif"
                elif 'youtube.com' in image_url.lower() or 'vimeo.com' in image_url.lower():
                    mime_type = "video/mp4"
                
                description = f"Found {len(data)} APOD images. Showing first image:\n"
                description += f"Date: {first_apod.get('date', 'Unknown')}\n"
                description += f"Title: {first_apod.get('title', 'No title')}\n"
                description += f"Explanation: {first_apod.get('explanation', 'No explanation available')}"
                
                result = {
                    "description": description,
                    "resource": {
                        "uri": image_url,
                        "mimeType": mime_type,
                        "name": f"APOD_{first_apod.get('date', 'unknown')}_{first_apod.get('title', 'untitled').replace(' ', '_')[:50]}"
                    }
                }
                
                return str(result)
            
            else:
                # Single image
                image_url = data.get('hdurl') or data.get('url', '')
                
                # Determine mime type based on URL
                mime_type = "image/jpeg"
                if image_url.lower().endswith('.png'):
                    mime_type = "image/png"
                elif image_url.lower().endswith('.gif'):
                    mime_type = "image/gif"
                elif 'youtube.com' in image_url.lower() or 'vimeo.com' in image_url.lower():
                    mime_type = "video/mp4"
                
                description = f"NASA Astronomy Picture of the Day\n"
                description += f"Date: {data.get('date', 'Unknown')}\n"
                description += f"Title: {data.get('title', 'No title')}\n"
                description += f"Explanation: {data.get('explanation', 'No explanation available')}"
                
                result = {
                    "description": description,
                    "resource": {
                        "uri": image_url,
                        "mimeType": mime_type,
                        "name": f"APOD_{data.get('date', 'unknown')}_{data.get('title', 'untitled').replace(' ', '_')[:50]}"
                    }
                }
                
                return str(result)
            
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
            
            # Build description with summary and detailed info
            description = f"NASA Near Earth Objects (NEO) Feed\n"
            description += f"Total asteroids found: {element_count}\n"
            description += f"Showing up to {limit_per_day} asteroids per day\n"
            
            # Add date range info
            if params:
                date_range = f"Date range: {params.get('start_date', 'auto')} to {params.get('end_date', 'auto')}"
            else:
                date_range = "Date range: Next 7 days (default)"
            description += f"{date_range}\n\n"
            
            # Process each date's asteroids (limited per day)
            total_shown = 0
            for date_str, asteroids in near_earth_objects.items():
                # Limit asteroids per day
                limited_asteroids = asteroids[:limit_per_day]
                total_shown += len(limited_asteroids)
                
                description += f"=== {date_str} ({len(asteroids)} asteroids total, showing {len(limited_asteroids)}) ===\n"
                
                for i, asteroid in enumerate(limited_asteroids, 1):
                    description += f"\n--- Asteroid {i} ---\n"
                    description += f"Name: {asteroid.get('name', 'Unknown')}\n"
                    description += f"Absolute Magnitude: {asteroid.get('absolute_magnitude_h', 'Unknown')}\n"
                    
                    # Diameter estimates
                    diameter = asteroid.get('estimated_diameter', {})
                    km_diameter = diameter.get('kilometers', {})
                    if km_diameter:
                        min_km = km_diameter.get('estimated_diameter_min', 0)
                        max_km = km_diameter.get('estimated_diameter_max', 0)
                        description += f"Estimated Diameter: {min_km:.3f} - {max_km:.3f} km\n"
                    
                    # Hazard status
                    is_hazardous = asteroid.get('is_potentially_hazardous_asteroid', False)
                    description += f"Potentially Hazardous: {'Yes' if is_hazardous else 'No'}\n"
                    
                    # Close approach data
                    close_approach = asteroid.get('close_approach_data', [])
                    if close_approach:
                        approach = close_approach[0]  # Get the first (closest) approach
                        description += f"Close Approach Date: {approach.get('close_approach_date_full', 'Unknown')}\n"
                        
                        # Velocity
                        velocity = approach.get('relative_velocity', {})
                        if velocity:
                            km_per_hour = velocity.get('kilometers_per_hour', 'Unknown')
                            description += f"Relative Velocity: {km_per_hour} km/h\n"
                        
                        # Miss distance
                        miss_distance = approach.get('miss_distance', {})
                        if miss_distance:
                            km_distance = miss_distance.get('kilometers', 'Unknown')
                            lunar_distance = miss_distance.get('lunar', 'Unknown')
                            description += f"Miss Distance: {km_distance} km ({lunar_distance} lunar distances)\n"
                        
                        description += f"Orbiting Body: {approach.get('orbiting_body', 'Unknown')}\n"
                    
                    # NASA JPL URL for more details
                    jpl_url = asteroid.get('nasa_jpl_url', '')
                    if jpl_url:
                        description += f"More Details: {jpl_url}\n"
                
                description += "\n"
            
            # Add summary statistics
            hazardous_count = 0
            for asteroids in near_earth_objects.values():
                hazardous_count += sum(1 for ast in asteroids if ast.get('is_potentially_hazardous_asteroid', False))
            
            description += f"Summary:\n"
            description += f"Total asteroids in feed: {element_count}\n"
            description += f"Asteroids shown: {total_shown}\n"
            description += f"Potentially hazardous asteroids (total): {hazardous_count}\n"
            description += f"Non-hazardous asteroids (total): {element_count - hazardous_count}\n"
            
            # Return consistent format (no image for NEO data, so no resource)
            result = {
                "description": description.strip(),
                "resource": {
                    "uri": api_url,
                    "mimeType": "application/json",
                    "name": f"NEO_Feed_{params.get('start_date', 'auto')}_{params.get('end_date', 'auto')}"
                }
            }
            
            return str(result)
            
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
            
            # For consistent format, return the first image with info about others
            first_image = images_to_process[0]
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
            
            # Build final image URL for the first image
            final_image_url = f"https://epic.gsfc.nasa.gov/archive/{image_type}/{year}/{month}/{day}/png/{image_name}.png"
            
            # Build description
            description = f"Earth Image{'s' if len(images_to_process) > 1 else ''} Found!\n"
            description += f"Image Type: {image_type.title()}\n"
            description += f"Images returned: {len(images_to_process)} of {len(data)} available\n"
            description += f"Showing first image:\n"
            description += f"Date: {image_date}\n"
            description += f"Caption: {caption}"
            
            # Return consistent format
            result = {
                "description": description,
                "resource": {
                    "uri": final_image_url,
                    "mimeType": "image/png",
                    "name": f"Earth_{image_type}_{year}{month}{day}_{image_name}"
                }
            }
            
            return str(result)
            
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
            
            # Build description
            description = f"GIBS Satellite Image Retrieved!\n"
            description += f"Layer: {layer}\n"
            description += f"Date: {date if date else 'Most recent available'}\n"
            description += f"Bounding Box: {bbox}\n"
            description += f"Coverage Area: {area_width:.2f}° longitude × {area_height:.2f}° latitude\n"
            description += f"Image Size: {width}×{height} pixels\n"
            description += f"Format: {format}\n"
            description += f"Projection: {projection.upper()}\n"
            description += f"Image Size: {len(response.content)} bytes"
            
            # Return consistent format
            result = {
                "description": description,
                "resource": {
                    "uri": final_url,
                    "mimeType": format,
                    "name": f"GIBS_{layer}_{date if date else 'latest'}_{width}x{height}"
                }
            }
            
            return str(result)
            
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
    
    description = "Available GIBS Layers:\n\n"
    
    for category, layers in layers_info.items():
        description += f"{category}:\n"
        for layer in layers:
            description += f"  - {layer}\n"
        description += "\n"
    
    description += "Popular Bounding Boxes:\n"
    description += "  - World: -180,-90,180,90\n"
    description += "  - North America: -170,15,-50,75\n"
    description += "  - Europe: -25,35,45,70\n"
    description += "  - Asia: 60,-10,150,55\n"
    description += "  - Australia: 110,-45,160,-10\n"
    description += "  - Africa: -25,-40,55,40\n"
    description += "  - South America: -85,-60,-30,15\n\n"
    
    description += "Usage Tips:\n"
    description += "- Use epsg4326 for geographic data, epsg3857 for web mapping\n"
    description += "- PNG format preserves transparency, JPEG is smaller file size\n"
    description += "- Date format: YYYY-MM-DD (not all layers support all dates)\n"
    description += "- Smaller bounding boxes provide higher detail\n"
    description += "- Maximum recommended image size: 2048x2048 pixels"
    
    # Return consistent format
    result = {
        "description": description,
        "resource": {
            "uri": "https://gibs.earthdata.nasa.gov/",
            "mimeType": "text/html",
            "name": "GIBS_Layers_Documentation"
        }
    }
    
    return str(result)

# def analyze_image_from_url(image_url: str, max_size: int = 1024, quality: int = 85) -> dict:
#     """
#     Fetch an image from URL and convert it to base64 for LLM analysis.
    
#     Args:
#         image_url: The URL of the image to analyze
#         max_size: Maximum image size in pixels (width or height). Default: 1024
#         quality: JPEG quality for compression (1-100). Default: 85
    
#     Returns:
#         Dict containing base64 image data and metadata
#     """
#     try:
#         # Fetch the image
#         response = requests.get(image_url, timeout=30)
#         response.raise_for_status()
        
#         # Verify it's an image
#         content_type = response.headers.get('content-type', '')
#         if not content_type.startswith('image/'):
#             raise ValueError(f"URL does not point to an image. Content-Type: {content_type}")
        
#         # Open and process the image
#         image_data = io.BytesIO(response.content)
#         image = Image.open(image_data)
        
#         # Convert to RGB if necessary (for JPEG compatibility)
#         if image.mode in ('RGBA', 'LA', 'P'):
#             image = image.convert('RGB')
        
#         # Resize if too large
#         original_dimensions = (image.width, image.height)
#         if image.width > max_size or image.height > max_size:
#             image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
#         # Convert to base64
#         output_buffer = io.BytesIO()
        
#         # Determine format based on original or use JPEG for compression
#         if content_type == 'image/png' and image.mode == 'RGBA':
#             image.save(output_buffer, format='PNG')
#             mime_type = 'image/png'
#         else:
#             image.save(output_buffer, format='JPEG', quality=quality)
#             mime_type = 'image/jpeg'
        
#         image_base64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
        
#         # Get image info
#         original_size = len(response.content)
#         compressed_size = len(output_buffer.getvalue())
        
#         return {
#             "success": True,
#             "base64_data": image_base64,
#             "mime_type": mime_type,
#             "original_url": image_url,
#             "original_dimensions": original_dimensions,
#             "processed_dimensions": (image.width, image.height),
#             "original_size_bytes": original_size,
#             "compressed_size_bytes": compressed_size,
#             "compression_ratio": (1 - compressed_size/original_size)*100,
#             "data_uri": f"data:{mime_type};base64,{image_base64}"
#         }
        
#     except requests.RequestException as e:
#         return {"success": False, "error": f"Failed to fetch image: {str(e)}"}
#     except Image.UnidentifiedImageError:
#         return {"success": False, "error": "Unable to process the image. Invalid image format."}
#     except Exception as e:
#         return {"success": False, "error": f"Error processing image: {str(e)}"}

# async def mcp_analyze_image_tool_definition(image_url: str, max_size: int = 1024, quality: int = 85):
#     """
#     MCP tool function that returns the image in a format the LLM can analyze.
#     """
#     result = analyze_image_from_url(image_url, max_size, quality)
    
#     if result["success"]:
#         return {
#             "type": "resource",
#             "resource": {
#                 "uri": result["data_uri"],
#                 "mimeType": result["mime_type"],
#                 "name": "Image for Analysis"
#             },
#             "metadata": {
#                 "original_url": result["original_url"],
#                 "dimensions": f"{result['processed_dimensions'][0]}×{result['processed_dimensions'][1]}",
#                 "original_size": f"{result['original_size_bytes']:,} bytes",
#                 "compressed_size": f"{result['compressed_size_bytes']:,} bytes",
#                 "compression_ratio": f"{result['compression_ratio']:.1f}%"
#             }
#         }
#     else:
#         return {
#             "type": "text",
#             "text": f"Error: {result['error']}"
#         }

def analyze_image_from_url(image_url: str, max_size: int = 1024, quality: int = 85) -> dict:
    """
    Fetch an image from URL and convert it to base64 for LLM analysis.
    
    Args:
        image_url: The URL of the image to analyze
        max_size: Maximum image size in pixels (width or height). Default: 1024
        quality: JPEG quality for compression (1-100). Default: 85
    
    Returns:
        Dict containing base64 image data and metadata
    """
    try:
        # Fetch the image
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()
        
        # Verify it's an image
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            raise ValueError(f"URL does not point to an image. Content-Type: {content_type}")
        
        # Open and process the image
        image_data = io.BytesIO(response.content)
        image = Image.open(image_data)
        
        # Convert to RGB if necessary (for JPEG compatibility)
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        
        # Resize if too large
        original_dimensions = (image.width, image.height)
        if image.width > max_size or image.height > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Convert to base64
        output_buffer = io.BytesIO()
        
        # Determine format based on original or use JPEG for compression
        if content_type == 'image/png' and image.mode == 'RGBA':
            image.save(output_buffer, format='PNG')
            mime_type = 'image/png'
        else:
            image.save(output_buffer, format='JPEG', quality=quality)
            mime_type = 'image/jpeg'
        
        image_base64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
        
        # Get image info
        original_size = len(response.content)
        compressed_size = len(output_buffer.getvalue())
        
        return {
            "success": True,
            "base64_data": image_base64,
            "mime_type": mime_type,
            "original_url": image_url,
            "original_dimensions": original_dimensions,
            "processed_dimensions": (image.width, image.height),
            "original_size_bytes": original_size,
            "compressed_size_bytes": compressed_size,
            "compression_ratio": (1 - compressed_size/original_size)*100,
            "data_uri": f"data:{mime_type};base64,{image_base64}"
        }
        
    except requests.RequestException as e:
        return {"success": False, "error": f"Failed to fetch image: {str(e)}"}
    except Image.UnidentifiedImageError:
        return {"success": False, "error": "Unable to process the image. Invalid image format."}
    except Exception as e:
        return {"success": False, "error": f"Error processing image: {str(e)}"}

# CORRECTED VERSION - Returns list of MCP content types
async def mcp_analyze_image_tool_definition(image_url: str, max_size: int = 1024, quality: int = 85) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    MCP tool function that returns the image in a format the LLM can analyze.
    """
    result = analyze_image_from_url(image_url, max_size, quality)
    
    if result["success"]:
        return [
            types.ImageContent(
                type="image",
                data=result["base64_data"],
                mimeType=result["mime_type"]
            ),
            types.TextContent(
                type="text",
                text=f"""Image Analysis Ready!

**Original URL:** {result['original_url']}
**Original Dimensions:** {result['original_dimensions'][0]}×{result['original_dimensions'][1]} pixels
**Processed Dimensions:** {result['processed_dimensions'][0]}×{result['processed_dimensions'][1]} pixels
**Format:** {result['mime_type']}
**Original Size:** {result['original_size_bytes']:,} bytes
**Compressed Size:** {result['compressed_size_bytes']:,} bytes
**Compression Ratio:** {result['compression_ratio']:.1f}%

The image has been processed and is ready for analysis. The LLM can now analyze the visual content, identify features, objects, patterns, and provide detailed insights about what's shown in the image."""
            )
        ]
    else:
        return [
            types.TextContent(
                type="text",
                text=f"Error: {result['error']}"
            )
        ]


# if __name__ == "__main__":
#     import asyncio
    
#     async def test_image_analysis():
#         # Test with a sample URL
#         # test_url = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&LAYERS=MODIS_Terra_CorrectedReflectance_TrueColor&BBOX=-10,30,40,50&WIDTH=512&HEIGHT=512&FORMAT=image/png&CRS=EPSG:4326&TIME=2023-07-01"
#         # test_url = "https://apod.nasa.gov/apod/image/2507/Trifid2048.jpg"
#         test_url = "https://apod.nasa.gov/apod/image/2507/Trifid2048.jpg"

#         # Using the synchronous version for testing
#         result = analyze_image_from_url(test_url)
        
#         if result["success"]:
#             print(f"Success! Image converted to base64.")
#             print(f"Original: {result['original_dimensions']} -> Processed: {result['processed_dimensions']}")
#             print(f"Size: {result['original_size_bytes']:,} -> {result['compressed_size_bytes']:,} bytes")
#             print(f"Base64 length: {len(result['base64_data'])} characters")
#             print(f"Compression ratio: {result['compression_ratio']:.1f}%")
#         else:
#             print(f"Error: {result['error']}")
        
#         # Also test the async version
#         print("\n--- Testing async version ---")
#         async_result = await mcp_analyze_image_tool_definition(test_url)
#         print(f"Async result type: {async_result['type']}")
#         if async_result['type'] == 'resource':
#             print(f"Resource URI: {async_result['resource']['uri'][:100]}...")
#             print(f"Metadata: {async_result['metadata']}")
#         else:
#             print(f"Text result: {async_result['text']}")
    
#     # Run the async test
#     asyncio.run(test_image_analysis())