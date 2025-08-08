import pytest
from unittest.mock import Mock, patch
from common_ai_core.providers import (
    OpenAIProvider, 
    AnthropicProvider, 
    LlamaProvider,
    ProviderError
)
from common_ai_core.types import Message, Role

def test_openai_provider_initialization():
    with patch('openai.OpenAI') as mock_openai:
        provider = OpenAIProvider(api_key="test-key")
        assert provider.model == "gpt-4o-mini"

def test_anthropic_provider_initialization():
    # Test that AnthropicProvider raises ProviderError when anthropic is not installed
    try:
        import anthropic
        # If anthropic is available, skip this test
        pytest.skip("anthropic is installed, cannot test ImportError handling")
    except ImportError:
        # If anthropic is not available, test that the provider handles it gracefully
        with pytest.raises(ProviderError) as exc_info:
            provider = AnthropicProvider(api_key="test-key")
        assert "Anthropic package not installed" in str(exc_info.value)

def test_openai_response_parsing():
    with patch('openai.OpenAI') as mock_openai:
        provider = OpenAIProvider(api_key="test-key")
        mock_response = Mock()
        mock_choice = Mock()
        mock_choice.message.content = "Test response"
        mock_response.choices = [mock_choice]
        
        result = provider.get_message_content(mock_response, stream=False)
        assert result == "Test response"

@pytest.fixture
def message_list():
    return [
        Message(Role.USER, "Hello"),
        Message(Role.ASSISTANT, "Hi there")
    ]

def test_provider_message_handling(message_list):
    class MockCompletions:
        def create(self, messages, model=None, stream=False, **kwargs):
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_choice = mock_response.choices[0]
            mock_choice.message = Mock()
            mock_choice.message.content = "Test response"
            return mock_response

    class MockChat:
        def __init__(self):
            self.completions = MockCompletions()

    class MockOpenAI:
        def __init__(self, api_key=None):
            self.chat = MockChat()

    with patch('openai.OpenAI', return_value=MockOpenAI()):
        provider = OpenAIProvider(api_key="test-key")
        response = provider.generate_completion(message_list, stream=False)
        assert response.choices[0].message.content == "Test response"

def test_llama_provider():
    # Skip this test if llama_cpp is not installed
    try:
        from llama_cpp import Llama
    except ImportError:
        pytest.skip("llama_cpp not installed")
    
    # Mock the Llama class to raise an error during initialization
    with patch('llama_cpp.Llama', side_effect=ValueError("Model not found")):
        with pytest.raises(ProviderError) as exc_info:
            LlamaProvider(model_path="nonexistent_path")
        assert "Model not found" in str(exc_info.value) 