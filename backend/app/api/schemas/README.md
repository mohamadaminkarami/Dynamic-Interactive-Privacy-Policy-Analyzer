# API Schemas

This directory contains all request and response schemas for the API endpoints.

## Structure

```
app/api/schemas/
├── __init__.py          # Package exports
├── policy.py           # Policy-related schemas
├── webpage.py          # Webpage-related schemas
└── README.md           # This file
```

## Schema Organization

### Policy Schemas (`policy.py`)
- `PolicyProcessingRequest` - Request model for policy analysis
- `PolicyProcessingResponse` - Response model for processed policy
- `UIComponent` - UI component structure for dynamic rendering

### Webpage Schemas (`webpage.py`)
- `WebpageGenerationRequest` - Request model for webpage generation
- `WebpageGenerationResponse` - Response model for webpage generation

## Usage

Import schemas in your route handlers:

```python
from app.api.schemas import (
    PolicyProcessingRequest,
    PolicyProcessingResponse,
    UIComponent,
    WebpageGenerationRequest,
    WebpageGenerationResponse,
)
```

## Benefits of This Structure

1. **Separation of Concerns**: Request/response models are separate from database models
2. **Maintainability**: Easy to find and modify schemas
3. **Reusability**: Schemas can be imported and used across different modules
4. **Type Safety**: Pydantic models provide validation and type hints
5. **Documentation**: Auto-generated API documentation from schemas

## Migration Notes

- Schemas were moved from `main.py` to this dedicated directory
- All imports have been updated to use the new location
- Tests have been created to verify the new structure works correctly 