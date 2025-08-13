# Usage Guide

## Installation

The tool is installed as a Python package and can be used in two ways:

### As a Command-Line Tool
```bash
# Extract a conversation
claude-extract extract --uuid <uuid> --input <file.json> --output <output.md>

# List conversations
claude-extract list-conversations --input <file.json>
```

### As a Python Module
```bash
python -m claude_conversation_extractor extract --uuid <uuid> --input <file.json> --output <output.md>
```

## Commands

### Extract Command
Extract a specific conversation by UUID and convert to markdown.

**Syntax:**
```bash
claude-extract extract [OPTIONS]
```

**Options:**
- `--uuid, -u TEXT`: UUID of the conversation to extract (required)
- `--input, -i PATH`: Path to the Claude export JSON file (required)
- `--output, -o PATH`: Output markdown file path (optional, defaults to `<uuid>.md`)
- `--verbose, -v`: Enable verbose output
- `--help`: Show help message

**Examples:**
```bash
# Basic extraction
claude-extract extract -u 28d595a3-5db0-492d-a49a-af74f13de505 -i data/conversations.json

# With custom output path
claude-extract extract -u 28d595a3-5db0-492d-a49a-af74f13de505 -i data/conversations.json -o my_conversation.md

# Verbose mode
claude-extract extract -u 28d595a3-5db0-492d-a49a-af74f13de505 -i data/conversations.json -v
```

### List Command
List available conversations in an export file.

**Syntax:**
```bash
claude-extract list-conversations [OPTIONS]
```

**Options:**
- `--input, -i PATH`: Path to the Claude export JSON file (required)
- `--limit, -l INTEGER`: Maximum number of conversations to list (default: 10)
- `--help`: Show help message

**Examples:**
```bash
# List first 10 conversations
claude-extract list-conversations -i data/conversations.json

# List first 5 conversations
claude-extract list-conversations -i data/conversations.json -l 5
```

## Real-World Example

Here's an actual example using the tool with real data:

```bash
# List conversations to find one to extract
claude-extract list-conversations -i data/conversations.json -l 3

# Output:
🔍 Loading export file: data/conversations.json

📋 Found 728 conversations
Showing first 3:

1. Untitled (6c92cf7d-5739-4694-a3e1-f337497971fb)
   📅 2024-07-23 18:38:03 | 💬 0 messages

2. Strategies for Crafting Effective Prompts (28d595a3-5db0-492d-a49a-af74f13de505)
   📅 2024-07-23 09:52:56 | 💬 2 messages

3. Asynchronous ClickHouse Client Connection (4b9569b1-e31f-4f88-91ef-6a24a313527f)
   📅 2024-07-19 23:05:05 | 💬 2 messages

# Extract the "Strategies for Crafting Effective Prompts" conversation
claude-extract extract \
  -u 28d595a3-5db0-492d-a49a-af74f13de505 \
  -i data/conversations.json \
  -o strategies_for_prompts.md

# Output:
✅ Conversation extracted successfully!
📁 Output: strategies_for_prompts.md
💬 Messages: 2
```

## Input File Format

The tool expects a JSON file with Claude export data containing:
```json
[
  {
    "uuid": "conversation-uuid",
    "name": "Conversation Name",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "account": {
      "uuid": "account-uuid"
    },
    "chat_messages": [
      {
        "uuid": "message-uuid",
        "text": "Message text",
        "sender": "human|assistant",
        "created_at": "2024-01-01T00:00:00Z",
        "content": [...],
        "attachments": [],
        "files": []
      }
    ]
  }
]
```

## Output Format

The tool generates markdown files with the following structure:

```markdown
# Conversation Name

## Conversation Details
- **UUID**: `conversation-uuid`
- **Created**: 2024-01-01 00:00:00 UTC
- **Updated**: 2024-01-01 00:00:00 UTC
- **Account**: `account-uuid`

## Messages

### 👤 Human - Message 1
*2024-01-01 00:00:00 UTC*

Message text content...

### 🤖 Claude - Message 2
*2024-01-01 00:00:00 UTC*

Response content...
```

## Error Handling

The tool provides clear error messages for common issues:

- **File not found**: When the input file doesn't exist
- **Invalid JSON**: When the input file isn't valid JSON
- **Conversation not found**: When the specified UUID doesn't exist
- **Validation errors**: When the JSON structure doesn't match expectations

## Verbose Mode

Enable verbose mode with `-v` flag to see:
- File loading progress
- UUID search status
- Conversion progress
- Detailed error information

## Examples

### Extract a Specific Conversation
```bash
# Find the conversation UUID first
claude-extract list-conversations -i data/conversations.json

# Extract the conversation
claude-extract extract \
  -u 28d595a3-5db0-492d-a49a-af74f13de505 \
  -i data/conversations.json \
  -o strategies_for_prompts.md
```

### Batch Processing
```bash
# Extract multiple conversations
for uuid in uuid1 uuid2 uuid3; do
  claude-extract extract -u $uuid -i data/conversations.json
done
```

### Working with Large Files

The tool is designed to handle large export files efficiently:

```bash
# Even with 44MB+ files containing 728+ conversations
claude-extract list-conversations -i data/conversations.json -l 5

# Memory usage remains constant regardless of file size
claude-extract extract -u <uuid> -i data/conversations.json -v
```

## Performance Tips

- **Use streaming**: The tool automatically uses streaming JSON parsing for memory efficiency
- **Limit listing**: Use the `-l` flag to limit the number of conversations listed
- **Verbose mode**: Use `-v` for debugging and monitoring progress
- **Output naming**: Use descriptive output filenames for better organization

## Troubleshooting

### Common Issues

1. **File not found**: Ensure the input file path is correct and the file exists
2. **Permission denied**: Check file permissions and ensure you have read access
3. **Invalid JSON**: Verify the export file is valid JSON format
4. **Conversation not found**: Double-check the UUID spelling and case

### Getting Help

```bash
# Show general help
claude-extract --help

# Show command-specific help
claude-extract extract --help
claude-extract list-conversations --help

# Show version
claude-extract --version
```
