"""Convert conversations to markdown format."""

from datetime import datetime

from .models import ChatMessage, Conversation, FileObject


class MarkdownConverter:
    """Converts Claude conversations to markdown format."""

    def __init__(self, conversation: Conversation):
        """Initialize with a conversation to convert.

        Args:
            conversation: The conversation to convert to markdown
        """
        self.conversation = conversation

    def convert(self) -> str:
        """Convert the conversation to markdown.

        Returns:
            The conversation formatted as markdown
        """
        lines = []

        # Header
        lines.append(f"# {self.conversation.name or 'Untitled Conversation'}")
        lines.append("")

        # Metadata
        lines.append("## Conversation Details")
        lines.append(f"- **UUID**: `{self.conversation.uuid}`")
        lines.append(
            f"- **Created**: {self._format_timestamp(self.conversation.created_at)}"
        )
        lines.append(
            f"- **Updated**: {self._format_timestamp(self.conversation.updated_at)}"
        )
        lines.append(f"- **Account**: `{self.conversation.account.uuid}`")
        lines.append("")

        # Messages
        if self.conversation.chat_messages:
            lines.append("## Messages")
            lines.append("")

            for i, message in enumerate(self.conversation.chat_messages, 1):
                lines.extend(self._format_message(message, i))
                lines.append("")
        else:
            lines.append("## Messages")
            lines.append("")
            lines.append("*No messages in this conversation.*")

        return "\n".join(lines)

    def _format_message(self, message: ChatMessage, message_number: int) -> list[str]:
        """Format a single message as markdown.

        Args:
            message: The message to format
            message_number: Sequential number for the message

        Returns:
            List of markdown lines for the message
        """
        lines = []

        # Message header
        sender_emoji = "👤" if message.sender == "human" else "🤖"
        sender_name = "Human" if message.sender == "human" else "Claude"

        lines.append(f"### {sender_emoji} {sender_name} - Message {message_number}")
        lines.append(f"*{self._format_timestamp(message.created_at)}*")
        lines.append("")

        # Message content
        if message.content:
            for content_item in message.content:
                if content_item.type == "text" and content_item.text:
                    # Format the text content
                    formatted_text = self._format_text_content(content_item.text)
                    lines.append(formatted_text)
                    lines.append("")

        # Attachments and files
        if message.attachments:
            lines.append("**Attachments:**")
            for attachment in message.attachments:
                lines.extend(self._format_file_object(attachment))
            lines.append("")

        if message.files:
            lines.append("**Files:**")
            for file in message.files:
                lines.extend(self._format_file_object(file))
            lines.append("")

        return lines

    def _format_file_object(self, file_obj: FileObject) -> list[str]:
        """Format a file object as markdown.

        Args:
            file_obj: The file object to format

        Returns:
            List of markdown lines for the file
        """
        lines = []

        # Basic file info
        file_info = f"- **{file_obj.file_name}**"
        if file_obj.file_size:
            file_info += f" ({file_obj.file_size} bytes)"
        if file_obj.file_type:
            file_info += f" - {file_obj.file_type}"
        lines.append(file_info)

        # File content if available
        if file_obj.extracted_content:
            lines.append("")
            lines.append("```")
            lines.append(file_obj.extracted_content)
            lines.append("```")
            lines.append("")

        return lines

    def _format_text_content(self, text: str) -> str:
        """Format text content with proper markdown.

        Args:
            text: Raw text content

        Returns:
            Formatted markdown text
        """
        # Handle code blocks (if they exist in the text)
        # This is a simple implementation - could be enhanced for more complex formatting
        return text.strip()

    def _format_timestamp(self, timestamp: datetime) -> str:
        """Format timestamp for display.

        Args:
            timestamp: The timestamp to format

        Returns:
            Formatted timestamp string
        """
        return timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")

    def save_to_file(self, output_path: str) -> None:
        """Convert and save the conversation to a markdown file.

        Args:
            output_path: Path where to save the markdown file
        """
        markdown_content = self.convert()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
