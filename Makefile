# Default target
.DEFAULT_GOAL := help

# Silent mode
MAKEFLAGS += -s

# Variables
BASE_BRANCH ?= main
COVERAGE_FILE ?= coverage.xml

# Help target
help:
	@echo "Available commands:"
	@echo "⚈ clean			---> 🧹 Remove all build, test, and cache files"
	@echo "⚈ clean-build		---> 🗑️  Remove build artifacts"

# Cleanup targets
clean-build:
	@echo "🗑️ Cleaning build artifacts..."
	rm -rf src/dist build dist *.egg-info

clean: clean-build
	@echo "🧹 Cleaning all artifacts..."
	rm -rf __pycache__ .tox .pytest_cache .coverage
	find . -type d -name "__pycache__" -exec rm -r {} +

.PHONY: help clean clean-build
