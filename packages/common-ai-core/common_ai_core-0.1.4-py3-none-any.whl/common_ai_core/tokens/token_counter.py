from abc import ABC, abstractmethod
import logging
from typing import Optional, List, Dict
from ..types import Message
from ..providers import LLMProvider, ProviderType

class TokenCounter(ABC):
    """Bas-klass för att räkna tokens i meddelandehistorik och/eller text"""
    
    def __init__(self, model_name: Optional[str] = None, verbose: bool = False):
        self.model_name = model_name
        self.verbose = verbose
        self.logger = logging.getLogger(f'common_ai_core.{self.__class__.__name__}')
        if verbose:
            self.logger.setLevel(logging.DEBUG)

    @abstractmethod
    def count_tokens_in_text(self, text: str) -> int:
        """Räkna antal tokens i given text"""
        pass

    @abstractmethod
    def count_tokens_in_messages(self, messages: List[Message]) -> int:
        """Räkna tokens för hela meddelandestrukturen"""
        pass

    def _fallback_count_tokens_in_text(self, text: str) -> int:
        """Enkel fallback-estimering av tokens baserat på ord/tecken"""
        if text is None:
            return 0
        return len(text.split()) + len([c for c in text if c in '.,!?;:'])

class OpenAITokenCounter(TokenCounter):
    """Token counter som använder tiktoken för OpenAI modeller"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", verbose: bool = False):
        super().__init__(model_name, verbose)
        try:
            import tiktoken
            self.tokenizer = tiktoken.encoding_for_model(model_name)
            if verbose:
                self.logger.debug(f"Using tiktoken for model: {model_name}")
        except ImportError:
            if verbose:
                self.logger.warning("tiktoken not installed, using fallback counter")
            self.tokenizer = None

    def count_tokens_in_text(self, text: str) -> int:
        if text is None:
            if self.verbose:
                self.logger.debug("Received None text, returning 0 tokens")
            return 0
        
        try:
            tokens = len(self.tokenizer.encode(text))
            if self.verbose:
                self.logger.debug(f"Counted {tokens} tokens for text: {text[:50]}...")
            return tokens
        except Exception as e:
            if self.verbose:
                self.logger.debug(f"Error counting tokens: {e}, using fallback")
            return self._fallback_count_tokens_in_text(text)

    def count_tokens_in_messages(self, messages: List[Message]) -> int:
        try:
            if not self.tokenizer:
                return self._fallback_count_tokens_in_text(Message.message_list_to_text(messages))
            
            # Konvertera till dict-format precis innan tokenizer-anrop
            messages_dict = Message.message_list_to_dict_list(messages)
            
            num_tokens = 0
            for message in messages_dict:
                num_tokens += 4
                for key, value in message.items():
                    num_tokens += len(self.tokenizer.encode(value))
                    if key == "name":
                        num_tokens += -1
            num_tokens += 2
            return num_tokens
        except Exception as e:
            if self.verbose:
                self.logger.warning(f"Error in token counting: {e}")
            return self._fallback_count_tokens_in_text(Message.message_list_to_text(messages))

class AnthropicTokenCounter(TokenCounter):
    """Token counter för Anthropic modeller"""
    
    def count_tokens_in_text(self, text: str) -> int:
        # TODO: Implementera Anthropic's tokenizer när det blir tillgängligt
        return self._fallback_count_tokens_in_text(text)

    def count_tokens_in_messages(self, messages: List[Message]) -> int:
        return self._fallback_count_tokens_in_text(Message.message_list_to_text(messages))

class LlamaTokenCounter(TokenCounter):
    """Token counter för Llama modeller"""
    
    def __init__(self, model_path: Optional[str] = None, verbose: bool = False):
        super().__init__(verbose=verbose)
        try:
            from llama_cpp import Llama
            self.tokenizer = Llama(model_path=model_path) if model_path else None
            if verbose and model_path:
                self.logger.debug(f"Using Llama tokenizer with model: {model_path}")
        except ImportError:
            if verbose:
                self.logger.warning("llama-cpp not installed, using fallback counter")
            self.tokenizer = None

    def count_tokens_in_text(self, text: str) -> int:
        if self.tokenizer:
            return len(self.tokenizer.tokenize(text))
        return self._fallback_count_tokens_in_text(text)

    def count_tokens_in_messages(self, messages: List[Message]) -> int:
        return self.count_tokens_in_text(Message.message_list_to_text(messages))

class FallbackTokenCounter(TokenCounter):
    def __init__(self, verbose: bool = False):
        super().__init__(verbose=verbose)

    def count_tokens_in_text(self, text: str) -> int:
        return self._fallback_count_tokens_in_text(text)

    def count_tokens_in_messages(self, messages: List[Message]) -> int:
        return self.count_tokens_in_text(Message.message_list_to_text(messages)) 


class TokenCounterFactory:
    @staticmethod
    def from_provider(provider: LLMProvider, verbose: bool = False) -> TokenCounter:
        """Skapa TokenCounter med rätt implementationer för given provider"""
        
        if provider.provider_type == ProviderType.OPENAI:
            return OpenAITokenCounter(model_name=provider.model, verbose=verbose)
        elif provider.provider_type == ProviderType.ANTHROPIC:
            return AnthropicTokenCounter(verbose=verbose)
        elif provider.provider_type == ProviderType.LLAMA:
            return LlamaTokenCounter(verbose=verbose)
        else:
            return FallbackTokenCounter(verbose=verbose)
            