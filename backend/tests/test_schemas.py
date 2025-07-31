"""
Test the new schema structure and imports
"""
import pytest
from datetime import datetime

from app.api.schemas import (
    PolicyProcessingRequest,
    PolicyProcessingResponse,
    UIComponent,
    WebpageGenerationRequest,
    WebpageGenerationResponse,
)


class TestPolicySchemas:
    """Test policy-related schemas"""

    def test_policy_processing_request(self):
        """Test PolicyProcessingRequest schema"""
        request = PolicyProcessingRequest(
            company_name="Test Company",
            policy_content="This is a test privacy policy content.",
            policy_title="Test Privacy Policy",
        )
        
        assert request.company_name == "Test Company"
        assert request.policy_content == "This is a test privacy policy content."
        assert request.policy_title == "Test Privacy Policy"
        assert request.max_chunk_size == 4000
        assert request.prioritize_user_rights is True

    def test_ui_component(self):
        """Test UIComponent schema"""
        component = UIComponent(
            id="test_component",
            type="highlight_card",
            priority=1,
            content={"title": "Test", "summary": "Test summary"},
            metadata={"test": "data"},
        )
        
        assert component.id == "test_component"
        assert component.type == "highlight_card"
        assert component.priority == 1
        assert component.content["title"] == "Test"
        assert component.metadata["test"] == "data"


class TestWebpageSchemas:
    """Test webpage-related schemas"""

    def test_webpage_generation_request(self):
        """Test WebpageGenerationRequest schema"""
        request = WebpageGenerationRequest(
            processing_id="test-id",
            template_id="modern",
            custom_options={"theme": "dark"},
        )
        
        assert request.processing_id == "test-id"
        assert request.template_id == "modern"
        assert request.custom_options["theme"] == "dark"

    def test_webpage_generation_response(self):
        """Test WebpageGenerationResponse schema"""
        response = WebpageGenerationResponse(
            webpage_id="webpage-123",
            template_id="modern",
            urls={"view": "/webpage/webpage-123"},
            created_at="2024-01-01T00:00:00",
            company_name="Test Company",
        )
        
        assert response.webpage_id == "webpage-123"
        assert response.template_id == "modern"
        assert response.urls["view"] == "/webpage/webpage-123"
        assert response.company_name == "Test Company"


class TestSchemaImports:
    """Test that all schemas can be imported correctly"""

    def test_all_schemas_importable(self):
        """Test that all schemas can be imported from the package"""
        # This test ensures that the __init__.py file is working correctly
        from app.api.schemas import (
            PolicyProcessingRequest,
            PolicyProcessingResponse,
            UIComponent,
            WebpageGenerationRequest,
            WebpageGenerationResponse,
        )
        
        # If we get here without errors, the imports work
        assert True 