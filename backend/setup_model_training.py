"""
Setup script for Model Training System
This script verifies all requirements are met for model training
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8+"""
    print("\n1️⃣  Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"   ❌ Python 3.8+ required. Current: {version.major}.{version.minor}")
        return False
    print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if all required packages are installed"""
    print("\n2️⃣  Checking dependencies...")
    required_packages = {
        'fastapi': 'fastapi',
        'tensorflow': 'tensorflow',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'PIL': 'Pillow',
        'supabase': 'supabase',
        'requests': 'requests'
    }
    
    missing = []
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\n   📦 Install missing packages:")
        print(f"   pip install {' '.join(missing)}")
        return False
    return True

def check_environment_variables():
    """Check if required environment variables are set"""
    print("\n3️⃣  Checking environment variables...")
    
    # Load .env if exists
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        print(f"   📄 Found .env file")
        from dotenv import load_dotenv
        load_dotenv(env_file)
    
    required_vars = {
        'SUPABASE_URL': 'Your Supabase project URL',
        'SUPABASE_ANON_KEY': 'Your Supabase anon key (for frontend)',
        'SUPABASE_SERVICE_KEY': 'Your Supabase service role key (for backend)'
    }
    
    missing = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            print(f"   ❌ {var} - NOT SET")
            print(f"      {description}")
            missing.append(var)
        else:
            # Mask sensitive values
            display = value[:20] + '...' if len(value) > 20 else value
            print(f"   ✅ {var} = {display}")
    
    if missing:
        print(f"\n   ⚙️  Set environment variables in .env file or system environment")
        return False
    return True

def check_supabase_connection():
    """Test connection to Supabase"""
    print("\n4️⃣  Testing Supabase connection...")
    try:
        from supabase import create_client
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not url or not key:
            print("   ❌ Missing Supabase credentials")
            return False
        
        supabase = create_client(url, key)
        
        # Test connection by fetching table info
        result = supabase.table('profiles').select('count').limit(1).execute()
        print(f"   ✅ Connected to Supabase")
        print(f"   📊 Database accessible")
        return True
    except Exception as e:
        print(f"   ❌ Connection failed: {str(e)}")
        return False

def check_directory_structure():
    """Verify required directories exist"""
    print("\n5️⃣  Checking directory structure...")
    
    base_dir = Path(__file__).parent
    required_dirs = {
        'app': 'Main application directory',
        'app/services': 'Services directory',
        'app/routes': 'Routes directory',
        'models': 'Model storage directory (will be created)',
        'training_logs': 'Training logs directory (will be created)',
        'uploads': 'Image uploads directory (will be created)'
    }
    
    all_exist = True
    for dir_path, description in required_dirs.items():
        full_path = base_dir / dir_path
        if full_path.exists():
            print(f"   ✅ {dir_path}/")
        else:
            # Create directory if it doesn't exist
            try:
                full_path.mkdir(parents=True, exist_ok=True)
                print(f"   ✨ Created {dir_path}/")
            except Exception as e:
                print(f"   ❌ {dir_path}/ - Could not create: {e}")
                all_exist = False
    
    return all_exist

def check_services_exist():
    """Check if model training services exist"""
    print("\n6️⃣  Checking model training services...")
    
    base_dir = Path(__file__).parent
    required_files = {
        'app/services/data_collection.py': 'Data collection service',
        'app/services/model_training.py': 'Model training service',
        'app/routes/model_training_routes.py': 'Model training API routes'
    }
    
    all_exist = True
    for file_path, description in required_files.items():
        full_path = base_dir / file_path
        if full_path.exists():
            # Check file size
            size_kb = full_path.stat().st_size / 1024
            print(f"   ✅ {file_path} ({size_kb:.1f} KB)")
        else:
            print(f"   ❌ {file_path} - NOT FOUND")
            all_exist = False
    
    return all_exist

def test_data_collection():
    """Test data collection service"""
    print("\n7️⃣  Testing data collection service...")
    try:
        from app.services.data_collection import DataCollectionService
        
        service = DataCollectionService()
        
        # Get statistics
        stats = service.get_model_performance_metrics()
        
        print(f"   ✅ Data collection service working")
        print(f"   📊 Found predictions in database:")
        print(f"      - Pest: {stats.get('total_predictions', {}).get('pest', 0)}")
        print(f"      - Disease: {stats.get('total_predictions', {}).get('disease', 0)}")
        print(f"      - Storage: {stats.get('total_predictions', {}).get('storage', 0)}")
        
        return True
    except Exception as e:
        print(f"   ❌ Data collection test failed: {str(e)}")
        return False

def test_model_training():
    """Test model training service initialization"""
    print("\n8️⃣  Testing model training service...")
    try:
        from app.services.model_training import ModelTrainingService
        
        service = ModelTrainingService()
        print(f"   ✅ Model training service initialized")
        print(f"   📁 Models will be saved to: {service.models_dir}")
        return True
    except Exception as e:
        print(f"   ❌ Model training test failed: {str(e)}")
        return False

def print_summary(checks):
    """Print summary of all checks"""
    print("\n" + "=" * 70)
    print("📊 Setup Summary")
    print("=" * 70)
    
    passed = sum(checks.values())
    total = len(checks)
    
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
    
    print("=" * 70)
    print(f"Result: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Your model training system is ready.")
        print("\nNext steps:")
        print("1. Start the backend server:")
        print("   python run_server.py")
        print("\n2. View API documentation:")
        print("   http://localhost:8000/docs")
        print("\n3. Check training data availability:")
        print("   curl http://localhost:8000/api/model-training/data-stats")
        print("\n4. Start your first training:")
        print("   curl -X POST http://localhost:8000/api/model-training/train \\")
        print('        -H "Content-Type: application/json" \\')
        print('        -d \'{"model_type": "pest", "epochs": 10}\'')
        print("\n📖 For more information, see MODEL_TRAINING_GUIDE.md")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("Refer to MODEL_TRAINING_GUIDE.md for detailed setup instructions.")
    
    print("=" * 70)

def main():
    """Run all checks"""
    print("=" * 70)
    print("🔍 AgroShield Model Training System Setup")
    print("=" * 70)
    
    checks = {
        "Python Version": check_python_version(),
        "Dependencies": check_dependencies(),
        "Environment Variables": check_environment_variables(),
        "Supabase Connection": check_supabase_connection(),
        "Directory Structure": check_directory_structure(),
        "Service Files": check_services_exist(),
        "Data Collection": test_data_collection(),
        "Model Training": test_model_training()
    }
    
    print_summary(checks)
    
    return all(checks.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
