#!/bin/bash
# Build Linux packages for different distributions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_error "This script is for Linux only"
    exit 1
fi

# Detect distribution
if command -v apt-get &> /dev/null; then
    DISTRO="debian"
    print_status "Detected Debian/Ubuntu distribution"
elif command -v dnf &> /dev/null; then
    DISTRO="fedora"
    print_status "Detected Fedora/RHEL distribution"
elif command -v pacman &> /dev/null; then
    DISTRO="arch"
    print_status "Detected Arch Linux distribution"
else
    print_warning "Unknown distribution, attempting generic build"
    DISTRO="generic"
fi

# Create build directory
BUILD_DIR="build-linux"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

print_status "Building Python package..."

# Build source distribution
python3 -m build --sdist

# Copy source distribution
cp dist/*.tar.gz "$BUILD_DIR/"

case $DISTRO in
    "debian")
        print_status "Building Debian package..."
        
        # Install required tools
        if ! command -v stdeb &> /dev/null; then
            print_status "Installing stdeb..."
            sudo apt-get update
            sudo apt-get install -y python3-stdeb dh-python
        fi
        
        # Build .deb package
        python3 setup.py --command-packages=stdeb.command bdist_deb
        
        # Copy .deb package
        cp deb_dist/*.deb "$BUILD_DIR/"
        print_status "Debian package built successfully"
        ;;
        
    "fedora")
        print_status "Building RPM package..."
        
        # Install required tools
        if ! command -v rpmbuild &> /dev/null; then
            print_status "Installing rpm-build..."
            sudo dnf install -y rpm-build python3-setuptools
        fi
        
        # Create RPM build directory structure
        RPM_BUILD_DIR="$HOME/rpmbuild"
        mkdir -p "$RPM_BUILD_DIR"/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
        
        # Copy source to RPM sources
        cp dist/*.tar.gz "$RPM_BUILD_DIR/SOURCES/"
        
        # Create spec file
        cat > "$RPM_BUILD_DIR/SPECS/claude-conversation-extractor.spec" << 'EOF'
Name:           claude-conversation-extractor
Version:        0.1.0
Release:        1%{?dist}
Summary:        Extract Claude conversations to markdown format

License:        MIT
URL:            https://github.com/yourusername/claude-conversation-extractor
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

Requires:       python3 >= 3.12
Requires:       python3dist(click) >= 8.2.1
Requires:       python3dist(ijson) >= 3.4.0
Requires:       python3dist(pydantic) >= 2.11.7
Requires:       python3dist(rich) >= 14.1.0

%description
A command-line tool to extract and convert Claude conversations to markdown format efficiently.

%prep
%autosetup

%build
%py3_build

%install
%py3_install

%files
%license LICENSE
%doc README.md
%{python3_sitelib}/%{name}
%{python3_sitelib}/%{name}-%{version}*
%{_bindir}/claude-conversation-extractor
%{_bindir}/claude-extract
%{_bindir}/cce

%changelog
* $(date '+%a %b %d %Y') Your Name <your.email@example.com> - 0.1.0-1
- Initial package release
EOF
        
        # Build RPM
        rpmbuild -ba "$RPM_BUILD_DIR/SPECS/claude-conversation-extractor.spec"
        
        # Copy RPM packages
        cp "$RPM_BUILD_DIR"/RPMS/*/*.rpm "$BUILD_DIR/"
        cp "$RPM_BUILD_DIR"/SRPMS/*.rpm "$BUILD_DIR/"
        print_status "RPM package built successfully"
        ;;
        
    "arch")
        print_status "Building Arch package..."
        
        # Create PKGBUILD
        cat > "$BUILD_DIR/PKGBUILD" << 'EOF'
# Maintainer: Your Name <your.email@example.com>
pkgname=claude-conversation-extractor
pkgver=0.1.0
pkgrel=1
pkgdesc="Extract Claude conversations to markdown format efficiently"
arch=('any')
url="https://github.com/yourusername/claude-conversation-extractor"
license=('MIT')
depends=('python' 'python-click' 'python-ijson' 'python-pydantic' 'python-rich')
makedepends=('python-build' 'python-installer')
source=("$pkgname-$pkgver.tar.gz")
sha256sums=('SKIP')

build() {
  cd "$srcdir/$pkgname-$pkgver"
  python -m build --wheel --no-isolation
}

package() {
  cd "$srcdir/$pkgname-$pkgver"
  python -m installer --destdir="$pkgdir" dist/*.whl
}
EOF
        
        # Copy source to build directory
        cp dist/*.tar.gz "$BUILD_DIR/"
        print_status "Arch package files created"
        ;;
        
    *)
        print_warning "Generic build - creating install script"
        
        # Create generic install script
        cat > "$BUILD_DIR/install.sh" << 'EOF'
#!/bin/bash
# Generic Linux installation script

set -e

echo "Installing Claude Conversation Extractor..."

# Check Python version
python3 --version

# Install dependencies
pip3 install --user click ijson pydantic rich

# Install the package
pip3 install --user .

echo "Installation complete!"
echo "Add ~/.local/bin to your PATH if not already there:"
echo "export PATH=\"\$HOME/.local/bin:\$PATH\""
echo ""
echo "Usage: claude-conversation-extractor --help"
EOF
        
        chmod +x "$BUILD_DIR/install.sh"
        ;;
esac

# Create README for the build
cat > "$BUILD_DIR/README.md" << 'EOF'
# Linux Package Installation

## Available Packages

This directory contains packages for different Linux distributions:

### Debian/Ubuntu (.deb)
- Install with: `sudo dpkg -i *.deb`
- If dependencies are missing: `sudo apt-get install -f`

### Fedora/RHEL (.rpm)
- Install with: `sudo dnf install *.rpm` or `sudo rpm -i *.rpm`

### Arch Linux
- Use the PKGBUILD file: `makepkg -si`

### Generic
- Run the install script: `./install.sh`

## System-wide Installation

After installing the package, the following commands will be available:
- `claude-conversation-extractor` (full command)
- `claude-extract` (short alias)
- `cce` (shortest alias)

## Usage Examples

```bash
# Extract a conversation
cce extract -u <uuid> -i <input.json>

# List conversations
cce list -i <input.json>

# Get help
cce --help
```

## Troubleshooting

- If commands are not found, ensure the package installed correctly
- Check that the binary directory is in your PATH
- Verify Python dependencies are installed
EOF

print_status "Linux packages built successfully!"
print_status "Build directory: $BUILD_DIR"
print_status "Read $BUILD_DIR/README.md for installation instructions"

# List built packages
echo ""
print_status "Built packages:"
ls -la "$BUILD_DIR/"
