"""
E-commerce Backend Setup Script
Converts the bash setup.sh to Python for v0 compatibility
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_header(message):
    """Print a formatted header message"""
    print("\n" + "="*50)
    print(f" {message}")
    print("="*50)

def print_step(step_num, message):
    """Print a formatted step message"""
    print(f"\n[Step {step_num}] {message}")

def check_python_version():
    """Check if Python version is compatible"""
    print_step(1, "Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def create_virtual_environment():
    """Create and activate virtual environment"""
    print_step(2, "Setting up Python virtual environment...")
    
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    try:
        # Create virtual environment
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print_step(3, "Installing Python dependencies...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        # Install dependencies
        subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ], check=True)
        
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_database_config():
    """Create database configuration"""
    print_step(4, "Creating database configuration...")
    
    config = {
        "database": {
            "host": "localhost",
            "port": 3306,
            "name": "ecommerce_db",
            "user": "root",
            "password": "password"
        },
        "api": {
            "host": "0.0.0.0",
            "port": 8000,
            "debug": True
        }
    }
    
    config_path = Path("config.json")
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        print("✅ Database configuration created")
        print(f"   Config file: {config_path.absolute()}")
        return True
    except Exception as e:
        print(f"❌ Failed to create config: {e}")
        return False

def verify_setup():
    """Verify the setup is complete"""
    print_step(5, "Verifying setup...")
    
    checks = [
        ("Virtual environment", Path("venv").exists()),
        ("Requirements file", Path("requirements.txt").exists()),
        ("Database schema", Path("database/schema.sql").exists()),
        ("Main API file", Path("api/main.py").exists()),
        ("Data loader", Path("scripts/load_data.py").exists()),
        ("Config file", Path("config.json").exists())
    ]
    
    all_good = True
    for check_name, check_result in checks:
        status = "✅" if check_result else "❌"
        print(f"   {status} {check_name}")
        if not check_result:
            all_good = False
    
    return all_good

def print_next_steps():
    """Print instructions for next steps"""
    print_header("Setup Complete!")
    
    print("\n🚀 Next Steps:")
    print("1. Ensure MySQL is running on your system")
    print("2. Create the database: CREATE DATABASE ecommerce_db;")
    print("3. Run the schema: mysql -u root -p ecommerce_db < database/schema.sql")
    print("4. Load sample data: python scripts/load_data.py")
    print("5. Start the API server: python api/main.py")
    
    print("\n📚 Useful Commands:")
    print("   • Test API health: curl http://localhost:8000/health")
    print("   • View API docs: http://localhost:8000/docs")
    print("   • Check logs: tail -f api.log")
    
    print("\n🔧 Configuration:")
    print("   • Database config: config.json")
    print("   • API settings: api/main.py")
    print("   • Dependencies: requirements.txt")

def main():
    """Main setup function"""
    print_header("E-commerce Backend Setup")
    print("Converting bash setup to Python for v0 compatibility")
    
    # Change to backend directory if not already there
    if Path("backend").exists() and not Path("api").exists():
        os.chdir("backend")
        print("📁 Changed to backend directory")
    
    steps = [
        check_python_version,
        create_virtual_environment,
        install_dependencies,
        create_database_config,
        verify_setup
    ]
    
    for step_func in steps:
        if not step_func():
            print(f"\n❌ Setup failed at: {step_func.__name__}")
            sys.exit(1)
    
    print_next_steps()
    print("\n🎉 Backend setup completed successfully!")

if __name__ == "__main__":
    main()
