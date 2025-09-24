# Legal Cases Management System

A comprehensive legal cases management system built with FastAPI (backend) and Electron (desktop frontend) designed for network deployment.

## 🏗️ Architecture

- **Backend**: FastAPI with SQLite database
- **Frontend**: Electron desktop application  
- **Deployment**: Network-based with single server, multiple clients
- **Platform**: Windows, Linux, macOS support

## 🚀 Features

### Core Functionality
- ⚖️ **Case Management**: Complete case lifecycle management
- 👥 **User Management**: Multi-user support with role-based access
- 📝 **Case Notes & Sessions**: Detailed case documentation
- 📊 **Statistics & Reports**: Comprehensive reporting system
- 🔒 **Authentication**: Secure login and session management

### Advanced Features
- 🔄 **Backup & Restore**: Automated database backup system
- 📤 **Export**: Multiple export formats (PDF, Excel, etc.)
- 🖨️ **Print**: Professional document printing
- ⚡ **Performance**: Optimized for large datasets
- 🌐 **Network Ready**: Multi-client network deployment

## 📦 Quick Start

### Server Setup (Windows)
```cmd
cd deployment
setup-server.bat          # Run as Administrator (first time)
start-server.bat          # Start the server
```

### Build Desktop Application
```cmd
cd deployment
build-desktop-app.bat     # Creates installer
```

### Client Installation
1. Install `Legal Cases Management Setup.exe` on each device
2. Edit `.env` file with server IP: `SERVER_IP=192.168.1.100`
3. Launch application from desktop icon

## 📁 Project Structure

```
legal-cases-app/
├── backend/              # FastAPI server
│   ├── main.py          # Application entry point
│   ├── config/          # Configuration management
│   ├── models/          # Database models
│   ├── routes/          # API endpoints
│   └── utils/           # Utility functions
├── frontend/            
│   └── desktop-app/     # Electron application
├── database/            # SQLite database files
├── deployment/          # Setup and build scripts
└── docs/               # Documentation
```

## 🔧 Development

### Prerequisites
- **Server**: Python 3.9+
- **Desktop App Build**: Node.js 16+
- **Clients**: No additional software needed

### Development Setup
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
python main.py

# Frontend (Development)
cd frontend/desktop-app
npm install
npm run electron-dev
```

## 🌐 Network Deployment

### Server Device
- Install Python 3.9+
- Set static IP address (recommended)
- Run server setup scripts
- Configure firewall (automatic)

### Client Devices  
- Install desktop application
- Configure server IP in `.env` file
- No development tools required

## 📋 Configuration

### Server Configuration (`.env.production.windows`)
```bash
HOST=0.0.0.0
PORT=8000
DATABASE_PATH=C:\legal-cases\database\legal_cases.db
SECRET_KEY=your-production-secret-key
```

### Client Configuration (`.env`)
```bash
SERVER_IP=192.168.1.100
SERVER_PORT=8000
APP_NAME=Legal Cases Management
AUTO_CONNECT=true
```

## 🔒 Security

- JWT-based authentication
- Role-based access control
- CORS protection
- Secure session management
- Automatic logout on inactivity

## 📚 Documentation

- [Windows Deployment Guide](deployment/WINDOWS_DEPLOYMENT_GUIDE.md)
- [Desktop App Guide](deployment/DESKTOP_APP_GUIDE.md)
- [Development Setup](DEVELOPMENT_FIXES.md)
- [API Documentation](backend/README.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the documentation in the `deployment/` folder
- Review troubleshooting guides
- Create an issue for bugs or feature requests

## 🔄 Version History

- **v1.0.0** - Initial release with full network deployment support
- Complete legal case management functionality
- Professional desktop application with installer
- Windows Service support for server
- Multi-platform client support
