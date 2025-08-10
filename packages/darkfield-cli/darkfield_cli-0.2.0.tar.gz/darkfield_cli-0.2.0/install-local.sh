#!/bin/bash

# darkfield CLI Local Installation Script

echo "🚀 Installing darkfield CLI locally..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "❌ Please run this script from the cli directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install in development mode
echo "📦 Installing darkfield CLI in development mode..."
pip install -e .

# Create symlink for global access
echo "🔗 Creating global command..."
sudo ln -sf $(pwd)/venv/bin/darkfield /usr/local/bin/darkfield 2>/dev/null || {
    echo "⚠️  Could not create global symlink. You can run the CLI with:"
    echo "   $(pwd)/venv/bin/darkfield"
}

echo "✅ Installation complete!"
echo ""
echo "Try running: darkfield --help"
echo ""
echo "Note: This is a development installation. The backend services need to be running."