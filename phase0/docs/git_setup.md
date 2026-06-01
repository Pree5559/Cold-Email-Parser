# Git Setup Guide

## Installation

### Windows
1. Download Git from https://git-scm.com/download/win
2. Run the installer with default options
3. Verify installation: Open Command Prompt and run:
   ```bash
   git --version
   ```

### macOS
Git is usually pre-installed. If not:
```bash
brew install git
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install git
```

## Configuration

After installing Git, configure your identity:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Verify configuration:
```bash
git config --list
```

## Verification

Run the verification script:
```bash
python phase0/setup/check_git.py
```

Expected output:
```
============================================================
Phase 0: Git Installation Check
============================================================
Checking Git installation...
✅ Git is installed: git version 2.x.x

Checking Git configuration...
✅ Git user.name: Your Name
✅ Git user.email: your.email@example.com

============================================================
✅ Git is installed and configured!
============================================================
```

## Troubleshooting

### "git: command not found"
- Ensure Git is installed
- Restart your terminal after installation
- Check PATH environment variable

### Configuration not showing
- Run the config commands again
- Check `~/.gitconfig` file (Linux/macOS) or `%USERPROFILE%\.gitconfig` (Windows)

## Next Steps

After Git is installed and configured:
1. Initialize Git repository in project directory:
   ```bash
   git init
   ```
2. Create .gitignore file (see project .gitignore template)
3. Make initial commit:
   ```bash
   git add .
   git commit -m "Initial commit"
   ```
4. (Optional) Create GitHub repository and push
