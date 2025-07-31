from typing import Any, Dict

from app.api.schemas import (
    PolicyProcessingRequest,
    WebpageGenerationRequest,
    WebpageGenerationResponse,
)
from app.core.config import settings
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from models import PrivacyPolicyDocument, ProcessedSection
from webpage_generator import WebpageGenerator

router = APIRouter()

# Initialize services

webpage_generator = WebpageGenerator()


# Additional utility endpoints


# Mount static files for generated webpages
router.mount(
    "/static/webpages",
    StaticFiles(directory="generated_webpages"),
    name="generated_webpages",
)

# Webpage Generation Endpoints


@router.get("/templates")
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


@router.post("/generate-webpage", response_model=WebpageGenerationResponse)
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


@router.get("/webpage/{webpage_id}")
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


@router.get("/embed/iframe/{webpage_id}")
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


@router.get("/embed/widget/{webpage_id}")
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


@router.get("/api/webpage/{webpage_id}")
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


@router.get("/webpages")
async def list_generated_webpages():
    """List all generated webpages"""
    try:
        webpages = webpage_generator.list_generated_webpages()
        return {"webpages": webpages, "total_count": len(webpages)}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list webpages: {str(e)}"
        )


@router.post("/analyze-and-generate", response_model=Dict[str, Any])
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
