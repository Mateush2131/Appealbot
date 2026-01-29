import subprocess
import sys
import os

def check_dependencies():
    """Check if all dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pydantic
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Installing dependencies from requirements.txt...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True

def main():
    print("=== Support Service API ===")
    print("Checking dependencies...")
    
    if not check_dependencies():
        print("Failed to install dependencies")
        return
    
    print("\nStarting server...")
    print("API Documentation: http://127.0.0.1:8000/docs")
    print("Press Ctrl+C to stop\n")
    
    # Start the server
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
    ])

if __name__ == "__main__":
    main()