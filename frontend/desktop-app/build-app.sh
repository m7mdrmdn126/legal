#!/bin/bash

# Legal Cases Desktop App - Universal Build Script
# This script can build for Linux, Windows, or both

show_help() {
    echo "Legal Cases Desktop App Build Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -l, --linux     Build for Linux (AppImage)"
    echo "  -w, --windows   Build for Windows (NSIS installer)"
    echo "  -a, --all       Build for all platforms"
    echo "  -c, --clean     Clean build directories first"
    echo "  -h, --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --linux               # Build Linux AppImage"
    echo "  $0 --windows             # Build Windows installer"
    echo "  $0 --all                 # Build for both platforms"
    echo "  $0 --clean --linux       # Clean and build for Linux"
}

# Initialize variables
BUILD_LINUX=false
BUILD_WINDOWS=false
CLEAN_BUILD=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -l|--linux)
            BUILD_LINUX=true
            shift
            ;;
        -w|--windows)
            BUILD_WINDOWS=true
            shift
            ;;
        -a|--all)
            BUILD_LINUX=true
            BUILD_WINDOWS=true
            shift
            ;;
        -c|--clean)
            CLEAN_BUILD=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# If no platform specified, show help
if [[ "$BUILD_LINUX" == false && "$BUILD_WINDOWS" == false ]]; then
    echo "Error: Please specify a build target"
    show_help
    exit 1
fi

echo "========================================"
echo "  Legal Cases Desktop App Builder"
echo "========================================"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed"
    echo "Please install npm with Node.js"
    exit 1
fi

echo "✅ Node.js $(node --version)"
echo "✅ npm $(npm --version)"
echo ""

# Clean build if requested
if [[ "$CLEAN_BUILD" == true ]]; then
    echo "🧹 Cleaning build directories..."
    rm -rf build/ dist/ node_modules/.cache/
    echo "✅ Build directories cleaned"
    echo ""
fi

# Create icon if it doesn't exist
echo "🎨 Checking application icon..."
if [[ ! -f "build-assets/icon.png" ]]; then
    echo "Creating application icon from SVG..."
    
    if command -v convert &> /dev/null; then
        # Use ImageMagick to convert SVG to PNG
        convert build-assets/icon.svg -resize 256x256 build-assets/icon.png
        echo "✅ PNG icon created"
    elif command -v inkscape &> /dev/null; then
        # Use Inkscape to convert SVG to PNG
        inkscape --export-filename=build-assets/icon.png --export-width=256 --export-height=256 build-assets/icon.svg
        echo "✅ PNG icon created with Inkscape"
    else
        echo "⚠️  Warning: No SVG converter found (ImageMagick or Inkscape)"
        echo "   Using default Electron icon for now"
    fi
fi

# Create ICO file for Windows if building for Windows
if [[ "$BUILD_WINDOWS" == true && ! -f "build-assets/icon.ico" ]]; then
    echo "Creating Windows ICO icon..."
    if command -v convert &> /dev/null; then
        convert build-assets/icon.png -resize 256x256 build-assets/icon.ico
        echo "✅ ICO icon created"
    else
        echo "⚠️  Warning: Cannot create ICO file without ImageMagick"
    fi
fi

echo ""

# Install dependencies
echo "📦 Installing dependencies..."
if [[ ! -d "node_modules" ]] || [[ "$CLEAN_BUILD" == true ]]; then
    npm install
    if [[ $? -ne 0 ]]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi
echo ""

# Build React application
echo "⚛️  Building React application..."
npm run build
if [[ $? -ne 0 ]]; then
    echo "❌ React build failed"
    exit 1
fi
echo "✅ React application built successfully"
echo ""

# Build for specified platforms
if [[ "$BUILD_LINUX" == true ]]; then
    echo "🐧 Building Linux AppImage..."
    npm run electron-pack-linux
    if [[ $? -eq 0 ]]; then
        echo "✅ Linux build completed successfully!"
        
        # Find and display the created file
        LINUX_FILE=$(find dist/ -name "*.AppImage" 2>/dev/null | head -1)
        if [[ -n "$LINUX_FILE" ]]; then
            echo "📱 Linux AppImage: $LINUX_FILE"
            echo "   Size: $(du -h "$LINUX_FILE" | cut -f1)"
        fi
    else
        echo "❌ Linux build failed"
    fi
    echo ""
fi

if [[ "$BUILD_WINDOWS" == true ]]; then
    echo "🪟 Building Windows installer..."
    npm run electron-pack-win
    if [[ $? -eq 0 ]]; then
        echo "✅ Windows build completed successfully!"
        
        # Find and display the created file
        WINDOWS_FILE=$(find dist/ -name "*.exe" 2>/dev/null | head -1)
        if [[ -n "$WINDOWS_FILE" ]]; then
            echo "💾 Windows installer: $WINDOWS_FILE"
            echo "   Size: $(du -h "$WINDOWS_FILE" | cut -f1)"
        fi
    else
        echo "❌ Windows build failed"
    fi
    echo ""
fi

echo "========================================"
echo "🎉 Build process completed!"
echo ""
echo "📁 Output directory: ./dist/"
if [[ -d "dist" ]]; then
    echo "📋 Built files:"
    ls -la dist/ | grep -E '\.(AppImage|exe)$' || echo "   No executable files found"
fi
echo ""
echo "🚀 You can now distribute the application files!"
echo "========================================"
