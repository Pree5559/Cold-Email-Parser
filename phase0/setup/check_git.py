#!/usr/bin/env python3
"""
Phase 0 Setup Script: Check Git Installation
Verifies Git is installed and configured
"""

import subprocess
import sys


def check_git_installed():
    """Check if Git is installed."""
    print("Checking Git installation...")
    
    try:
        result = subprocess.run(["git", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Git is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ ERROR: Git is not installed")
            return False
    except FileNotFoundError:
        print("❌ ERROR: Git is not found in PATH")
        return False
    except Exception as e:
        print(f"❌ ERROR checking Git: {e}")
        return False


def check_git_config():
    """Check if Git user is configured."""
    print("\nChecking Git configuration...")
    
    try:
        # Check user.name
        name_result = subprocess.run(["git", "config", "--global", "user.name"],
                                     capture_output=True, text=True)
        if name_result.returncode == 0 and name_result.stdout.strip():
            print(f"✅ Git user.name: {name_result.stdout.strip()}")
        else:
            print("⚠️  WARNING: Git user.name not configured")
            print("   Run: git config --global user.name \"Your Name\"")
        
        # Check user.email
        email_result = subprocess.run(["git", "config", "--global", "user.email"],
                                      capture_output=True, text=True)
        if email_result.returncode == 0 and email_result.stdout.strip():
            print(f"✅ Git user.email: {email_result.stdout.strip()}")
        else:
            print("⚠️  WARNING: Git user.email not configured")
            print("   Run: git config --global user.email \"your.email@example.com\"")
        
        return True
    except Exception as e:
        print(f"❌ ERROR checking Git configuration: {e}")
        return False


def main():
    """Main function to run all checks."""
    print("=" * 60)
    print("Phase 0: Git Installation Check")
    print("=" * 60)
    
    git_ok = check_git_installed()
    config_ok = check_git_config()
    
    print("\n" + "=" * 60)
    if git_ok:
        print("✅ Git is installed and configured!")
        print("=" * 60)
        return 0
    else:
        print("❌ Git is not installed. Please install Git from https://git-scm.com")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
