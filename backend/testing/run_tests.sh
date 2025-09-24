#!/bin/bash

# Legal Cases Backend API Testing Suite
# This script runs comprehensive tests for all API endpoints

echo "======================================"
echo "Legal Cases Backend API Testing Suite"
echo "======================================"

# Check if we're in the correct directory
if [ ! -f "main.py" ]; then
    echo "Error: Please run this script from the backend directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "../.venv" ]; then
    echo "Error: Virtual environment not found. Please set up the project first."
    exit 1
fi

# Activate virtual environment
source ../.venv/bin/activate

# Install test requirements
echo "Installing test dependencies..."
pip install -r testing/requirements-test.txt -q

# Ensure the server is running
echo "Starting the server for testing..."
python main.py &
SERVER_PID=$!
sleep 5

# Function to cleanup server
cleanup() {
    echo "Cleaning up server..."
    kill $SERVER_PID 2>/dev/null
    exit
}
trap cleanup EXIT INT TERM

# Wait for server to be ready
echo "Waiting for server to be ready..."
for i in {1..10}; do
    if curl -s http://localhost:8000/docs > /dev/null; then
        echo "Server is ready!"
        break
    fi
    sleep 2
    if [ $i -eq 10 ]; then
        echo "Server failed to start"
        exit 1
    fi
done

echo ""
echo "Running comprehensive API tests..."
echo "=================================="

# Run all tests with verbose output
cd testing

echo ""
echo "1. Testing Authentication..."
python -m pytest test_auth.py -v --tb=short

echo ""
echo "2. Testing User Management..."
python -m pytest test_users.py -v --tb=short

echo ""
echo "3. Testing Case Types..."
python -m pytest test_case_types.py -v --tb=short

echo ""
echo "4. Testing Cases..."
python -m pytest test_cases.py -v --tb=short

echo ""
echo "5. Testing Case Sessions..."
python -m pytest test_case_sessions.py -v --tb=short

echo ""
echo "6. Testing Case Notes..."
python -m pytest test_case_notes.py -v --tb=short

echo ""
echo "7. Testing Statistics..."
python -m pytest test_statistics.py -v --tb=short

echo ""
echo "8. Testing Arabic Search..."
python -m pytest test_arabic_search.py -v --tb=short

echo ""
echo "9. Testing Integration Workflows..."
python -m pytest test_integration.py -v --tb=short

echo ""
echo "Running all tests together for final verification..."
python -m pytest . -v --tb=short --durations=10

echo ""
echo "======================================"
echo "Testing completed!"
echo "======================================"

# Generate coverage report if coverage is available
if command -v coverage &> /dev/null; then
    echo "Generating coverage report..."
    coverage run -m pytest .
    coverage report
    coverage html
    echo "Coverage report generated in htmlcov/"
fi
