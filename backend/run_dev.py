"""
Quick development server runner for AgroShield backend.

Usage:
    python run_dev.py
    
Then open http://localhost:8000/docs for API documentation.
"""
import uvicorn
import sys
from pathlib import Path

# Add backend to path so app imports work
sys.path.insert(0, str(Path(__file__).resolve().parent))

if __name__ == '__main__':
    print('🚀 Starting AgroShield Backend (Dev Mode)')
    print('📖 API Docs: http://localhost:8000/docs')
    print('🔥 Hot reload enabled - edit files and they will auto-reload')
    print('')
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)
