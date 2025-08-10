"""Chat system integrating the MCP Client with Language Model functionality"""

from .app.chat.chat import Chat
from .local.local_chat import open_local_chat

__all__ = ["Chat", "open_local_chat"]
