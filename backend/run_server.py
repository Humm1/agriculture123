"""
Backend Server Startup Script
Run this file to start the AgroShield FastAPI backend server
"""

import uvicorn
import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Starting AgroShield Backend Server")
    print("=" * 70)
    print("📍 Backend Location:", os.getcwd())
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("=" * 70)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
