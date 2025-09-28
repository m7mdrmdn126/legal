# Windows Setup Guide - Legal Cases Desktop App

## Quick Start for Windows Users

### Prerequisites
1. **Node.js** (v16 or higher) - Download from [nodejs.org](https://nodejs.org/)
2. **Git** (optional) - Download from [git-scm.com](https://git-scm.com/)

### Installation Methods

#### Method 1: Using PowerShell Script (Recommended)
1. Open PowerShell as Administrator
2. Navigate to the project folder:
   ```powershell
   cd "path\to\legal_cases\app-v2\frontend\desktop-app"
   ```
3. Allow script execution (first time only):
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
4. Run the setup script:
   ```powershell
   .\start-windows.ps1
   ```

#### Method 2: Using Batch File
1. Open Command Prompt
2. Navigate to the project folder
3. Run:
   ```cmd
   start-windows.bat
   ```

#### Method 3: Manual npm Commands
```cmd
# Install cross-platform dependency first
npm install cross-env --save-dev

# For development
npm run electron-dev

# For building Windows installer
npm run build-windows
```

### Windows-Specific Commands

The package.json now includes Windows-optimized commands:

- `npm run start:win` - Start React app (Windows env vars)
- `npm run build:win` - Build for production (Windows env vars)
- `npm run electron-dev:win` - Development with Electron (Windows)

### Troubleshooting

#### Common Issues on Windows:

1. **"'GENERATE_SOURCEMAP' is not recognized"**
   - Solution: Use `cross-env` or Windows-specific commands (`npm run start:win`)

2. **"NODE_NO_WARNINGS is not recognized"**
   - Solution: Install cross-env: `npm install cross-env --save-dev`

3. **PowerShell execution policy error**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **Port 3000 already in use**
   - Kill the process: `netstat -ano | findstr :3000`
   - Then: `taskkill /PID <PID> /F`

5. **Build fails with memory error**
   - Set environment variable: `set NODE_OPTIONS=--max-old-space-size=4096`

#### Performance Tips for Windows:

1. **Disable Windows Defender real-time scanning** for the project folder (temporarily)
2. **Use SSD storage** for better performance
3. **Close unnecessary applications** during build
4. **Use Windows Terminal** instead of Command Prompt for better performance

### Environment Variables for Windows

For manual setup, set these in Command Prompt:
```cmd
set GENERATE_SOURCEMAP=false
set NODE_NO_WARNINGS=1
set NODE_OPTIONS=--max-old-space-size=4096
```

Or in PowerShell:
```powershell
$env:GENERATE_SOURCEMAP="false"
$env:NODE_NO_WARNINGS="1"
$env:NODE_OPTIONS="--max-old-space-size=4096"
```

### Build Output

After successful build:
- **Development**: App opens automatically in Electron window
- **Production**: Installer created in `dist/` folder
- **File name**: `Legal-Cases-Management-{version}-Windows-Setup.exe`

### File Permissions

If you encounter permission issues:
1. Run Command Prompt as Administrator
2. Or change folder permissions to allow full control for your user

### Antivirus Considerations

Some antivirus software may flag the Electron app:
1. Add the project folder to antivirus exceptions
2. Add the built executable to trusted applications
3. This is normal for Electron apps and safe if you built it yourself

## Quick Commands Reference

```cmd
# Install dependencies
npm install

# Development (cross-platform)
npm run electron-dev

# Development (Windows-specific)
npm run electron-dev:win

# Build (cross-platform)
npm run build-windows

# Build (Windows-specific)
npm run build:win
```

## Support

If you encounter issues:
1. Check Node.js version: `node --version`
2. Clear npm cache: `npm cache clean --force`
3. Delete node_modules and reinstall: `rmdir /s node_modules && npm install`
4. Check Windows Event Viewer for system-level errors
