#!/bin/bash

set -e

echo "Creating virtual environment..."
py -m venv venv

echo "Activating virtual environment..."
source venv/Scripts/activate

echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Installing Playwright browsers..."
playwright install chromium

echo "Starting Flask server on http://localhost:8000"
py app.py
