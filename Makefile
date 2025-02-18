include .env

default: run
MAKEFLAGS += -s

help:
	@echo "⚈ run			---> 🎮 Run project locally (default)."
	@echo "⚈ debug			---> 🕵️  Debug project locally."
	@echo "⚈ freeze		---> 🧊 Freeze requirements."
	@echo "⚈ sort			---> ⬇️  Sort requirements and env files alphabetically."
	@echo "⚈ publish		---> 🚀 Build and publish a new package version."

run:
	@echo "\n> 🎮 Running the project locally... (default)\n"

debug:
	@echo "\n> 🕵️  Debugging the project locally...\n"

clean:
	@echo "\n> 🧹 Cleaning up...\n"
	find . -type d -name "__pycache__" -exec rm -r {} +

freeze:
	@echo "\n> 🧊 Freezing the requirements...\n"
	@for file in requirements*.txt; do \
		if [ -f $$file ]; then \
			pip3 freeze -q -r $$file | sed '/freeze/,$$ d' > requirements-froze.txt && mv requirements-froze.txt $$file; \
			echo "Froze requirements in $$file"; \
		else \
			echo "$$file not found, skipping..."; \
		fi \
	done
	@python scripts/update_pyproject.py

sort:
	@echo "\n> ⬇️ Sorting requirements and env files alphabetically...\n"
	@for file in requirements*.txt; do \
		if [ -f $$file ]; then \
			sort --ignore-case -u -o $$file{,}; \
			echo "Sorted $$file"; \
		else \
			echo "$$file not found, skipping..."; \
		fi \
	done
	@for file in .env*; do \
		if [ -f $$file ]; then \
			sort --ignore-case -u -o $$file{,}; \
			echo "Sorted $$file"; \
		else \
			echo "$$file not found, skipping..."; \
		fi \
	done

publish:
	@echo "\n> 🚀 Building and publishing a new package version...\n"
	@echo "\n> 📦 Installing build dependencies...\n"
	pip install -r requirements-build.txt
	@echo "\n> 🗑️ Erasing previous build...\n"
	rm -rf src/dist
	@echo "\n> ⬆️ Bumping package version...\n"
	bump2version patch --verbose
	@echo "\n> 🔨 Building package...\n"
	python -m build src
	@echo "\n> 🌐 Uploading package to Test PyPi...\n"
	python -m twine upload --repository usepolvo-cli src/dist/*
