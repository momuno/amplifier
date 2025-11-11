.PHONY: help install dev-backend dev-frontend test check clean

# Workspace configuration (can be overridden)
WORKSPACE ?= $(shell pwd)

help:
	@echo "doc-studio - AI-amplified interactive workspace for documentation"
	@echo ""
	@echo "Available commands:"
	@echo "  make install               - Install all dependencies (backend + frontend)"
	@echo "  make dev-backend           - Start backend dev server (uses current directory)"
	@echo "  make dev-frontend          - Start frontend dev server"
	@echo "  make test                  - Run tests"
	@echo "  make check                 - Run linting and type checks"
	@echo "  make clean                 - Remove build artifacts"
	@echo ""
	@echo "Configuration:"
	@echo "  WORKSPACE=<path>          - Set workspace directory (default: current directory)"
	@echo ""
	@echo "Usage examples:"
	@echo "  # Run doc-studio for current repository:"
	@echo "  cd /path/to/your/repo"
	@echo "  /path/to/doc_studio/make dev-backend"
	@echo ""
	@echo "  # Or specify workspace explicitly:"
	@echo "  make dev-backend WORKSPACE=/path/to/your/repo"

install:
	@echo "Installing backend dependencies..."
	uv sync
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

dev-backend:
	@echo "Starting backend dev server on http://localhost:8000"
	@echo "Workspace: $(WORKSPACE)"
	DOC_STUDIO_WORKSPACE=$(WORKSPACE) uv run uvicorn doc_studio.server:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "Starting frontend dev server on http://localhost:5173"
	cd frontend && npm run dev

test:
	uv run pytest

check:
	uv run ruff check .
	uv run ruff format --check .
	uv run pyright

clean:
	rm -rf .venv
	rm -rf frontend/node_modules
	rm -rf frontend/dist
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
