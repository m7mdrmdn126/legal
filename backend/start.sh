#!/bin/bash

# Legal Cases Management System - Startup Script

echo "🚀 Starting Legal Cases Management System Backend..."

# Check if virtual environment exists
if [ ! -d "../.venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source ../.venv/bin/activate

# Check if database exists
if [ ! -f "../database/legal_cases.db" ]; then
    echo "❌ Database not found. Please create the database first."
    echo "Run: cd ../database && python schema.py"
    exit 1
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip install -q -r requirements.txt

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "✅ Dependencies installed"
echo "🔧 Configuration loaded from .env file"
echo "💾 Database: ../database/legal_cases.db"
echo "🌐 Starting server at http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "📖 Redoc Documentation: http://localhost:8000/redoc"
echo ""
echo "🔑 Default Admin Login:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
