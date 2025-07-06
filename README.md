# Dynamic Interactive Decentralized Privacy Policy System

A system that transforms legal privacy policy content using LLMs to create dynamically designed, user-friendly interfaces that prioritize user impact over company preferences.

## 🎯 Project Goals

1. **Decentralized Privacy Policy Presentation**: Move away from centralized UI controlled by companies
2. **User-Centric Prioritization**: Rank policy content based on user impact, not company preferences  
3. **Enhanced User Engagement**: Create interactive, engaging content that encourages users to read policies

## 🏗️ System Architecture

The system consists of 5 core components:

1. **Content Ingestion API**: Accepts and preprocesses privacy policy content
2. **LLM Content Processor**: Analyzes content using AI to extract key information
3. **Importance Ranking Engine**: Prioritizes content based on user impact 
4. **Dynamic UI Generator**: Creates engaging interfaces automatically
5. **Component Library**: Reusable UI elements and visual assets

## 🚀 Current Status

✅ **Completed**: 
- System architecture design
- LLM integration setup with OpenAI
- Data models and processing pipeline
- Content analysis and user impact assessment

🔧 **In Progress**:
- LLM provider integration and testing

## 📋 Setup Instructions

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up environment variables**:
Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL_PRIMARY=gpt-4-1106-preview
OPENAI_MODEL_SECONDARY=gpt-3.5-turbo-1106
```

3. **Test the integration**:
```bash
python test_llm_integration.py
```

## 🧪 Testing

The test suite includes:

- **Basic Functionality**: Service initialization and health checks
- **Individual Functions**: Structure analysis, entity extraction, user impact analysis
- **Content Processing**: End-to-end processing of sample privacy policy content

Expected test output:
```
✅ LLM Service initialized successfully
✅ Primary Model: gpt-4-1106-preview
✅ Secondary Model: gpt-3.5-turbo-1106
🎯 Overall: 3/3 tests passed
```

## 🔍 LLM Processing Strategy

### Multi-Stage Processing Pipeline:

1. **Content Preprocessing**: Text extraction, cleaning, and intelligent chunking
2. **Structure Analysis**: Identify sections, hierarchy, and legal clause types
3. **Entity Extraction**: Extract data types, user rights, company obligations
4. **Legal Framework Mapping**: Map to GDPR, CCPA, and other regulations
5. **User Impact Analysis**: Assess real-world impact and risk levels

### Key Features:

- **Dual Model Approach**: GPT-4 for complex analysis, GPT-3.5 for routine tasks
- **Parallel Processing**: Multiple analysis tasks run simultaneously for efficiency
- **Rate Limiting**: Built-in API rate limiting and cost optimization
- **Structured Output**: JSON-formatted responses for consistent data processing

## 📊 Data Models

The system uses structured data models for:

- **ContentChunk**: Individual sections of privacy policies
- **ProcessedSection**: Analyzed content with extracted entities and impact assessment
- **UserImpactAnalysis**: Risk levels, user control, and transparency scores
- **PrivacyPolicyDocument**: Complete processed document with metadata

## 🔮 Next Steps

1. **API Endpoints**: Design and implement REST API for content processing
2. **Dynamic UI Engine**: Create component generation system
3. **Importance Ranking**: Implement user-centric content prioritization
4. **Frontend Interface**: Build user-facing policy viewer
5. **Integration Testing**: End-to-end system testing

## 🛠️ Development

### Project Structure
```
├── config.py              # Configuration management
├── models.py              # Pydantic data models
├── llm_service.py         # LLM integration service
├── test_llm_integration.py # Integration tests
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

### Key Technologies
- **Backend**: Python, FastAPI, Pydantic
- **LLM**: OpenAI GPT-4 and GPT-3.5
- **Processing**: Async/await for parallel processing
- **Data**: Structured JSON with validation

---

*This project is in active development. The LLM integration is complete and ready for testing.* 