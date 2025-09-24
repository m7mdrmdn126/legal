#!/bin/bash
# Legal Cases Management System - Clean Development Start
# This script starts the application with reduced console noise

echo "Starting Legal Cases Management System..."
echo "========================================"

# Suppress Node.js deprecation warnings
export NODE_NO_WARNINGS=1
export NODE_OPTIONS="--no-deprecation --no-warnings"

# Start the application
npm run electron-dev
