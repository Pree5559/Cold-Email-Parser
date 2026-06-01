# IDE Setup Guide

## Recommended IDEs

### Cursor (Recommended)
Cursor is an AI-powered code editor built on VS Code.

1. Download from https://cursor.sh
2. Install with default options
3. Open the project folder in Cursor

### VS Code
1. Download from https://code.visualstudio.com
2. Install with default options
3. Open the project folder in VS Code

## Required Extensions

### For Cursor/VS Code

1. **Python** (by Microsoft)
   - Install from Extensions panel
   - Search: "Python"
   - Publisher: Microsoft

2. **Pylance** (by Microsoft) - VS Code only
   - Install from Extensions panel
   - Search: "Pylance"
   - Publisher: Microsoft

3. **GitLens** (by GitKraken) - Optional but recommended
   - Install from Extensions panel
   - Search: "GitLens"
   - Publisher: GitKraken

## Configuration

### Select Python Interpreter

1. Open Command Palette: `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type: "Python: Select Interpreter"
3. Select the virtual environment interpreter:
   - Windows: `./venv/Scripts/python.exe`
   - Mac/Linux: `./venv/bin/python`

### Configure Settings

Create `.vscode/settings.json` in project root:

```json
{
    "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

## Verification

1. Open Cursor/VS Code
2. Open the project folder
3. Create a test file `test.py`:
   ```python
   print("Hello from IDE!")
   ```
4. Run the file (F5 or right-click → Run Python File)
5. Verify output appears in terminal

## Troubleshooting

### Python interpreter not found
- Ensure virtual environment is created
- Select correct interpreter path
- Reload window: `Ctrl+Shift+P` → "Developer: Reload Window"

### Extensions not installing
- Check internet connection
- Try installing from VS Code Marketplace website
- Restart IDE after installation

### Code not running
- Check Python interpreter is selected
- Verify file is saved
- Check terminal for error messages

## Next Steps

After IDE is set up:
1. Run `python phase0/setup/verify_environment.py` to verify everything
2. Start Phase 1 development
