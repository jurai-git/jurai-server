

# Data format:
"""
{
    "contents": [
        {
            "role": "user",
            "parts": [{"text": "user_query"}]
        },
        {
            "role": "user",
            "parts": [{"text": "raw_rag_data"}]
        },
        {
            "role": "model",
            "parts": [{"text": "model_answer"}]
        }
    ]
}
This
"""
from enum import Enum


class RoleEnum(str, Enum):
    USER = "user"
    MODEL = "model"

class MessageType(str, Enum):
    DEFAULT = "default"
    RAG = "rag"

from typing import TypedDict, Literal, List

class GeminiPart(TypedDict):
    text: str

class GeminiMessage(TypedDict):
    role: RoleEnum
    parts: List[GeminiPart]


