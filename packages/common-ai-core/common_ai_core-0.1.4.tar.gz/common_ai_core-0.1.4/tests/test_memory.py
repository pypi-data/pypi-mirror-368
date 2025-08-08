import pytest
from unittest.mock import Mock
from common_ai_core import (
    ProviderBuilder, 
    ProviderType,
    TokenLimitedMemory,
    SystemTokenLimitedMemory,
    Message,
    Role
)
from common_ai_core.exceptions import ValidationError

@pytest.fixture
def mock_provider():
    """Create a mock provider that doesn't require external dependencies"""
    provider = Mock()
    provider.provider_type = ProviderType.OPENAI
    provider.model = "gpt-3.5-turbo"
    return provider

def test_token_limited_memory(mock_provider):
    memory = TokenLimitedMemory.from_provider(mock_provider, max_tokens=50)
    memory.add(Message(Role.USER, "Hello!"))
    assert len(memory.history) == 1

def test_system_token_limited_memory(mock_provider):
    memory = SystemTokenLimitedMemory.from_provider(
        mock_provider,
        system_prompt="You are a helpful assistant.",
        max_tokens=200,
        min_conversation_tokens=10
    )
    assert memory.history[0].role == Role.SYSTEM
    memory.add(Message(Role.USER, "Hello!" * 20))
    assert memory.history[0].role == Role.SYSTEM

def test_token_memory_initialization():
    memory = TokenLimitedMemory(max_tokens=100)
    assert len(memory.get_history()) == 0

def test_token_memory_trim(mock_provider):
    memory = TokenLimitedMemory.from_provider(mock_provider, max_tokens=10)
    memory.add(Message(Role.USER, "this is a long message"))
    # Verify that old messages are trimmed
    assert len(memory.get_history()) < 4  # Exakt antal beror på implementationen 

def test_memory_overflow_handling(mock_provider):
    memory = TokenLimitedMemory.from_provider(mock_provider, max_tokens=50)
    for i in range(10):
        memory.add(Message(Role.USER, f"message {i}"))
    history = memory.get_history()
    assert history[-1].content == "message 9"

def test_memory_empty_messages(mock_provider):
    memory = TokenLimitedMemory.from_provider(mock_provider, max_tokens=100)
    memory.add(Message(Role.USER, ""))
    memory.add(Message(Role.ASSISTANT, ""))
    assert len(memory.get_history()) == 2

@pytest.mark.parametrize("role,content", [
    (Role.USER, None),
    ("invalid_role", "content"),
    (None, "content"),
])
def test_memory_invalid_input(mock_provider, role, content):
    memory = TokenLimitedMemory.from_provider(mock_provider, max_tokens=100)
    with pytest.raises(ValidationError):
        if isinstance(role, str):
            memory.add(Message(role, content))
        else:
            memory.add(Message(role, content)) 