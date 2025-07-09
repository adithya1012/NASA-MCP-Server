import datetime
import os
from typing import Any
import httpx

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