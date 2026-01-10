#!/bin/bash
# Collectivist Collection Initializer (Unix/Linux/macOS)
# Checks for Python + dependencies, installs what's needed and asks user if they want to begin analyzing

set -e

echo "🌸 Collectivist Collection Initializer"
echo "======================================"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    echo "   Please install Python 3.8+ and try again"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Found Python $PYTHON_VERSION"

# Check if pip is available
if ! python3 -m pip --version &> /dev/null; then
    echo "❌ pip is required but not found"
    echo "   Please install pip and try again"
    exit 1
fi

echo "✅ Found pip"

# Check for required packages
echo
echo "📦 Checking dependencies..."

MISSING_PACKAGES=()

# Check each required package
for package in "requests" "pyyaml" "pathlib"; do
    if ! python3 -c "import $package" 2>/dev/null; then
        MISSING_PACKAGES+=("$package")
    fi
done

# Install missing packages if any
if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo "📥 Installing missing packages: ${MISSING_PACKAGES[*]}"
    python3 -m pip install "${MISSING_PACKAGES[@]}"
    echo "✅ Dependencies installed"
else
    echo "✅ All dependencies satisfied"
fi

echo
echo "🎯 Collection initialized successfully!"
echo

# Ask if user wants to start analysis
read -p "Would you like to analyze this collection now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔍 Starting collection analysis..."
    python3 src/__main__.py analyze
else
    echo
    echo "💡 To analyze later, run:"
    echo "   python3 .collection/src/__main__.py analyze"
    echo
    echo "📚 For help, run:"
    echo "   python3 .collection/src/__main__.py --help"
fi