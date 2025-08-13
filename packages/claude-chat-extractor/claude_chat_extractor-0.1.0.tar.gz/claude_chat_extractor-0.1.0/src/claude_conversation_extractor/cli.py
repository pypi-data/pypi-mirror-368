"""Command-line interface for Claude conversation extractor."""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .extractor import ConversationExtractor
from .markdown_converter import MarkdownConverter

console = Console()


@click.group()
@click.version_option()
def cli() -> None:
    """Extract Claude conversations from JSON exports and convert to markdown."""
    pass


@cli.command()
@click.option("--uuid", "-u", required=True, help="UUID of the conversation to extract")
@click.option(
    "--input",
    "-i",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to the Claude export JSON file",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output markdown file path (default: <uuid>.md)",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def extract(uuid: str, input: Path, output: Path | None, verbose: bool) -> None:
    """Extract a conversation by UUID and convert to markdown."""
    try:
        if verbose:
            console.print(f"🔍 Loading export file: {input}")

        # Initialize extractor
        extractor = ConversationExtractor(input)

        if verbose:
            console.print(f"🎯 Searching for conversation: {uuid}")

        # Extract conversation using streaming
        conversation = extractor.extract_conversation(uuid)

        if conversation is None:
            console.print(f"❌ Conversation with UUID '{uuid}' not found", style="red")
            sys.exit(1)

        if verbose:
            console.print(f"✅ Found conversation: {conversation.name or 'Untitled'}")
            console.print("📝 Converting to markdown...")

        # Convert to markdown
        converter = MarkdownConverter(conversation)

        # Determine output path
        if output is None:
            output = Path(f"{uuid}.md")

        # Save to file
        converter.save_to_file(str(output))

        # Success message
        success_text = Text()
        success_text.append("✅ ", style="green")
        success_text.append("Conversation extracted successfully!\n")
        success_text.append(f"📁 Output: {output}\n")
        success_text.append(f"💬 Messages: {len(conversation.chat_messages)}")

        console.print(Panel(success_text, title="Success", border_style="green"))

    except FileNotFoundError as e:
        console.print(f"❌ File not found: {e}", style="red")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.option(
    "--input",
    "-i",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to the Claude export JSON file",
)
@click.option(
    "-l",
    "--limit",
    default=10,
    help="Maximum number of conversations to list (default: 10)",
)
def list_conversations(input: Path, limit: int) -> None:
    """List available conversations in the export file."""
    try:
        console.print(f"🔍 Loading export file: {input}")

        extractor = ConversationExtractor(input)

        # Get conversations using streaming
        conversations = extractor.list_conversations(limit)

        if not conversations:
            console.print("📭 No conversations found in the export file")
            return

        # Get total count for display
        total_count = extractor.get_conversation_count()
        console.print(f"\n📋 Found {total_count} conversations")
        console.print(f"Showing first {len(conversations)}:\n")

        for i, conv in enumerate(conversations, 1):
            # Create conversation info
            info = Text()
            info.append(f"{i}. ", style="bold blue")
            info.append(conv.name or "Untitled", style="bold")
            info.append(f" ({conv.uuid})", style="dim")
            info.append(f"\n   📅 {conv.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            info.append(f" | 💬 {len(conv.chat_messages)} messages")

            console.print(info)
            console.print()

        if total_count > limit:
            console.print(f"... and {total_count - limit} more conversations")

    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
