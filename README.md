# Dynamic Interactive Privacy Policy Analyzer

A full-stack system that transforms legal privacy policy content using LLMs to create dynamically designed, user-friendly interfaces that prioritize user impact over company preferences.

## 🎯 Project Goals

1. **Decentralized Privacy Policy Presentation**: Move away from centralized UI controlled by companies
2. **User-Centric Prioritization**: Rank policy content based on user impact, not company preferences  
3. **Enhanced User Engagement**: Create interactive, engaging content that encourages users to read policies

## 🏗️ System Architecture

The system consists of a modern microservices architecture with two main components:

### Backend (FastAPI)
- **Content Ingestion API**: Accepts and preprocesses privacy policy content
- **LLM Content Processor**: Analyzes content using AI to extract key information
- **Importance Ranking Engine**: Prioritizes content based on user impact 
- **Dynamic UI Generator**: Creates engaging interfaces automatically
- **RESTful API**: Provides endpoints for frontend communication

### Frontend (Next.js)
- **Interactive Policy Viewer**: User-friendly interface for viewing policies
- **Dynamic Components**: Reusable UI elements and visual assets
- **Responsive Design**: Modern, accessible interface with smooth animations
- **Real-time Updates**: Dynamic content rendering based on backend analysis

## 🚀 Current Status

✅ **Completed**: 
- Full-stack system architecture with FastAPI backend and Next.js frontend
- Docker containerization with docker-compose orchestration
- LLM integration setup with OpenAI (GPT-4o and GPT-4o-mini)
- Data models and processing pipeline with Pydantic validation
- Content analysis and user impact assessment
- Interactive UI components with animations and drag-and-drop
- Health checks and monitoring setup

🔧 **In Progress**:
- Advanced content prioritization algorithms
- Enhanced interactive elements and user engagement features

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.116.1
- **Runtime**: Python 3.11
- **AI/LLM**: OpenAI API (GPT-4o, GPT-4o-mini)
- **Data Validation**: Pydantic 2.11.7
- **Server**: Uvicorn with async support
- **Configuration**: Environment-based settings with pydantic-settings

### Frontend
- **Framework**: Next.js 15.3.5 with App Router
- **Runtime**: React 19 with TypeScript 5
- **Styling**: Tailwind CSS 4
- **Animations**: Framer Motion 12.23.0
- **Interactions**: DnD Kit for drag-and-drop functionality
- **Build**: Turbopack for fast development

### DevOps
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose with health checks
- **Networking**: Custom Docker network with service discovery
- **Development**: Hot reload support for both services

## 📋 Setup Instructions

### Prerequisites
- Docker (version 20.10 or later)
- Docker Compose (version 2.0 or later)
- OpenAI API key

### 🐳 Docker Deployment (Recommended)

1. **Clone the repository**:
```bash
git clone <repository-url>
cd Dynamic-Interactive-Decentralized-Privacy-Policy-System
```

2. **Set up environment variables**:
```bash
# Create .env file in project root
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

3. **Build and start the services**:
```bash
docker-compose up --build
```

4. **Access the application**:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 🔧 Local Development

For development with hot reload:

1. **Install dependencies**:
```bash
# Backend dependencies
pip install -r backend/requirements.txt

# Frontend dependencies
cd frontend && npm install
```

2. **Set up environment variables**:
```bash
# Create .env file in project root
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL_PRIMARY=gpt-4o
OPENAI_MODEL_SECONDARY=gpt-4o-mini
```

3. **Start both services**:
```bash
# Using Makefile (recommended)
make run-all

# Or manually:
# Backend (Terminal 1)
cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (Terminal 2)
cd frontend && npm run dev
```

## 🧪 Testing

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Frontend health (via Docker)
curl http://localhost:3000
```

## 🔍 LLM Processing Strategy

### Multi-Stage Processing Pipeline:

1. **Content Preprocessing**: Text extraction, cleaning, and intelligent chunking
2. **Structure Analysis**: Identify sections, hierarchy, and legal clause types
3. **Entity Extraction**: Extract data types, user rights, company obligations
4. **Legal Framework Mapping**: Map to GDPR, CCPA, and other regulations
5. **User Impact Analysis**: Assess real-world impact and risk levels

### Key Features:

- **Dual Model Approach**: GPT-4o for complex analysis, GPT-4o-mini for routine tasks
- **Parallel Processing**: Multiple analysis tasks run simultaneously for efficiency
- **Rate Limiting**: Built-in API rate limiting and cost optimization
- **Structured Output**: JSON-formatted responses for consistent data processing

## 📊 Data Models

The system uses structured Pydantic models for:

- **ContentChunk**: Individual sections of privacy policies
- **ProcessedSection**: Analyzed content with extracted entities and impact assessment
- **UserImpactAnalysis**: Risk levels, user control, and transparency scores
- **PrivacyPolicyDocument**: Complete processed document with metadata

## 📁 Project Structure

```
Dynamic-Interactive-Decentralized-Privacy-Policy-System/
├── backend/                     # FastAPI backend service
│   ├── app/
│   │   ├── api/                # API routes and endpoints
│   │   │   ├── routes/         # Route handlers
│   │   │   └── schemas/        # Request/response schemas
│   │   ├── core/               # Core configuration
│   │   ├── models/             # Data models
│   │   ├── services/           # Business logic and LLM integration
│   │   └── utils/              # Utility functions
│   ├── Dockerfile              # Backend container configuration
│   ├── main.py                 # FastAPI application entry point
│   └── requirements.txt        # Python dependencies
├── frontend/                   # Next.js frontend application
│   ├── src/
│   │   ├── app/               # Next.js App Router pages
│   │   ├── components/        # React components
│   │   │   ├── policy/        # Policy-specific components
│   │   │   └── ui/            # Reusable UI components
│   │   ├── lib/               # Frontend utilities and API client
│   │   └── types/             # TypeScript type definitions
│   ├── Dockerfile             # Frontend container configuration
│   └── package.json           # Node.js dependencies and scripts
├── docker-compose.yml         # Multi-service orchestration
├── Makefile                   # Development workflow commands
└── README.Docker.md           # Docker-specific documentation
```

## 🔧 Available Commands

### Docker Commands
```bash
# Start all services
docker-compose up --build

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Development Commands (via Makefile)
```bash
make install-all      # Install all dependencies
make run-all          # Run both backend and frontend
make run-server       # Run backend only
make run-client       # Run frontend only
make test-backend     # Run backend tests
make health-check     # Check service health
make clean           # Stop all processes
```

## 🚨 Environment Variables

### Required
- `OPENAI_API_KEY`: Your OpenAI API key

### Optional
- `OPENAI_MODEL_PRIMARY`: Primary model (default: gpt-4o)
- `OPENAI_MODEL_SECONDARY`: Secondary model (default: gpt-4o-mini)
- `LITELLM_PROXY_URL`: LiteLLM proxy URL if using one
- `DEBUG`: Enable debug mode (default: true in development)


---

*This project uses modern containerization with Docker for easy deployment and development. The system is designed for scalability and maintainability with a clean separation between frontend and backend services.* 
