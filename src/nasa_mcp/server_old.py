# src/nasa_mcp/server.py
import asyncio
import json
import sys
from typing import Any, Sequence
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from nasa_api import (
    get_earth_image_definition, 
    get_gibs_image_definition, 
    get_gibs_layers_definition, 
    get_mars_image_definition, 
    get_astronomy_picture_of_the_day_tool_defnition, 
    get_neo_feed_definition, 
    mcp_analyze_image_tool_definition
)

# Create MCP server instance
server = Server("nasa-mcp-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="get_apod",
            description="Gets the Astronomy Picture of the Day (APOD) from the NASA website.",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "(YYYY-MM-DD). Default is today. The date of the APOD image to retrieve"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "(YYYY-MM-DD). The start of a date range. Cannot be used with date."
                    },
                    "end_date": {
                        "type": "string",
                        "description": "(YYYY-MM-DD). The end of the date range, when used with start_date."
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of randomly chosen images. Cannot be used with date or start_date/end_date."
                    }
                }
            }
        ),
        types.Tool(
            name="get_mars_image",
            description="Request to Mars Rover Image. Fetch any images on Mars Rover.",
            inputSchema={
                "type": "object",
                "properties": {
                    "earth_date": {
                        "type": "string",
                        "description": "(YYYY-MM-DD). Corresponding date on earth when the photo was taken."
                    },
                    "sol": {
                        "type": "integer",
                        "description": "Martian sol of the Rover's mission. Default 1000."
                    },
                    "camera": {
                        "type": "string",
                        "description": "Camera type: FHAZ, RHAZ, MAST, CHEMCAM, MAHLI, MARDI, NAVCAM, PANCAM, MINITES"
                    }
                }
            }
        ),
        types.Tool(
            name="get_neo_feed",
            description="Gets Near Earth Objects (NEO) data from NASA's NeoWs API.",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "(YYYY-MM-DD). Default is today. The starting date for asteroid search."
                    },
                    "end_date": {
                        "type": "string",
                        "description": "(YYYY-MM-DD). Default is 7 days after start_date. The ending date."
                    },
                    "limit_per_day": {
                        "type": "integer",
                        "description": "Maximum number of asteroids to show per day. Default is 2."
                    }
                }
            }
        ),
        types.Tool(
            name="get_earth_image_tool",
            description="Request to Earth Polychromatic Imaging Camera (EPIC) API. Fetch satellite images of Earth.",
            inputSchema={
                "type": "object",
                "properties": {
                    "earth_date": {
                        "type": "string",
                        "description": "(YYYY-MM-DD). Date when the photo was taken."
                    },
                    "type": {
                        "type": "string",
                        "description": "Type of image: natural, enhanced, aerosol, cloud"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of images to retrieve. Default is 1."
                    }
                }
            }
        ),
        types.Tool(
            name="get_gibs_image",
            description="Request to NASA GIBS (Global Imagery Browse Services) API. Fetch satellite imagery of Earth.",
            inputSchema={
                "type": "object",
                "properties": {
                    "layer": {
                        "type": "string",
                        "description": "The imagery layer to fetch. Default: MODIS_Terra_CorrectedReflectance_TrueColor"
                    },
                    "bbox": {
                        "type": "string",
                        "description": "Bounding box as 'min_lon,min_lat,max_lon,max_lat'. Default: '-180,-90,180,90'"
                    },
                    "date": {
                        "type": "string",
                        "description": "(YYYY-MM-DD) Date for the imagery."
                    },
                    "width": {
                        "type": "integer",
                        "description": "Image width in pixels. Default 512."
                    },
                    "height": {
                        "type": "integer",
                        "description": "Image height in pixels. Default 512."
                    },
                    "format": {
                        "type": "string",
                        "description": "Image format: image/png, image/jpeg"
                    },
                    "projection": {
                        "type": "string",
                        "description": "Coordinate system: epsg4326, epsg3857"
                    }
                }
            }
        ),
        types.Tool(
            name="get_gibs_layers",
            description="Get information about available GIBS layers and their capabilities.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="get_image_analyze",
            description="Fetch an image from URL and convert it to base64 for LLM analysis.",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_url": {
                        "type": "string",
                        "description": "The URL of the image to analyze."
                    }
                },
                "required": ["image_url"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls."""
    if arguments is None:
        arguments = {}

    try:
        if name == "get_apod":
            result = await get_astronomy_picture_of_the_day_tool_defnition(
                arguments.get("date"),
                arguments.get("start_date"), 
                arguments.get("end_date"),
                arguments.get("count")
            )
            return [types.TextContent(type="text", text=result)]
            
        elif name == "get_mars_image":
            result = await get_mars_image_definition(
                arguments.get("earth_date"),
                arguments.get("sol"),
                arguments.get("camera")
            )
            return [types.TextContent(type="text", text=result)]
            
        elif name == "get_neo_feed":
            result = await get_neo_feed_definition(
                arguments.get("start_date"),
                arguments.get("end_date"),
                arguments.get("limit_per_day", 2)
            )
            return [types.TextContent(type="text", text=result)]
            
        elif name == "get_earth_image_tool":
            result = await get_earth_image_definition(
                arguments.get("earth_date"),
                arguments.get("type"),
                arguments.get("limit", 1)
            )
            return [types.TextContent(type="text", text=result)]
            
        elif name == "get_gibs_image":
            result = await get_gibs_image_definition(
                arguments.get("layer", "MODIS_Terra_CorrectedReflectance_TrueColor"),
                arguments.get("bbox", "-180,-90,180,90"),
                arguments.get("date"),
                arguments.get("width", 512),
                arguments.get("height", 512),
                arguments.get("format", "image/png"),
                arguments.get("projection", "epsg4326")
            )
            return [types.TextContent(type="text", text=result)]
            
        elif name == "get_gibs_layers":
            result = await get_gibs_layers_definition()
            return [types.TextContent(type="text", text=result)]
            
        elif name == "get_image_analyze":
            image_url = arguments.get("image_url")
            if not image_url:
                raise ValueError("image_url is required")
            result = await mcp_analyze_image_tool_definition(image_url)
            return [result]  # This returns ImageContent directly
            
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def handle_mcp(request: Request) -> Response:
    """Handle MCP requests over HTTP."""
    if request.method == "POST":
        try:
            # Read the request body
            body = await request.body()
            
            # Parse JSON-RPC request
            json_request = json.loads(body.decode())
            
            # Process the request through MCP server
            async def read_request():
                yield json_request
            
            async def write_response(response):
                return response
            
            # Handle the request
            responses = []
            async for response in server.run(
                read_stream=read_request(),
                write_stream=write_response,
                initialization_options=InitializationOptions(
                    server_name="nasa-mcp-server",
                    server_version="1.0.0"
                )
            ):
                responses.append(response)
            
            # Return JSON response
            if len(responses) == 1:
                return Response(
                    content=json.dumps(responses[0]),
                    media_type="application/json"
                )
            else:
                # Multiple responses - use SSE
                async def generate_sse():
                    for response in responses:
                        yield f"data: {json.dumps(response)}\n\n"
                
                return StreamingResponse(
                    generate_sse(),
                    media_type="text/event-stream"
                )
                
        except Exception as e:
            return Response(
                content=json.dumps({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    },
                    "id": None
                }),
                media_type="application/json",
                status_code=500
            )
    
    elif request.method == "GET":
        # Optional: Support server-initiated SSE streams
        async def generate_sse():
            yield "data: {\"type\": \"ping\"}\n\n"
        
        return StreamingResponse(
            generate_sse(),
            media_type="text/event-stream"
        )
    
    else:
        return Response(status_code=405)

# Create Starlette application
starlette_app = Starlette(
    routes=[
        Route("/mcp", endpoint=handle_mcp, methods=["POST", "GET"]),
        Route("/", endpoint=lambda request: Response("NASA MCP Server is running"), methods=["GET"])
    ]
)

def main():
    """Main entry point for the server"""
    if len(sys.argv) > 1 and sys.argv[1] == "--stdio":
        # Run with stdio transport for development
        print("Running with stdio transport...")
        asyncio.run(mcp.server.stdio.stdio_server(server))
    else:
        # Run with HTTP transport
        import uvicorn
        print("Starting NASA MCP Server on http://0.0.0.0:8000")
        print("MCP endpoint available at: http://0.0.0.0:8000/mcp")
        uvicorn.run(starlette_app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()

