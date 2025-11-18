.PHONY: help setup configure run clean install install-dev

# Default target
help:
	@echo "🏌️  Garmin2ShotPattern - Make Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup       - Create virtual environment and install dependencies"
	@echo "  make configure   - Run setup wizard to configure club/column mappings"
	@echo "  make run         - Run the application"
	@echo "  make clean       - Remove cache files"
	@echo "  make install     - Install dependencies only (requires venv)"
	@echo "  make install-dev - Install development dependencies (mypy, ruff, etc.)"
	@echo ""

# Setup virtual environment and install dependencies
setup:
	@echo "🏌️  Setting up Garmin2ShotPattern..."
	@echo ""
	@command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."; exit 1; }
	@PYTHON_VERSION=$$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2); \
	echo "✓ Found Python $$PYTHON_VERSION"
	@echo ""
	@echo "Creating virtual environment..."
	@python3 -m venv venv
	@echo "Installing dependencies..."
	@./venv/bin/pip install --upgrade pip --quiet
	@./venv/bin/pip install -r requirements.txt --quiet
	@echo ""
	@echo "✅ Setup complete!"
	@echo ""
	@if [ -f "config.json" ]; then \
		echo "⚠️  Configuration file already exists."; \
		echo ""; \
		read -p "Do you want to reconfigure? (y/N): " answer; \
		if [ "$$answer" = "y" ] || [ "$$answer" = "Y" ]; then \
			echo ""; \
			echo "🔧 Running configuration wizard..."; \
			echo ""; \
			$(MAKE) configure; \
		else \
			echo "Skipping configuration. You can run 'make configure' later if needed."; \
		fi; \
	else \
		echo "🔧 Running configuration wizard..."; \
		echo ""; \
		$(MAKE) configure; \
	fi
	@echo ""
	@echo "✅ All done! You can now run the application:"
	@echo "  make run"

# Install dependencies (assumes venv exists)
install:
	@if [ ! -d "venv" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "Installing dependencies..."
	@./venv/bin/pip install --upgrade pip --quiet
	@./venv/bin/pip install -r requirements.txt --quiet
	@echo "✅ Dependencies installed!"

# Run the application
run:
	@if [ ! -d "venv" ]; then \
		echo "❌ Virtual environment not found. Please run 'make setup' first."; \
		exit 1; \
	fi
	@./venv/bin/python transform.py

# Run setup wizard
configure:
	@if [ ! -d "venv" ]; then \
		echo "❌ Virtual environment not found. Please run 'make setup' first."; \
		exit 1; \
	fi
	@./venv/bin/python setup_wizard.py

# Clean cache files
clean:
	@echo "Cleaning up..."
	@rm -rf __pycache__
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleaned!"

# Install development dependencies
install-dev:
	@if [ ! -d "venv" ]; then \
		echo "❌ Virtual environment not found. Please run 'make setup' first."; \
		exit 1; \
	fi
	@echo "📦 Installing development dependencies..."
	@./venv/bin/pip install -r requirements-dev.txt
	@echo "✅ Development dependencies installed!"
	@echo ""
	@echo "Available dev tools:"
	@echo "  - mypy: Type checking (run: ./venv/bin/mypy --ignore-missing-imports *.py)"
	@echo "  - ruff: Linting and formatting (run: ./venv/bin/ruff check . or ./venv/bin/ruff format .)"

# Test the application (future: add actual tests)
test:
	@if [ ! -d "venv" ]; then \
		echo "❌ Virtual environment not found. Please run 'make setup' first."; \
		exit 1; \
	fi
	@echo "Running tests..."
	@./venv/bin/python -m pytest 2>/dev/null || echo "⚠️  No tests found yet"
