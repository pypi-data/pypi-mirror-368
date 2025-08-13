"""Tests for the conversation extractor."""

from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from claude_conversation_extractor.extractor import ConversationExtractor


class TestConversationExtractor:
    """Test cases for ConversationExtractor."""

    def test_init(self) -> None:
        """Test extractor initialization."""
        extractor = ConversationExtractor("test.json")
        assert extractor.export_file_path == Path("test.json")

    @patch("pathlib.Path.exists")
    def test_stream_conversations_file_not_found(self, mock_exists: Mock) -> None:
        """Test streaming from non-existent export file."""
        mock_exists.return_value = False

        extractor = ConversationExtractor("nonexistent.json")

        with pytest.raises(FileNotFoundError):
            list(extractor.stream_conversations())

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("ijson.items")
    def test_stream_conversations_success(
        self, mock_ijson_items: Mock, mock_file: Mock, mock_exists: Mock
    ) -> None:
        """Test successful conversation streaming."""
        mock_exists.return_value = True

        # Mock conversation data
        mock_conversation_data = {
            "uuid": "test-uuid",
            "name": "Test Conversation",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "account": {"uuid": "account-uuid"},
            "chat_messages": [],
        }

        # Mock ijson.items to return the conversation data
        mock_ijson_items.return_value = [mock_conversation_data]

        extractor = ConversationExtractor("test.json")
        conversations = list(extractor.stream_conversations())

        assert len(conversations) == 1
        assert conversations[0].uuid == "test-uuid"
        assert conversations[0].name == "Test Conversation"

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("ijson.items")
    def test_find_conversation_not_found(
        self, mock_ijson_items: Mock, mock_file: Mock, mock_exists: Mock
    ) -> None:
        """Test finding non-existent conversation."""
        mock_exists.return_value = True

        # Mock ijson.items to return empty list
        mock_ijson_items.return_value = []

        extractor = ConversationExtractor("test.json")
        result = extractor.find_conversation("test-uuid")
        assert result is None

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("ijson.items")
    def test_find_conversation_found(
        self, mock_ijson_items: Mock, mock_file: Mock, mock_exists: Mock
    ) -> None:
        """Test finding existing conversation."""
        mock_exists.return_value = True

        # Mock conversation data
        mock_conversation_data = {
            "uuid": "test-uuid",
            "name": "Test Conversation",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "account": {"uuid": "account-uuid"},
            "chat_messages": [],
        }

        # Mock ijson.items to return the conversation data
        mock_ijson_items.return_value = [mock_conversation_data]

        extractor = ConversationExtractor("test.json")
        result = extractor.find_conversation("test-uuid")

        assert result is not None
        assert result.uuid == "test-uuid"
        assert result.name == "Test Conversation"

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("ijson.items")
    def test_get_conversation_count(
        self, mock_ijson_items: Mock, mock_file: Mock, mock_exists: Mock
    ) -> None:
        """Test getting conversation count."""
        mock_exists.return_value = True

        # Mock ijson.items to return 3 conversations
        mock_conversation_data = [
            {
                "uuid": "uuid1",
                "name": "Conv1",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "account": {"uuid": "acc1"},
                "chat_messages": [],
            },
            {
                "uuid": "uuid2",
                "name": "Conv2",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "account": {"uuid": "acc2"},
                "chat_messages": [],
            },
            {
                "uuid": "uuid3",
                "name": "Conv3",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "account": {"uuid": "acc3"},
                "chat_messages": [],
            },
        ]
        mock_ijson_items.return_value = mock_conversation_data

        extractor = ConversationExtractor("test.json")
        count = extractor.get_conversation_count()
        assert count == 3

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("ijson.items")
    def test_list_conversations_with_limit(
        self, mock_ijson_items: Mock, mock_file: Mock, mock_exists: Mock
    ) -> None:
        """Test listing conversations with limit."""
        mock_exists.return_value = True

        # Mock ijson.items to return 5 conversations
        mock_conversation_data = [
            {
                "uuid": f"uuid{i}",
                "name": f"Conv{i}",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "account": {"uuid": f"acc{i}"},
                "chat_messages": [],
            }
            for i in range(1, 6)
        ]
        mock_ijson_items.return_value = mock_conversation_data

        extractor = ConversationExtractor("test.json")
        conversations = extractor.list_conversations(limit=3)

        assert len(conversations) == 3
        assert conversations[0].uuid == "uuid1"
        assert conversations[1].uuid == "uuid2"
        assert conversations[2].uuid == "uuid3"
