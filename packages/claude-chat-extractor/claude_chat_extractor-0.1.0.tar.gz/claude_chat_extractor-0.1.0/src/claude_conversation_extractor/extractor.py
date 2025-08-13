"""Core conversation extraction logic."""

from collections.abc import Iterator
from pathlib import Path

import ijson

from .models import Conversation


class ConversationExtractor:
    """Extracts conversations from Claude export files using streaming JSON parsing."""

    def __init__(self, export_file_path: str | Path):
        """Initialize with path to Claude export file.

        Args:
            export_file_path: Path to the JSON export file
        """
        self.export_file_path = Path(export_file_path)

    def stream_conversations(self) -> Iterator[Conversation]:
        """Stream conversations from the export file without loading everything into memory.

        Yields:
            Conversation objects one at a time

        Raises:
            FileNotFoundError: If export file doesn't exist
            ijson.JSONError: If file is not valid JSON
        """
        if not self.export_file_path.exists():
            raise FileNotFoundError(f"Export file not found: {self.export_file_path}")

        with open(self.export_file_path, "rb") as f:
            # Parse conversations array items directly
            conversations = ijson.items(f, "item")

            for conversation_data in conversations:
                try:
                    # Create Conversation object and yield it
                    conversation = Conversation.model_validate(conversation_data)
                    yield conversation
                except Exception as e:
                    # Log validation errors but continue processing
                    print(f"Warning: Skipping invalid conversation: {e}")
                    continue

    def find_conversation(self, uuid: str) -> Conversation | None:
        """Find a conversation by its UUID using streaming.

        Args:
            uuid: The conversation UUID to search for

        Returns:
            The conversation if found, None otherwise
        """
        for conversation in self.stream_conversations():
            if conversation.uuid == uuid:
                return conversation

        return None

    def extract_conversation(self, uuid: str) -> Conversation | None:
        """Extract conversation by UUID using streaming.

        Args:
            uuid: The conversation UUID to extract

        Returns:
            The conversation if found, None otherwise
        """
        return self.find_conversation(uuid)

    def get_conversation_count(self) -> int:
        """Get the total number of conversations in the export file.

        Returns:
            Number of conversations
        """
        count = 0
        for _ in self.stream_conversations():
            count += 1
        return count

    def list_conversations(self, limit: int = 10) -> list[Conversation]:
        """List conversations up to a limit using streaming.

        Args:
            limit: Maximum number of conversations to return

        Returns:
            List of conversations
        """
        conversations = []
        for conversation in self.stream_conversations():
            conversations.append(conversation)
            if len(conversations) >= limit:
                break
        return conversations
