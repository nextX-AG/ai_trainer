#!/bin/bash

# Farben für Output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Setting up Cursor AI development environment...${NC}"

# Python venv erstellen
echo -e "${YELLOW}Creating Python virtual environment...${NC}"
python -m venv venv
source venv/bin/activate

# Basis-Installation
echo -e "${YELLOW}Installing base requirements...${NC}"
pip install -e .

# Entwickler-Tools installieren
echo -e "${YELLOW}Installing development requirements...${NC}"
pip install -e ".[dev]"

# Git Hooks installieren
echo -e "${YELLOW}Setting up git hooks...${NC}"
pre-commit install

# Projektstruktur erstellen
echo -e "${YELLOW}Creating project structure...${NC}"
mkdir -p src/{api,base,modules,utils}
mkdir -p tests/{unit,integration}
mkdir -p data/{raw,processed,models}

# Logging-Verzeichnis erstellen
mkdir -p logs

echo -e "${GREEN}Setup complete! Activate the environment with: source venv/bin/activate${NC}" 