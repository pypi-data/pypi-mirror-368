# Claude Conversation Extractor

A powerful command-line tool to extract specific conversations from Claude export files and convert them to readable markdown format.

## 🚀 Status: Production Ready

This tool is **fully implemented and tested** with real Claude export data. It successfully processes large export files (tested with 728+ conversations) using memory-efficient streaming JSON parsing.

## Features

- 🎯 **UUID-based Extraction**: Find and extract conversations by their unique identifier
- 📝 **Markdown Conversion**: Convert conversations to clean, readable markdown
- 🔍 **Conversation Discovery**: List available conversations in export files
- 🚀 **High Performance**: Efficiently handle large export files using streaming JSON parsing
- 🎨 **Rich CLI**: Beautiful terminal interface with progress indicators and emojis
- 🛡️ **Error Handling**: Graceful error handling and validation
- 💾 **Memory Efficient**: Processes large files without loading everything into memory
- 🧪 **Fully Tested**: Comprehensive test suite with 100% pass rate

## Quick Start

### Installation

#### Option 1: From PyPI (Recommended)
```bash
# Install system-wide
pip install claude-conversation-extractor

# Or install for current user only
pip install --user claude-conversation-extractor
```

#### Option 2: From Source
```bash
# Clone the repository
git clone <repository-url>
cd claude-conversation-extractor

# Install dependencies
uv sync

# Install the tool
pip install .
```

#### Option 3: Platform-Specific
- **macOS**: `pipx install claude-conversation-extractor` (recommended) or `brew install claude-conversation-extractor`
- **Linux**: Use distribution package managers or build scripts
- **Windows**: Use Chocolatey, Scoop, or build executable

📖 **See [Installation Guide](docs/installation.md) for detailed instructions**

### Basic Usage

```bash
# List available conversations (shows first 10 by default)
claude-extract list-conversations -i data/conversations.json

# Extract a specific conversation
claude-extract extract \
  -u 28d595a3-5db0-492d-a49a-af74f13de505 \
  -i data/conversations.json \
  -o my_conversation.md
```

## Available Commands

After installation, the tool is available system-wide and can be invoked using any of these names:
- `claude-extract` (recommended)
- `cce` (shortest)
- `claude-conversation-extractor` (full name)

### System-wide Availability
Once installed, you can use the tool from any directory:
```bash
# From anywhere on your system
cce --help
cce list -i /path/to/conversations.json
cce extract -u <uuid> -i /path/to/conversations.json
```

### Extract Command
Extract a conversation by UUID and convert to markdown:
```bash
claude-extract extract -u <uuid> -i <input.json> -o <output.md>
# or
cce extract -u <uuid> -i <input.json> -o <output.md>
```

**Options:**
- `-u, --uuid`: UUID of the conversation to extract (required)
- `-i, --input`: Path to the Claude export JSON file (required)
- `-o, --output`: Output markdown file path (optional, defaults to `<uuid>.md`)
- `-v, --verbose`: Enable verbose output

### List Command
List available conversations in an export file:
```bash
claude-extract list-conversations -i <input.json> -l 10
# or
cce list-conversations -i <input.json> -l 10
```

**Options:**
- `-i, --input`: Path to the Claude export JSON file (required)
- `-l, --limit`: Maximum number of conversations to list (default: 10)

## Input Format

The tool expects a JSON file with Claude export data containing:
- Conversation metadata (UUID, name, timestamps)
- Chat messages with sender information
- Content with timestamps and citations
- File attachments and references

## Output Format

Generated markdown includes:
- Conversation header with metadata
- Chronological message flow
- Clear sender identification (Human/Claude) with emojis
- Timestamps and formatting
- Attachment information

## Performance & Scalability

- **Streaming Processing**: Uses `ijson` for memory-efficient JSON parsing
- **Large File Support**: Successfully tested with 44MB+ export files
- **Fast UUID Lookup**: Efficient conversation search without loading entire file

## 📦 Distribution & Installation

### Package Managers
- **PyPI**: `pip install claude-conversation-extractor`
- **Homebrew**: `brew install claude-conversation-extractor` (macOS)
- **Chocolatey**: `choco install claude-conversation-extractor` (Windows)
- **Scoop**: `scoop install claude-conversation-extractor` (Windows)

### Build Scripts
- **Linux**: `./scripts/build-linux.sh` - Creates .deb, .rpm, and Arch packages
- **Windows**: `python scripts/build-windows.py` - Creates standalone executable

### Docker
```bash
docker run --rm -v $(pwd):/work yourusername/claude-conversation-extractor --help
```

📖 **See [Distribution Guide](docs/distribution.md) for detailed build instructions**
- **Memory Usage**: Constant memory usage regardless of file size

## Development

### Project Structure
```
claude-conversation-extractor/
├── src/claude_conversation_extractor/
│   ├── __init__.py
│   ├── models.py          # Pydantic data models
│   ├── extractor.py       # Core extraction logic with streaming
│   ├── markdown_converter.py # Markdown formatting
│   └── cli.py            # Command-line interface with Rich
├── tests/                 # Test suite (7 tests, 100% pass rate)
├── docs/                  # Documentation
└── pyproject.toml        # Project configuration with UV
```

### Running Tests
```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage (if pytest-cov is installed)
uv run pytest tests/ --cov=src/
```

### Development Setup
```bash
# Install in development mode
uv sync --dev

# Run the tool
uv run claude-extract --help
```

## Requirements

- Python 3.12+
- UV package manager
- Claude export JSON file

## Dependencies

- **Click**: Command-line interface framework
- **Pydantic**: Data validation and serialization
- **Rich**: Enhanced terminal output with colors and formatting
- **ijson**: Streaming JSON parser for memory efficiency
- **Pytest**: Testing framework
- **MyPy**: Static type checking
- **Ruff**: Fast Python linter and formatter

## Documentation

- [Requirements](docs/requirements.md) - Detailed project requirements and specifications
- [Usage Guide](docs/usage.md) - Comprehensive usage instructions and examples
- [Implementation Status](docs/implementation-status.md) - Current implementation details and technical overview

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `uv run pytest tests/ -v`
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions, please open an issue on GitHub.

## Recent Updates

- ✅ **v0.1.0**: Initial release with full functionality
- ✅ Streaming JSON processing for large files
- ✅ Complete CLI with extract and list commands
- ✅ Comprehensive test suite
- ✅ Type-safe implementation with Pydantic models
- ✅ Memory-efficient processing architecture
