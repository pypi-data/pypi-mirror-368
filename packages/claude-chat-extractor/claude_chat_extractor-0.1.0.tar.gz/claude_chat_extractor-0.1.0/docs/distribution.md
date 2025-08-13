# Distribution Guide

This guide covers how to make `claude-conversation-extractor` available system-wide across different platforms.

## 1. PyPI Distribution (Recommended)

### Prerequisites
- Python 3.12+
- `build` package: `pip install build`
- `twine` package: `pip install twine`
- PyPI account (create at https://pypi.org)

### Build and Upload

1. **Build the package:**
   ```bash
   python -m build
   ```

2. **Upload to PyPI:**
   ```bash
   python -m twine upload dist/*
   ```

3. **Install globally:**
   ```bash
   pip install claude-conversation-extractor
   ```

### Usage after installation:
```bash
# Full command
claude-conversation-extractor extract -u <uuid> -i <input.json>

# Short aliases
claude-extract -u <uuid> -i <input.json>
cce -u <uuid> -i <input.json>
```

## 2. Homebrew (macOS)

### Create Homebrew Formula

1. **Create a formula file** `claude-conversation-extractor.rb`:
   ```ruby
   class ClaudeConversationExtractor < Formula
     desc "Extract Claude conversations to markdown"
     homepage "https://github.com/yourusername/claude-conversation-extractor"
     url "https://files.pythonhosted.org/packages/source/c/claude-conversation-extractor/claude-conversation-extractor-0.1.0.tar.gz"
     sha256 "YOUR_SHA256_HERE"
     license "MIT"
   
     depends_on "python@3.12"
   
     def install
       system "python3", "-m", "pip", "install", *std_pip_args, "."
     end
   
     test do
       system "#{bin}/cce", "--help"
     end
   end
   ```

2. **Submit to Homebrew:**
   - Fork https://github.com/Homebrew/homebrew-core
   - Add your formula
   - Submit a pull request

### Alternative: Personal Tap
```bash
# Create personal tap
brew tap yourusername/tap
# Add formula to your tap repository
```

## 3. Linux Package Managers

### Debian/Ubuntu (.deb)

1. **Install required tools:**
   ```bash
   sudo apt install python3-stdeb dh-python
   ```

2. **Build package:**
   ```bash
   python3 setup.py --command-packages=stdeb.command bdist_deb
   ```

3. **Install:**
   ```bash
   sudo dpkg -i deb_dist/python3-claude-conversation-extractor_*.deb
   ```

### RPM (Red Hat/CentOS/Fedora)

1. **Install required tools:**
   ```bash
   sudo dnf install rpm-build python3-setuptools
   ```

2. **Create spec file** and build RPM package

### Arch Linux (AUR)

Create a PKGBUILD file for the Arch User Repository.

## 4. Windows

### Chocolatey

1. **Create nuspec file** with package metadata
2. **Build and push** to Chocolatey repository

### Scoop

1. **Create manifest file** in JSON format
2. **Submit** to main bucket or create custom bucket

### MSI Installer

Use tools like `cx_Freeze` or `PyInstaller` to create Windows executables.

## 5. Docker Distribution

### Create Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install .

ENTRYPOINT ["cce"]
```

### Build and distribute
```bash
docker build -t claude-conversation-extractor .
docker run claude-conversation-extractor --help
```

## 6. Local Development Installation

### Editable install
```bash
pip install -e .
```

### From source
```bash
git clone https://github.com/yourusername/claude-conversation-extractor
cd claude-conversation-extractor
pip install .
```

## 7. CI/CD Pipeline

### GitHub Actions Example
```yaml
name: Build and Release

on:
  push:
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: |
          pip install build twine
          python -m build
          python -m twine upload --username ${{ secrets.PYPI_USERNAME }} --password ${{ secrets.PYPI_PASSWORD }} dist/*
```

## 8. Testing Distribution

### Test PyPI
```bash
# Upload to test PyPI first
python -m twine upload --repository testpypi dist/*

# Install from test PyPI
pip install --index-url https://test.pypi.org/simple/ claude-conversation-extractor
```

### Verify installation
```bash
# Check if commands are available
which cce
cce --help
```

## 9. Troubleshooting

### Common Issues

1. **Command not found**: Ensure `~/.local/bin` is in your PATH
2. **Permission errors**: Use `pip install --user` for user installation
3. **Version conflicts**: Use virtual environments for development

### PATH Configuration

Add to your shell profile (`.bashrc`, `.zshrc`, etc.):
```bash
export PATH="$HOME/.local/bin:$PATH"
```

## 10. Maintenance

### Version Management
- Use semantic versioning
- Update `pyproject.toml` version before releases
- Tag releases in git

### Dependency Updates
- Regularly update dependencies
- Test compatibility with new Python versions
- Monitor security vulnerabilities

### User Support
- Maintain documentation
- Respond to issues and PRs
- Provide migration guides for breaking changes
