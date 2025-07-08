#!/usr/bin/env python3
"""
Test script for LLM integration
This script tests the basic functionality of the LLM service
"""

import asyncio
import os
from dotenv import load_dotenv
from .llm_service import LLMService
from .models import ContentChunk

# Load environment variables
load_dotenv()

# Sample privacy policy content for testing
SAMPLE_CONTENT = """
Data Collection and Usage

We collect personal information when you create an account, including your name, email address, and phone number. We also collect behavioral data such as your browsing history, search queries, and interaction patterns with our service. This information is used to personalize your experience, improve our services, and for marketing purposes.

Your data may be shared with third-party partners for advertising and analytics purposes. You have the right to access, modify, or delete your personal information at any time by contacting our support team.
"""

async def test_basic_functionality():
    """Test basic LLM service functionality"""
    print("🔧 Testing LLM Service Integration...")
    
    try:
        # Initialize the service
        llm_service = LLMService()
        print("✅ LLM Service initialized successfully")
        
        # Test health check
        print("\n📊 Testing health check...")
        health_result = await llm_service.health_check()
        print(f"Health Status: {health_result['status']}")
        
        if health_result['status'] == 'healthy':
            print(f"✅ Primary Model: {health_result['model_primary']}")
            print(f"✅ Secondary Model: {health_result['model_secondary']}")
            print(f"✅ Response Time: {health_result['response_time']:.2f}s")
        else:
            print(f"❌ Health check failed: {health_result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to initialize LLM service: {str(e)}")
        return False
    
    return True

async def test_content_processing():
    """Test processing of sample privacy policy content"""
    print("\n🔍 Testing Content Processing...")
    
    try:
        llm_service = LLMService()
        
        # Create a sample content chunk
        chunk = ContentChunk(
            id="test-section-1",
            content=SAMPLE_CONTENT,
            section_title="Data Collection and Usage",
            position=1,
            tokens=int(len(SAMPLE_CONTENT.split()) * 1.3)  # Rough token estimate
        )
        
        print(f"📄 Processing sample content: {chunk.section_title}")
        print(f"📏 Content length: {len(chunk.content)} characters")
        
        # Process the section
        processed_section = await llm_service.process_section(chunk)
        
        print("\n✅ Processing completed successfully!")
        print(f"📋 Summary: {processed_section.summary}")
        print(f"🎯 Importance Score: {processed_section.importance_score:.2f}")
        print(f"⚠️  Risk Level: {processed_section.user_impact.risk_level}")
        print(f"🎮 User Control: {processed_section.user_impact.user_control}/5")
        print(f"👁️  Transparency: {processed_section.user_impact.transparency_score}/5")
        
        if processed_section.data_types:
            print(f"📊 Data Types: {', '.join([dt.value for dt in processed_section.data_types])}")
        
        if processed_section.user_rights:
            print(f"👤 User Rights: {', '.join([ur.value for ur in processed_section.user_rights])}")
        
        if processed_section.entities:
            print(f"🔍 Entities Found: {len(processed_section.entities)}")
            for entity in processed_section.entities[:3]:  # Show first 3 entities
                print(f"  - {entity.entity_type}: {entity.value} (confidence: {entity.confidence:.2f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Content processing failed: {str(e)}")
        return False

async def test_individual_functions():
    """Test individual LLM functions"""
    print("\n🧪 Testing Individual Functions...")
    
    try:
        llm_service = LLMService()
        
        # Test structure analysis
        print("📊 Testing structure analysis...")
        structure = await llm_service.analyze_structure(SAMPLE_CONTENT)
        print(f"  Section Type: {structure.get('section_type', 'N/A')}")
        print(f"  Complexity: {structure.get('complexity_level', 'N/A')}")
        
        # Test entity extraction
        print("\n🔍 Testing entity extraction...")
        entities = await llm_service.extract_entities(SAMPLE_CONTENT)
        print(f"  Found {len(entities)} entities")
        
        # Test user impact analysis
        print("\n👤 Testing user impact analysis...")
        impact = await llm_service.analyze_user_impact(SAMPLE_CONTENT)
        print(f"  Risk Level: {impact.risk_level}")
        print(f"  Key Concerns: {len(impact.key_concerns)} items")
        
        # Test summary generation
        print("\n📝 Testing summary generation...")
        summary = await llm_service.generate_summary(SAMPLE_CONTENT)
        print(f"  Summary length: {len(summary)} characters")
        
        print("\n✅ All individual function tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Individual function tests failed: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting LLM Integration Tests")
    print("=" * 50)
    
    # Check if API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OpenAI API key not found!")
        print("Please set OPENAI_API_KEY environment variable")
        print("You can create a .env file with: OPENAI_API_KEY=your_key_here")
        return
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Individual Functions", test_individual_functions),
        ("Content Processing", test_content_processing),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔥 Running {test_name} Test...")
        try:
            result = await test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} Test: PASSED")
            else:
                print(f"❌ {test_name} Test: FAILED")
        except Exception as e:
            print(f"❌ {test_name} Test: ERROR - {str(e)}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! LLM integration is working correctly.")
        print("\nNext steps:")
        print("1. Create a .env file with your OpenAI API key")
        print("2. Run: python test_llm_integration.py")
        print("3. If tests pass, you're ready to build the API endpoints!")
    else:
        print("⚠️  Some tests failed. Please check the configuration and API key.")

if __name__ == "__main__":
    asyncio.run(main()) 