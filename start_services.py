import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def run_backend():
    """Run the FastAPI backend"""
    print("🚀 Starting FastAPI backend on port 8000...")
    try:
        # Add backend directory to Python path
        env = os.environ.copy()
        backend_path = os.path.join(os.path.dirname(__file__), 'backend')
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{backend_path}:{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = backend_path
        
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "backend.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ], env=env, cwd=os.path.dirname(__file__))
    except KeyboardInterrupt:
        print("🛑 Backend stopped")
    except Exception as e:
        print(f"❌ Error running backend: {e}")

def run_frontend():
    """Run the Streamlit frontend"""
    print("🚀 Starting Streamlit frontend on port 5000...")
    try:
        # Wait a bit for backend to start
        time.sleep(3)
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "app.py", 
            "--server.port", "5000",
            "--server.address", "0.0.0.0"
        ], cwd=os.path.dirname(__file__))
    except KeyboardInterrupt:
        print("🛑 Frontend stopped")
    except Exception as e:
        print(f"❌ Error running frontend: {e}")

def check_requirements():
    """Check if required environment variables are set"""
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Please set these environment variables before running the application.")
        return False
    
    return True

def main():
    """Main function to start both services"""
    print("🔧 AI Document Analysis Application")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        return
    
    print("✅ Environment variables configured")
    print("🔄 Starting services...")
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Start frontend in main thread
    try:
        run_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
    
    print("👋 Services stopped")

if __name__ == "__main__":
    main()
