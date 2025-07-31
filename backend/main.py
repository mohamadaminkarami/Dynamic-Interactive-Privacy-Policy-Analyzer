import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

import uvicorn
from app.core.config import settings
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from llm_service import LLMService
from models import (ContentChunk, PrivacyPolicyDocument, ProcessedSection,
                     RiskLevel)
from webpage_generator import WebpageGenerator


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Privacy Policy System Backend starting up...")
    yield
    # Shutdown
    print("🛑 Privacy Policy System Backend shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Transform privacy policies into user-centric, dynamic interfaces using AI",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.get


# ------------------------------


# Initialize services
llm_service = LLMService()
webpage_generator = WebpageGenerator()


# Request/Response Models
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


# Health Check Endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test LLM service
        llm_health = await llm_service.health_check()

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": settings.APP_VERSION,
            "llm_service": llm_health,
            "uptime": "running",
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


# Content Chunking Function
def chunk_content(
    content: str, max_chunk_size: int = 4000, overlap: int = 200
) -> List[ContentChunk]:
    """Intelligently chunk content for processing"""
    chunks = []

    # Split by paragraphs first
    paragraphs = content.split("\n\n")
    current_chunk = ""
    chunk_position = 0

    for paragraph in paragraphs:
        # If adding this paragraph would exceed chunk size
        if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
            # Create chunk from current content
            chunk_id = f"chunk_{chunk_position}"
            chunks.append(
                ContentChunk(
                    id=chunk_id,
                    content=current_chunk.strip(),
                    section_title=extract_section_title(current_chunk),
                    position=chunk_position,
                    tokens=estimate_tokens(current_chunk),
                )
            )

            # Start new chunk with overlap
            overlap_text = (
                current_chunk[-overlap:]
                if len(current_chunk) > overlap
                else current_chunk
            )
            current_chunk = overlap_text + "\n\n" + paragraph
            chunk_position += 1
        else:
            # Add paragraph to current chunk
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph

    # Add final chunk if there's remaining content
    if current_chunk.strip():
        chunk_id = f"chunk_{chunk_position}"
        chunks.append(
            ContentChunk(
                id=chunk_id,
                content=current_chunk.strip(),
                section_title=extract_section_title(current_chunk),
                position=chunk_position,
                tokens=estimate_tokens(current_chunk),
            )
        )

    return chunks


def extract_section_title(content: str) -> Optional[str]:
    """Extract section title from content"""
    lines = content.split("\n")
    for line in lines[:3]:  # Check first 3 lines
        line = line.strip()
        if line and len(line) < 100 and not line.endswith("."):
            # Likely a title
            return line
    return None


def estimate_tokens(text: str) -> int:
    """Estimate token count for text"""
    return int(len(text.split()) * 1.3)


# UI Component Generation
def generate_ui_components(document: PrivacyPolicyDocument) -> List[UIComponent]:
    """Generate dynamic UI components from processed document"""
    components = []

    # Sort sections by importance score
    sorted_sections = sorted(
        document.sections, key=lambda s: s.importance_score, reverse=True
    )

    for i, section in enumerate(sorted_sections):
        # Determine component type based on content and new scoring
        component_type = determine_component_type(section)

        # Create component with enhanced numerical scoring
        component = UIComponent(
            id=f"component_{section.id}",
            type=component_type,
            priority=i + 1,
            content={
                "title": section.title,
                "summary": section.summary,
                "risk_level": section.user_impact.risk_level.value,
                # Enhanced numerical scores
                "sensitivity_score": section.user_impact.sensitivity_score,
                "privacy_impact_score": section.user_impact.privacy_impact_score,
                "data_sharing_risk": section.user_impact.data_sharing_risk,
                # Original scores
                "user_control": section.user_impact.user_control,
                "transparency_score": section.user_impact.transparency_score,
                "key_concerns": section.user_impact.key_concerns,
                "user_rights": [right.value for right in section.user_rights],
                "data_types": [dt.value for dt in section.data_types],
                "importance_score": section.importance_score,
                "original_content": section.original_content,
                # Enhanced UI features
                "engagement_level": section.user_impact.engagement_level,
                "requires_quiz": section.user_impact.requires_quiz,
                "requires_visual_aid": section.user_impact.requires_visual_aid,
                "text_emphasis_level": section.user_impact.text_emphasis_level,
                "highlight_color": section.user_impact.highlight_color,
                "font_weight": section.user_impact.font_weight,
                # Additional metadata
                "word_count": section.word_count,
                "reading_time": section.reading_time,
                # Styled content for text visualization
                "styled_content": (
                    section.styled_content.dict() if section.styled_content else None
                ),
                "styled_summary": (
                    section.styled_summary.dict() if section.styled_summary else None
                ),
                # Quiz data for high-sensitivity sections
                "quiz": section.quiz.dict() if section.quiz else None,
            },
            metadata={
                "processing_timestamp": section.processing_timestamp.isoformat(),
                "entities_count": len(section.entities),
                "actionable_rights": [
                    right.value for right in section.user_impact.actionable_rights
                ],
                "section_priority": section.section_priority,
                "ui_enhancement_features": {
                    "needs_interaction": section.user_impact.engagement_level
                    in ["interactive", "quiz"],
                    "high_attention": section.user_impact.sensitivity_score >= 8.0,
                    "visual_aids_needed": section.user_impact.requires_visual_aid,
                    "quiz_recommended": section.user_impact.requires_quiz,
                    "styled_content_available": section.styled_content is not None
                    and section.styled_content.styling_applied,
                    "styled_summary_available": section.styled_summary is not None
                    and section.styled_summary.styling_applied,
                },
            },
        )

        components.append(component)

    return components


def determine_component_type(section: ProcessedSection) -> str:
    """Determine the best UI component type for a section based on enhanced scoring"""

    # Use engagement level as primary determinant
    if section.user_impact.engagement_level == "quiz":
        return "quiz_component"

    if section.user_impact.engagement_level == "interactive":
        return "interactive_component"

    # High sensitivity scores get special treatment
    if section.user_impact.sensitivity_score >= 8.0:
        return "high_sensitivity_card"

    # High privacy impact = warning component
    if section.user_impact.privacy_impact_score >= 7.0:
        return "privacy_warning"

    # High importance = highlight card
    if section.importance_score > 0.8:
        return "highlight_card"

    # High data sharing risk = risk warning
    if section.user_impact.data_sharing_risk >= 7.0:
        return "risk_warning"

    # User rights = interactive component
    if section.user_rights:
        return "rights_interactive"

    # Data collection = data card
    if section.data_types:
        return "data_collection_card"

    # Default = standard card
    return "standard_card"


# Main Processing Endpoint
@app.post("/analyze-policy", response_model=PolicyProcessingResponse)
async def analyze_policy(request: PolicyProcessingRequest):
    """
    Analyze a privacy policy and generate user-centric dynamic UI components
    """
    start_time = time.time()
    processing_id = str(uuid.uuid4())

    try:
        # Validate input
        if len(request.policy_content.strip()) < 100:
            raise HTTPException(
                status_code=400,
                detail="Policy content too short. Minimum 100 characters required.",
            )

        # Step 1: Chunk the content
        chunks = chunk_content(
            request.policy_content, max_chunk_size=request.max_chunk_size
        )

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="Failed to process policy content. Unable to create chunks.",
            )

        # Step 2: Process chunks in parallel
        print(f"🔄 Processing {len(chunks)} chunks for {request.company_name}")

        # Process chunks concurrently (but respect rate limits)
        processed_sections = []
        for chunk in chunks:
            try:
                section = await llm_service.process_section(chunk)
                processed_sections.append(section)
                print(f"✅ Processed chunk {chunk.position}: {section.title}")
            except Exception as e:
                print(f"⚠️  Failed to process chunk {chunk.position}: {str(e)}")
                # Continue with other chunks
                continue

        if not processed_sections:
            raise HTTPException(
                status_code=500, detail="Failed to process any sections of the policy."
            )

        # Step 3: Calculate overall document metrics
        overall_risk = calculate_overall_risk(processed_sections)
        user_friendliness = calculate_user_friendliness(processed_sections)

        # Calculate enhanced numerical scores
        overall_sensitivity = calculate_overall_sensitivity(processed_sections)
        overall_privacy_impact = calculate_overall_privacy_impact(processed_sections)
        compliance_score = calculate_compliance_score(processed_sections)
        readability_score = calculate_readability_score(processed_sections)

        # Calculate document statistics
        total_words = sum(section.word_count for section in processed_sections)
        estimated_reading_time = max(1, total_words // 200)  # ~200 words per minute
        high_risk_count = sum(
            1
            for section in processed_sections
            if section.user_impact.sensitivity_score >= 8.0
        )
        interactive_count = sum(
            1
            for section in processed_sections
            if section.user_impact.engagement_level in ["interactive", "quiz"]
        )

        # Step 4: Create processed document
        document = PrivacyPolicyDocument(
            id=processing_id,
            company_name=request.company_name,
            title=request.policy_title,
            version=request.version,
            effective_date=request.effective_date,
            sections=processed_sections,
            overall_risk_level=overall_risk,
            user_friendliness_score=user_friendliness,
            # Enhanced numerical scores
            overall_sensitivity_score=overall_sensitivity,
            overall_privacy_impact=overall_privacy_impact,
            compliance_score=compliance_score,
            readability_score=readability_score,
            # Document statistics
            total_word_count=total_words,
            estimated_reading_time=estimated_reading_time,
            high_risk_sections=high_risk_count,
            interactive_sections=interactive_count,
            processing_status="completed",
        )

        # Step 5: Generate dynamic UI components
        ui_components = generate_ui_components(document)

        processing_time = time.time() - start_time

        print(f"🎉 Policy processing completed in {processing_time:.2f}s")
        print(f"📊 Generated {len(ui_components)} UI components")

        return PolicyProcessingResponse(
            processing_id=processing_id,
            document=document,
            ui_components=ui_components,
            processing_time=processing_time,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal processing error: {str(e)}"
        )


def calculate_overall_risk(sections: List[ProcessedSection]) -> RiskLevel:
    """Calculate overall risk level from all sections"""
    risk_scores = {"high": 3, "medium": 2, "low": 1}

    if not sections:
        return RiskLevel.MEDIUM

    total_score = sum(
        risk_scores[section.user_impact.risk_level.value] for section in sections
    )
    avg_score = total_score / len(sections)

    if avg_score >= 2.5:
        return RiskLevel.HIGH
    elif avg_score >= 1.5:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.LOW


def calculate_user_friendliness(sections: List[ProcessedSection]) -> int:
    """Calculate overall user friendliness score (1-5)"""
    if not sections:
        return 3

    total_transparency = sum(
        section.user_impact.transparency_score for section in sections
    )
    total_control = sum(section.user_impact.user_control for section in sections)

    avg_transparency = total_transparency / len(sections)
    avg_control = total_control / len(sections)

    # Combine transparency and control scores
    friendliness = (avg_transparency + avg_control) / 2
    return int(round(friendliness))


def calculate_overall_sensitivity(sections: List[ProcessedSection]) -> float:
    """Calculate overall sensitivity score (0-10) from all sections"""
    if not sections:
        return 5.0

    # Weight by importance score
    weighted_sum = sum(
        section.user_impact.sensitivity_score * section.importance_score
        for section in sections
    )
    total_weight = sum(section.importance_score for section in sections)

    if total_weight == 0:
        return sum(section.user_impact.sensitivity_score for section in sections) / len(
            sections
        )

    return round(weighted_sum / total_weight, 1)


def calculate_overall_privacy_impact(sections: List[ProcessedSection]) -> float:
    """Calculate overall privacy impact score (0-10) from all sections"""
    if not sections:
        return 5.0

    # Weight by importance score
    weighted_sum = sum(
        section.user_impact.privacy_impact_score * section.importance_score
        for section in sections
    )
    total_weight = sum(section.importance_score for section in sections)

    if total_weight == 0:
        return sum(
            section.user_impact.privacy_impact_score for section in sections
        ) / len(sections)

    return round(weighted_sum / total_weight, 1)


def calculate_compliance_score(sections: List[ProcessedSection]) -> float:
    """Calculate compliance score (0-10) based on transparency and user control"""
    if not sections:
        return 5.0

    # Calculate based on transparency and user control
    avg_transparency = sum(
        section.user_impact.transparency_score for section in sections
    ) / len(sections)
    avg_control = sum(section.user_impact.user_control for section in sections) / len(
        sections
    )

    # Convert from 1-5 scale to 0-10 scale
    compliance = ((avg_transparency + avg_control) / 2) * 2
    return round(compliance, 1)


def calculate_readability_score(sections: List[ProcessedSection]) -> float:
    """Calculate readability score (0-10) based on section complexity and clarity"""
    if not sections:
        return 5.0

    # Base score on transparency scores and content complexity
    avg_transparency = sum(
        section.user_impact.transparency_score for section in sections
    ) / len(sections)

    # Adjust based on content length (longer sections are typically harder to read)
    avg_word_count = sum(section.word_count for section in sections) / len(sections)
    length_penalty = min(2.0, avg_word_count / 200)  # Penalty for long sections

    readability = (avg_transparency * 2) - length_penalty
    return round(max(0.0, min(10.0, readability)), 1)


# Additional utility endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/models")
async def available_models():
    """Get available LLM models"""
    return {
        "primary_model": llm_service.primary_model,
        "secondary_model": llm_service.secondary_model,
        "rate_limit": llm_service.max_requests_per_minute,
    }


# Mount static files for generated webpages
app.mount(
    "/static/webpages",
    StaticFiles(directory="generated_webpages"),
    name="generated_webpages",
)

# Webpage Generation Endpoints


@app.get("/templates")
async def get_available_templates():
    """Get available webpage templates"""
    try:
        return {
            "templates": webpage_generator.get_available_templates(),
            "total_count": len(webpage_generator.templates),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve templates: {str(e)}"
        )


@app.post("/generate-webpage", response_model=WebpageGenerationResponse)
async def generate_webpage(request: WebpageGenerationRequest):
    """
    Generate an embeddable webpage from existing policy analysis
    """
    try:
        # For now, we'll need to store analysis results to retrieve them later
        # This is a simplified version - in production you'd have a database

        # Mock data for testing - replace with actual data retrieval
        # In a real implementation, you'd retrieve the document and components
        # from a database using the processing_id

        # For demonstration, create a simple mock document
        from .models import RiskLevel

        document = PrivacyPolicyDocument(
            id=request.processing_id,
            company_name="Demo Company",
            title="Privacy Policy",
            sections=[],
            overall_risk_level=RiskLevel.MEDIUM,
            user_friendliness_score=4,
            overall_sensitivity_score=6.5,
            overall_privacy_impact=7.2,
            compliance_score=8.1,
            readability_score=7.5,
            total_word_count=500,
            estimated_reading_time=3,
            high_risk_sections=1,
            interactive_sections=2,
            processing_status="completed",
        )

        # Mock ProcessedSections
        from .models import DataType, UserImpactAnalysis, UserRight

        sections = [
            ProcessedSection(
                id="demo_1",
                title="Data Collection",
                original_content="We collect personal information including email, name, and usage data to provide our services. This data may be shared with third parties for marketing purposes.",
                summary="We collect personal information including email, name, and usage data to provide our services.",
                user_impact=UserImpactAnalysis(
                    risk_level=RiskLevel.MEDIUM,
                    sensitivity_score=6.8,
                    privacy_impact_score=7.1,
                    data_sharing_risk=6.5,
                    user_control=3,
                    transparency_score=4,
                    key_concerns=[
                        "Data retention period unclear",
                        "Third-party sharing",
                    ],
                    actionable_rights=[UserRight.ACCESS, UserRight.DELETION],
                    engagement_level="standard",
                    requires_quiz=False,
                    requires_visual_aid=False,
                    text_emphasis_level=2,
                    highlight_color="yellow",
                    font_weight="medium",
                ),
                component_type="highlight_card",
                section_priority=1,
                data_types=[DataType.PERSONAL, DataType.BEHAVIORAL],
                user_rights=[
                    UserRight.ACCESS,
                    UserRight.DELETION,
                    UserRight.PORTABILITY,
                ],
                importance_score=0.85,
                word_count=150,
            )
        ]

        # Generate webpage
        webpage_metadata = webpage_generator.generate_webpage(
            document=document,
            sections=sections,
            template_id=request.template_id,
            custom_options=request.custom_options,
        )

        return WebpageGenerationResponse(
            webpage_id=webpage_metadata["webpage_id"],
            template_id=webpage_metadata["template_id"],
            urls=webpage_metadata["urls"],
            created_at=webpage_metadata["created_at"],
            company_name=webpage_metadata["company_name"],
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Webpage generation failed: {str(e)}"
        )


@app.get("/webpage/{webpage_id}")
async def serve_webpage(webpage_id: str):
    """Serve a generated webpage"""
    try:
        webpage_info = webpage_generator.get_webpage_info(webpage_id)
        if not webpage_info:
            raise HTTPException(status_code=404, detail="Webpage not found")

        # Serve the HTML file
        html_file = webpage_generator.output_dir / webpage_id / "index.html"
        if not html_file.exists():
            raise HTTPException(status_code=404, detail="Webpage file not found")

        with open(html_file, "r", encoding="utf-8") as f:
            content = f.read()

        return HTMLResponse(content=content)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to serve webpage: {str(e)}"
        )


@app.get("/embed/iframe/{webpage_id}")
async def serve_iframe_embed(webpage_id: str):
    """Serve webpage optimized for iframe embedding"""
    try:
        webpage_info = webpage_generator.get_webpage_info(webpage_id)
        if not webpage_info:
            raise HTTPException(status_code=404, detail="Webpage not found")

        # Create iframe-optimized version
        iframe_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{webpage_info.get('company_name', 'Company')} Privacy Policy</title>
            <style>
                body {{ margin: 0; padding: 0; font-family: system-ui, sans-serif; }}
                iframe {{ width: 100%; height: 600px; border: none; }}
            </style>
        </head>
        <body>
            <iframe src="/webpage/{webpage_id}" title="Privacy Policy"></iframe>
            <script>
                // Auto-resize iframe based on content
                window.addEventListener('message', function(e) {{
                    if (e.data.type === 'resize') {{
                        document.querySelector('iframe').style.height = e.data.height + 'px';
                    }}
                }});
            </script>
        </body>
        </html>
        """

        return HTMLResponse(content=iframe_html)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to serve iframe: {str(e)}")


@app.get("/embed/widget/{webpage_id}")
async def serve_widget_embed(webpage_id: str):
    """Serve JavaScript widget for embedding"""
    try:
        webpage_info = webpage_generator.get_webpage_info(webpage_id)
        if not webpage_info:
            raise HTTPException(status_code=404, detail="Webpage not found")

        # Create JavaScript widget
        widget_js = f"""
        (function() {{
            var containerId = 'privacy-policy-widget-{webpage_id}';
            var container = document.getElementById(containerId);
            
            if (container) {{
                var iframe = document.createElement('iframe');
                iframe.src = '{settings.APP_VERSION}/embed/iframe/{webpage_id}';
                iframe.style.width = '100%';
                iframe.style.height = '600px';
                iframe.style.border = 'none';
                iframe.title = '{webpage_info.get("company_name", "Company")} Privacy Policy';
                
                container.appendChild(iframe);
                
                // Auto-resize functionality
                window.addEventListener('message', function(e) {{
                    if (e.data.type === 'resize' && e.data.source === '{webpage_id}') {{
                        iframe.style.height = e.data.height + 'px';
                    }}
                }});
            }}
        }})();
        """

        return HTMLResponse(content=widget_js, media_type="application/javascript")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to serve widget: {str(e)}")


@app.get("/api/webpage/{webpage_id}")
async def get_webpage_info(webpage_id: str):
    """Get metadata about a generated webpage"""
    try:
        webpage_info = webpage_generator.get_webpage_info(webpage_id)
        if not webpage_info:
            raise HTTPException(status_code=404, detail="Webpage not found")

        return webpage_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve webpage info: {str(e)}"
        )


@app.get("/webpages")
async def list_generated_webpages():
    """List all generated webpages"""
    try:
        webpages = webpage_generator.list_generated_webpages()
        return {"webpages": webpages, "total_count": len(webpages)}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list webpages: {str(e)}"
        )


@app.post("/analyze-and-generate", response_model=Dict[str, Any])
async def analyze_and_generate_webpage(request: PolicyProcessingRequest):
    """
    Analyze a privacy policy AND generate a webpage in one step
    """
    try:
        # Step 1: Analyze the policy (reuse existing logic)
        analysis_response = await analyze_policy(request)

        # Step 2: Generate webpage from analysis
        webpage_request = WebpageGenerationRequest(
            processing_id=analysis_response.processing_id,
            template_id="modern",  # Default template
            custom_options={},
        )

        webpage_response = await generate_webpage(webpage_request)

        # Return combined response
        return {
            "analysis": analysis_response.dict(),
            "webpage": webpage_response.dict(),
            "message": "Policy analyzed and webpage generated successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Analysis and generation failed: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
