#!/bin/bash

# Legal Cases Desktop App - Linux Build Script
echo "Building Legal Cases Desktop App for Linux..."

# Check if Node.js and npm are installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed. Please install Node.js first."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed. Please install npm first."
    exit 1
fi

# Create simple icon if it doesn't exist
if [ ! -f "build-assets/icon.png" ]; then
    echo "Creating simple app icon..."
    mkdir -p build-assets
    # Create a simple SVG icon and convert it to PNG using imagemagick (if available)
    cat > build-assets/icon.svg << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
  <rect width="256" height="256" rx="32" fill="#2563eb"/>
  <text x="128" y="140" font-family="Arial, sans-serif" font-size="180" font-weight="bold" text-anchor="middle" fill="white">⚖</text>
  <text x="128" y="220" font-family="Arial, sans-serif" font-size="24" font-weight="bold" text-anchor="middle" fill="white">Legal Cases</text>
</svg>
EOF
    
    # Try to convert SVG to PNG using imagemagick
    if command -v convert &> /dev/null; then
        convert build-assets/icon.svg build-assets/icon.png
        echo "Icon created successfully"
    else
        echo "Warning: ImageMagick not found. Using default Electron icon."
    fi
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Build React app
echo "Building React application..."
npm run build

# Build Electron app for Linux
echo "Building Electron app for Linux..."
npm run electron-pack-linux

echo "Linux build completed!"
echo "The AppImage file should be in the dist/ folder"
