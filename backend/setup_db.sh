#!/bin/bash
# Database setup script for TrendPulse

set -e

echo "🔧 Setting up TrendPulse Database..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate || source venv/Scripts/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Generate migration
echo "🗄️  Generating initial migration..."
alembic revision --autogenerate -m "initial_auth_tables"

echo "✅ Database setup complete!"
echo ""
echo "Next steps:"
echo "1. Review the generated migration in alembic/versions/"
echo "2. Apply migration: alembic upgrade head"
echo "3. Start the server: uvicorn app.main:app --reload"
