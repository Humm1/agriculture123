"""
AgroShield Quick Start Script
Automated setup for Phase 1 & 2 deployment
"""

import os
import sys
import subprocess
from pathlib import Path
import json


def print_header(text: str):
    """Print formatted header."""
    print("\n" + "="*60)
    print(text)
    print("="*60)


def check_python_version():
    """Verify Python 3.10+ is installed."""
    print_header("CHECKING PYTHON VERSION")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"✗ Python 3.10+ required. Found: {version.major}.{version.minor}")
        sys.exit(1)
    
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")


def create_directory_structure():
    """Create necessary directories."""
    print_header("CREATING DIRECTORY STRUCTURE")
    
    directories = [
        "data/plant_diseases/healthy",
        "data/plant_diseases/late_blight",
        "data/plant_diseases/early_blight",
        "data/plant_diseases/bacterial_wilt",
        "data/plant_diseases/powdery_mildew",
        "data/plant_diseases/leaf_rust",
        "data/plant_diseases/fall_armyworm",
        "data/plant_diseases/maize_streak_virus",
        "data/plant_diseases/anthracnose",
        "data/plant_diseases/fusarium_wilt",
        "data/soil_images/images",
        "data/weather_history",
        "models/plant_health",
        "models/soil_diagnostics",
        "models/climate_prediction",
        "config",
        "logs"
    ]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {directory}")


def install_dependencies():
    """Install Python dependencies."""
    print_header("INSTALLING DEPENDENCIES")
    
    requirements_files = [
        "backend/requirements.txt",
        "backend/requirements-test.txt"
    ]
    
    for req_file in requirements_files:
        if Path(req_file).exists():
            print(f"\nInstalling from {req_file}...")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", req_file
                ], check=True)
                print(f"✓ Installed dependencies from {req_file}")
            except subprocess.CalledProcessError:
                print(f"✗ Failed to install from {req_file}")
                return False
    
    return True


def create_config_template():
    """Create API configuration template."""
    print_header("CREATING CONFIGURATION TEMPLATE")
    
    config_path = Path("config/api_keys.json")
    
    if config_path.exists():
        print("⚠️  config/api_keys.json already exists. Skipping.")
        return
    
    config_template = {
        "api_keys": {
            "cgiar": "YOUR_CGIAR_API_KEY",
            "kephis": "YOUR_KEPHIS_API_KEY",
            "openweathermap": "YOUR_OPENWEATHERMAP_KEY",
            "accuweather": "YOUR_ACCUWEATHER_KEY (optional)",
            "huggingface": "YOUR_HUGGINGFACE_TOKEN",
            "africas_talking": "YOUR_AFRICAS_TALKING_KEY"
        },
        "instructions": "Replace placeholder values with actual API keys. See API_SETUP_GUIDE.md for details."
    }
    
    with open(config_path, 'w') as f:
        json.dump(config_template, f, indent=2)
    
    print(f"✓ Created: {config_path}")
    print("  → Edit this file with your API keys")


def create_gitignore():
    """Create .gitignore for sensitive files."""
    print_header("CREATING .GITIGNORE")
    
    gitignore_path = Path(".gitignore")
    
    gitignore_content = """# AgroShield - Sensitive files
config/api_keys.json
.env
*.env

# Model files (large)
models/**/*.keras
models/**/*.h5
models/**/*.tflite

# Training data (large)
data/plant_diseases/
data/soil_images/
data/weather_history/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
logs/
*.log

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db
"""
    
    with open(gitignore_path, 'w') as f:
        f.write(gitignore_content)
    
    print(f"✓ Created: {gitignore_path}")


def create_env_template():
    """Create .env template file."""
    print_header("CREATING ENVIRONMENT TEMPLATE")
    
    env_path = Path(".env.template")
    
    env_content = """# AgroShield Environment Variables
# Copy this file to .env and fill in your values

# API Keys
CGIAR_API_KEY=your_cgiar_api_key_here
KEPHIS_API_KEY=your_kephis_api_key_here
OPENWEATHERMAP_API_KEY=your_openweathermap_key_here
ACCUWEATHER_API_KEY=your_accuweather_key_here (optional)
HUGGINGFACE_TOKEN=your_huggingface_token_here

# SMS Provider (choose one)
AFRICAS_TALKING_API_KEY=your_africas_talking_key
AFRICAS_TALKING_USERNAME=your_username
# OR
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_number

# Database (if needed)
DATABASE_URL=sqlite:///agroshield.db

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false
"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"✓ Created: {env_path}")
    print("  → Copy to .env and configure")


def print_next_steps():
    """Print next steps for user."""
    print_header("SETUP COMPLETE!")
    
    print("""
✓ Directory structure created
✓ Dependencies installed
✓ Configuration templates created

NEXT STEPS:

1. Phase 1: Model Training (2-4 weeks)
   
   a) Collect disease images:
      → Place 500+ images per class in data/plant_diseases/<class_name>/
      → See PHASE_1_2_DEPLOYMENT_GUIDE.md for data sources
   
   b) Train plant health model:
      python backend/app/ml/train_plant_health_model.py
   
   c) Collect soil data:
      → Correlate soil images with lab NPK measurements
      → Create data/soil_images/labels.csv
   
   d) Train soil diagnostics model:
      python backend/app/ml/train_soil_diagnostics_model.py
   
   e) Collect weather history:
      → 10+ years of daily weather data
      → Save as data/weather_history.csv
   
   f) Train climate prediction model:
      python backend/app/ml/train_climate_prediction_model.py

2. Phase 2: API Configuration (1 week - can run in parallel)
   
   a) Apply for API keys:
      → CGIAR: research@cgiar.org
      → KEPHIS: kephis.go.ke/developers
      → OpenWeatherMap: openweathermap.org/api
      → Hugging Face: huggingface.co
      → See API_SETUP_GUIDE.md for detailed instructions
   
   b) Configure API keys:
      → Edit config/api_keys.json
      → Or set environment variables in .env
   
   c) Validate API keys:
      python backend/app/config/api_config.py

3. Phase 3: Integration Testing (2 weeks)
   
   a) Run test suite:
      python run_tests.py --coverage
   
   b) Validate accuracy:
      python backend/app/ml/validate_model.py

4. Phase 4: Production Deployment (1 week)
   
   a) Deploy TFLite models to mobile app
   b) Deploy backend to cloud server
   c) Enable monitoring dashboard

DOCUMENTATION:
- Complete guide: PHASE_1_2_DEPLOYMENT_GUIDE.md
- API setup: API_SETUP_GUIDE.md
- TensorFlow integration: TENSORFLOW_INTEGRATION_GUIDE.md
- Testing: TESTING_MONITORING_GUIDE.md

SUPPORT:
- Email: support@agroshield.ke
- Docs: README.md

Good luck! 🚀
""")


def main():
    """Main setup function."""
    print_header("AGROSHIELD QUICK START SETUP")
    print("Automated setup for Phase 1 & 2 deployment")
    
    try:
        # Step 1: Check Python version
        check_python_version()
        
        # Step 2: Create directory structure
        create_directory_structure()
        
        # Step 3: Install dependencies
        if not install_dependencies():
            print("\n⚠️  Some dependencies failed to install.")
            print("Please check errors and try manual installation:")
            print("  pip install -r backend/requirements.txt")
        
        # Step 4: Create configuration files
        create_config_template()
        create_env_template()
        create_gitignore()
        
        # Step 5: Print next steps
        print_next_steps()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
