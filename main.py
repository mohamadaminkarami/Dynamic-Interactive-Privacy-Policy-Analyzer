from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
import time
from datetime import datetime
import uuid

from llm_service import LLMService
from models import (
    PrivacyPolicyDocument, ProcessedSection, RiskLevel,
    ContentChunk, UserImpactAnalysis
)
from config import config

# Initialize FastAPI app
app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="Transform privacy policies into user-centric, dynamic interfaces using AI",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM service
llm_service = LLMService()

# Request/Response Models
class PolicyProcessingRequest(BaseModel):
    """Request model for policy processing"""
    company_name: str = Field(..., description="Name of the company")
    policy_title: str = Field(default="Privacy Policy", description="Title of the policy")
    policy_content: str = Field(..., description="Raw privacy policy text")
    version: Optional[str] = Field(None, description="Policy version")
    effective_date: Optional[datetime] = Field(None, description="Policy effective date")
    
    # Processing options
    max_chunk_size: Optional[int] = Field(default=4000, description="Maximum chunk size for processing")
    prioritize_user_rights: Optional[bool] = Field(default=True, description="Prioritize user rights in analysis")

class UIComponent(BaseModel):
    """UI component structure for dynamic rendering"""
    id: str = Field(..., description="Unique component ID")
    type: str = Field(..., description="Component type (card, highlight, interactive, etc.)")
    priority: int = Field(..., description="Display priority (1=highest)")
    content: Dict[str, Any] = Field(..., description="Component content and props")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class PolicyProcessingResponse(BaseModel):
    """Response model for processed policy"""
    processing_id: str = Field(..., description="Unique processing ID")
    document: PrivacyPolicyDocument = Field(..., description="Processed policy document")
    ui_components: List[UIComponent] = Field(..., description="Dynamic UI components")
    processing_time: float = Field(..., description="Total processing time in seconds")
    timestamp: datetime = Field(default_factory=datetime.now, description="Processing timestamp")

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
            "version": config.APP_VERSION,
            "llm_service": llm_health,
            "uptime": "running"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

# Content Chunking Function
def chunk_content(content: str, max_chunk_size: int = 4000, overlap: int = 200) -> List[ContentChunk]:
    """Intelligently chunk content for processing"""
    chunks = []
    
    # Split by paragraphs first
    paragraphs = content.split('\n\n')
    current_chunk = ""
    chunk_position = 0
    
    for paragraph in paragraphs:
        # If adding this paragraph would exceed chunk size
        if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
            # Create chunk from current content
            chunk_id = f"chunk_{chunk_position}"
            chunks.append(ContentChunk(
                id=chunk_id,
                content=current_chunk.strip(),
                section_title=extract_section_title(current_chunk),
                position=chunk_position,
                tokens=estimate_tokens(current_chunk)
            ))
            
            # Start new chunk with overlap
            overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
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
        chunks.append(ContentChunk(
            id=chunk_id,
            content=current_chunk.strip(),
            section_title=extract_section_title(current_chunk),
            position=chunk_position,
            tokens=estimate_tokens(current_chunk)
        ))
    
    return chunks

def extract_section_title(content: str) -> Optional[str]:
    """Extract section title from content"""
    lines = content.split('\n')
    for line in lines[:3]:  # Check first 3 lines
        line = line.strip()
        if line and len(line) < 100 and not line.endswith('.'):
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
    sorted_sections = sorted(document.sections, key=lambda s: s.importance_score, reverse=True)
    
    for i, section in enumerate(sorted_sections):
        # Determine component type based on content
        component_type = determine_component_type(section)
        
        # Create component
        component = UIComponent(
            id=f"component_{section.id}",
            type=component_type,
            priority=i + 1,
            content={
                "title": section.title,
                "summary": section.summary,
                "risk_level": section.user_impact.risk_level.value,
                "user_control": section.user_impact.user_control,
                "transparency_score": section.user_impact.transparency_score,
                "key_concerns": section.user_impact.key_concerns,
                "user_rights": [right.value for right in section.user_rights],
                "data_types": [dt.value for dt in section.data_types],
                "importance_score": section.importance_score,
                "original_content": section.content
            },
            metadata={
                "processing_timestamp": section.processing_timestamp.isoformat(),
                "entities_count": len(section.entities),
                "actionable_rights": [right.value for right in section.user_impact.actionable_rights]
            }
        )
        
        components.append(component)
    
    return components

def determine_component_type(section: ProcessedSection) -> str:
    """Determine the best UI component type for a section"""
    
    # High importance = highlight card
    if section.importance_score > 0.8:
        return "highlight_card"
    
    # High risk = warning component
    if section.user_impact.risk_level == RiskLevel.HIGH:
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
                detail="Policy content too short. Minimum 100 characters required."
            )
        
        # Step 1: Chunk the content
        chunks = chunk_content(
            request.policy_content, 
            max_chunk_size=request.max_chunk_size
        )
        
        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="Failed to process policy content. Unable to create chunks."
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
                status_code=500,
                detail="Failed to process any sections of the policy."
            )
        
        # Step 3: Calculate overall document metrics
        overall_risk = calculate_overall_risk(processed_sections)
        user_friendliness = calculate_user_friendliness(processed_sections)
        
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
            processing_status="completed"
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
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal processing error: {str(e)}"
        )

def calculate_overall_risk(sections: List[ProcessedSection]) -> RiskLevel:
    """Calculate overall risk level from all sections"""
    risk_scores = {"high": 3, "medium": 2, "low": 1}
    
    if not sections:
        return RiskLevel.MEDIUM
    
    total_score = sum(risk_scores[section.user_impact.risk_level.value] for section in sections)
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
    
    total_transparency = sum(section.user_impact.transparency_score for section in sections)
    total_control = sum(section.user_impact.user_control for section in sections)
    
    avg_transparency = total_transparency / len(sections)
    avg_control = total_control / len(sections)
    
    # Combine transparency and control scores
    friendliness = (avg_transparency + avg_control) / 2
    return int(round(friendliness))

# Additional utility endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Dynamic Interactive Decentralized Privacy Policy System",
        "version": config.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/models")
async def available_models():
    """Get available LLM models"""
    return {
        "primary_model": llm_service.primary_model,
        "secondary_model": llm_service.secondary_model,
        "rate_limit": llm_service.max_requests_per_minute
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 