# Installation Guide

This guide covers how to install `claude-conversation-extractor` on different platforms and make it available system-wide.

## Quick Start

### From PyPI (Recommended)
```bash
pip install claude-conversation-extractor
```

### From Source
```bash
git clone https://github.com/yourusername/claude-conversation-extractor
cd claude-conversation-extractor
pip install .
```

## Platform-Specific Installation

### 🐍 Python (All Platforms)

#### Global Installation
```bash
# Install for all users (requires admin/sudo)
sudo pip install claude-conversation-extractor

# Install for current user only
pip install --user claude-conversation-extractor
```

#### Virtual Environment Installation
```bash
# Create virtual environment
python -m venv claude-env
source claude-env/bin/activate  # On Windows: claude-env\Scripts\activate

# Install in virtual environment
pip install claude-conversation-extractor
```

#### Verify Installation
```bash
# Check if commands are available
claude-conversation-extractor --help
claude-extract --help
cce --help

# Check version
claude-conversation-extractor --version
```

### 🍎 macOS

#### pipx (Recommended)
```bash
# Install pipx if not already installed
brew install pipx

# Install the tool
pipx install claude-conversation-extractor
```

#### Homebrew (Alternative)
```bash
# Install via Homebrew (requires creating a formula first)
brew install claude-conversation-extractor

# Or if using a custom tap
brew tap yourusername/tap
brew install claude-conversation-extractor
```

#### Manual Installation
```bash
# Install Python dependencies
brew install python@3.12

# Install the tool
pip3 install claude-conversation-extractor
```

#### PATH Configuration
Add to your shell profile (`~/.zshrc`, `~/.bash_profile`):
```bash
export PATH="/usr/local/bin:$HOME/.local/bin:$PATH"
```

### 🐧 Linux

#### Debian/Ubuntu
```bash
# Install system dependencies
sudo apt update
sudo apt install python3-pip python3-venv

# Install the tool
pip3 install --user claude-conversation-extractor

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"
```

#### Fedora/RHEL/CentOS
```bash
# Install system dependencies
sudo dnf install python3-pip python3-setuptools

# Install the tool
pip3 install --user claude-conversation-extractor

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"
```

#### Arch Linux
```bash
# Install from AUR
yay -S claude-conversation-extractor

# Or install manually
sudo pacman -S python-pip
pip install --user claude-conversation-extractor
```

#### Generic Linux
```bash
# Use the provided build script
./scripts/build-linux.sh

# Follow the instructions in the generated build directory
```

### 🪟 Windows

#### Chocolatey
```bash
# Install Chocolatey first, then:
choco install claude-conversation-extractor
```

#### Scoop
```bash
# Install Scoop first, then:
scoop install claude-conversation-extractor
```

#### Manual Installation
```bash
# Install Python from python.org
# Then install the tool
pip install claude-conversation-extractor
```

#### Build Executable
```bash
# Use the provided build script
python scripts/build-windows.py

# Follow the instructions in the generated installer directory
```

#### PATH Configuration
1. Copy the executable to a directory (e.g., `C:\Tools\`)
2. Add that directory to your PATH environment variable
3. Restart command prompt

### 🐳 Docker

#### Pull and Run
```bash
# Pull the image
docker pull yourusername/claude-conversation-extractor

# Run the tool
docker run --rm -v $(pwd):/work yourusername/claude-conversation-extractor extract -u <uuid> -i /work/input.json
```

#### Build Locally
```bash
# Build the image
docker build -t claude-conversation-extractor .

# Run the tool
docker run --rm -v $(pwd):/work claude-conversation-extractor --help
```

## Development Installation

### Editable Install
```bash
# Clone the repository
git clone https://github.com/yourusername/claude-conversation-extractor
cd claude-conversation-extractor

# Install in editable mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### From Source
```bash
# Clone and install
git clone https://github.com/yourusername/claude-conversation-extractor
cd claude-conversation-extractor
python setup.py install
```

## Verification and Testing

### Test Commands
```bash
# Test help command
cce --help

# Test version
cce --version

# Test list command (if you have a sample file)
cce list -i sample.json
```

### Check Installation Location
```bash
# Find where the tool is installed
which cce
which claude-conversation-extractor

# Check Python package location
python -c "import claude_conversation_extractor; print(claude_conversation_extractor.__file__)"
```

## Troubleshooting

### Common Issues

#### Command Not Found
```bash
# Check if the tool is installed
pip list | grep claude-conversation-extractor

# Check PATH
echo $PATH

# Reinstall if needed
pip uninstall claude-conversation-extractor
pip install claude-conversation-extractor
```

#### Permission Errors
```bash
# Use user installation
pip install --user claude-conversation-extractor

# Or use virtual environment
python -m venv claude-env
source claude-env/bin/activate
pip install claude-conversation-extractor
```

#### Python Version Issues
```bash
# Check Python version
python --version
python3 --version

# Ensure Python 3.12+ is available
python3.12 --version
```

#### Dependency Issues
```bash
# Upgrade pip
pip install --upgrade pip

# Install with specific Python version
python3.12 -m pip install claude-conversation-extractor
```

### Platform-Specific Issues

#### macOS
- Ensure Homebrew is up to date: `brew update`
- Check Python installation: `brew list python@3.12`

#### Linux
- Install system packages: `sudo apt install python3-dev` (Ubuntu/Debian)
- Use virtual environment to avoid permission issues

#### Windows
- Ensure Python is in PATH
- Use PowerShell or Command Prompt as Administrator if needed
- Check Windows Defender isn't blocking the executable

## Uninstallation

### Remove the Tool
```bash
# Uninstall via pip
pip uninstall claude-conversation-extractor

# Or if installed via package manager
# Homebrew: brew uninstall claude-conversation-extractor
# apt: sudo apt remove claude-conversation-extractor
# dnf: sudo dnf remove claude-conversation-extractor
```

### Clean Up
```bash
# Remove configuration files (if any)
rm -rf ~/.config/claude-conversation-extractor

# Remove from PATH (edit shell profile files)
# Remove the export PATH line you added
```

## Next Steps

After successful installation:

1. **Read the Usage Guide**: See `docs/usage.md` for detailed usage examples
2. **Check Requirements**: Ensure you have the required input format
3. **Test with Sample Data**: Try the tool with a small export file first
4. **Explore Features**: Use `cce --help` to see all available options

## Support

If you encounter issues:

1. Check this troubleshooting section
2. Review the [GitHub Issues](https://github.com/yourusername/claude-conversation-extractor/issues)
3. Create a new issue with details about your system and error messages
4. Check the [Requirements](docs/requirements.md) for system compatibility
