# NASA MCP Server

A Model Context Protocol (MCP) server that provides access to NASA's public APIs, including Astronomy Picture of the Day (APOD), Mars Rover Images, and Near Earth Objects (NEO) data.

## Features

- **Astronomy Picture of the Day (APOD)**: Get daily astronomy images with descriptions
- **Mars Rover Images**: Access photos from Mars rovers with various camera options
- **Near Earth Objects (NEO)**: Retrieve asteroid data and close approach information
- **Earth Images (EPIC)**: Get satellite images of Earth from NASA's DSCOVR satellite
- **GIBS Satellite Imagery**: Access high-resolution Earth imagery from NASA's Global Imagery Browse Services

## Installation

Install the package from PyPI:

```bash
pip install nasa-mcp-server
```

Or using uvx (recommended for MCP usage):

```bash
uvx nasa-mcp-server
```

## Setup

### Get NASA API Key

1. Visit [NASA API Portal](https://api.nasa.gov/)
2. Generate your free API key
3. Keep the API key handy for configuration

### VS Code Configuration

Add the following to your VS Code `mcp.json` configuration file:

```json
{
  "servers": {
    "nasa-mcp": {
      "command": "uvx",
      "args": ["nasa-mcp-server"],
      "env": {
        "NASA_API_KEY": "YOUR_NASA_API_KEY_HERE"
      }
    }
  }
}
```

Replace `YOUR_NASA_API_KEY_HERE` with your actual NASA API key.

### Claude Desktop Configuration

Add the following to your Claude Desktop configuration:

**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`
**macOS**: `~/Library/Application\ Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "nasa-mcp": {
      "command": "uvx",
      "args": ["nasa-mcp-server"],
      "env": {
        "NASA_API_KEY": "YOUR_NASA_API_KEY_HERE"
      }
    }
  }
}
```

Replace `YOUR_NASA_API_KEY_HERE` with your actual NASA API key.

## Available Tools

### 1. get_apod - Astronomy Picture of the Day

Get stunning astronomy images with detailed descriptions from NASA's APOD service.

**Parameters:**

- `date` (YYYY-MM-DD): Specific date for APOD image (default: today)
- `start_date` (YYYY-MM-DD): Start date for date range (cannot be used with `date`)
- `end_date` (YYYY-MM-DD): End date for date range (default: today)
- `count` (int): Number of random images to retrieve (cannot be used with date parameters)

**Example Usage:**

- Get today's APOD: `get_apod()`
- Get APOD for specific date: `get_apod(date="2024-01-15")`
- Get APOD for date range: `get_apod(start_date="2024-01-01", end_date="2024-01-07")`
- Get 5 random APODs: `get_apod(count=5)`

### 2. get_mars_image - Mars Rover Images

Access photos taken by Mars rovers with various camera perspectives.

**Parameters:**

- `earth_date` (YYYY-MM-DD): Earth date when photo was taken (default: today)
- `sol` (int): Martian sol (day) of the rover's mission (default: 1000)
- `camera` (string): Camera type to use

**Available Cameras:**

- `FHAZ`: Front Hazard Avoidance Camera
- `RHAZ`: Rear Hazard Avoidance Camera
- `MAST`: Mast Camera
- `CHEMCAM`: Chemistry and Camera Complex
- `MAHLI`: Mars Hand Lens Imager
- `MARDI`: Mars Descent Imager
- `NAVCAM`: Navigation Camera
- `PANCAM`: Panoramic Camera
- `MINITES`: Miniature Thermal Emission Spectrometer (Mini-TES)

**Example Usage:**

- Get images from today: `get_mars_image()`
- Get images from specific Earth date: `get_mars_image(earth_date="2024-01-15")`
- Get images from specific sol: `get_mars_image(sol=500)`
- Get images from specific camera: `get_mars_image(camera="MAST")`

### 3. get_neo_feed - Near Earth Objects

Retrieve information about asteroids and their close approaches to Earth.

**Parameters:**

- `start_date` (YYYY-MM-DD): Start date for asteroid search (default: today)
- `end_date` (YYYY-MM-DD): End date for asteroid search (default: 7 days after start_date)
- `limit_per_day` (int): Maximum number of asteroids to show per day (default: 2)

**Note:** Maximum date range is 7 days as per NASA API limitations.

**Example Usage:**

- Get next 7 days of NEO data: `get_neo_feed()`
- Get NEO data for specific date range: `get_neo_feed(start_date="2024-01-15", end_date="2024-01-20")`
- Limit results per day: `get_neo_feed(limit_per_day=5)`

### 4. get_earth_image_tool - Earth Images (EPIC)

Get satellite images of Earth from NASA's DSCOVR satellite using the Earth Polychromatic Imaging Camera (EPIC).

**Parameters:**

- `earth_date` (YYYY-MM-DD): Date when the photo was taken (default: latest available)
- `type` (string): Type of image to retrieve
- `limit` (int): Number of images to retrieve (default: 1, max recommended: 10)

**Available Image Types:**

- `natural`: Natural color images (default)
- `enhanced`: Enhanced color images
- `aerosol`: Aerosol images
- `cloud`: Cloud images

**Example Usage:**

- Get latest Earth images: `get_earth_image_tool()`
- Get images for specific date: `get_earth_image_tool(earth_date="2024-01-15")`
- Get enhanced color images: `get_earth_image_tool(type="enhanced")`
- Get multiple images: `get_earth_image_tool(limit=5)`

### 5. get_gibs_image - GIBS Satellite Imagery

Access high-resolution satellite imagery of Earth from NASA's Global Imagery Browse Services (GIBS).

**Parameters:**

- `layer` (string): The imagery layer to fetch (default: "MODIS_Terra_CorrectedReflectance_TrueColor")
- `bbox` (string): Bounding box as "min_lon,min_lat,max_lon,max_lat" (default: "-180,-90,180,90")
- `date` (YYYY-MM-DD): Date for the imagery (default: most recent available)
- `width` (int): Image width in pixels (default: 512, max recommended: 2048)
- `height` (int): Image height in pixels (default: 512, max recommended: 2048)
- `format` (string): Image format - "image/png" or "image/jpeg" (default: "image/png")
- `projection` (string): Coordinate system - "epsg4326" or "epsg3857" (default: "epsg4326")

**Popular Imagery Layers:**

- `MODIS_Terra_CorrectedReflectance_TrueColor`: Terra satellite true color (default)
- `MODIS_Aqua_CorrectedReflectance_TrueColor`: Aqua satellite true color
- `VIIRS_SNPP_CorrectedReflectance_TrueColor`: VIIRS satellite true color
- `MODIS_Terra_CorrectedReflectance_Bands721`: Terra false color
- `MODIS_Aqua_CorrectedReflectance_Bands721`: Aqua false color
- `Reference_Labels_15m`: Political boundaries and labels
- `Reference_Features_15m`: Coastlines and water bodies
- `MODIS_Terra_Aerosol`: Aerosol optical depth
- `MODIS_Terra_Land_Surface_Temp_Day`: Land surface temperature

**Example Bounding Boxes:**

- World: `"-180,-90,180,90"`
- USA: `"-125,25,-65,50"`
- Europe: `"0,40,40,70"`

**Example Usage:**

- Get world imagery: `get_gibs_image()`
- Get USA true color imagery: `get_gibs_image(bbox="-125,25,-65,50")`
- Get false color imagery: `get_gibs_image(layer="MODIS_Terra_CorrectedReflectance_Bands721")`
- Get high-resolution imagery: `get_gibs_image(width=1024, height=1024)`
- Get imagery for specific date: `get_gibs_image(date="2024-01-15")`

### 6. get_gibs_layers - Available GIBS Layers

Get information about all available GIBS layers and their capabilities.

**Parameters:** None

**Example Usage:**

- Get all available layers: `get_gibs_layers()`

## Error Handling

The server includes comprehensive error handling for:

- Invalid date formats
- Network timeouts
- Invalid API keys
- NASA API-specific errors

## Requirements

- Python 3.8+
- NASA API key (free from [NASA API Portal](https://api.nasa.gov/))
- Internet connection for API access

## Links

- **PyPI Package**: https://pypi.org/project/nasa-mcp-server/
- **NASA API Documentation**: https://api.nasa.gov/
- **MCP Documentation**: https://modelcontextprotocol.io/

## Support

For issues and support, please visit the package repository or NASA API documentation for API-related questions.

## License

This project uses NASA's public APIs. Please refer to NASA's API terms of service for usage guidelines.

## Developper

I am Adithya. I developped this package as part of the internship project. Wanted to talk more, shoot me an email at adithyasn7@gmail.com
