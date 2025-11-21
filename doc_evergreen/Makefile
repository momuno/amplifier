# doc_evergreen Makefile

.PHONY: help install test check regen-doc

help: ## Show this help message
	@echo "doc_evergreen - AI-powered documentation generator"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies and set up development environment
	@echo "Installing doc_evergreen dependencies..."
	cd .. && uv sync
	@echo ""
	@echo "✅ Installation complete!"
	@echo ""
	@echo "Usage:"
	@echo "  make regen-doc TEMPLATE=examples/simple.json"
	@echo "  make regen-doc TEMPLATE=templates/amplifier_readme.json AUTO=true"
	@echo ""

test: ## Run all tests
	@echo "Running tests..."
	PYTHONPATH=.. uv run pytest tests/ -v

check: ## Run code quality checks
	@echo "Running quality checks..."
	cd .. && make check

regen-doc: ## Regenerate documentation from template (TEMPLATE=path [AUTO=true] [OUTPUT=path])
	@if [ -z "$(TEMPLATE)" ]; then \
		echo "Error: TEMPLATE parameter required"; \
		echo ""; \
		echo "Usage:"; \
		echo "  make regen-doc TEMPLATE=examples/simple.json"; \
		echo "  make regen-doc TEMPLATE=templates/amplifier_readme.json AUTO=true"; \
		echo "  make regen-doc TEMPLATE=examples/simple.json OUTPUT=custom/path.md"; \
		echo "  make regen-doc TEMPLATE=examples/simple.json OUTPUT=test.md AUTO=true"; \
		echo ""; \
		echo "Parameters:"; \
		echo "  TEMPLATE  - Path to template JSON file (required)"; \
		echo "  AUTO      - Set to 'true' for auto-approve mode (optional)"; \
		echo "  OUTPUT    - Override output path from template (optional)"; \
		exit 1; \
	fi
	@CMD="PYTHONPATH=.. uv run python -m cli regen-doc"; \
	if [ "$(AUTO)" = "true" ]; then \
		CMD="$$CMD --auto-approve"; \
	fi; \
	if [ -n "$(OUTPUT)" ]; then \
		CMD="$$CMD --output $(OUTPUT)"; \
	fi; \
	$$CMD $(TEMPLATE)
