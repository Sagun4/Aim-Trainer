#!/usr/bin/env python3
"""
Elite Aim Trainer Pro v2.0 - Launcher
Easy startup launcher with dependency checking
"""

import sys
import subprocess
import importlib.util
import os

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required!")
        print(f"Current version: {sys.version}")
        print("Please update Python and try again.")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} - Compatible")
    return True

def check_dependency(package_name, pip_name=None):
    """Check if a package is installed"""
    if pip_name is None:
        pip_name = package_name
    
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        print(f"❌ Missing dependency: {package_name}")
        return False, pip_name
    else:
        try:
            module = importlib.import_module(package_name)
            version = getattr(module, '__version__', 'Unknown')
            print(f"✅ {package_name} {version} - Installed")
            return True, None
        except ImportError:
            print(f"❌ Failed to import: {package_name}")
            return False, pip_name

def install_dependencies():
    """Install missing dependencies"""
    print("\n🔧 Installing missing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies automatically.")
        print("Please run: pip install -r requirements.txt")
        return False

def main():
    """Main launcher function"""
    print("🎯 Elite Aim Trainer Pro v2.0 - Launcher")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        return
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    missing_deps = []
    
    # Check pygame
    success, pip_name = check_dependency("pygame")
    if not success:
        missing_deps.append(pip_name)
    
    # Check numpy (optional)
    success, pip_name = check_dependency("numpy")
    if not success:
        print("⚠️  NumPy not found - Some features will be disabled")
    
    # Install missing dependencies if any
    if missing_deps:
        print(f"\n❌ Missing required dependencies: {', '.join(missing_deps)}")
        
        if os.path.exists("requirements.txt"):
            response = input("Install missing dependencies automatically? (y/n): ").lower()
            if response in ['y', 'yes']:
                if not install_dependencies():
                    input("Press Enter to exit...")
                    return
            else:
                print("Please install dependencies manually and try again.")
                input("Press Enter to exit...")
                return
        else:
            print("requirements.txt not found. Please install pygame manually:")
            print("pip install pygame")
            input("Press Enter to exit...")
            return
    
    # Check if main file exists
    if not os.path.exists("aim.py"):
        print("❌ Error: aim.py not found!")
        print("Please make sure you're running this from the correct directory.")
        input("Press Enter to exit...")
        return
    
    print("\n🚀 All checks passed! Starting Elite Aim Trainer Pro...")
    print("=" * 50)
    
    # Launch the game
    try:
        import aim
        # The game will start automatically when aim.py is imported
    except Exception as e:
        print(f"❌ Error starting the game: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        input("Press Enter to exit...")
