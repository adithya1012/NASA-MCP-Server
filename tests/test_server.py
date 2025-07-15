import pytest
import asyncio
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from nasa_mcp.server import get_apod, get_mars_image, get_neo_feed, get_earth_image_tool, get_gibs_image, get_gibs_layers, get_image_analyze
import mcp.types as types


class TestAPODTool:
    """Test cases for the Astronomy Picture of the Day (APOD) tool."""
    
    @pytest.mark.asyncio
    async def test_get_apod_default(self):
        """Test APOD with default parameters."""
        with patch('nasa_mcp.nasa_api.get_astronomy_picture_of_the_day_tool_defnition') as mock_api:
            mock_api.return_value = "Mock APOD result"
            result = await get_apod()
            assert result == "Mock APOD result"
            mock_api.assert_called_once_with(None, None, None, None)
    
    @pytest.mark.asyncio
    async def test_get_apod_with_date(self):
        """Test APOD with specific date."""
        with patch('nasa_mcp.nasa_api.get_astronomy_picture_of_the_day_tool_defnition') as mock_api:
            mock_api.return_value = "Mock APOD result for date"
            result = await get_apod(date="2024-01-15")
            assert result == "Mock APOD result for date"
            mock_api.assert_called_once_with("2024-01-15", None, None, None)
    
    @pytest.mark.asyncio
    async def test_get_apod_with_date_range(self):
        """Test APOD with date range."""
        with patch('nasa_mcp.nasa_api.get_astronomy_picture_of_the_day_tool_defnition') as mock_api:
            mock_api.return_value = "Mock APOD result for range"
            result = await get_apod(start_date="2024-01-01", end_date="2024-01-07")
            assert result == "Mock APOD result for range"
            mock_api.assert_called_once_with(None, "2024-01-01", "2024-01-07", None)
    
    @pytest.mark.asyncio
    async def test_get_apod_with_count(self):
        """Test APOD with count parameter."""
        with patch('nasa_mcp.nasa_api.get_astronomy_picture_of_the_day_tool_defnition') as mock_api:
            mock_api.return_value = "Mock APOD result for count"
            result = await get_apod(count=5)
            assert result == "Mock APOD result for count"
            mock_api.assert_called_once_with(None, None, None, 5)


class TestMarsImageTool:
    """Test cases for the Mars Rover Images tool."""
    
    @pytest.mark.asyncio
    async def test_get_mars_image_default(self):
        """Test Mars image with default parameters."""
        with patch('nasa_mcp.nasa_api.get_mars_image_definition') as mock_api:
            mock_api.return_value = "Mock Mars image result"
            result = await get_mars_image()
            assert result == "Mock Mars image result"
            mock_api.assert_called_once_with(None, None, None)
    
    @pytest.mark.asyncio
    async def test_get_mars_image_with_earth_date(self):
        """Test Mars image with earth date."""
        with patch('nasa_mcp.nasa_api.get_mars_image_definition') as mock_api:
            mock_api.return_value = "Mock Mars image result for earth date"
            result = await get_mars_image(earth_date="2024-01-15")
            assert result == "Mock Mars image result for earth date"
            mock_api.assert_called_once_with("2024-01-15", None, None)
    
    @pytest.mark.asyncio
    async def test_get_mars_image_with_sol(self):
        """Test Mars image with sol parameter."""
        with patch('nasa_mcp.nasa_api.get_mars_image_definition') as mock_api:
            mock_api.return_value = "Mock Mars image result for sol"
            result = await get_mars_image(sol=500)
            assert result == "Mock Mars image result for sol"
            mock_api.assert_called_once_with(None, 500, None)
    
    @pytest.mark.asyncio
    async def test_get_mars_image_with_camera(self):
        """Test Mars image with camera parameter."""
        with patch('nasa_mcp.nasa_api.get_mars_image_definition') as mock_api:
            mock_api.return_value = "Mock Mars image result for camera"
            result = await get_mars_image(camera="MAST")
            assert result == "Mock Mars image result for camera"
            mock_api.assert_called_once_with(None, None, "MAST")
    
    @pytest.mark.asyncio
    async def test_get_mars_image_with_all_params(self):
        """Test Mars image with all parameters."""
        with patch('nasa_mcp.nasa_api.get_mars_image_definition') as mock_api:
            mock_api.return_value = "Mock Mars image result for all params"
            result = await get_mars_image(earth_date="2024-01-15", sol=500, camera="NAVCAM")
            assert result == "Mock Mars image result for all params"
            mock_api.assert_called_once_with("2024-01-15", 500, "NAVCAM")


class TestNEOFeedTool:
    """Test cases for the Near Earth Objects (NEO) tool."""
    
    @pytest.mark.asyncio
    async def test_get_neo_feed_default(self):
        """Test NEO feed with default parameters."""
        with patch('nasa_mcp.nasa_api.get_neo_feed_definition') as mock_api:
            mock_api.return_value = "Mock NEO feed result"
            result = await get_neo_feed()
            assert result == "Mock NEO feed result"
            mock_api.assert_called_once_with(None, None, 2)
    
    @pytest.mark.asyncio
    async def test_get_neo_feed_with_date_range(self):
        """Test NEO feed with date range."""
        with patch('nasa_mcp.nasa_api.get_neo_feed_definition') as mock_api:
            mock_api.return_value = "Mock NEO feed result for range"
            result = await get_neo_feed(start_date="2024-01-15", end_date="2024-01-20")
            assert result == "Mock NEO feed result for range"
            mock_api.assert_called_once_with("2024-01-15", "2024-01-20", 2)
    
    @pytest.mark.asyncio
    async def test_get_neo_feed_with_limit(self):
        """Test NEO feed with custom limit."""
        with patch('nasa_mcp.nasa_api.get_neo_feed_definition') as mock_api:
            mock_api.return_value = "Mock NEO feed result for limit"
            result = await get_neo_feed(limit_per_day=5)
            assert result == "Mock NEO feed result for limit"
            mock_api.assert_called_once_with(None, None, 5)


class TestEarthImageTool:
    """Test cases for the Earth Images (EPIC) tool."""
    
    @pytest.mark.asyncio
    async def test_get_earth_image_default(self):
        """Test Earth image with default parameters."""
        with patch('nasa_mcp.nasa_api.get_earth_image_definition') as mock_api:
            mock_api.return_value = "Mock Earth image result"
            result = await get_earth_image_tool()
            assert result == "Mock Earth image result"
            mock_api.assert_called_once_with(None, None, 1)
    
    @pytest.mark.asyncio
    async def test_get_earth_image_with_date(self):
        """Test Earth image with specific date."""
        with patch('nasa_mcp.nasa_api.get_earth_image_definition') as mock_api:
            mock_api.return_value = "Mock Earth image result for date"
            result = await get_earth_image_tool(earth_date="2024-01-15")
            assert result == "Mock Earth image result for date"
            mock_api.assert_called_once_with("2024-01-15", None, 1)
    
    @pytest.mark.asyncio
    async def test_get_earth_image_with_type(self):
        """Test Earth image with specific type."""
        with patch('nasa_mcp.nasa_api.get_earth_image_definition') as mock_api:
            mock_api.return_value = "Mock Earth image result for type"
            result = await get_earth_image_tool(type="enhanced")
            assert result == "Mock Earth image result for type"
            mock_api.assert_called_once_with(None, "enhanced", 1)
    
    @pytest.mark.asyncio
    async def test_get_earth_image_with_limit(self):
        """Test Earth image with custom limit."""
        with patch('nasa_mcp.nasa_api.get_earth_image_definition') as mock_api:
            mock_api.return_value = "Mock Earth image result for limit"
            result = await get_earth_image_tool(limit=5)
            assert result == "Mock Earth image result for limit"
            mock_api.assert_called_once_with(None, None, 5)


class TestGIBSImageTool:
    """Test cases for the GIBS Satellite Imagery tool."""
    
    @pytest.mark.asyncio
    async def test_get_gibs_image_default(self):
        """Test GIBS image with default parameters."""
        with patch('nasa_mcp.nasa_api.get_gibs_image_definition') as mock_api:
            mock_api.return_value = "Mock GIBS image result"
            result = await get_gibs_image()
            assert result == "Mock GIBS image result"
            mock_api.assert_called_once_with(
                "MODIS_Terra_CorrectedReflectance_TrueColor",
                "-180,-90,180,90",
                None,
                512,
                512,
                "image/png",
                "epsg4326"
            )
    
    @pytest.mark.asyncio
    async def test_get_gibs_image_with_layer(self):
        """Test GIBS image with specific layer."""
        with patch('nasa_mcp.nasa_api.get_gibs_image_definition') as mock_api:
            mock_api.return_value = "Mock GIBS image result for layer"
            result = await get_gibs_image(layer="MODIS_Aqua_CorrectedReflectance_TrueColor")
            assert result == "Mock GIBS image result for layer"
            mock_api.assert_called_once_with(
                "MODIS_Aqua_CorrectedReflectance_TrueColor",
                "-180,-90,180,90",
                None,
                512,
                512,
                "image/png",
                "epsg4326"
            )
    
    @pytest.mark.asyncio
    async def test_get_gibs_image_with_bbox(self):
        """Test GIBS image with specific bounding box."""
        with patch('nasa_mcp.nasa_api.get_gibs_image_definition') as mock_api:
            mock_api.return_value = "Mock GIBS image result for bbox"
            result = await get_gibs_image(bbox="-125,25,-65,50")
            assert result == "Mock GIBS image result for bbox"
            mock_api.assert_called_once_with(
                "MODIS_Terra_CorrectedReflectance_TrueColor",
                "-125,25,-65,50",
                None,
                512,
                512,
                "image/png",
                "epsg4326"
            )
    
    @pytest.mark.asyncio
    async def test_get_gibs_image_with_dimensions(self):
        """Test GIBS image with custom dimensions."""
        with patch('nasa_mcp.nasa_api.get_gibs_image_definition') as mock_api:
            mock_api.return_value = "Mock GIBS image result for dimensions"
            result = await get_gibs_image(width=1024, height=768)
            assert result == "Mock GIBS image result for dimensions"
            mock_api.assert_called_once_with(
                "MODIS_Terra_CorrectedReflectance_TrueColor",
                "-180,-90,180,90",
                None,
                1024,
                768,
                "image/png",
                "epsg4326"
            )
    
    @pytest.mark.asyncio
    async def test_get_gibs_image_with_date(self):
        """Test GIBS image with specific date."""
        with patch('nasa_mcp.nasa_api.get_gibs_image_definition') as mock_api:
            mock_api.return_value = "Mock GIBS image result for date"
            result = await get_gibs_image(date="2024-01-15")
            assert result == "Mock GIBS image result for date"
            mock_api.assert_called_once_with(
                "MODIS_Terra_CorrectedReflectance_TrueColor",
                "-180,-90,180,90",
                "2024-01-15",
                512,
                512,
                "image/png",
                "epsg4326"
            )


class TestGIBSLayersTool:
    """Test cases for the GIBS Layers Information tool."""
    
    @pytest.mark.asyncio
    async def test_get_gibs_layers(self):
        """Test GIBS layers tool."""
        with patch('nasa_mcp.nasa_api.get_gibs_layers_definition') as mock_api:
            mock_api.return_value = "Mock GIBS layers result"
            result = await get_gibs_layers()
            assert result == "Mock GIBS layers result"
            mock_api.assert_called_once_with()


class TestImageAnalyzeTool:
    """Test cases for the Image Analysis tool."""
    
    @pytest.mark.asyncio
    async def test_get_image_analyze_success(self):
        """Test image analysis with successful result."""
        mock_image_content = types.ImageContent(
            type="image",
            data="base64_encoded_data",
            mimeType="image/jpeg"
        )
        
        with patch('nasa_mcp.nasa_api.mcp_analyze_image_tool_definition') as mock_api:
            mock_api.return_value = mock_image_content
            result = await get_image_analyze("https://example.com/image.jpg")
            assert result == mock_image_content
            mock_api.assert_called_once_with("https://example.com/image.jpg")
    
    @pytest.mark.asyncio
    async def test_get_image_analyze_with_nasa_url(self):
        """Test image analysis with NASA URL."""
        mock_image_content = types.ImageContent(
            type="image",
            data="base64_encoded_data",
            mimeType="image/png"
        )
        
        with patch('nasa_mcp.nasa_api.mcp_analyze_image_tool_definition') as mock_api:
            mock_api.return_value = mock_image_content
            result = await get_image_analyze("https://apod.nasa.gov/apod/image/2401/example.jpg")
            assert result == mock_image_content
            mock_api.assert_called_once_with("https://apod.nasa.gov/apod/image/2401/example.jpg")


class TestIntegrationScenarios:
    """Integration test scenarios for common use cases."""
    
    @pytest.mark.asyncio
    async def test_apod_and_image_analysis_workflow(self):
        """Test workflow: get APOD then analyze the image."""
        # Mock APOD response with image URL
        apod_response = {
            "description": "NASA Astronomy Picture of the Day\nDate: 2024-01-15\nTitle: Test Image",
            "resource": {
                "type": "image",
                "uri": "https://apod.nasa.gov/apod/image/2401/test.jpg",
                "mimeType": "image/jpeg",
                "name": "APOD_2024-01-15_Test_Image"
            }
        }
        
        mock_image_content = types.ImageContent(
            type="image",
            data="base64_encoded_data",
            mimeType="image/jpeg"
        )
        
        with patch('nasa_mcp.nasa_api.get_astronomy_picture_of_the_day_tool_defnition') as mock_apod:
            mock_apod.return_value = str(apod_response)
            
            with patch('nasa_mcp.nasa_api.mcp_analyze_image_tool_definition') as mock_analyze:
                mock_analyze.return_value = mock_image_content
                
                # Get APOD
                apod_result = await get_apod(date="2024-01-15")
                assert apod_result == str(apod_response)
                
                # Parse result and analyze image
                result_dict = eval(apod_result)  # In real scenario, use json.loads
                image_url = result_dict["resource"]["uri"]
                
                # Analyze the image
                analysis_result = await get_image_analyze(image_url)
                assert analysis_result == mock_image_content
                
                mock_apod.assert_called_once_with("2024-01-15", None, None, None)
                mock_analyze.assert_called_once_with("https://apod.nasa.gov/apod/image/2401/test.jpg")


if __name__ == "__main__":
    pytest.main([__file__])