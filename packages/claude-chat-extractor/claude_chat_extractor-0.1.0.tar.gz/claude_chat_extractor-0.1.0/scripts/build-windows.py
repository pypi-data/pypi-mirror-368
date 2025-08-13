#!/usr/bin/env python3
"""Build Windows executable using PyInstaller."""

import shutil
import subprocess
import sys
from pathlib import Path


def build_windows_executable():
    """Build Windows executable using PyInstaller."""

    # Install PyInstaller if not available
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyinstaller"], check=True
        )

    # Clean previous builds
    dist_dir = Path("dist")
    build_dir = Path("build")
    spec_file = Path("claude-conversation-extractor.spec")

    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if spec_file.exists():
        spec_file.unlink()

    # Build executable
    print("Building Windows executable...")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--onefile",
            "--name=claude-conversation-extractor",
            "--add-data=src/claude_conversation_extractor;claude_conversation_extractor",
            "src/claude_conversation_extractor/cli.py",
        ],
        check=True,
    )

    # Create installer directory
    installer_dir = Path("installer")
    installer_dir.mkdir(exist_ok=True)

    # Copy executable and create batch file
    exe_path = dist_dir / "claude-conversation-extractor.exe"
    if exe_path.exists():
        shutil.copy2(exe_path, installer_dir / "claude-conversation-extractor.exe")

        # Create batch file for easy access
        batch_content = """@echo off
REM Claude Conversation Extractor
REM Add this directory to your PATH for system-wide access

echo Claude Conversation Extractor
echo Usage: claude-conversation-extractor --help
echo.
echo To install system-wide, add this directory to your PATH environment variable.
echo.
pause
"""
        with open(installer_dir / "install.bat", "w") as f:
            f.write(batch_content)

        # Create README
        readme_content = """# Windows Installation

## Quick Start
1. Run `install.bat` to see usage instructions
2. Use `claude-conversation-extractor.exe --help` to see available commands

## System-wide Installation
To make the tool available system-wide:

1. Copy `claude-conversation-extractor.exe` to a directory in your PATH
   - Recommended: `C:\\Windows\\System32\\` (requires admin)
   - Alternative: Create a custom directory and add it to PATH

2. Add to PATH manually:
   - Right-click "This PC" → Properties → Advanced system settings
   - Click "Environment Variables"
   - Edit "Path" variable and add your custom directory

3. Restart command prompt and test:
   ```
   claude-conversation-extractor --help
   ```

## Available Commands
- `claude-conversation-extractor extract -u <uuid> -i <input.json>`
- `claude-conversation-extractor list -i <input.json>`
- Short alias: `cce`

## Troubleshooting
- If "command not found", ensure the executable is in your PATH
- Run as administrator if copying to System32
- Check Windows Defender isn't blocking the executable
"""
        with open(installer_dir / "README.md", "w") as f:
            f.write(readme_content)

        print("✅ Windows executable built successfully!")
        print(f"📁 Executable: {installer_dir / 'claude-conversation-extractor.exe'}")
        print(f"📁 Installer directory: {installer_dir}")
        print("📖 Read README.md for installation instructions")

    else:
        print("❌ Failed to build executable")
        sys.exit(1)


if __name__ == "__main__":
    if sys.platform != "win32":
        print("This script is for Windows only")
        sys.exit(1)

    build_windows_executable()
