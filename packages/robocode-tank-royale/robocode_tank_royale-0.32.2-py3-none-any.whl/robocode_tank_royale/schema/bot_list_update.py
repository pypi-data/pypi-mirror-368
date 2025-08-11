"""
Generated Python class from bot-list-update.schema.yaml
This file is auto-generated. Do not edit manually.
"""

from .message import Message
from .bot_info import BotInfo

class BotListUpdate(Message):
    """Bot list update"""

    def __init__(self, bots: list[BotInfo | None] | None, type: 'Message.Type | None'):
        if bots is None:
            raise ValueError("The 'bots' parameter must be provided.")
        if type is None:
            raise ValueError("The 'type' parameter must be provided.")
        super().__init__(type)
        self.bots = bots
