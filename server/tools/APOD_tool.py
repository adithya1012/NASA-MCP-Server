# src/nasa_mcp/nasa_api.py
import datetime
import os
from typing import Any
import httpx

# Get NASA API key from environment variable (set by MCP client)
NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")
MARS_API = "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?"
APOD_API = "https://api.nasa.gov/planetary/apod?"

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