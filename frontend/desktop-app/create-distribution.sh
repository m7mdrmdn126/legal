#!/bin/bash

# Legal Cases Desktop App Distribution Package Creator
# This script creates a distribution package with both Linux and Windows apps

VERSION="1.0.0"
PACKAGE_NAME="Legal-Cases-Management-v${VERSION}"
DIST_DIR="distribution"

echo "========================================"
echo "  Legal Cases Distribution Packager"
echo "========================================"
echo ""

# Check if dist directory exists
if [ ! -d "dist" ]; then
    echo "❌ Error: dist directory not found"
    echo "Please build the applications first using:"
    echo "  ./build-app.sh --all"
    exit 1
fi

# Create distribution directory
echo "📁 Creating distribution package..."
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

# Copy applications
echo "📱 Copying Linux AppImage..."
if [ -f "dist/Legal-Cases-Management-${VERSION}-Linux.AppImage" ]; then
    cp "dist/Legal-Cases-Management-${VERSION}-Linux.AppImage" "$DIST_DIR/"
    echo "✅ Linux AppImage copied"
else
    echo "⚠️  Linux AppImage not found"
fi

echo "💾 Copying Windows installer..."
if [ -f "dist/Legal-Cases-Management-${VERSION}-Windows-Setup.exe" ]; then
    cp "dist/Legal-Cases-Management-${VERSION}-Windows-Setup.exe" "$DIST_DIR/"
    echo "✅ Windows installer copied"
else
    echo "⚠️  Windows installer not found"
fi

# Copy documentation
echo "📄 Copying documentation..."
cp BUILD_GUIDE.md "$DIST_DIR/" 2>/dev/null || echo "⚠️  BUILD_GUIDE.md not found"
cp BUILD_REPORT.md "$DIST_DIR/" 2>/dev/null || echo "⚠️  BUILD_REPORT.md not found"
cp README.md "$DIST_DIR/" 2>/dev/null || echo "⚠️  README.md not found"

# Copy .env file template
echo "⚙️  Creating configuration template..."
cat > "$DIST_DIR/.env.template" << 'EOF'
# Legal Cases Desktop App Configuration Template
# Copy this file to .env and modify the values as needed

# Backend API URL (change this to match your server)
REACT_APP_API_URL=http://localhost:8000

# Debug mode (set to true for development)
DEBUG=false

# Application title (optional customization)
# REACT_APP_TITLE="نظام إدارة القضايا القانونية"
EOF

# Generate checksums
echo "🔐 Generating checksums..."
cd "$DIST_DIR"

if command -v md5sum &> /dev/null; then
    md5sum *.AppImage *.exe > checksums.md5 2>/dev/null || true
fi

if command -v sha256sum &> /dev/null; then
    sha256sum *.AppImage *.exe > checksums.sha256 2>/dev/null || true
fi

# Create installation instructions
cat > "INSTALLATION.md" << 'EOF'
# Installation Instructions / تعليمات التثبيت
## Legal Cases Management System Desktop App

### System Requirements / متطلبات النظام:
- **Linux**: Ubuntu 16.04+ or equivalent
- **Windows**: Windows 7 SP1+ (64-bit)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB free space

### Linux Installation (AppImage):
1. Open terminal in this folder
2. Make the file executable:
   ```bash
   chmod +x Legal-Cases-Management-*-Linux.AppImage
   ```
3. Run the application:
   ```bash
   ./Legal-Cases-Management-*-Linux.AppImage
   ```

### Windows Installation:
1. Right-click on `Legal-Cases-Management-*-Windows-Setup.exe`
2. Select "Run as administrator"
3. Follow the installation wizard
4. Launch from Start Menu or Desktop shortcut

### Backend Setup:
1. Make sure the backend server is running
2. Copy `.env.template` to `.env`
3. Update the `REACT_APP_API_URL` if needed
4. Restart the desktop app if configuration was changed

### Verification:
Check file integrity using provided checksums:
- `checksums.md5` - MD5 hashes
- `checksums.sha256` - SHA256 hashes

### Support:
- Check BUILD_GUIDE.md for detailed instructions
- See BUILD_REPORT.md for technical details
EOF

cd ..

# Create archive
echo "📦 Creating distribution archive..."
if command -v tar &> /dev/null; then
    tar -czf "${PACKAGE_NAME}.tar.gz" "$DIST_DIR"
    echo "✅ Created ${PACKAGE_NAME}.tar.gz"
fi

if command -v zip &> /dev/null; then
    zip -r "${PACKAGE_NAME}.zip" "$DIST_DIR"
    echo "✅ Created ${PACKAGE_NAME}.zip"
fi

# Show summary
echo ""
echo "========================================"
echo "📋 Distribution Package Summary"
echo "========================================"
echo ""
echo "📁 Distribution folder: $DIST_DIR/"
ls -la "$DIST_DIR/" | grep -v "^total"
echo ""

if [ -f "${PACKAGE_NAME}.tar.gz" ] || [ -f "${PACKAGE_NAME}.zip" ]; then
    echo "📦 Archive files:"
    ls -lah *.tar.gz *.zip 2>/dev/null || true
    echo ""
fi

echo "🎉 Distribution package created successfully!"
echo ""
echo "Next steps:"
echo "1. Test the applications on target systems"
echo "2. Upload to distribution platform"
echo "3. Share installation instructions"
echo "4. Provide checksums for verification"
echo ""
echo "========================================"
