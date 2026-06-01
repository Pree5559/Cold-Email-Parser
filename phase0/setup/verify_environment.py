#!/usr/bin/env python3
"""
Phase 0 Setup Script: Verify Development Environment
Runs all checks to ensure the development environment is ready
"""

import sys
import subprocess
import os


def check_python():
    """Check Python installation."""
    print("Checking Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (need 3.8+)")
        return False


def check_pip():
    """Check pip installation."""
    print("Checking pip...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {result.stdout.strip()}")
            return True
        else:
            print("❌ pip not working")
            return False
    except Exception as e:
        print(f"❌ {e}")
        return False


def check_git():
    """Check Git installation."""
    print("Checking Git...")
    try:
        result = subprocess.run(["git", "--version"],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {result.stdout.strip()}")
            return True
        else:
            print("❌ Git not installed")
            return False
    except FileNotFoundError:
        print("❌ Git not found")
        return False


def check_venv():
    """Check if virtual environment exists."""
    print("Checking virtual environment...")
    venv_path = "venv"
    if os.path.exists(venv_path):
        print(f"✅ Virtual environment exists: {venv_path}/")
        return True
    else:
        print(f"❌ Virtual environment not found: {venv_path}/")
        print("   Run: python phase0/setup/setup_venv.py")
        return False


def check_directory_structure():
    """Check if required directories exist."""
    print("Checking directory structure...")
    required_dirs = [
        "phase0/setup",
        "phase0/docs",
        "phase1",
        "phase2",
        "phase3/templates",
        "phase4/api",
        "phase4/docker",
        "docs",
        "tests/test_phase1",
        "tests/test_phase2",
        "tests/test_phase3",
        "tests/test_phase4",
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ (missing)")
            all_exist = False
    
    return all_exist


def run_test_file():
    """Create and run a test Python file."""
    print("\nRunning test file...")
    
    test_code = """
import sys
import os

print("Test file execution successful!")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
"""
    
    try:
        result = subprocess.run([sys.executable, "-c", test_code],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Test file executed successfully")
            print(result.stdout)
            return True
        else:
            print("❌ Test file execution failed")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {e}")
        return False


def main():
    """Main verification function."""
    print("=" * 60)
    print("Phase 0: Development Environment Verification")
    print("=" * 60)
    print()
    
    checks = {
        "Python": check_python(),
        "pip": check_pip(),
        "Git": check_git(),
        "Virtual Environment": check_venv(),
        "Directory Structure": check_directory_structure(),
        "Test Execution": run_test_file(),
    }
    
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    passed = sum(checks.values())
    total = len(checks)
    
    for check, result in checks.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {check}")
    
    print("=" * 60)
    print(f"Results: {passed}/{total} checks passed")
    print("=" * 60)
    
    if passed == total:
        print("\n✅ All checks passed! Environment is ready for development.")
        return 0
    else:
        print(f"\n❌ {total - passed} check(s) failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
