"""
Webpage-related request and response schemas
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class WebpageGenerationRequest(BaseModel):
    """Request model for webpage generation"""

    processing_id: str = Field(..., description="ID from policy analysis")
    template_id: str = Field(default="modern", description="Template to use")
    custom_options: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Custom options"
    )


class WebpageGenerationResponse(BaseModel):
    """Response model for webpage generation"""

    webpage_id: str = Field(..., description="Generated webpage ID")
    template_id: str = Field(..., description="Template used")
    urls: Dict[str, str] = Field(..., description="Access URLs")
    created_at: str = Field(..., description="Creation timestamp")
    company_name: str = Field(..., description="Company name")
