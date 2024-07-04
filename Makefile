# Makefile for KalloPic project

# Variables
VENV_DIR = venv
PYTHON = $(VENV_DIR)/Scripts/python
PIP = $(VENV_DIR)/Scripts/pip
PYINSTALLER = $(VENV_DIR)/Scripts/pyinstaller
MAIN_SCRIPT = kallopic/main.py
APP_NAME = KalloPic
ICON_PATH = resources/logo/logo.ico
SPEC_FILE = kallopic.spec

# Targets

.PHONY: all venv install run build clean

all: venv install run

# Create virtual environment
venv:
    @echo "Creating virtual environment..."
    @python -m venv $(VENV_DIR)

# Install dependencies
install: venv
    @echo "Installing dependencies..."
    @$(PIP) install -r requirements.txt

# Run the application
run: install
    @echo "Running the application..."
    @$(PYTHON) $(MAIN_SCRIPT)

# Build the application
build: install
    @echo "Building the application..."
    @$(PYINSTALLER) --onefile --icon=$(ICON_PATH) $(MAIN_SCRIPT) --name=$(APP_NAME) --add-data=resources/logo/logo.ico;resources/logo

# Clean build files
clean:
    @echo "Cleaning build files..."
    @rm -rf build dist __pycache__ $(VENV_DIR) *.spec

# Ensure make treats these targets as phony (not files)
.PHONY: venv install run build clean