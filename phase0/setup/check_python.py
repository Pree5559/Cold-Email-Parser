#!/usr/bin/env python3
"""
Phase 0 Setup Script: Check Python Installation
Verifies Python 3.8+ is installed and accessible
"""

import sys
import subprocess


def check_python_version():
    """Check if Python 3.8+ is installed."""
    print("Checking Python installation...")
    
    # Check Python version
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ ERROR: Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print("✅ Python version is compatible (3.8+)")
    return True


def check_pip():
    """Check if pip is installed and working."""
    print("\nChecking pip installation...")
    
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ pip is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ ERROR: pip is not working")
            return False
    except Exception as e:
        print(f"❌ ERROR checking pip: {e}")
        return False


def main():
    """Main function to run all checks."""
    print("=" * 60)
    print("Phase 0: Python Installation Check")
    print("=" * 60)
    
    python_ok = check_python_version()
    pip_ok = check_pip()
    
    print("\n" + "=" * 60)
    if python_ok and pip_ok:
        print("✅ All Python checks passed!")
        print("=" * 60)
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
