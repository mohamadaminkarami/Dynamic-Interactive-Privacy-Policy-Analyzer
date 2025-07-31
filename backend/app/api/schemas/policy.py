"""
Policy-related request and response schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from app.models import PrivacyPolicyDocument
from pydantic import BaseModel, Field


class PolicyProcessingRequest(BaseModel):
    """Request model for policy processing"""

    company_name: str = Field(..., description="Name of the company")
    policy_title: str = Field(
        default="Privacy Policy", description="Title of the policy"
    )
    policy_content: str = Field(..., description="Raw privacy policy text")
    version: Optional[str] = Field(None, description="Policy version")
    effective_date: Optional[datetime] = Field(
        None, description="Policy effective date"
    )

    # Processing options
    max_chunk_size: Optional[int] = Field(
        default=4000, description="Maximum chunk size for processing"
    )
    prioritize_user_rights: Optional[bool] = Field(
        default=True, description="Prioritize user rights in analysis"
    )


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


class PolicyProcessingResponse(BaseModel):
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
