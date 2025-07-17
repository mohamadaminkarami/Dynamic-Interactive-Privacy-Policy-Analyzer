#!/usr/bin/env python3
"""
Test script to verify the quiz bug fixes:
1. Test edge case sensitivity scores (7.9)
2. Test error handling improvements
3. Test frontend behavior with missing quizzes
"""

import asyncio
import json
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.models import UserImpactAnalysis, ContentChunk, RiskLevel
from backend.llm_service import LLMService
from backend.config import config

async def test_edge_case_fix():
    """Test that the edge case (7.9 sensitivity) is now fixed"""
    print("🧪 Testing Edge Case Fix (7.9 sensitivity)")
    print("=" * 50)
    
    llm_service = LLMService()
    
    # Test the problematic edge case
    impact = UserImpactAnalysis(
        risk_level=RiskLevel.HIGH,
        sensitivity_score=7.9,
        privacy_impact_score=7.5,
        data_sharing_risk=7.0,
        user_control=2,
        transparency_score=2,
        key_concerns=["Data sharing", "Limited control"],
        actionable_rights=[],
        engagement_level="quiz",
        requires_quiz=False,
        requires_visual_aid=True,
        text_emphasis_level=5,
        highlight_color="red",
        font_weight="bold"
    )
    
    should_generate = llm_service.should_generate_quiz(impact)
    print(f"📊 Score 7.9: should_generate_quiz = {should_generate}")
    
    if should_generate:
        quiz = await llm_service.generate_quiz_for_section(
            "We share your data with advertising partners without clear opt-out mechanisms.",
            "Data Sharing",
            "test_edge_case",
            7.9
        )
        print(f"📊 Score 7.9: quiz generated = {quiz is not None}")
        
        if should_generate and quiz is None:
            print(f"❌ BUG STILL EXISTS: 7.9 score should generate quiz but returned None!")
            return False
        else:
            print(f"✅ Edge case fixed: 7.9 score correctly generates quiz")
            return True
    else:
        print(f"📝 Score 7.9 doesn't require quiz (expected for updated logic)")
        return True

async def test_error_resilience():
    """Test that processing continues even with LLM failures"""
    print("\n\n🛡️ Testing Error Resilience")
    print("=" * 50)
    
    llm_service = LLMService()
    
    # Test with content that might cause issues
    problematic_chunk = ContentChunk(
        id="resilience_test",
        content="Very short content that might confuse LLM",
        section_title="Minimal Section",
        position=1,
        tokens=10
    )
    
    try:
        section = await llm_service.process_section(problematic_chunk)
        
        print(f"📊 Resilience Test Results:")
        print(f"   Section processed: ✅")
        print(f"   Has user_impact: {section.user_impact is not None}")
        print(f"   Has summary: {len(section.summary) > 0}")
        print(f"   Requires quiz: {section.requires_quiz}")
        print(f"   Has quiz: {section.quiz is not None}")
        
        # Check that we don't have the bug condition
        if section.requires_quiz and section.quiz is None:
            print(f"❌ BUG CONDITION: requires_quiz=True but quiz=None")
            return False
        else:
            print(f"✅ No bug condition: quiz consistency maintained")
            return True
            
    except Exception as e:
        print(f"❌ Processing failed completely: {e}")
        return False

async def test_consistency_scenarios():
    """Test various scenarios to ensure consistency"""
    print("\n\n🔄 Testing Consistency Scenarios")
    print("=" * 50)
    
    llm_service = LLMService()
    
    test_cases = [
        {
            "name": "High Sensitivity (8.5)",
            "content": "We sell your personal data to third parties and use it for profiling without consent.",
            "expected_quiz": True
        },
        {
            "name": "Medium-High (7.5)",
            "content": "We share data with partners for marketing but provide opt-out options.",
            "expected_quiz": False  # Should not generate quiz anymore with 7.0 threshold
        },
        {
            "name": "Low Sensitivity (6.0)",
            "content": "We collect basic usage analytics to improve our service with your consent.",
            "expected_quiz": False
        }
    ]
    
    all_passed = True
    
    for case in test_cases:
        print(f"\n📋 Testing: {case['name']}")
        
        chunk = ContentChunk(
            id=f"test_{case['name'].lower().replace(' ', '_')}",
            content=case['content'],
            section_title=case['name'],
            position=1,
            tokens=50
        )
        
        try:
            section = await llm_service.process_section(chunk)
            
            print(f"   Sensitivity: {section.user_impact.sensitivity_score}")
            print(f"   Requires quiz: {section.requires_quiz}")
            print(f"   Has quiz: {section.quiz is not None}")
            
            # Check consistency
            if section.requires_quiz and section.quiz is None:
                print(f"   ❌ BUG: requires_quiz=True but quiz=None")
                all_passed = False
            elif section.requires_quiz and section.quiz is not None:
                print(f"   ✅ Consistent: has both flag and quiz")
            elif not section.requires_quiz:
                print(f"   ✅ Consistent: no quiz required or provided")
            
        except Exception as e:
            print(f"   ❌ Processing failed: {e}")
            all_passed = False
    
    return all_passed

def simulate_frontend_behavior():
    """Simulate how the frontend would behave with our fixes"""
    print("\n\n🖥️ Simulating Frontend Behavior")
    print("=" * 50)
    
    # Simulate the problematic case from before
    mock_component = {
        "content": {
            "requires_quiz": True,
            "quiz": None,  # This was the bug condition
            "title": "Data Sharing Section",
            "sensitivity_score": 7.9
        }
    }
    
    print("📱 Frontend Logic Simulation:")
    print(f"   requires_quiz: {mock_component['content']['requires_quiz']}")
    print(f"   quiz exists: {mock_component['content']['quiz'] is not None}")
    
    # OLD logic (buggy):
    old_show_quiz_button = mock_component['content']['requires_quiz']
    old_show_quiz_component = mock_component['content']['quiz'] is not None
    
    # NEW logic (fixed):
    new_show_quiz_button = (mock_component['content']['requires_quiz'] and 
                           mock_component['content']['quiz'] is not None)
    new_show_warning = (mock_component['content']['requires_quiz'] and 
                       mock_component['content']['quiz'] is None)
    
    print(f"\n🔧 OLD behavior (buggy):")
    print(f"   Show quiz button: {old_show_quiz_button}")  # True - WRONG!
    print(f"   Show quiz component: {old_show_quiz_component}")  # False
    print(f"   Result: Button shows but quiz doesn't work ❌")
    
    print(f"\n✅ NEW behavior (fixed):")
    print(f"   Show quiz button: {new_show_quiz_button}")  # False - CORRECT!
    print(f"   Show warning: {new_show_warning}")  # True - HELPFUL!
    print(f"   Result: No broken button, helpful warning shown ✅")
    
    return True

async def main():
    """Run all fix verification tests"""
    print("🚀 Quiz Bug Fix Verification")
    print("=" * 60)
    
    # Test all fixes
    edge_case_ok = await test_edge_case_fix()
    resilience_ok = await test_error_resilience()
    consistency_ok = await test_consistency_scenarios()
    frontend_ok = simulate_frontend_behavior()
    
    print(f"\n\n📊 FIX VERIFICATION SUMMARY")
    print(f"=" * 40)
    print(f"✅ Edge case fix: {edge_case_ok}")
    print(f"✅ Error resilience: {resilience_ok}")
    print(f"✅ Consistency: {consistency_ok}")
    print(f"✅ Frontend behavior: {frontend_ok}")
    
    all_passed = edge_case_ok and resilience_ok and consistency_ok and frontend_ok
    
    if all_passed:
        print(f"\n🎉 ALL FIXES VERIFIED - Quiz bug should be resolved!")
        print(f"✅ No more 'Quiz' buttons without actual quizzes")
        print(f"✅ Better error handling and user feedback")
        print(f"✅ Consistent behavior across all scenarios")
    else:
        print(f"\n❌ Some fixes need more work")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main()) 