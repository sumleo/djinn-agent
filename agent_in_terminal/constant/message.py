from enum import StrEnum


class Sender(StrEnum):
    USER = "user"
    AGENT = "assistant"
    TOOL = "tool"
