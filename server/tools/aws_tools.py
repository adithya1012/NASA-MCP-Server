
import datetime
import os
from typing import Any, Optional
import httpx
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from mcp.server.fastmcp import FastMCP
from mars_img import get_mars_image_definition
from earth_img import get_earth_image_definition

mcp = FastMCP("weather")

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

MARS_BASE_API = "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?"
NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

async def make_nws_request(url):
    """Make request to NWS API with proper error handling"""
    header = {
        "User-agent" : USER_AGENT,
        "Accept" : "application/geo+json"
    }
    async with httpx.AsyncClient() as clint:
        try:
            response = await clint.get(url, headers=header, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return None

def get_bedrock_client():
    """Initialize and return AWS Bedrock Runtime client"""
    try:
        if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
            return boto3.client(
                'bedrock-agent-runtime',
                region_name=AWS_REGION,
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
        else:
            # Use default credential chain (IAM roles, profiles, etc.)
            return boto3.client('bedrock-agent-runtime', region_name=AWS_REGION)
    except (ClientError, NoCredentialsError) as e:
        raise Exception(f"Failed to initialize AWS Bedrock client: {str(e)}")

def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
    Event:{props.get ('event', 'Unknown')}
    Area: {props.get ('areaDes', 'Unknown')} 
    Severity: {props.get( 'severity', 'Unknown')}
    Description: {props.get('description', 'No description available')} 
    Instructions: {props.get('instruction', 'No specific instructions provided')}
    """

def format_retrieval_results(response):
    """Format AWS Knowledge Base retrieval results"""
    if 'retrievalResults' not in response:
        return "No results found."
    
    results = []
    for i, result in enumerate(response['retrievalResults'], 1):
        content = result.get('content', {}).get('text', 'No content available')
        score = result.get('score', 0)
        
        # Extract metadata if available
        metadata = result.get('metadata', {})
        source = metadata.get('source', 'Unknown source')
        
        formatted_result = f"""
Result {i} (Score: {score:.3f}):
Source: {source}
Content: {content}
        """
        results.append(formatted_result.strip())
    
    return "\n\n---\n\n".join(results)

@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.
    Args:
    state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)
    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."
    if not data["features"]:
        return "No active alerts for this state."
    alerts = [format_alert(feature) for feature in data[ "features"]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_add(a, b) -> str:
    """Returns the sum of two numbers.
    Args:
    a: Integer
    b: Integer
    """
    return int(a)+int(b)

@mcp.tool()
async def get_mars_image_tool(earth_date: Any = None, sol: Any = None, camera: Any = None) -> str:
    """Request to Mars Rover Image. Fetch any images on Mars Rover. Each rover has its own set of photos stored in the database, which can be queried separately. There are several possible queries that can be made against the API.\n
    Parameters:\n
        - earth_date: (optinal) Corresponding date on earth when the photo was taken. This should be in "YYYY-MM-DD" format. Default pass today's date\n
        - sol: (optinal) This is Martian sol of the Rover's mission. This is integer. Values can range from 0 to max found in endpoint. Default pass 1000.\n
        - camera: (optinal) Each camera has a unique function and perspective, and they are named as follows string:\n
            FHAZ: Front Hazard Avoidance Camera\n
            RHAZ: Rear Hazard Avoidance Camera\n
            MAST: Mast Camera\n
            CHEMCAM: Chemistry and Camera Complex\n
            MAHLI: Mars Hand Lens Imager\n
            MARDI: Mars Descent Imager\n
            NAVCAM: Navigation Camera\n
            PANCAM: Panoramic Camera\n
            MINITES: Miniature Thermal Emission Spectrometer (Mini-TES)\n
            You can use any one of the camera value at a time.\n
    """
    return await get_mars_image_definition(earth_date, sol, camera)

@mcp.tool()
async def get_earth_image_tool(earth_date: Any = None, type: Any = None) -> str:
    """Request to Earth Polychromatic Imaging Camera (EPIC) API. Fetch satellite images of Earth from NASA's DSCOVR satellite.\n
    Parameters:\n
        - earth_date: (optional) Date when the photo was taken. This should be in "YYYY-MM-DD" format. If not provided, will get latest available images.\n
        - type: (optional) Type of image to retrieve. Options are:\n
            "natural" - Natural color images (default)\n
            "enhanced" - Enhanced color images\n
            "cloud" - Cloud color images
    """
    return await get_earth_image_definition(earth_date, type)

@mcp.tool()
async def retrieve_from_knowledge_base(
    knowledge_base_id: str,
    query: str,
    max_results: int = 5,
    next_token: Optional[str] = None
) -> str:
    """Retrieve information from an AWS Knowledge Base using semantic search.
    
    Args:
        knowledge_base_id: The ID of the AWS Knowledge Base to query
        query: The search query to find relevant information
        max_results: Maximum number of results to return (default: 5, max: 100)
        next_token: Token for pagination (optional)
    """
    try:
        client = get_bedrock_client()
        
        # Prepare the request parameters
        request_params = {
            'knowledgeBaseId': knowledge_base_id,
            'retrievalQuery': {
                'text': query
            },
            'retrievalConfiguration': {
                'vectorSearchConfiguration': {
                    'numberOfResults': min(max_results, 100)
                }
            }
        }
        
        if next_token:
            request_params['nextToken'] = next_token
        
        # Make the retrieval request
        response = client.retrieve(**request_params)
        
        # Format and return the results
        formatted_results = format_retrieval_results(response)
        
        # Add pagination info if available
        if 'nextToken' in response:
            formatted_results += f"\n\nNext Token (for pagination): {response['nextToken']}"
        
        return formatted_results
        
    except Exception as e:
        return f"Error retrieving from knowledge base: {str(e)}"

@mcp.tool()
async def retrieve_and_generate(
    knowledge_base_id: str,
    query: str,
    model_arn: str = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
    max_results: int = 5
) -> str:
    """Retrieve information from AWS Knowledge Base and generate a response using a foundation model.
    
    Args:
        knowledge_base_id: The ID of the AWS Knowledge Base to query
        query: The search query and generation prompt
        model_arn: ARN of the foundation model to use for generation
        max_results: Maximum number of results to retrieve (default: 5)
    """
    try:
        client = get_bedrock_client()
        
        request_params = {
            'knowledgeBaseId': knowledge_base_id,
            'modelArn': model_arn,
            'input': {
                'text': query
            },
            'retrieveAndGenerateConfiguration': {
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': knowledge_base_id,
                    'modelArn': model_arn,
                    'retrievalConfiguration': {
                        'vectorSearchConfiguration': {
                            'numberOfResults': min(max_results, 100)
                        }
                    }
                }
            }
        }
        
        response = client.retrieve_and_generate(**request_params)
        
        # Extract the generated response
        output = response.get('output', {}).get('text', 'No response generated')
        
        # Add citation information if available
        citations = response.get('citations', [])
        if citations:
            output += "\n\nSources:"
            for i, citation in enumerate(citations, 1):
                for reference in citation.get('retrievedReferences', []):
                    content = reference.get('content', {}).get('text', '')[:200] + "..."
                    metadata = reference.get('metadata', {})
                    source = metadata.get('source', 'Unknown source')
                    output += f"\n{i}. {source}: {content}"
        
        return output
        
    except Exception as e:
        return f"Error in retrieve and generate: {str(e)}"

@mcp.tool()
async def list_knowledge_bases() -> str:
    """List available AWS Knowledge Bases in the current region.
    
    Note: This requires additional AWS permissions (bedrock:ListKnowledgeBases)
    """
    try:
        # Use bedrock-agent client for listing knowledge bases
        client = boto3.client('bedrock-agent', region_name=AWS_REGION)
        
        response = client.list_knowledge_bases()
        
        if not response.get('knowledgeBaseSummaries'):
            return "No knowledge bases found in the current region."
        
        kb_list = []
        for kb in response['knowledgeBaseSummaries']:
            kb_info = f"""
Knowledge Base ID: {kb.get('knowledgeBaseId', 'Unknown')}
Name: {kb.get('name', 'Unknown')}
Description: {kb.get('description', 'No description')}
Status: {kb.get('status', 'Unknown')}
Created: {kb.get('createdAt', 'Unknown')}
Updated: {kb.get('updatedAt', 'Unknown')}
            """
            kb_list.append(kb_info.strip())
        
        return "\n\n---\n\n".join(kb_list)
        
    except Exception as e:
        return f"Error listing knowledge bases: {str(e)}"

if __name__ == "__main__":
    mcp.run()