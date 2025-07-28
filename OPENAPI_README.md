# NASA OpenAPI Specification

This file documents the OpenAPI 3.1 specification for the NASA MCP Server API endpoints.

## Overview

The `nasa_openapi.yaml` file provides a comprehensive OpenAPI specification that documents all NASA API endpoints available through this MCP server. This specification can be used for:

- API documentation generation
- Client SDK generation
- API testing and validation
- Integration with API management tools

## Endpoints Documented

### Implemented Endpoints
These endpoints correspond to working MCP tools:

- `GET /apod` - Astronomy Picture of the Day
- `GET /mars-photos` - Mars Rover Photos
- `GET /neo-feed` - Near Earth Objects Feed
- `GET /earth` - Earth Imagery (EPIC)
- `GET /gibs` - GIBS Satellite Imagery
- `GET /gibs/layers` - Available GIBS Layers
- `POST /analyze-image` - Image Analysis Tool

### Future Endpoints
These endpoints are documented but not yet implemented:

- `GET /neo-lookup/{asteroid_id}` - Asteroid Details by ID
- `GET /tech-transfer` - Technology Transfer Data
- `GET /insight-weather` - Mars Weather from InSight
- `GET /donki/cme` - Coronal Mass Ejection Data
- `GET /donki/notifications` - Solar Activity Notifications
- `GET /eonet-events` - Natural Disaster Events
- `GET /eonet-categories` - EONET Categories

## Usage

### Viewing the Specification

You can view the OpenAPI specification using:

1. **Swagger UI**: Upload the `nasa_openapi.yaml` file to [editor.swagger.io](https://editor.swagger.io/)
2. **Redoc**: Use any Redoc-compatible viewer
3. **Postman**: Import the OpenAPI file directly

### Validation

The specification has been validated using:

```bash
# Install validator
pip install openapi-spec-validator

# Validate the specification
python -c "
from openapi_spec_validator import validate_spec
import yaml
with open('nasa_openapi.yaml', 'r') as f:
    spec = yaml.safe_load(f)
validate_spec(spec)
print('Specification is valid!')
"
```

### Testing

Run the included test script to validate the specification:

```bash
python test_openapi.py
```

## API Key

Most endpoints require a NASA API key. You can:

1. Use `DEMO_KEY` for limited testing
2. Get a free API key at [api.nasa.gov](https://api.nasa.gov/)
3. Set the `api_key` query parameter in requests

## Schema Definitions

The specification includes comprehensive schema definitions for:

- Request parameters
- Response formats
- Error responses
- Image resources
- Astronomical data structures

## Security

The API uses API key authentication via query parameter. All endpoints support the `api_key` parameter for authentication with NASA services.

## Contributing

When adding new endpoints:

1. Update the `nasa_openapi.yaml` file
2. Add corresponding schemas if needed
3. Run `python test_openapi.py` to validate
4. Update this documentation

## Standards Compliance

- OpenAPI 3.1.0 compliant
- JSON Schema compatible
- RESTful design principles
- Comprehensive error handling
- Detailed parameter documentation