"""NASA MCP Server - Access Mars Rover images via MCP protocol"""

__version__ = "0.1.0"
__author__ = "adithya"
__email__ = "adithyasn7@gmil.com"

from .server import main
from .nasa_api import get_mars_image_definition

__all__ = ["main", "get_mars_image_definition"]