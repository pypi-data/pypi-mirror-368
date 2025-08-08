import pytest
from unittest.mock import Mock, patch, MagicMock
from common_ai_core import CompletionChat, StreamingChat, TokenLimitedMemory, Message, Role, TokenTracker
from common_ai_core.providers import LLMProvider, ProviderType
from common_ai_core.exceptions import ProviderError, ConnectionError, ValidationError, ChatError

@pytest.fixture
def mock_streaming_provider():
    provider = Mock(spec=LLMProvider)
    provider.provider_type = ProviderType.OPENAI
    provider.model = "gpt-3.5-turbo"
    
    def create_mock_stream(*args, **kwargs):  # Acceptera alla argument
        mock_stream = MagicMock()
        mock_chunks = [
            create_mock_chunk("Hello"),
            create_mock_chunk(" world"),
            create_mock_chunk("!")
        ]
        mock_stream.__iter__.return_value = iter(mock_chunks)
        return mock_stream
    
    # Skapa ny stream för varje anrop
    provider.generate_completion.side_effect = create_mock_stream
    provider.get_message_content.side_effect = lambda chunk, stream: chunk.content if stream else chunk
    return provider

@pytest.fixture
def mock_completion_provider():
    provider = Mock(spec=LLMProvider)
    provider.provider_type = ProviderType.OPENAI
    provider.model = "gpt-3.5-turbo"
    
    mock_response = Mock()
    mock_response.content = "Hello, how can I help?"
    provider.generate_completion.return_value = mock_response
    provider.get_message_content.return_value = "Hello, how can I help?"
    return provider

def create_mock_chunk(content: str):
    chunk = Mock()
    chunk.content = content
    return chunk

@pytest.fixture
def memory(mock_completion_provider):
    return TokenLimitedMemory.from_provider(mock_completion_provider, max_tokens=1000)

def test_completion_chat(mock_completion_provider, memory):
    chat = CompletionChat(llm_provider=mock_completion_provider, memory=memory)
    response = chat.chat("Hello")
    assert response == "Hello, how can I help?"

def test_streaming_chat(mock_streaming_provider, memory):
    chat = StreamingChat(llm_provider=mock_streaming_provider, memory=memory)
    response_stream = chat.chat("Hello")
    responses = list(response_stream)
    assert responses == ["Hello", " world", "!"]

@pytest.mark.parametrize("error,expected_type,expected_message", [
    (ProviderError("API Error"), ProviderError, "API Error"),
    (ConnectionError("Timeout"), ConnectionError, "Timeout"),
    (ValidationError("Bad input"), ValidationError, "Bad input"),
    (Exception("Unknown error"), ChatError, "Unexpected error in chat: Unknown error")
])
def test_chat_error_handling(mock_completion_provider, memory, error, expected_type, expected_message):
    chat = CompletionChat(llm_provider=mock_completion_provider, memory=memory)
    mock_completion_provider.generate_completion.side_effect = error
    
    with pytest.raises(expected_type) as exc_info:
        chat.chat("Hello")
    assert str(exc_info.value) == expected_message

def test_chat_memory_integration(mock_streaming_provider, memory):
    chat = StreamingChat(llm_provider=mock_streaming_provider, memory=memory)
    
    # Första meddelandet
    responses = list(chat.chat("First message"))  # Konsumera streamen
    assert responses == ["Hello", " world", "!"]
    
    # Andra meddelandet
    responses = list(chat.chat("Second message"))  # Konsumera streamen
    assert responses == ["Hello", " world", "!"]
    
    # Verifiera historik
    history = memory.get_history()
    assert len(history) == 4  # 2 user messages + 2 assistant responses
    
    # Verifiera ordning och innehåll
    assert history[0].role == Role.USER
    assert history[0].content == "First message"
    assert history[1].role == Role.ASSISTANT
    assert history[1].content == "Hello world!"
    assert history[2].role == Role.USER
    assert history[2].content == "Second message"
    assert history[3].role == Role.ASSISTANT
    assert history[3].content == "Hello world!" 