from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


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

class TextSegment(BaseModel):
    """Individual text segment with sensitivity-based styling"""
    id: str = Field(..., description="Unique segment identifier")
    text: str = Field(..., description="The text content")
    sensitivity_score: float = Field(..., ge=0.0, le=10.0, description="Sensitivity score for this segment")
    start_position: int = Field(..., description="Start position in original text")
    end_position: int = Field(..., description="End position in original text")
    
    # Styling properties
    highlight_color: str = Field(default="neutral", description="Background highlight color")
    text_color: str = Field(default="default", description="Text color")
    font_weight: str = Field(default="normal", description="Font weight")
    text_emphasis: int = Field(default=1, ge=1, le=5, description="Text emphasis level")
    requires_attention: bool = Field(default=False, description="Whether this segment requires special attention")
    
    # Contextual information
    context_type: str = Field(default="general", description="Type of content: data_collection, sharing, rights, etc.")
    key_terms: List[str] = Field(default_factory=list, description="Key terms that triggered high sensitivity")

class StyledContent(BaseModel):
    """Content with sensitivity-based styling applied"""
    original_text: str = Field(..., description="Original text content")
    segments: List[TextSegment] = Field(default_factory=list, description="Text segments with styling")
    overall_sensitivity: float = Field(..., ge=0.0, le=10.0, description="Overall sensitivity of the content")
    styling_applied: bool = Field(default=False, description="Whether styling has been applied")
    
    # Styling statistics
    high_sensitivity_count: int = Field(default=0, description="Number of high-sensitivity segments")
    medium_sensitivity_count: int = Field(default=0, description="Number of medium-sensitivity segments")
    total_segments: int = Field(default=0, description="Total number of segments")

class QuizOption(BaseModel):
    """Individual quiz answer option"""
    id: str = Field(..., description="Unique option identifier")
    text: str = Field(..., description="Option text")
    is_correct: bool = Field(..., description="Whether this is the correct answer")
    explanation: Optional[str] = Field(None, description="Explanation for why this is/isn't correct")

class QuizQuestion(BaseModel):
    """Individual quiz question"""
    id: str = Field(..., description="Unique question identifier")
    question_text: str = Field(..., description="The question text")
    question_type: str = Field(default="multiple_choice", description="Type: multiple_choice, true_false, fill_blank")
    options: List[QuizOption] = Field(default_factory=list, description="Answer options")
    correct_explanation: str = Field(..., description="Detailed explanation of the correct answer")
    difficulty: str = Field(default="medium", description="Difficulty: easy, medium, hard")
    points: int = Field(default=1, description="Points awarded for correct answer")
    
    # Content context
    related_content: str = Field(..., description="The original content this question is based on")
    sensitivity_score: float = Field(..., ge=0.0, le=10.0, description="Sensitivity score of related content")
    learning_objective: str = Field(..., description="What the user should learn from this question")

class InteractiveQuiz(BaseModel):
    """Complete quiz for a privacy policy section"""
    id: str = Field(..., description="Unique quiz identifier")
    title: str = Field(..., description="Quiz title")
    description: str = Field(..., description="Brief description of what the quiz covers")
    section_id: str = Field(..., description="ID of the policy section this quiz belongs to")
    
    # Quiz content
    questions: List[QuizQuestion] = Field(default_factory=list, description="Quiz questions")
    estimated_time_minutes: int = Field(default=2, description="Estimated completion time")
    passing_score: int = Field(default=70, description="Minimum percentage to pass")
    
    # Quiz metadata
    total_points: int = Field(default=0, description="Total points available")
    sensitivity_threshold: float = Field(default=8.0, description="Minimum sensitivity score that triggered this quiz")
    created_at: datetime = Field(default_factory=datetime.now, description="Quiz creation timestamp")
    
    # Learning outcomes
    learning_objectives: List[str] = Field(default_factory=list, description="What users will learn")
    key_takeaways: List[str] = Field(default_factory=list, description="Important points to remember")

class QuizResult(BaseModel):
    """User's quiz completion result"""
    quiz_id: str = Field(..., description="Quiz that was taken")
    user_id: Optional[str] = Field(None, description="User identifier (if available)")
    score: int = Field(..., description="Points earned")
    total_points: int = Field(..., description="Total points possible")
    percentage: float = Field(..., description="Percentage score")
    passed: bool = Field(..., description="Whether the user passed")
    time_taken_seconds: int = Field(..., description="Time taken to complete")
    answers: Dict[str, str] = Field(default_factory=dict, description="Question ID to selected answer ID mapping")
    completed_at: datetime = Field(default_factory=datetime.now, description="Completion timestamp")

class UserImpactAnalysis(BaseModel):
    """Analysis of how a policy section impacts users"""
    # Legacy support - derived from sensitivity_score
    risk_level: RiskLevel = Field(..., description="Risk level to users")
    
    # New numerical scoring system (0-10)
    sensitivity_score: float = Field(..., ge=0.0, le=10.0, description="Numerical sensitivity score (0-10)")
    privacy_impact_score: float = Field(..., ge=0.0, le=10.0, description="Impact on user privacy (0-10)")
    data_sharing_risk: float = Field(..., ge=0.0, le=10.0, description="Risk of data sharing/misuse (0-10)")
    
    # Existing scores (1-5)
    user_control: int = Field(..., ge=1, le=5, description="Level of user control (1-5)")
    transparency_score: int = Field(..., ge=1, le=5, description="Transparency score (1-5)")
    
    # Content categorization
    key_concerns: List[str] = Field(default_factory=list, description="Key concerns for users")
    actionable_rights: List[UserRight] = Field(default_factory=list, description="Rights users can exercise")
    
    # Advanced UI features
    engagement_level: str = Field(default="standard", description="UI engagement level: standard, interactive, quiz")
    requires_quiz: bool = Field(default=False, description="Whether this section needs an interactive quiz")
    requires_visual_aid: bool = Field(default=False, description="Whether this section needs AI-generated images")
    text_emphasis_level: int = Field(default=1, ge=1, le=5, description="Text emphasis level for styling (1-5)")
    
    # Visual styling hints
    highlight_color: str = Field(default="neutral", description="Suggested highlight color: neutral, yellow, orange, red")
    font_weight: str = Field(default="normal", description="Suggested font weight: normal, medium, bold")
    
    @property
    def derived_risk_level(self) -> RiskLevel:
        """Derive risk level from sensitivity score for backward compatibility"""
        if self.sensitivity_score >= 7.0:
            return RiskLevel.HIGH
        elif self.sensitivity_score >= 4.0:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

class ProcessedSection(BaseModel):
    """Processed section with enhanced analysis and UI components"""
    id: str = Field(..., description="Unique section identifier")
    title: str = Field(..., description="Section title")
    original_content: str = Field(..., description="Original policy text")
    summary: str = Field(..., description="AI-generated summary")
    styled_content: Optional[StyledContent] = Field(None, description="Content with sensitivity-based styling")
    styled_summary: Optional[StyledContent] = Field(None, description="Summary with sensitivity-based styling")
    
    # Analysis data
    user_impact: UserImpactAnalysis = Field(..., description="User impact analysis")
    component_type: str = Field(..., description="UI component type")
    section_priority: int = Field(..., description="Display priority (1-based)")
    
    # Quiz data for high-sensitivity content
    quiz: Optional[InteractiveQuiz] = Field(None, description="Interactive quiz for high-sensitivity sections (8+)")
    requires_quiz: bool = Field(default=False, description="Whether this section requires a quiz")
    
    # Extracted information
    data_types: List[DataType] = Field(default_factory=list, description="Types of data mentioned")
    user_rights: List[UserRight] = Field(default_factory=list, description="User rights mentioned")
    entities: List[ExtractedEntity] = Field(default_factory=list, description="Extracted entities")
    
    # Legal framework
    legal_frameworks: List[LegalFramework] = Field(default_factory=list, description="Applicable legal frameworks")
    
    # Enhanced scoring metadata
    importance_score: float = Field(..., ge=0.0, le=1.0, description="Importance score for ranking")
    word_count: int = Field(default=0, description="Number of words in section")
    reading_time: int = Field(default=0, description="Estimated reading time in seconds")
    processing_timestamp: datetime = Field(default_factory=datetime.now, description="When this was processed")

    def calculate_priority(self) -> int:
        """Calculate section priority based on various factors"""
        # Base priority on sensitivity score
        priority = int(self.user_impact.sensitivity_score * 10)
        
        # Boost for privacy impact
        priority += int(self.user_impact.privacy_impact_score * 5)
        
        # Boost for data sharing risk
        priority += int(self.user_impact.data_sharing_risk * 3)
        
        # Boost for interactive elements
        if self.requires_quiz:
            priority += 50
        
        return priority

class PrivacyPolicyDocument(BaseModel):
    """Complete processed privacy policy document"""
    id: str = Field(..., description="Unique document identifier")
    company_name: str = Field(..., description="Company name")
    title: str = Field(..., description="Policy title")
    version: Optional[str] = Field(None, description="Policy version")
    effective_date: Optional[datetime] = Field(None, description="Policy effective date")
    
    # Content
    sections: List[ProcessedSection] = Field(default_factory=list, description="Processed sections")
    
    # Legacy analysis (backward compatibility)
    overall_risk_level: RiskLevel = Field(..., description="Overall risk level")
    user_friendliness_score: int = Field(..., ge=1, le=5, description="User friendliness score")
    
    # Enhanced numerical analysis
    overall_sensitivity_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Overall sensitivity (0-10)")
    overall_privacy_impact: float = Field(default=0.0, ge=0.0, le=10.0, description="Overall privacy impact (0-10)")
    compliance_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Compliance with privacy standards (0-10)")
    readability_score: float = Field(default=0.0, ge=0.0, le=10.0, description="How easy to understand (0-10)")
    
    # Document statistics
    total_word_count: int = Field(default=0, description="Total words in document")
    estimated_reading_time: int = Field(default=0, description="Estimated reading time in minutes")
    high_risk_sections: int = Field(default=0, description="Number of high-risk sections")
    interactive_sections: int = Field(default=0, description="Number of sections requiring interaction")
    
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