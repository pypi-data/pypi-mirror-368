from abc import ABC, abstractmethod
import logging
from typing import List, Optional, Tuple
from .types import Message, Role
from common_ai_core.providers import LLMProvider, ProviderType
from common_ai_core.tokens.token_counter import TokenCounterFactory
from common_ai_core.exceptions import ValidationError

logger = logging.getLogger('common_ai_core')

class MemoryBase(ABC):
    """Base class for memory implementations.
    
    This abstract class defines the interface for all memory implementations
    and provides common functionality for storing and managing chat history.
    
    Attributes:
        history: List of stored messages
    """
    
    def __init__(self) -> None:
        self.history: List[Message] = []
    
    @abstractmethod
    def add(self, message: Message) -> None:
        """Add a message to memory."""
        pass

    def get_history(self) -> List[Message]:
        """Get all messages in memory."""
        return self.history
    
    @abstractmethod
    def get_memory_usage_str(self) -> str:
        """Get a string describing current memory usage."""
        pass

    def pretty_print(self, user_color: str = '\033[94m', assistant_color: str = '\033[92m', 
                    system_color: str = '\033[93m', reset_color: str = '\033[0m', width: int = 80) -> None:
        """
        Print chat history with colors.
        
        Args:
            user_color: ANSI color for user messages
            assistant_color: ANSI color for assistant messages
            system_color: ANSI color for system messages
            reset_color: ANSI code to reset color
            width: Maximum width of output
        """
        print("\nChat History:")
        print("=" * width)
        
        for msg in self.history:
            content = msg.content
            if msg.role == Role.SYSTEM:
                formatted = f"{system_color}System: {content}{reset_color}"
                padding = (width - len(formatted)) // 2
                print(" " * padding + formatted)
            elif msg.role == Role.USER:
                formatted = f"{user_color}User: {content}{reset_color}"
                print(formatted.rjust(width))
            else:
                formatted = f"{assistant_color}Assistant: {content}{reset_color}"
                print(formatted.ljust(width))
            print("-" * width)
        
        print(f"\n{self.get_memory_usage_str()}")

class TokenLimitedMemory(MemoryBase):
    """Memory implementation that limits total tokens across all stored messages.
    
    This memory type uses a token counter to track token usage and removes oldest
    messages when the token limit is exceeded.
    
    Attributes:
        max_tokens: Maximum number of tokens to store
        verbose: Enable verbose logging
        token_counter: Counter for tracking token usage
    """
    
    @classmethod
    def from_provider(cls, provider: LLMProvider, max_tokens: int, verbose: bool = False) -> 'TokenLimitedMemory':
        """Create memory instance from provider."""
        if max_tokens <= 0:
            raise ValidationError("max_tokens must be positive")
            
        memory = cls(max_tokens=max_tokens, verbose=verbose)
        memory.token_counter = TokenCounterFactory.from_provider(provider, verbose=verbose)
        return memory

    def __init__(self, max_tokens: int, verbose: bool = False) -> None:
        if max_tokens <= 0:
            raise ValidationError("max_tokens must be positive")
            
        super().__init__()
        self.verbose = verbose
        self.logger = logging.getLogger(f'common_ai_core.{self.__class__.__name__}')
        if verbose:
            self.logger.setLevel(logging.DEBUG)
        self.max_tokens = max_tokens
        self.token_counter = None  # Set by from_provider
    
    def add(self, message: Message) -> None:
        """Add message and trim history if needed."""
        if message.role not in [Role.USER, Role.ASSISTANT, Role.SYSTEM]:
            raise ValidationError(f"Invalid role: {message.role}")
        if message.content is None:
            raise ValidationError("Content cannot be None")
            
        self.history.append(message)
        if self.verbose:
            self.logger.debug(f"Added {message.role}-message - Memory total tokens now: {self.get_memory_usage_str()}")
        self._trim_history()
    
    def _trim_history(self) -> None:
        """Remove oldest messages until under token limit."""
        if not self.token_counter:
            return
            
        while self.history:
            total_tokens = self.token_counter.count_tokens_in_messages(self.history)
            if total_tokens <= self.max_tokens:
                break
                
            removed = self.history.pop(0)
            if self.verbose:
                self.logger.debug(f"Removed {removed.role}-message to stay under token limit")
    
    def get_memory_usage_str(self) -> str:
        """Get current token usage information."""
        if not self.token_counter:
            return f"Memory contains {len(self.history)} messages (token counting not available)"
            
        total_tokens = self.token_counter.count_tokens_in_messages(self.history)
        return f"Memory contains {len(self.history)} messages ({total_tokens}/{self.max_tokens} tokens)"

class SystemTokenLimitedMemory(TokenLimitedMemory):
    """TokenLimitedMemory som behåller en system prompt"""
    
    @classmethod
    def from_provider(cls, provider: LLMProvider, system_prompt: str, max_tokens: int, 
                     min_conversation_tokens: int = 100, verbose: bool = False) -> 'MemoryBase':
        """Create appropriate memory implementation based on provider type"""
        if provider.provider_type == ProviderType.GEMINI:
            # For Gemini, create a special memory that prepends system prompt to first user message
            memory = TokenLimitedMemory.from_provider(provider, max_tokens=max_tokens, verbose=verbose)
            memory.system_prompt = system_prompt
            
            # Store the original add method
            original_add = memory.add
            
            # Define a new method that correctly handles self
            def add_with_system_prompt(self, message: Message) -> None:
                if message.role == Role.USER and not any(m.role == Role.USER for m in self.history):
                    # This is the first user message, prepend system prompt
                    combined_content = f"{self.system_prompt}\n\n{message.content}"
                    modified_message = Message(Role.USER, combined_content)
                    original_add(modified_message)
                else:
                    original_add(message)
            
            # Replace the add method with our new one
            import types
            memory.add = types.MethodType(add_with_system_prompt, memory)
            
            return memory
        else:
            # For other providers, create a new instance and initialize it properly
            memory = cls(max_tokens=max_tokens, verbose=verbose)
            memory.token_counter = TokenCounterFactory.from_provider(provider, verbose=verbose)
            
            # Validate system prompt size
            system_message = Message(Role.SYSTEM, system_prompt)
            system_tokens = memory.token_counter.count_tokens_in_messages([system_message])
            remaining_tokens = max_tokens - system_tokens
            
            if remaining_tokens < min_conversation_tokens:
                raise ValidationError(
                    f"System prompt uses {system_tokens} of {max_tokens} tokens. "
                    f"Need at least {min_conversation_tokens} tokens for conversation"
                )
                
            if verbose:
                memory.logger.debug(
                    f"System prompt uses {system_tokens} tokens. "
                    f"{remaining_tokens} tokens available for conversation"
                )
                
            memory.system_message = system_message
            memory.add(system_message)
            return memory

class PromptLimitedMemory(MemoryBase):
    """Memory implementation that limits number of prompt-response pairs.
    
    This memory type keeps a fixed number of the most recent interactions,
    where each interaction consists of a user prompt and an assistant response.
    
    Attributes:
        max_prompts: Maximum number of prompt-response pairs to store
    """
    
    def __init__(self, max_prompts: int) -> None:
        if max_prompts <= 0:
            raise ValidationError("max_prompts must be positive")
            
        super().__init__()
        self.max_prompts = max_prompts
    
    def add(self, message: Message) -> None:
        """Add message and trim history if needed."""
        if message.role not in [Role.USER, Role.ASSISTANT, Role.SYSTEM]:
            raise ValidationError(f"Invalid role: {message.role}")
        if message.content is None:
            raise ValidationError("Content cannot be None")
            
        self.history.append(message)
        self._trim_history()
    
    def _trim_history(self) -> None:
        """Remove oldest messages if over prompt limit."""
        if len(self.history) > self.max_prompts * 2:
            self.history = self.history[-self.max_prompts * 2:]

    def get_memory_usage_str(self) -> str:
        """Get current prompt usage information."""
        current_prompts = len(self.history) // 2
        return f"Memory Usage: {current_prompts}/{self.max_prompts} prompts"

class SystemPromptLimitedMemory(PromptLimitedMemory):
    """PromptLimitedMemory som behåller en system prompt"""
    
    @classmethod
    def from_provider(cls, provider: LLMProvider, system_prompt: str, max_prompts: int, verbose: bool = False) -> 'MemoryBase':
        """Create appropriate memory implementation based on provider type"""
        if provider.provider_type == ProviderType.GEMINI:
            # For Gemini, create a special memory that prepends system prompt to first user message
            memory = PromptLimitedMemory(max_prompts=max_prompts)
            memory.system_prompt = system_prompt
            memory.verbose = verbose
            memory.logger = logging.getLogger(f'common_ai_core.GeminiSystemPromptMemory')
            if verbose:
                memory.logger.setLevel(logging.DEBUG)
                
            # Override add method for this instance
            original_add = memory.add
            def add_with_system_prompt(message: Message) -> None:
                if message.role == Role.USER and not any(m.role == Role.USER for m in memory.history):
                    # This is the first user message, prepend system prompt
                    combined_content = f"{system_prompt}\n\n{message.content}"
                    modified_message = Message(Role.USER, combined_content)
                    original_add(modified_message)
                else:
                    original_add(message)
            
            memory.add = add_with_system_prompt.__get__(memory)
            return memory
        else:
            # For other providers, create a new instance directly
            memory = cls(system_prompt=system_prompt, max_prompts=max_prompts, verbose=verbose)
            return memory

    def __init__(self, system_prompt: str, max_prompts: int, verbose: bool = False):
        super().__init__(max_prompts)
        self.verbose = verbose
        self.logger = logging.getLogger(f'common_ai_core.{self.__class__.__name__}')
        if verbose:
            self.logger.setLevel(logging.DEBUG)
            
        # Spara och lägg till system prompt
        self.system_message = Message(Role.SYSTEM, system_prompt)
        self.add(self.system_message)
    
    def add(self, message: Message) -> None:
        """Add message and trim history if needed."""
        if message.role not in [Role.USER, Role.ASSISTANT, Role.SYSTEM]:
            raise ValidationError(f"Invalid role: {message.role}")
        if message.content is None:
            raise ValidationError("Content cannot be None")
            
        self.history.append(message)
        self._trim_history()
    
    def _trim_history(self):
        """Trimma historik men behåll system prompt"""
        super()._trim_history()  # Låt parent göra sin trimning
        
        # Kolla om system prompt finns kvar
        if not self.history or self.history[0].role != Role.SYSTEM:
            self.history.insert(0, self.system_message) 