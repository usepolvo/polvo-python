# Default target
.DEFAULT_GOAL := help

# Silent mode
MAKEFLAGS += -s

# Variables
BASE_BRANCH ?= main
COVERAGE_FILE ?= coverage.xml
FOLDER ?= .

# Help target
help:
	@echo "Available commands:"
	@echo "⚈ help			---> 💡 Show this help"
	@echo "⚈ fmt			---> 🎨 Format code"
	@echo "⚈ sort			---> ⬇️ Sort requirements and env files"
	@echo "⚈ freeze			---> 🧊 Freeze requirements"
	@echo "⚈ clean			---> 🧹 Remove all build, test, and cache files"
	@echo "⚈ clean-build		---> 🗑️  Remove build artifacts"

# Code formatting and organization
fmt:
	@echo "🎨 Formatting code in $(FOLDER)..."
	black --line-length 100 $(FOLDER)

sort:
	@echo "\n> ⬇️ Sorting requirements and env files in $(FOLDER)...\n"
	@for file in $(FOLDER)/requirements*.txt; do \
		if [ -f $$file ]; then \
			sort --ignore-case -u -o $$file{,}; \
			echo "Sorted $$file"; \
		fi \
	done
	@for file in $(FOLDER)/.env*; do \
		if [ -f $$file ]; then \
			sort --ignore-case -u -o $$file{,}; \
			echo "Sorted $$file"; \
		fi \
	done

freeze:
	@echo "\n> 🧊 Freezing requirements in $(FOLDER)...\n"
	@for file in $(FOLDER)/requirements*.txt; do \
		echo "Freezing $$file"; \
		cp "$$file" "$$file.backup"; \
		uv pip install -q --python .venv/bin/python -r "$$file"; \
		rm -f "$$file.temp"; touch "$$file.temp"; \
		grep -v "^#" "$$file" | grep -v "^\s*$$" | while read -r line; do \
			base_pkg=`echo "$$line" | cut -d'[' -f1 | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1 | xargs`; \
			if [ -n "$$base_pkg" ]; then \
				pkg_with_extras=`echo "$$line" | grep -o "[a-zA-Z0-9_.-]\+\(\[[a-zA-Z0-9_,.-]\+\]\)\?" | head -1`; \
				if [ -z "$$pkg_with_extras" ]; then pkg_with_extras="$$base_pkg"; fi; \
				ver=`uv pip list --python .venv/bin/python | grep "^$$base_pkg " | awk '{print $$2}'`; \
				if [ -n "$$ver" ]; then \
					echo "$$pkg_with_extras==$$ver" >> "$$file.temp"; \
				fi; \
			fi; \
		done; \
		if [ -s "$$file.temp" ]; then \
			mv "$$file.temp" "$$file"; \
			echo "Successfully froze $$file"; \
		else \
			mv "$$file.backup" "$$file"; \
			echo "Warning: Could not freeze $$file, restored from backup"; \
		fi; \
		rm -f "$$file.backup" 2>/dev/null || true; \
	done
	@python scripts/update_pyproject.py || echo "Warning: update_pyproject.py script failed"


# Cleanup targets
clean-build:
	@echo "🗑️ Cleaning build artifacts..."
	rm -rf src/dist build dist *.egg-info

clean: clean-build
	@echo "🧹 Cleaning all artifacts..."
	rm -rf __pycache__ .tox .pytest_cache .coverage
	find . -type d -name "__pycache__" -exec rm -r {} +

.PHONY: help clean clean-build
