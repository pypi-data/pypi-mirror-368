import pytest
from unittest.mock import Mock, MagicMock
from common_ai_core.tokens.token_counter import (
    TokenCounter, 
    OpenAITokenCounter,
    FallbackTokenCounter,
    TokenCounterFactory,
    LlamaTokenCounter
)
from common_ai_core.types import Message, Role
from common_ai_core.providers import LLMProvider, ProviderType

@pytest.fixture
def mock_provider():
    provider = Mock(spec=LLMProvider)
    provider.provider_type = ProviderType.OPENAI
    provider.model = "gpt-3.5-turbo"
    return provider

@pytest.fixture
def openai_counter():
    return OpenAITokenCounter(model_name="gpt-3.5-turbo", verbose=True)

@pytest.fixture
def fallback_counter():
    return FallbackTokenCounter(verbose=True)

def test_openai_counter_text(openai_counter):
    text = "Hello world!"
    tokens = openai_counter.count_tokens_in_text(text)
    assert tokens > 0

def test_openai_counter_messages(openai_counter):
    messages = [
        Message(Role.USER, "Hello"),
        Message(Role.ASSISTANT, "Hi there!")
    ]
    tokens = openai_counter.count_tokens_in_messages(messages)
    assert tokens > 0

def test_fallback_counter_text(fallback_counter):
    text = "Hello world!"
    tokens = fallback_counter.count_tokens_in_text(text)
    assert tokens == 3  # "Hello" + "world" + ""

def test_fallback_counter_messages(fallback_counter):
    messages = [
        Message(Role.USER, "Hello"),
        Message(Role.ASSISTANT, "Hi there!")
    ]
    tokens = fallback_counter.count_tokens_in_messages(messages)
    assert tokens == 10  

def test_factory_openai(mock_provider):
    counter = TokenCounterFactory.from_provider(mock_provider)
    assert isinstance(counter, OpenAITokenCounter)

def test_factory_fallback():
    provider = Mock(spec=LLMProvider)
    provider.provider_type = ProviderType.LLAMA
    counter = TokenCounterFactory.from_provider(provider)
    assert isinstance(counter, LlamaTokenCounter)

def test_none_text_handling(fallback_counter):
    assert fallback_counter.count_tokens_in_text(None) == 0

def test_empty_messages_handling(fallback_counter):
    assert fallback_counter.count_tokens_in_messages([]) == 0
