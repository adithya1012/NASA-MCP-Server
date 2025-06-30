import datetime
import os
from typing import Any
import httpx

# Constants
NEOWS_API = "https://api.nasa.gov/neo/rest/v1/feed?"
NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")

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
                    result += f"ID: {asteroid.get('id', 'Unknown')}\n"
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