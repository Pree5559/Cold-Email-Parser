#!/usr/bin/env python3
"""
Phase 0 Setup Script: Create Virtual Environment
Creates and configures Python virtual environment
"""

import sys
import subprocess
import os


def create_virtual_environment(venv_name="venv"):
    """Create a Python virtual environment."""
    print(f"Creating virtual environment: {venv_name}")
    
    try:
        result = subprocess.run([sys.executable, "-m", "venv", venv_name],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Virtual environment created: {venv_name}/")
            return True
        else:
            print(f"❌ ERROR creating virtual environment: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def upgrade_pip(venv_name="venv"):
    """Upgrade pip in the virtual environment."""
    print("\nUpgrading pip in virtual environment...")
    
    # Determine pip executable path based on OS
    if os.name == 'nt':  # Windows
        pip_path = f"{venv_name}\\Scripts\\pip.exe"
    else:  # Unix-like
        pip_path = f"{venv_name}/bin/pip"
    
    try:
        result = subprocess.run([pip_path, "install", "--upgrade", "pip"],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ pip upgraded successfully")
            return True
        else:
            print(f"❌ ERROR upgrading pip: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def print_activation_instructions(venv_name="venv"):
    """Print instructions for activating the virtual environment."""
    print("\n" + "=" * 60)
    print("Virtual Environment Setup Complete!")
    print("=" * 60)
    print("\nTo activate the virtual environment:")
    print("\nWindows:")
    print(f"  {venv_name}\\Scripts\\activate")
    print("\nMac/Linux:")
    print(f"  source {venv_name}/bin/activate")
    print("\nTo deactivate:")
    print("  deactivate")
    print("=" * 60)


def main():
    """Main function to set up virtual environment."""
    print("=" * 60)
    print("Phase 0: Virtual Environment Setup")
    print("=" * 60)
    
    venv_name = "venv"
    
    # Check if venv already exists
    if os.path.exists(venv_name):
        print(f"⚠️  Virtual environment '{venv_name}' already exists")
        response = input("Delete and recreate? (y/n): ")
        if response.lower() == 'y':
            import shutil
            shutil.rmtree(venv_name)
            print(f"Deleted existing {venv_name}")
        else:
            print("Keeping existing virtual environment")
            print_activation_instructions(venv_name)
            return 0
    
    # Create virtual environment
    venv_ok = create_virtual_environment(venv_name)
    
    if venv_ok:
        # Upgrade pip
        pip_ok = upgrade_pip(venv_name)
        
        if pip_ok:
            print_activation_instructions(venv_name)
            return 0
        else:
            print("❌ Failed to upgrade pip")
            return 1
    else:
        print("❌ Failed to create virtual environment")
        return 1


if __name__ == "__main__":
    sys.exit(main())
