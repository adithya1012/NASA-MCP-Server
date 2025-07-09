import datetime
import os
from typing import Any, Dict, Union
import httpx
import base64
import requests
import io
from PIL import Image
import mcp.types as types

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