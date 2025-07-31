"""
Policy-related request and response schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from app.models import PrivacyPolicyDocument
from pydantic import BaseModel, Field


class PolicyAnalyzeRequest(BaseModel):
    """Request model for policy processing"""

    company_name: str = Field(..., description="Name of the company")
    company_url: Optional[str] = Field(None, description="URL of the company")
    contact_email: Optional[str] = Field(None, description="Contact email of the company")
    policy_content: str = Field(..., description="Raw privacy policy text")


class UIComponent(BaseModel):
    """UI component structure for dynamic rendering"""

    id: str = Field(..., description="Unique component ID")
    type: str = Field(
        ..., description="Component type (card, highlight, interactive, etc.)"
    )
    priority: int = Field(..., description="Display priority (1=highest)")
    content: Dict[str, Any] = Field(..., description="Component content and props")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class PolicyAnalyzeResponse(BaseModel):
    """Response model for processed policy"""

    processing_id: str = Field(..., description="Unique processing ID")
    document: PrivacyPolicyDocument = Field(
        ..., description="Processed policy document"
    )
    ui_components: List[UIComponent] = Field(..., description="Dynamic UI components")
    processing_time: float = Field(..., description="Total processing time in seconds")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Processing timestamp"
    )


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    timestamp: str
    version: str
    llm_service: Dict[str, Any]
    uptime: str
