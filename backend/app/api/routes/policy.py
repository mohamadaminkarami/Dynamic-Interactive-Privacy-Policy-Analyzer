"""
Policy analysis API routes
"""

import time
import uuid
from datetime import datetime

from app.api.schemas import (
    HealthResponse,
    PolicyProcessingRequest,
    PolicyProcessingResponse,
)
from app.core.config import settings
from app.utils.policy import (
    calculate_compliance_score,
    calculate_overall_privacy_impact,
    calculate_overall_risk,
    calculate_overall_sensitivity,
    calculate_readability_score,
    calculate_user_friendliness,
    chunk_content,
    generate_ui_components,
)
from fastapi import APIRouter, HTTPException
from llm_service import LLMService
from models import PrivacyPolicyDocument

llm_service = LLMService()

router = APIRouter()


@router.post(
    "/analyze",
    response_model=PolicyProcessingResponse,
    summary="Analyze privacy policy content",
    description="Process privacy policy content and generate AI-powered analysis with UI components",
)
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


@router.get(
    "/health",
    summary="Health check for policy service",
    response_model=HealthResponse,
)
async def health_check():
    """Health check endpoint"""
    try:
        # Test LLM service
        llm_health = await llm_service.health_check()

        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            version=settings.APP_VERSION,
            llm_service=llm_health,
            uptime="running",
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@router.get("/models", summary="Get available AI models")
async def available_models():
    """Get available LLM models"""
    return {
        "primary_model": llm_service.primary_model,
        "secondary_model": llm_service.secondary_model,
        "rate_limit": llm_service.max_requests_per_minute,
    }
