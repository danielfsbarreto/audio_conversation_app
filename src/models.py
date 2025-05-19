from typing import Any

from pydantic import BaseModel


class Message(BaseModel):
    content: str = ""
    content_base64: str
    content_bytes: Any
    role: str

    @property
    def from_assistant(self):
        return self.role == "assistant"

    @property
    def from_user(self):
        return self.role == "user"


class Conversation(BaseModel):
    id: str
    messages: list[Message] = []
