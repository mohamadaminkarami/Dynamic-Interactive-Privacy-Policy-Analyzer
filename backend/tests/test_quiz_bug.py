#!/usr/bin/env python3
"""
Test script to reproduce the quiz bug:
- requires_quiz = True but quiz = None
"""

import asyncio
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.models import UserImpactAnalysis, ContentChunk, RiskLevel
from app.services.policy_analyzer import PolicyAnalyzer



async def test_quiz_bug():
    """Test the quiz generation bug scenario"""
    print("🧪 Testing Quiz Bug Reproduction")
    print("=" * 50)
    
    # Initialize LLM service
    policy_analyzer = PolicyAnalyzer()
    
    # Create a high-sensitivity user impact that should trigger quiz
    high_sensitivity_impact = UserImpactAnalysis(
        risk_level=RiskLevel.HIGH,
        sensitivity_score=8.5,  # High enough to trigger quiz
        privacy_impact_score=8.0,  # High enough to trigger quiz
        data_sharing_risk=7.5,
        user_control=2,
        transparency_score=2,
        key_concerns=["Data sharing with third parties", "Limited user control"],
        actionable_rights=[],
        engagement_level="quiz",
        requires_quiz=False,  # Will be set by should_generate_quiz
        requires_visual_aid=True,
        text_emphasis_level=5,
        highlight_color="red",
        font_weight="bold"
    )
    
    # Test should_generate_quiz logic
    should_generate = policy_analyzer.should_generate_quiz(high_sensitivity_impact)
    print(f"📊 Should generate quiz: {should_generate}")
    print(f"📊 Sensitivity score: {high_sensitivity_impact.sensitivity_score}")
    print(f"📊 Privacy impact: {high_sensitivity_impact.privacy_impact_score}")
    
    # Create a test content chunk
    test_chunk = ContentChunk(
        id="test_chunk_1",
        content="""
        We share your personal data with third-party advertising partners who may use this information 
        to create detailed profiles about you for targeted advertising. This includes your browsing history, 
        purchase behavior, location data, and demographic information. We may sell this data to data brokers 
        who further distribute it to other companies. You cannot opt out of this data sharing.
        """,
        section_title="Data Sharing Practices",
        position=1,
        tokens=150
    )
    
    print(f"\n🔍 Testing quiz generation for high-sensitivity content...")
    print(f"Content: {test_chunk.content[:100]}...")
    
    try:
        # Test direct quiz generation
        quiz = await policy_analyzer.generate_quiz_for_section(
            test_chunk.content,
            test_chunk.section_title or "Test Section",
            test_chunk.id,
            high_sensitivity_impact.sensitivity_score
        )
        
        print(f"\n📋 Quiz generation result:")
        print(f"   Quiz object: {quiz is not None}")
        if quiz:
            print(f"   Quiz ID: {quiz.id}")
            print(f"   Questions: {len(quiz.questions)}")
            print(f"   Title: {quiz.title}")
        else:
            print("   ❌ Quiz is None - this is the bug!")
        
        # Test full section processing
        print(f"\n🔄 Testing full section processing...")
        section = await policy_analyzer.process_section(test_chunk)
        
        print(f"\n📊 Section processing results:")
        print(f"   requires_quiz: {section.requires_quiz}")
        print(f"   quiz object: {section.quiz is not None}")
        print(f"   sensitivity_score: {section.user_impact.sensitivity_score}")
        
        # This is the bug condition
        if section.requires_quiz and section.quiz is None:
            print(f"\n🐛 BUG REPRODUCED!")
            print(f"   - requires_quiz = {section.requires_quiz}")
            print(f"   - quiz = {section.quiz}")
            print(f"   - This will show quiz button but no quiz content!")
            
        elif section.requires_quiz and section.quiz is not None:
            print(f"\n✅ Working correctly:")
            print(f"   - requires_quiz = {section.requires_quiz}")
            print(f"   - quiz has {len(section.quiz.questions)} questions")
            
        else:
            print(f"\n📝 No quiz required for this content")
            
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        print(f"   This might be the cause of the quiz bug!")
        
        # Test if we can still get user impact analysis
        try:
            impact = await policy_analyzer.analyze_user_impact(test_chunk.content)
            should_quiz = policy_analyzer.should_generate_quiz(impact)
            print(f"\n📊 Impact analysis succeeded:")
            print(f"   Sensitivity: {impact.sensitivity_score}")
            print(f"   Should generate quiz: {should_quiz}")
            print(f"   But quiz generation failed - this is the bug!")
        except Exception as e2:
            print(f"   Even impact analysis failed: {e2}")

if __name__ == "__main__":
    asyncio.run(test_quiz_bug()) 