#!/bin/bash
set -e

echo "Building frontend..."
cd frontend
npm install
npm run build

echo "Installing backend dependencies..."
cd ../backend
pip install -r requirements.txt

echo "Build complete!"
