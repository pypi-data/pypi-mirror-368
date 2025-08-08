class CommonAICoreError(Exception):
    """Base exception for all common-ai-core errors"""
    pass


class LLMError(CommonAICoreError):
    """Base exception for LLM-related errors"""
    pass


class ProviderError(LLMError):
    """Exception raised when there's an error with a specific provider"""
    pass


class ConnectionError(LLMError):
    """Exception raised when there's a connection error"""
    pass


class ValidationError(CommonAICoreError):
    """Exception raised when there's a validation error"""
    pass


class ChatError(CommonAICoreError):
    """Exception raised when there's an error in chat functionality"""
    pass


class MemoryError(CommonAICoreError):
    """Exception raised when there's an error with memory management"""
    pass


class TokenLimitError(CommonAICoreError):
    """Exception raised when token limits are exceeded"""
    pass 