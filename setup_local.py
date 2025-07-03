#!/usr/bin/env python3
"""
Local Setup Script for AI Document Analysis Application
This script helps you set up the application on your local machine.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_step(step, description):
    print(f"\n🔧 Step {step}: {description}")

def run_command(command, description=""):
    """Run a shell command and return success status"""
    try:
        print(f"   Running: {command}")
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        if result.stdout:
            print(f"   ✅ {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        if e.stderr:
            print(f"   Error details: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} is not compatible")
        print("   Please install Python 3.11 or higher")
        return False

def create_env_file():
    """Create .env file template"""
    env_content = """# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_API_VERSION=2024-02-01

# Optional: Uncomment and modify if needed
# AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo
# AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("   ✅ Created .env file template")
        return True
    except Exception as e:
        print(f"   ❌ Error creating .env file: {e}")
        return False

def install_requirements():
    """Install Python requirements"""
    requirements = [
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "python-multipart==0.0.6",
        "PyPDF2==3.0.1",
        "python-docx==1.1.0",
        "tiktoken==0.5.1",
        "faiss-cpu==1.7.4",
        "numpy==1.24.3",
        "openai==1.3.3",
        "pydantic==2.5.0",
        "streamlit==1.28.1",
        "requests==2.31.0",
        "python-dotenv==1.0.0"
    ]
    
    print("   Installing Python packages...")
    for req in requirements:
        if not run_command(f"pip install {req}", f"Installed {req.split('==')[0]}"):
            return False
    
    print("   ✅ All packages installed successfully")
    return True

def main():
    print_header("AI Document Analysis - Local Setup")
    print("This script will help you set up the application on your local machine.")
    
    # Step 1: Check Python version
    print_step(1, "Checking Python version")
    if not check_python_version():
        return
    
    # Step 2: Create virtual environment
    print_step(2, "Setting up virtual environment")
    if not run_command("python -m venv venv", "Created virtual environment"):
        print("   ⚠️  Virtual environment creation failed, continuing with global installation")
    
    # Step 3: Activate virtual environment (instructions)
    print_step(3, "Virtual environment activation")
    if platform.system() == "Windows":
        activate_cmd = "venv\\Scripts\\activate"
    else:
        activate_cmd = "source venv/bin/activate"
    
    print(f"   To activate virtual environment, run: {activate_cmd}")
    print("   ⚠️  Please activate the virtual environment manually before proceeding")
    
    # Step 4: Install requirements
    print_step(4, "Installing Python packages")
    if not install_requirements():
        print("   ❌ Package installation failed")
        return
    
    # Step 5: Create .env file
    print_step(5, "Creating environment configuration")
    if not create_env_file():
        print("   ❌ Environment file creation failed")
        return
    
    # Step 6: Configuration instructions
    print_step(6, "Configuration required")
    print("   ⚠️  IMPORTANT: You need to configure your Azure OpenAI credentials")
    print("   📝 Edit the .env file and replace 'your_api_key_here' with your actual values")
    print("   📍 Get your credentials from: https://portal.azure.com/")
    
    # Step 7: Running instructions
    print_step(7, "Running the application")
    print("   Once configured, you can run the application with:")
    print("   📱 Full app: python start_services.py")
    print("   🔧 Backend only: python run_backend.py")
    print("   🎨 Frontend only: streamlit run app.py --server.port 5000")
    
    # Final summary
    print_header("Setup Complete!")
    print("✅ Python environment ready")
    print("✅ Dependencies installed")
    print("✅ Configuration template created")
    print("")
    print("📋 Next steps:")
    print("1. Activate virtual environment (if created)")
    print("2. Edit .env file with your Azure OpenAI credentials")
    print("3. Run: python start_services.py")
    print("4. Open: http://localhost:5000")
    print("")
    print("🆘 Need help? Check README.md for troubleshooting")

if __name__ == "__main__":
    main()