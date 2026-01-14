#!/usr/bin/env bash
# FREQ-AI-VERTEX (SOL) Installation Script
# Sophisticated Operational Lattice - Multi-node AI orchestration system
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/dre-orchestrator-ai/FREQ-AI-VERTEX/main/install.sh | bash
#   Or with options:
#   curl -fsSL https://raw.githubusercontent.com/dre-orchestrator-ai/FREQ-AI-VERTEX/main/install.sh | bash -s -- --gcp --venv

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/dre-orchestrator-ai/FREQ-AI-VERTEX.git"
INSTALL_DIR="${HOME}/.freq-ai-vertex"
MIN_PYTHON_VERSION="3.9"

# Parse command line arguments
INSTALL_GCP=false
INSTALL_DEV=false
USE_VENV=false
SKIP_CLONE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --gcp)
            INSTALL_GCP=true
            shift
            ;;
        --dev)
            INSTALL_DEV=true
            shift
            ;;
        --venv)
            USE_VENV=true
            shift
            ;;
        --skip-clone)
            SKIP_CLONE=true
            shift
            ;;
        --help)
            cat << EOF
FREQ-AI-VERTEX (SOL) Installation Script

Usage:
  install.sh [OPTIONS]

Options:
  --gcp         Install with Google Cloud Platform dependencies
  --dev         Install development dependencies
  --venv        Create and use a virtual environment
  --skip-clone  Skip repository cloning (use if already cloned)
  --help        Show this help message

Examples:
  # Basic installation
  curl -fsSL https://raw.githubusercontent.com/dre-orchestrator-ai/FREQ-AI-VERTEX/main/install.sh | bash

  # Install with GCP support in a virtual environment
  curl -fsSL https://raw.githubusercontent.com/dre-orchestrator-ai/FREQ-AI-VERTEX/main/install.sh | bash -s -- --gcp --venv

  # Install development environment
  curl -fsSL https://raw.githubusercontent.com/dre-orchestrator-ai/FREQ-AI-VERTEX/main/install.sh | bash -s -- --dev --venv

EOF
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Helper functions
print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}  ${GREEN}FREQ-AI-VERTEX (SOL) Installation${NC}                         ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  Sophisticated Operational Lattice                         ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${BLUE}==>${NC} ${1}"
}

print_success() {
    echo -e "${GREEN}✓${NC} ${1}"
}

print_error() {
    echo -e "${RED}✗${NC} ${1}"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} ${1}"
}

check_python() {
    print_step "Checking Python installation..."

    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        echo "Please install Python ${MIN_PYTHON_VERSION} or higher"
        echo "Visit: https://www.python.org/downloads/"
        exit 1
    fi

    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_success "Found Python ${PYTHON_VERSION}"

    # Check if version meets minimum requirement
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
        print_error "Python ${PYTHON_VERSION} is too old"
        echo "Minimum required version: ${MIN_PYTHON_VERSION}"
        exit 1
    fi
}

check_pip() {
    print_step "Checking pip installation..."

    if ! python3 -m pip --version &> /dev/null; then
        print_error "pip is not installed"
        echo "Installing pip..."
        python3 -m ensurepip --upgrade || {
            print_error "Failed to install pip"
            echo "Please install pip manually: https://pip.pypa.io/en/stable/installation/"
            exit 1
        }
    fi

    print_success "pip is available"
}

check_git() {
    print_step "Checking git installation..."

    if ! command -v git &> /dev/null; then
        print_error "git is not installed"
        echo "Please install git: https://git-scm.com/downloads"
        exit 1
    fi

    print_success "git is available"
}

setup_venv() {
    if [ "$USE_VENV" = true ]; then
        print_step "Creating virtual environment..."

        if [ ! -d "${INSTALL_DIR}/venv" ]; then
            python3 -m venv "${INSTALL_DIR}/venv" || {
                print_error "Failed to create virtual environment"
                exit 1
            }
            print_success "Virtual environment created"
        else
            print_warning "Virtual environment already exists"
        fi

        # Activate virtual environment
        source "${INSTALL_DIR}/venv/bin/activate"
        print_success "Virtual environment activated"
    fi
}

clone_repository() {
    if [ "$SKIP_CLONE" = true ]; then
        print_step "Skipping repository clone..."
        if [ ! -d "${INSTALL_DIR}" ]; then
            print_error "Install directory ${INSTALL_DIR} does not exist"
            echo "Remove --skip-clone flag or clone the repository manually"
            exit 1
        fi
        return
    fi

    print_step "Cloning repository..."

    if [ -d "${INSTALL_DIR}" ]; then
        print_warning "Directory ${INSTALL_DIR} already exists"
        read -p "Do you want to remove it and clone fresh? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "${INSTALL_DIR}"
        else
            print_step "Updating existing repository..."
            cd "${INSTALL_DIR}"
            git pull origin main || {
                print_warning "Failed to update repository, continuing with existing version"
            }
            return
        fi
    fi

    git clone "${REPO_URL}" "${INSTALL_DIR}" || {
        print_error "Failed to clone repository"
        exit 1
    }

    print_success "Repository cloned to ${INSTALL_DIR}"
}

install_package() {
    print_step "Installing FREQ-AI-VERTEX..."

    cd "${INSTALL_DIR}"

    # Build install command based on options
    INSTALL_CMD="python3 -m pip install -e ."

    if [ "$INSTALL_GCP" = true ] && [ "$INSTALL_DEV" = true ]; then
        INSTALL_CMD="python3 -m pip install -e .[gcp,dev]"
        print_step "Installing with GCP and development dependencies..."
    elif [ "$INSTALL_GCP" = true ]; then
        INSTALL_CMD="python3 -m pip install -e .[gcp]"
        print_step "Installing with GCP dependencies..."
    elif [ "$INSTALL_DEV" = true ]; then
        INSTALL_CMD="python3 -m pip install -e .[dev]"
        print_step "Installing with development dependencies..."
    else
        print_step "Installing base package..."
    fi

    $INSTALL_CMD || {
        print_error "Failed to install package"
        exit 1
    }

    print_success "Package installed successfully"
}

verify_installation() {
    print_step "Verifying installation..."

    python3 -c "import sol; from sol.nodes import StrategicOP" &> /dev/null || {
        print_error "Installation verification failed"
        echo "Package was installed but imports are failing"
        exit 1
    }

    print_success "Installation verified"
}

print_next_steps() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}  Installation Complete!                                     ${GREEN}║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Installation directory: ${INSTALL_DIR}"

    if [ "$USE_VENV" = true ]; then
        echo ""
        echo "To activate the virtual environment:"
        echo -e "  ${BLUE}source ${INSTALL_DIR}/venv/bin/activate${NC}"
    fi

    echo ""
    echo "Quick start:"
    echo -e "  ${BLUE}cd ${INSTALL_DIR}${NC}"
    echo -e "  ${BLUE}python3${NC}"
    echo ""
    echo "  >>> from sol.nodes import StrategicOP, GOVEngine"
    echo "  >>> from sol.governance import FreqLaw"
    echo "  >>> strategic_op = StrategicOP()"
    echo "  >>> print(f\"Node: {strategic_op.node_type.value}\")"
    echo ""
    echo "Documentation: https://github.com/dre-orchestrator-ai/FREQ-AI-VERTEX#readme"
    echo ""

    if [ "$INSTALL_GCP" = false ]; then
        print_warning "GCP dependencies not installed"
        echo "To install GCP support later:"
        echo -e "  ${BLUE}cd ${INSTALL_DIR} && pip install -e .[gcp]${NC}"
        echo ""
    fi
}

# Main installation flow
main() {
    print_header

    check_python
    check_pip
    check_git
    clone_repository
    setup_venv
    install_package
    verify_installation
    print_next_steps
}

# Run main installation
main
