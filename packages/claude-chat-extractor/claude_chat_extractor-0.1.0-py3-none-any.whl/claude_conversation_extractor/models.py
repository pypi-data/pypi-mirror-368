"""Data models for Claude conversation extraction."""

from datetime import datetime

from pydantic import BaseModel, Field, RootModel


class Account(BaseModel):
    """Account information."""

    uuid: str


class Citation(BaseModel):
    """Citation information."""

    # Add citation fields as needed based on the actual data structure
    pass


class FileObject(BaseModel):
    """File attachment information."""

    file_name: str
    file_size: int | None = None
    file_type: str | None = None
    extracted_content: str | None = None


class Content(BaseModel):
    """Message content with timestamps."""

    start_timestamp: datetime | None = None
    stop_timestamp: datetime | None = None
    type: str
    text: str | None = None
    citations: list[Citation] = Field(default_factory=list)


class ChatMessage(BaseModel):
    """Individual chat message."""

    uuid: str
    text: str
    content: list[Content]
    sender: str  # "human" or "assistant"
    created_at: datetime
    updated_at: datetime
    attachments: list[FileObject] = Field(default_factory=list)
    files: list[FileObject] = Field(default_factory=list)


class Conversation(BaseModel):
    """Complete conversation with messages."""

    uuid: str
    name: str
    created_at: datetime
    updated_at: datetime
    account: Account
    chat_messages: list[ChatMessage] = Field(default_factory=list)


class ClaudeExport(RootModel[list[Conversation]]):
    """Root structure of Claude export file."""

    @property
    def conversations(self) -> list[Conversation]:
        """Get the list of conversations."""
        return self.root
