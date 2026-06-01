# Python Setup Guide

## Installation

### Windows
1. Download Python from https://www.python.org/downloads/
2. Run the installer
3. **Important**: Check "Add Python to PATH" during installation
4. Verify installation: Open Command Prompt and run:
   ```bash
   python --version
   pip --version
   ```

### macOS
1. Install Homebrew (if not installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Install Python:
   ```bash
   brew install python
   ```
3. Verify installation:
   ```bash
   python3 --version
   pip3 --version
   ```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
python3 --version
pip3 --version
```

## Verification

Run the verification script:
```bash
python phase0/setup/check_python.py
```

Expected output:
```
============================================================
Phase 0: Python Installation Check
============================================================
Checking Python installation...
Python version: 3.11.x
✅ Python version is compatible (3.8+)

Checking pip installation...
✅ pip is installed: pip 23.x.x

============================================================
✅ All Python checks passed!
============================================================
```

## Troubleshooting

### "python: command not found"
- Windows: Reinstall Python with "Add to PATH" checked
- macOS/Linux: Use `python3` instead of `python`

### "pip: command not found"
- Ensure pip was installed with Python
- Reinstall Python or install pip separately

### Version too old
- Uninstall old Python version
- Install Python 3.8 or higher

## Next Steps

After Python is installed and verified:
1. Run `python phase0/setup/check_git.py` to verify Git
2. Run `python phase0/setup/setup_venv.py` to create virtual environment
3. Run `python phase0/setup/verify_environment.py` to verify everything
