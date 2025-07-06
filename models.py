from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class RiskLevel(str, Enum):
    """Risk level for privacy policy sections"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class DataType(str, Enum):
    """Types of data collected"""
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    FINANCIAL = "financial"

class UserRight(str, Enum):
    """User rights under privacy policies"""
    ACCESS = "access"
    DELETION = "deletion"
    PORTABILITY = "portability"
    OPT_OUT = "opt_out"
    CORRECTION = "correction"
    CONSENT_WITHDRAWAL = "consent_withdrawal"

class LegalFramework(str, Enum):
    """Legal frameworks and regulations"""
    GDPR = "gdpr"
    CCPA = "ccpa"
    PIPEDA = "pipeda"
    HIPAA = "hipaa"
    FERPA = "ferpa"

class ContentChunk(BaseModel):
    """Individual chunk of privacy policy content"""
    id: str = Field(..., description="Unique identifier for the chunk")
    content: str = Field(..., description="The actual text content")
    section_title: Optional[str] = Field(None, description="Title of the section")
    position: int = Field(..., description="Position in the original document")
    tokens: Optional[int] = Field(None, description="Estimated token count")

class ExtractedEntity(BaseModel):
    """Extracted entity from privacy policy content"""
    entity_type: str = Field(..., description="Type of entity")
    value: str = Field(..., description="The extracted value")
    context: str = Field(..., description="Context where it was found")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")

class UserImpactAnalysis(BaseModel):
    """Analysis of how a policy section impacts users"""
    risk_level: RiskLevel = Field(..., description="Risk level to users")
    user_control: int = Field(..., ge=1, le=5, description="Level of user control (1-5)")
    transparency_score: int = Field(..., ge=1, le=5, description="Transparency score (1-5)")
    key_concerns: List[str] = Field(default_factory=list, description="Key concerns for users")
    actionable_rights: List[UserRight] = Field(default_factory=list, description="Rights users can exercise")

class ProcessedSection(BaseModel):
    """Processed section of a privacy policy"""
    id: str = Field(..., description="Unique identifier")
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Original content")
    summary: str = Field(..., description="AI-generated summary")
    
    # Extracted information
    data_types: List[DataType] = Field(default_factory=list, description="Types of data mentioned")
    user_rights: List[UserRight] = Field(default_factory=list, description="User rights mentioned")
    entities: List[ExtractedEntity] = Field(default_factory=list, description="Extracted entities")
    
    # Analysis
    user_impact: UserImpactAnalysis = Field(..., description="User impact analysis")
    legal_frameworks: List[LegalFramework] = Field(default_factory=list, description="Applicable legal frameworks")
    
    # Metadata
    importance_score: float = Field(..., ge=0.0, le=1.0, description="Importance score for ranking")
    processing_timestamp: datetime = Field(default_factory=datetime.now, description="When this was processed")

class PrivacyPolicyDocument(BaseModel):
    """Complete processed privacy policy document"""
    id: str = Field(..., description="Unique document identifier")
    company_name: str = Field(..., description="Company name")
    title: str = Field(..., description="Policy title")
    version: Optional[str] = Field(None, description="Policy version")
    effective_date: Optional[datetime] = Field(None, description="Policy effective date")
    
    # Content
    sections: List[ProcessedSection] = Field(default_factory=list, description="Processed sections")
    
    # Overall analysis
    overall_risk_level: RiskLevel = Field(..., description="Overall risk level")
    user_friendliness_score: int = Field(..., ge=1, le=5, description="User friendliness score")
    
    # Processing metadata
    processing_status: str = Field(default="pending", description="Processing status")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

class LLMRequest(BaseModel):
    """Request to LLM for processing"""
    prompt: str = Field(..., description="The prompt to send to LLM")
    model: str = Field(..., description="Model to use")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0, description="Temperature for generation")
    max_tokens: int = Field(default=1000, ge=1, le=4000, description="Maximum tokens to generate")
    response_format: Optional[str] = Field(None, description="Response format (json, text)")

class LLMResponse(BaseModel):
    """Response from LLM"""
    content: str = Field(..., description="Generated content")
    llm_model: str = Field(..., description="Model that generated the response")
    tokens_used: int = Field(..., description="Tokens consumed")
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp") 