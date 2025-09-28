# Legal Cases Desktop App Build Guide

## نظام إدارة القضايا القانونية - دليل إنشاء التطبيق المكتبي

This guide will help you build desktop applications for Linux and Windows from the Legal Cases Management System.

## Prerequisites / المتطلبات المسبقة

### Required Software:
1. **Node.js** (v16 or higher) - https://nodejs.org/
2. **npm** (comes with Node.js)
3. **Git** (for version control)

### Optional (for icon generation):
- **ImageMagick** (recommended for icon conversion)
- **Inkscape** (alternative for SVG to PNG conversion)

### Installing ImageMagick:

#### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install imagemagick
```

#### On Windows:
Download from: https://imagemagick.org/script/download.php#windows

#### On macOS:
```bash
brew install imagemagick
```

## Quick Start / البدء السريع

### 1. Navigate to the desktop app directory:
```bash
cd frontend/desktop-app
```

### 2. Use the universal build script:

#### Build for Linux:
```bash
./build-app.sh --linux
```

#### Build for Windows:
```bash
./build-app.sh --windows
```

#### Build for both platforms:
```bash
./build-app.sh --all
```

#### Clean build (removes cache and rebuilds everything):
```bash
./build-app.sh --clean --all
```

## Manual Build Process / عملية البناء اليدوية

If you prefer to build manually or need more control:

### Step 1: Install Dependencies
```bash
cd frontend/desktop-app
npm install
```

### Step 2: Build React Application
```bash
npm run build
```

### Step 3: Build Desktop Applications

#### For Linux (AppImage):
```bash
npm run electron-pack-linux
```

#### For Windows (NSIS Installer):
```bash
npm run electron-pack-win
```

## Platform-Specific Scripts / سكريبت خاص بكل منصة

### Linux Build Script:
```bash
./build-linux.sh
```

### Windows Build Script (run in Windows):
```batch
build-windows.bat
```

## Output Files / ملفات الإخراج

After successful build, you'll find the applications in the `dist/` folder:

- **Linux**: `Legal-Cases-Management-1.0.0-Linux.AppImage`
- **Windows**: `Legal-Cases-Management-1.0.0-Windows-Setup.exe`

## File Sizes / أحجام الملفات

Typical file sizes:
- Linux AppImage: ~150-200 MB
- Windows Installer: ~100-150 MB

## Installation Instructions / تعليمات التثبيت

### Linux AppImage:
1. Make the file executable: `chmod +x Legal-Cases-Management-*.AppImage`
2. Run it: `./Legal-Cases-Management-*.AppImage`
3. Or double-click in file manager

### Windows Installer:
1. Run the `.exe` file as Administrator
2. Follow the installation wizard
3. The app will be available in Start Menu and Desktop (if selected)

## Configuration / التكوين

### Environment Variables:
The app reads configuration from a `.env` file in the desktop-app directory.

### Backend URL Configuration:
Edit the `.env` file to set the backend server URL:
```
REACT_APP_API_URL=http://localhost:8000
```

## Troubleshooting / استكشاف الأخطاء وإصلاحها

### Common Issues:

#### 1. Build fails with "electron-builder not found":
```bash
npm install electron-builder --save-dev
```

#### 2. Icon not found errors:
- Make sure SVG icon exists in `build-assets/icon.svg`
- Install ImageMagick for automatic icon conversion
- Or manually create PNG/ICO icons in `build-assets/`

#### 3. React build fails:
```bash
npm run build
```
Check for any TypeScript or React errors in the output.

#### 4. Permission denied (Linux):
```bash
chmod +x ./build-app.sh
chmod +x ./build-linux.sh
```

#### 5. Windows build on Linux:
Windows builds can be created on Linux, but you may need wine for testing:
```bash
sudo apt install wine
```

## Advanced Configuration / التكوين المتقدم

### Custom Build Options:

#### Build for specific architecture:
```bash
# 64-bit only
npm run build && npx electron-builder --linux --x64

# 32-bit (if needed)
npm run build && npx electron-builder --linux --ia32
```

#### Custom output directory:
```bash
npm run build && npx electron-builder --linux --dir
```

### Signing Applications (Production):

#### Windows Code Signing:
Add to package.json build configuration:
```json
"win": {
  "certificateFile": "certificate.p12",
  "certificatePassword": "password"
}
```

#### macOS Code Signing:
```json
"mac": {
  "identity": "Developer ID Application: Your Name"
}
```

## Testing the Applications / اختبار التطبيقات

### Before Distribution:

1. **Test on target platforms**
2. **Verify all features work offline**
3. **Check Arabic text rendering**
4. **Test with different screen resolutions**
5. **Verify auto-updater (if implemented)**

### Test Commands:
```bash
# Test Linux AppImage
./dist/Legal-Cases-Management-*.AppImage

# Test Windows (using wine on Linux)
wine ./dist/Legal-Cases-Management-*-Setup.exe
```

## Distribution / التوزيع

### File Sharing:
- Upload to file sharing service
- Create checksums for verification
- Provide installation instructions

### Auto-Updates:
For production deployment, consider implementing auto-updates using electron-updater.

## Support / الدعم

### System Requirements:
- **Linux**: Ubuntu 16.04+, CentOS 7+, or equivalent
- **Windows**: Windows 7 SP1+ (64-bit)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB free space

### Browser Compatibility:
The app uses Electron with Chromium engine, ensuring consistent behavior across platforms.

---

## Notes / ملاحظات

- The desktop app includes the same features as the web version
- All Arabic text and RTL layout are preserved
- The app can work offline after initial setup
- Backend server must be running for full functionality

For additional help, check the project documentation or contact the development team.
