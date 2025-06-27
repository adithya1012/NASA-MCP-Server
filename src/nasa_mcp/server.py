# src/nasa_mcp/server.py
import asyncio
import sys
from typing import Any
from mcp.server.fastmcp import FastMCP
from nasa_api import get_mars_image_definition

# Create FastMCP server instance
mcp = FastMCP("nasa-mcp-server")

@mcp.tool()
async def get_mars_image_tool(earth_date: Any = None, sol: Any = None, camera: Any = None) -> str:
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
    return await get_mars_image_definition(earth_date, sol, camera)

def main():
    """Main entry point for the server"""
    # Use stdio transport for standard MCP clients (Claude Desktop, VS Code)
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()