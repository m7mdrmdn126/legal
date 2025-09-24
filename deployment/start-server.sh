#!/bin/bash
# Legal Cases Management System - Production Server Startup Script

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
DATABASE_DIR="$PROJECT_ROOT/database"
LOG_DIR="/opt/legal-cases/logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    sudo mkdir -p /opt/legal-cases/{database,logs,backups}
    sudo chown -R $USER:$USER /opt/legal-cases
    
    # Ensure local directories exist
    mkdir -p "$DATABASE_DIR"
    mkdir -p "$LOG_DIR"
}

# Check dependencies
check_dependencies() {
    log "Checking dependencies..."
    
    if ! command -v python3 &> /dev/null; then
        error "Python3 is not installed"
        exit 1
    fi
    
    if ! command -v pip3 &> /dev/null; then
        error "Pip3 is not installed"
        exit 1
    fi
    
    log "Dependencies check passed"
}

# Install Python packages
install_packages() {
    log "Installing Python packages..."
    
    cd "$BACKEND_DIR"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log "Created virtual environment"
    fi
    
    # Activate virtual environment and install packages
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    log "Python packages installed"
}

# Setup database
setup_database() {
    log "Setting up database..."
    
    cd "$BACKEND_DIR"
    source venv/bin/activate
    
    # Copy database to production location if needed
    PROD_DB="/opt/legal-cases/database/legal_cases.db"
    SOURCE_DB="$DATABASE_DIR/legal_cases.db"
    
    if [ -f "$SOURCE_DB" ] && [ ! -f "$PROD_DB" ]; then
        cp "$SOURCE_DB" "$PROD_DB"
        log "Database copied to production location"
    elif [ ! -f "$PROD_DB" ]; then
        # Create initial database
        python -c "
import sys
sys.path.insert(0, '.')
from config.database import init_db, get_db
init_db()
"
        log "Initial database created"
    fi
    
    log "Database setup complete"
}

# Get network configuration
get_network_info() {
    log "Network configuration:"
    
    # Get primary network interface
    INTERFACE=$(ip route | grep default | awk '{print $5}' | head -n1)
    SERVER_IP=$(ip addr show "$INTERFACE" | grep "inet " | awk '{print $2}' | cut -d/ -f1 | head -n1)
    
    echo "  Interface: $INTERFACE"
    echo "  Server IP: $SERVER_IP"
    echo "  Server will be accessible at: http://$SERVER_IP:8000"
    echo ""
    
    # Save server IP to file for client configuration
    echo "$SERVER_IP" > /opt/legal-cases/server-ip.txt
    log "Server IP saved to /opt/legal-cases/server-ip.txt"
}

# Start the server
start_server() {
    log "Starting Legal Cases Management Server..."
    
    cd "$BACKEND_DIR"
    source venv/bin/activate
    
    # Load production environment
    if [ -f "$PROJECT_ROOT/deployment/.env.production" ]; then
        export $(cat "$PROJECT_ROOT/deployment/.env.production" | grep -v '^#' | xargs)
        log "Loaded production environment variables"
    fi
    
    # Start server with uvicorn
    log "Server starting on $HOST:$PORT..."
    log "Press Ctrl+C to stop the server"
    
    uvicorn main:app \
        --host "${HOST:-0.0.0.0}" \
        --port "${PORT:-8000}" \
        --reload \
        --log-level info \
        --access-log \
        --log-config /dev/null
}

# Main execution
main() {
    log "Legal Cases Management System - Server Setup"
    log "============================================="
    
    create_directories
    check_dependencies
    install_packages
    setup_database
    get_network_info
    
    log "Server setup complete!"
    log "============================================="
    
    start_server
}

# Handle script interruption
trap 'log "Server stopped by user"; exit 0' INT TERM

# Run main function
main "$@"
