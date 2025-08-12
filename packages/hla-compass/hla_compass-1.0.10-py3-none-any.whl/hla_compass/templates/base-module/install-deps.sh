#!/bin/bash
# Installation helper for HLA-Compass module dependencies
# Handles Python 3.13 and platform-specific issues

set -e

echo "==========================================="
echo "HLA-Compass Module Dependency Installer"
echo "==========================================="

# Detect Python version
PYTHON_VERSION=$(python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo "Detected Python $PYTHON_VERSION"

# Detect platform
OS=$(uname -s)
ARCH=$(uname -m)

echo "Platform: $OS $ARCH"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Python 3.13 on macOS ARM64
if [[ "$PYTHON_MAJOR" == "3" && "$PYTHON_MINOR" == "13" && "$OS" == "Darwin" && "$ARCH" == "arm64" ]]; then
    echo ""
    echo "⚠️  Python 3.13 on Apple Silicon detected"
    echo "   Using optimized dependencies..."
    
    # Create temporary requirements file with updated versions
    cat > /tmp/requirements_py313.txt << EOF
# Optimized for Python 3.13
numpy>=1.26.0
pandas>=2.2.3
EOF
    
    # Try pip installation first
    echo ""
    echo "Installing with pip..."
    if pip install -r /tmp/requirements_py313.txt; then
        echo "✅ Dependencies installed successfully with pip"
    else
        echo "❌ pip installation failed"
        
        # Suggest conda as alternative
        if command_exists conda; then
            echo ""
            echo "Trying conda installation..."
            conda install -y numpy pandas
            echo "✅ Dependencies installed successfully with conda"
        else
            echo ""
            echo "💡 Alternative solutions:"
            echo "   1. Install Miniconda: https://docs.conda.io/en/latest/miniconda.html"
            echo "   2. Use x86 emulation: arch -x86_64 pip install -r backend/requirements.txt"
            echo "   3. Use lighter alternative: pip install polars"
            exit 1
        fi
    fi
    
    # Clean up
    rm -f /tmp/requirements_py313.txt
else
    # Standard installation for other Python versions
    echo ""
    echo "Installing standard dependencies..."
    
    if pip install -r backend/requirements.txt; then
        echo "✅ Dependencies installed successfully"
    else
        echo "❌ Installation failed"
        echo ""
        echo "💡 Troubleshooting tips:"
        echo "   1. Upgrade pip: python -m pip install --upgrade pip"
        echo "   2. Install wheel: pip install wheel"
        echo "   3. Use virtual environment: python -m venv venv && source venv/bin/activate"
        echo "   4. Check compiler tools: xcode-select --install (macOS)"
        exit 1
    fi
fi

# Install additional dependencies for UI modules if frontend exists
if [ -d "frontend" ]; then
    echo ""
    echo "Installing frontend dependencies..."
    cd frontend
    
    if npm install; then
        echo "✅ Frontend dependencies installed successfully"
    else
        echo "⚠️  Frontend installation had issues (non-critical)"
    fi
    
    cd ..
fi

echo ""
echo "==========================================="
echo "✅ Installation complete!"
echo "==========================================="
echo ""
echo "Next steps:"
echo "  1. Test your module: hla-compass test --local"
echo "  2. Build package: hla-compass build"
echo ""