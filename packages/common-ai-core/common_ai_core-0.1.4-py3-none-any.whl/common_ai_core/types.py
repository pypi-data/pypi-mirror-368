from enum import Enum
from typing import Dict, List

class Role(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message:
    def __init__(self, role: Role, content: str):
        self.role = role
        self.content = content

    def to_dict(self) -> Dict[str, str]:
        """Konvertera till provider-format"""
        return {
            "role": self.role.value,
            "content": self.content
        }

    def to_text(self) -> str:
        """Konvertera till text-representation"""
        return f"{self.role}: {self.content}"

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'Message':
        """Skapa från provider-format"""
        return cls(Role(data["role"]), data["content"])

    def __str__(self):
        return f"{self.role}: {self.content}"

    def __repr__(self):
        return f"Message(role={self.role}, content='{self.content}')"

    @staticmethod
    def message_list_to_text(messages: List['Message']) -> str:
        """Konvertera en lista av meddelanden till text"""
        return "\n".join(msg.to_text() for msg in messages)

    @staticmethod
    def message_list_to_dict_list(messages: List['Message']) -> List[Dict[str, str]]:
        """Konvertera en lista av meddelanden till provider-format"""
        return [msg.to_dict() for msg in messages]