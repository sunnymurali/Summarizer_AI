#!/bin/bash

# AI Document Analysis - Installation Script
# This script installs all required dependencies for the application

echo "🚀 AI Document Analysis - Installing Dependencies"
echo "=================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python version $python_version is not supported. Please install Python 3.11 or higher."
    exit 1
fi

echo "✅ Python version $python_version is compatible"

# Install pip if not available
if ! command -v pip3 &> /dev/null; then
    echo "📦 Installing pip..."
    python3 -m ensurepip --upgrade
fi

# Upgrade pip
echo "⬆️ Upgrading pip..."
python3 -m pip install --upgrade pip

# Install requirements
echo "📦 Installing Python packages..."

packages=(
    "fastapi==0.104.1"
    "uvicorn==0.24.0"
    "python-multipart==0.0.6"
    "PyPDF2==3.0.1"
    "python-docx==1.1.0"
    "tiktoken==0.5.1"
    "faiss-cpu==1.7.4"
    "numpy==1.24.3"
    "openai==1.3.3"
    "pydantic==2.5.0"
    "streamlit==1.28.1"
    "requests==2.31.0"
    "python-dotenv==1.0.0"
)

for package in "${packages[@]}"; do
    echo "Installing $package..."
    if ! python3 -m pip install "$package"; then
        echo "❌ Failed to install $package"
        exit 1
    fi
done

echo "✅ All packages installed successfully!"
echo ""
echo "🔧 Next steps:"
echo "1. Configure your Azure OpenAI credentials in .env file"
echo "2. Run the application with: python start_services.py"
echo "3. Open http://localhost:5000 in your browser"
echo ""
echo "📋 For detailed setup instructions, see README.md"