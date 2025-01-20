#!/bin/bash

echo "Installiere Cursor AI..."

# Aktiviere venv
source venv/bin/activate

# Deinstalliere alte Version
pip uninstall cursor-ai -y

# Installiere Projekt und Dependencies
pip install -e .

# Überprüfe Installation
python -c "import supabase" && echo "Installation erfolgreich!" || echo "Installation fehlgeschlagen!" 