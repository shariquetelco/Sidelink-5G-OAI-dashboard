#!/bin/bash
#
# OAI 5G Sidelink Dashboard - Installation Script
# Author: Ahmad Sharique (ahmad@iabg.de)
# Company: IABG mbH Munich
# Description: Automated installation for OAI Sidelink Dashboard
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
print_banner() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                                                                ║"
    echo "║       OAI 5G Sidelink Tactical Dashboard Installer            ║"
    echo "║                                                                ║"
    echo "║       IABG mbH Munich - 5G Division                            ║"
    echo "║       Author: Ahmad Sharique                                   ║"
    echo "║                                                                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Functions
print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

print_step() {
    echo -e "${CYAN}▶ $1${NC}"
}

# Check if running as root
check_root() {
    if [ "$EUID" -eq 0 ]; then 
        print_error "Please do not run as root. Run as regular user."
        exit 1
    fi
}

# Check system requirements
check_system() {
    print_header "Checking System Requirements"
    
    # Check OS
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        print_success "Operating System: $PRETTY_NAME"
    else
        print_error "Cannot determine OS version"
        exit 1
    fi
    
    # Check available disk space (need at least 5GB)
    AVAILABLE_SPACE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
    if [ "$AVAILABLE_SPACE" -lt 5 ]; then
        print_error "Insufficient disk space. Need at least 5GB, have ${AVAILABLE_SPACE}GB"
        exit 1
    fi
    print_success "Available disk space: ${AVAILABLE_SPACE}GB"
    
    # Check RAM (need at least 4GB)
    TOTAL_RAM=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$TOTAL_RAM" -lt 4 ]; then
        print_error "Insufficient RAM. Need at least 4GB, have ${TOTAL_RAM}GB"
        exit 1
    fi
    print_success "Total RAM: ${TOTAL_RAM}GB"
    
    echo ""
}

# Check dependencies
check_dependencies() {
    print_header "Checking Dependencies"
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python 3 found: $PYTHON_VERSION"
    else
        print_error "Python 3 is not installed"
        print_info "Install with: sudo apt-get install python3 python3-pip"
        exit 1
    fi
    
    # Check Docker
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | sed 's/,//')
        print_success "Docker found: $DOCKER_VERSION"
    else
        print_error "Docker is not installed"
        print_info "Install with: sudo apt-get install docker.io"
        exit 1
    fi
    
    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f4 | sed 's/,//')
        print_success "Docker Compose found: $COMPOSE_VERSION"
    else
        print_error "Docker Compose is not installed"
        print_info "Install with: sudo apt-get install docker-compose"
        exit 1
    fi
    
    # Check if user is in docker group
    if groups | grep -q docker; then
        print_success "User is in docker group"
    else
        print_error "User is not in docker group"
        print_info "Add yourself with: sudo usermod -aG docker $USER"
        print_info "Then logout and login again"
        exit 1
    fi
    
    echo ""
}

# Install Python dependencies
install_python_deps() {
    print_header "Installing Python Dependencies"
    
    if [ -f "requirements.txt" ]; then
        print_step "Installing from requirements.txt..."
        pip3 install --user -r requirements.txt --break-system-packages 2>/dev/null || \
        pip3 install --user -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
    
    echo ""
}

# Build Docker image
build_docker() {
    print_header "Building Docker Image"
    
    print_step "Building image: iabg/oai-sidelink-dashboard:latest"
    docker-compose build
    print_success "Docker image built successfully"
    
    echo ""
}

# Create necessary directories
create_directories() {
    print_header "Creating Directories"
    
    mkdir -p docs/screenshots
    print_success "Directory structure created"
    
    echo ""
}

# Display usage instructions
show_usage() {
    print_header "Installation Complete!"
    
    echo ""
    echo -e "${GREEN}✓ OAI Sidelink Dashboard is ready to use!${NC}"
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}QUICK START GUIDE${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BLUE}Step 1: Start OAI Sidelink UEs${NC}"
    echo ""
    echo -e "  ${YELLOW}Terminal 1 - SyncRef UE:${NC}"
    echo "  cd /path/to/oai-5g-sidelink/cmake_targets/ran_build/build"
    echo "  sudo LD_LIBRARY_PATH=\$PWD:\$LD_LIBRARY_PATH ./nr-uesoftmodem \\"
    echo "    -O ../../../targets/PROJECTS/NR-SIDELINK/CONF/sl_sync_ref.conf \\"
    echo "    --sa --sl-mode 2 --sync-ref --rfsim \\"
    echo "    --rfsimulator.serveraddr server \\"
    echo "    --rfsimulator.serverport 4048 \\"
    echo "    2>&1 | tee ~/syncref_sl.log"
    echo ""
    echo -e "  ${YELLOW}Terminal 2 - Nearby UE:${NC}"
    echo "  cd /path/to/oai-5g-sidelink/cmake_targets/ran_build/build"
    echo "  sudo LD_LIBRARY_PATH=\$PWD:\$LD_LIBRARY_PATH \\"
    echo "    RFSIMULATOR=127.0.0.1 ./nr-uesoftmodem \\"
    echo "    -O ../../../targets/PROJECTS/NR-SIDELINK/CONF/sl_ue1.conf \\"
    echo "    --sa --sl-mode 2 --rfsim \\"
    echo "    --rfsimulator.serverport 4048 \\"
    echo "    2>&1 | tee ~/nearby_ue_sl.log"
    echo ""
    echo -e "${BLUE}Step 2: Start Dashboard${NC}"
    echo ""
    echo -e "  ${GREEN}Option A - Docker (Recommended):${NC}"
    echo "    docker-compose up -d"
    echo ""
    echo -e "  ${GREEN}Option B - Direct Python:${NC}"
    echo "    python3 app.py"
    echo ""
    echo -e "${BLUE}Step 3: Access Dashboard${NC}"
    echo ""
    echo -e "  ${GREEN}Open browser:${NC} http://localhost:5000"
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}MANAGEMENT COMMANDS${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "  Stop dashboard:      docker-compose down"
    echo "  View logs:           docker-compose logs -f"
    echo "  Restart:             docker-compose restart"
    echo "  Rebuild:             docker-compose build"
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}TROUBLESHOOTING${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "  Check health:        curl http://localhost:5000/api/health"
    echo "  Check UE logs:       ls -lh ~/syncref_sl.log ~/nearby_ue_sl.log"
    echo "  Check containers:    docker ps"
    echo ""
    echo -e "${GREEN}For support: ahmad@iabg.de${NC}"
    echo ""
}

# Main installation flow
main() {
    print_banner
    
    check_root
    check_system
    check_dependencies
    create_directories
    install_python_deps
    build_docker
    
    show_usage
}

# Run main function
main
