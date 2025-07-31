#!/usr/bin/env python3
"""
Comprehensive quiz bug testing:
1. Test various failure scenarios
2. Test actual API endpoint
3. Debug the exact conditions causing the bug
"""

import asyncio
import json
import sys
import os
import requests
from unittest.mock import patch

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.models import UserImpactAnalysis, ContentChunk, RiskLevel
from backend.llm_service import LLMService

async def test_quiz_failure_scenarios():
    """Test various scenarios that could cause quiz generation to fail"""
    print("🧪 Testing Quiz Failure Scenarios")
    print("=" * 50)
    
    llm_service = LLMService()
    
    # Scenario 1: LLM API failure simulation
    print("\n📋 Scenario 1: Simulating LLM API failure")
    
    # Create test content
    test_chunk = ContentChunk(
        id="test_fail_1",
        content="We share your data with advertisers without your consent and sell it to data brokers.",
        section_title="High Risk Data Sharing",
        position=1,
        tokens=50
    )
    
    # Mock the LLM call to simulate failure
    original_call_llm = llm_service._call_llm
    
    async def mock_failing_llm_call(request):
        print("   🔴 Simulating LLM API failure...")
        raise Exception("Simulated API failure")
    
    with patch.object(llm_service, '_call_llm', mock_failing_llm_call):
        try:
            quiz = await llm_service.generate_quiz_for_section(
                test_chunk.content,
                test_chunk.section_title,
                test_chunk.id,
                9.0  # High sensitivity
            )
            print(f"   Quiz result: {quiz}")
            if quiz is None:
                print("   🐛 BUG CONDITION: Quiz is None due to API failure!")
        except Exception as e:
            print(f"   Exception caught: {e}")
    
    # Scenario 2: JSON parsing failure
    print("\n📋 Scenario 2: Simulating JSON parsing failure")
    
    async def mock_invalid_json_response(request):
        from backend.models import LLMResponse
        return LLMResponse(
            content="This is not valid JSON at all!",
            llm_model="test",
            tokens_used=100,
            processing_time=1.0
        )
    
    with patch.object(llm_service, '_call_llm', mock_invalid_json_response):
        quiz = await llm_service.generate_quiz_for_section(
            test_chunk.content,
            test_chunk.section_title,
            test_chunk.id,
            9.0
        )
        print(f"   Quiz result: {quiz}")
        if quiz is None:
            print("   🐛 BUG CONDITION: Quiz is None due to JSON parsing failure!")
    
    # Scenario 3: Edge case sensitivity scores
    print("\n📋 Scenario 3: Testing edge case sensitivity scores")
    
    edge_cases = [7.9, 8.0, 8.1]
    for score in edge_cases:
        impact = UserImpactAnalysis(
            risk_level=RiskLevel.HIGH,
            sensitivity_score=score,
            privacy_impact_score=score,
            data_sharing_risk=score,
            user_control=2,
            transparency_score=2,
            key_concerns=["Test concern"],
            actionable_rights=[],
            engagement_level="quiz",
            requires_quiz=False,
            requires_visual_aid=True,
            text_emphasis_level=5,
            highlight_color="red",
            font_weight="bold"
        )
        
        should_generate = llm_service.should_generate_quiz(impact)
        print(f"   Score {score}: should_generate_quiz = {should_generate}")
        
        if should_generate:
            quiz = await llm_service.generate_quiz_for_section(
                "Test content that should trigger quiz",
                "Test Section",
                f"test_{score}",
                score
            )
            print(f"   Score {score}: quiz generated = {quiz is not None}")
            
            if should_generate and quiz is None:
                print(f"   🐛 BUG CONDITION: Score {score} should generate quiz but returned None!")

async def test_full_section_processing():
    """Test full section processing pipeline"""
    print("\n\n🔄 Testing Full Section Processing Pipeline")
    print("=" * 50)
    
    llm_service = LLMService()
    
    # Test with problematic content
    problematic_content = ContentChunk(
        id="problematic_1",
        content="""
        Privacy Policy Section: We collect, use, share, and monetize your personal information including 
        browsing history, location data, contacts, messages, photos, and behavioral patterns. We share 
        this data with hundreds of third-party partners including advertisers, data brokers, and government 
        agencies. You cannot opt out of data collection or sharing. We retain your data indefinitely and 
        may use it for any purpose including creating detailed profiles for marketing and surveillance.
        """,
        section_title="Comprehensive Data Collection and Sharing",
        position=1,
        tokens=200
    )
    
    try:
        section = await llm_service.process_section(problematic_content)
        
        print(f"📊 Processing Results:")
        print(f"   Section ID: {section.id}")
        print(f"   Sensitivity Score: {section.user_impact.sensitivity_score}")
        print(f"   Privacy Impact: {section.user_impact.privacy_impact_score}")
        print(f"   Data Sharing Risk: {section.user_impact.data_sharing_risk}")
        print(f"   requires_quiz: {section.requires_quiz}")
        print(f"   quiz object exists: {section.quiz is not None}")
        
        if section.quiz:
            print(f"   Quiz questions: {len(section.quiz.questions)}")
            for i, q in enumerate(section.quiz.questions):
                print(f"     Q{i+1}: {q.question_text[:60]}...")
        
        # Check for bug condition
        if section.requires_quiz and section.quiz is None:
            print(f"\n🐛 BUG REPRODUCED IN FULL PIPELINE!")
            print(f"   - requires_quiz = {section.requires_quiz}")
            print(f"   - quiz = {section.quiz}")
            return True
        else:
            print(f"\n✅ Full pipeline working correctly")
            return False
            
    except Exception as e:
        print(f"\n❌ Error in full section processing: {e}")
        print(f"   This could cause the bug!")
        return True

def test_api_endpoint():
    """Test the actual API endpoint with problematic content"""
    print("\n\n🌐 Testing Actual API Endpoint")
    print("=" * 50)
    
    # Test data that should trigger high sensitivity and quizzes
    test_policy = {
        "company_name": "Bug Test Company",
        "policy_content": """
        Privacy Policy
        
        Data Collection: We collect all personal information including browsing history, location data, 
        contacts, messages, photos, biometric data, and behavioral patterns through tracking technologies.
        
        Data Sharing: We share your personal data with hundreds of third-party partners including 
        advertisers, data brokers, government agencies, and foreign companies. This data is sold, 
        licensed, and distributed globally without restriction.
        
        User Control: You cannot opt out of data collection, sharing, or processing. We do not provide 
        mechanisms to delete, modify, or access your data. All data is retained indefinitely.
        
        Consequences: Your data may be used for surveillance, discrimination, and manipulation. We are 
        not responsible for how third parties use your information or any resulting harm.
        """
    }
    
    try:
        # Make API request to local server
        response = requests.post(
            "http://localhost:8000/analyze-policy",
            json=test_policy,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"📊 API Response Analysis:")
            print(f"   Processing time: {data['processing_time']:.2f}s")
            print(f"   UI components: {len(data['ui_components'])}")
            
            # Check each component for the bug
            bug_found = False
            for i, component in enumerate(data['ui_components']):
                content = component['content']
                requires_quiz = content.get('requires_quiz', False)
                has_quiz = content.get('quiz') is not None
                
                print(f"\n   Component {i+1}:")
                print(f"     Title: {content['title']}")
                print(f"     Sensitivity: {content['sensitivity_score']}")
                print(f"     requires_quiz: {requires_quiz}")
                print(f"     has_quiz: {has_quiz}")
                
                if requires_quiz and not has_quiz:
                    print(f"     🐛 BUG FOUND! Quiz required but missing!")
                    bug_found = True
                elif requires_quiz and has_quiz:
                    quiz = content['quiz']
                    print(f"     ✅ Quiz present with {len(quiz['questions'])} questions")
            
            if not bug_found:
                print(f"\n✅ No bugs found in API response")
            else:
                print(f"\n🐛 BUG CONFIRMED in API response!")
                
            return bug_found
            
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return True
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to API (http://localhost:8000)")
        print(f"   Make sure backend server is running: uvicorn backend.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return True

async def main():
    """Run all tests"""
    print("🚀 Comprehensive Quiz Bug Testing")
    print("=" * 60)
    
    # Test failure scenarios
    await test_quiz_failure_scenarios()
    
    # Test full pipeline
    pipeline_bug = await test_full_section_processing()
    
    # Test API endpoint
    api_bug = test_api_endpoint()
    
    print(f"\n\n📊 SUMMARY")
    print(f"=" * 30)
    if pipeline_bug or api_bug:
        print(f"🐛 BUG CONFIRMED - Quiz indicators show but quizzes don't render")
        print(f"   Pipeline bug: {pipeline_bug}")
        print(f"   API bug: {api_bug}")
    else:
        print(f"✅ No bugs found - system working correctly")
        print(f"   The issue might be intermittent or content-specific")

if __name__ == "__main__":
    asyncio.run(main()) 