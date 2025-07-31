# Dynamic Interactive Decentralized Privacy Policy System
# Makefile for development workflow

.PHONY: help run-server run-client run-all install-backend install-frontend install-all test-backend clean

# Default target
help:
	@echo "🚀 Dynamic Interactive Decentralized Privacy Policy System"
	@echo "=================================================="
	@echo "Available commands:"
	@echo ""
	@echo "  make run-server    - Run backend server (http://localhost:8000)"
	@echo "  make run-client    - Run frontend client (http://localhost:3000)"
	@echo "  make run-all       - Run both backend and frontend concurrently"
	@echo ""
	@echo "  make install-backend   - Install backend dependencies"
	@echo "  make install-frontend  - Install frontend dependencies"
	@echo "  make install-all       - Install all dependencies"
	@echo ""
	@echo "  make test-backend      - Run backend API tests"
	@echo "  make clean            - Clean up processes and cache"
	@echo ""
	@echo "  make help             - Show this help message"

# Backend commands
run-server:
	@echo "Starting FastAPI backend server on http://localhost:8000"
	@echo "API Documentation will be available at http://localhost:8000/docs"
	cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend commands  
run-client:
	@echo "🎨 Starting frontend client..."
	@echo "Client will be available at: http://localhost:3000"
	cd frontend && npm run dev

# Run both backend and frontend concurrently
run-all:
	@echo "🚀 Starting both backend and frontend..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "Press Ctrl+C to stop both servers"
	@echo ""
	@echo "Starting backend server in background..."
	python -m uvicorn backend.main:app --reload --port 8000 & \
	BACKEND_PID=$$!; \
	echo "Backend PID: $$BACKEND_PID"; \
	sleep 3; \
	echo "Starting frontend client..."; \
	cd frontend && npm run dev & \
	FRONTEND_PID=$$!; \
	echo "Frontend PID: $$FRONTEND_PID"; \
	echo "Both servers started. Press Ctrl+C to stop..."; \
	trap "echo 'Stopping servers...'; kill $$BACKEND_PID $$FRONTEND_PID 2>/dev/null || true; exit" INT TERM; \
	wait

# Installation commands
install-backend:
	@echo "📦 Installing backend dependencies..."
	pip install -r backend/requirements.txt

install-frontend:
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install

install-all: install-backend install-frontend
	@echo "✅ All dependencies installed!"

# Testing commands
test-backend:
	@echo "🧪 Running backend tests..."
	cd backend && python test_api.py

# Utility commands
clean:
	@echo "🧹 Cleaning up..."
	@pkill -f "uvicorn backend.main:app" || true
	@pkill -f "npm run dev" || true
	@pkill -f "next dev" || true
	@echo "✅ Cleanup complete!"

# Development helpers
dev-setup: install-all
	@echo "🛠️  Development setup complete!"
	@echo "Run 'make run-all' to start both servers"

# Production build (for future use)
build-frontend:
	@echo "🏗️  Building frontend for production..."
	cd frontend && npm run build

# Health check
health-check:
	@echo "🔍 Checking server health..."
	@curl -s http://localhost:8000/health | python -m json.tool || echo "Backend server not running"

# Quick start guide
quick-start:
	@echo "🚀 Quick Start Guide:"
	@echo "1. make install-all    # Install dependencies"
	@echo "2. make run-all        # Start both servers"
	@echo "3. Open http://localhost:3000 in your browser"
	@echo "4. Use Ctrl+C to stop servers" 