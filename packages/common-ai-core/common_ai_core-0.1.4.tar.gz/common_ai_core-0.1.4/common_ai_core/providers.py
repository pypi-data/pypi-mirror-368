from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional, Union
import os
from enum import Enum, auto
from .types import Message, Role
import logging
from .exceptions import ProviderError, ConnectionError, ValidationError

class ProviderType(Enum):
    """Supported LLM provider types."""
    OPENAI = auto()
    ANTHROPIC = auto()
    LLAMA = auto()
    DEEPSEEK = auto()  # Add DeepSeek provider type
    GEMINI = auto()    # Add Gemini provider type

ModelResponse = Any  # TODO: Make this more specific per provider

class LLMProvider(ABC):
    """Base class for LLM providers."""
    
    def __init__(self, provider_type: ProviderType, verbose: bool = False) -> None:
        self.provider_type = provider_type
        self.verbose = verbose
        self.logger = logging.getLogger(f'common_ai_core.{self.__class__.__name__}')
        if verbose:
            self.logger.setLevel(logging.DEBUG)

    @abstractmethod
    def generate_completion(self, messages: List[Message], stream: bool = False) -> ModelResponse:
        """Generate a completion from the provider."""
        pass

    def get_message_content(self, response: ModelResponse, stream: bool = False) -> Optional[str]:
        """
        Extract message content from response.
        
        Args:
            response: Provider's response
            stream: Whether this is a streaming response
            
        Returns:
            Optional[str]: Message content or None for empty stream chunks
            
        Raises:
            ProviderError: If response format is invalid or content extraction fails
        """
        try:
            if stream:
                return self._extract_stream_content(response)
            else:
                if not self._is_valid_response(response):
                    raise ProviderError("Invalid response format")
                return self._extract_content(response)
        except Exception as e:
            raise ProviderError(f"Failed to extract content: {str(e)}") from e

    @abstractmethod
    def extract_token_counts(self, response: ModelResponse) -> Optional[Tuple[int, int]]:
        """
        Extract token counts from response.
        
        Returns:
            Optional[Tuple[int, int]]: (input_tokens, output_tokens) or None if unavailable
        """
        pass

    @abstractmethod
    def _is_valid_response(self, response: ModelResponse) -> bool:
        """Check if response has valid format."""
        pass

    @abstractmethod
    def _extract_stream_content(self, response: ModelResponse) -> Optional[str]:
        """Extract content from streaming response."""
        pass

    @abstractmethod
    def _extract_content(self, response: ModelResponse) -> str:
        """Extract content from complete response."""
        pass

    def _handle_error(self, e: Exception, context: str) -> None:
        """Base error handling for all providers."""
        if "Connection" in str(e) or "timeout" in str(e).lower():
            raise ConnectionError(f"{context}: {str(e)}") from e
        raise ProviderError(f"{context}: {str(e)}") from e

    def get_reasoning_prompt(self) -> str:
        """
        Get a provider-specific reasoning prompt.
        
        Returns:
            str: A prompt that encourages step-by-step reasoning
        """
        # Default reasoning prompt
        return (
            "Think step by step to solve this problem. First, break down the problem "
            "into parts. Then, work through each part systematically. Show your reasoning "
            "for each step. Finally, provide your answer."
        )
    
    def extract_reasoning(self, response_text: str) -> dict:
        """
        Extract reasoning steps and final answer from response text.
        
        Args:
            response_text: The full text response from the model
            
        Returns:
            dict: Dictionary with reasoning steps and final answer
        """
        import re
        
        # Default structure if we can't parse reasoning
        result = {
            "reasoning": [],
            "answer": response_text,
            "full_response": response_text
        }
        
        # Generic extraction patterns
        reasoning_patterns = [
            # Pattern 1: Numbered steps
            r"(?:Step|)\s*(\d+)[:.]\s*(.*?)(?=(?:Step|)\s*\d+[:.]\s*|\Z)",
            # Pattern 2: "Let's think step by step" pattern
            r"(?:Let's|I'll) think step by step:(.*?)(?=(?:Therefore|So|Thus|In conclusion|Final answer)(.*))",
            # Pattern 3: Thought/Action/Observation pattern
            r"(?:Thought|Reasoning):(.*?)(?=(?:Action|Observation):|$)"
        ]
        
        for pattern in reasoning_patterns:
            matches = re.findall(pattern, response_text, re.DOTALL)
            if matches:
                if isinstance(matches[0], tuple):
                    # For numbered steps pattern
                    reasoning_steps = [step.strip() for _, step in matches]
                else:
                    # For other patterns
                    reasoning_steps = [match.strip() for match in matches]
                
                result["reasoning"] = reasoning_steps
                
                # Try to extract the final answer
                final_answer_patterns = [
                    r"(?:Therefore|So|Thus|In conclusion|Final answer)[:.](.*)",
                    r"(?:Answer|Result)[:.](.*)"
                ]
                
                for ans_pattern in final_answer_patterns:
                    ans_match = re.search(ans_pattern, response_text, re.DOTALL)
                    if ans_match:
                        result["answer"] = ans_match.group(1).strip()
                        break
                
                break
        
        return result

class OpenAIProvider(LLMProvider):
    """Provider implementation for OpenAI's API."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", temperature: float = 0.3, max_tokens: int = 2000) -> None:
        super().__init__(ProviderType.OPENAI)
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.model = model
            self.temperature = temperature
            self.max_tokens = max_tokens
        except Exception as e:
            self._handle_error(e, "OpenAI initialization")

    def generate_completion(self, messages: List[Message], stream: bool = False) -> ModelResponse:
        """Generate completion using OpenAI's API."""
        try:
            messages_dict = Message.message_list_to_dict_list(messages)
            
            # Prepare parameters based on model
            params = {
                "model": self.model,
                "messages": messages_dict,
                "stream": stream,
            }
            
            # Handle different parameter names for different model versions
            if self.model.startswith(("gpt-3.5", "gpt-4")) and not self.model.startswith(("gpt-3.5-turbo-0125", "gpt-4-0125", "gpt-4o", "gpt-4o-mini")):
                # Older models use max_tokens
                params["max_tokens"] = self.max_tokens
                params["temperature"] = self.temperature
            elif self.model.startswith("o3-"):
                # o3 models don't support temperature and use max_completion_tokens
                params["max_completion_tokens"] = self.max_tokens
            else:
                # Newer models (gpt-4o, gpt-4o-mini, etc.) use max_completion_tokens and support temperature
                params["max_completion_tokens"] = self.max_tokens
                params["temperature"] = self.temperature
                
            if self.verbose:
                self.logger.debug(f"OpenAI API parameters: {params}")
                
            return self.client.chat.completions.create(**params)
        except Exception as e:
            self._handle_error(e, "OpenAI completion")

    def _is_valid_response(self, response: ModelResponse) -> bool:
        return hasattr(response, 'choices') and response.choices

    def _extract_stream_content(self, response: ModelResponse) -> Optional[str]:
        if not self._is_valid_response(response):
            return None
        delta = response.choices[0].delta
        return delta.content if hasattr(delta, 'content') else None

    def _extract_content(self, response: ModelResponse) -> str:
        return response.choices[0].message.content

    def extract_token_counts(self, response: ModelResponse) -> Optional[Tuple[int, int]]:
        try:
            usage = response.usage
            if not usage:
                return None
            
            if not hasattr(usage, 'prompt_tokens') or not hasattr(usage, 'completion_tokens'):
                return None
                
            if self.verbose:
                self.logger.debug(f"Extracted tokens - input: {usage.prompt_tokens}, output: {usage.completion_tokens}")
            
            return usage.prompt_tokens, usage.completion_tokens
            
        except AttributeError as e:
            if self.verbose:
                self.logger.warning(f"Failed to extract tokens from OpenAI response: {e}")
            return None

    def _handle_error(self, e: Exception, context: str) -> None:
        """OpenAI specific error handling"""
        from openai import OpenAIError, APIConnectionError, APITimeoutError
        
        if isinstance(e, (APIConnectionError, APITimeoutError)):
            raise ConnectionError(f"{context}: {str(e)}") from e
        elif isinstance(e, OpenAIError):
            raise ProviderError(f"{context}: {str(e)}") from e
            
        super()._handle_error(e, context)

    def get_reasoning_prompt(self) -> str:
        """Get OpenAI-specific reasoning prompt."""
        return (
            "Let's think step by step to solve this problem. Break it down into parts, "
            "work through each part systematically, and show your reasoning. "
            "After your analysis, provide your final answer."
        )
    
    def extract_reasoning(self, response_text: str) -> dict:
        """Extract reasoning using OpenAI-specific patterns."""
        import re
        
        result = {
            "reasoning": [],
            "answer": response_text,
            "full_response": response_text
        }
        
        # For o3-mini models, try to extract any structured reasoning
        if hasattr(self, 'model') and self.model.startswith("o3-"):
            # Try to find any numbered or bulleted lists
            step_patterns = [
                # Numbered steps
                r"(?:\d+\.|\(\d+\))\s*(.*?)(?=\d+\.|\(\d+\)|\Z)",
                # Bulleted steps
                r"(?:•|-|\*)\s*(.*?)(?=•|-|\*|\Z)",
                # Paragraph breaks as steps
                r"(?<=\n\n)(.*?)(?=\n\n|\Z)"
            ]
            
            for pattern in step_patterns:
                steps = re.findall(pattern, response_text, re.DOTALL)
                if steps and len(steps) > 1:  # At least 2 steps to consider it reasoning
                    result["reasoning"] = [step.strip() for step in steps if step.strip()]
                    
                    # Try to extract final answer from the last paragraph
                    paragraphs = response_text.split("\n\n")
                    if len(paragraphs) > 1 and any(keyword in paragraphs[-1].lower() 
                                                  for keyword in ["answer", "result", "therefore", "so", "thus"]):
                        result["answer"] = paragraphs[-1].strip()
                    break
        
        # If no reasoning found with o3-specific patterns, try standard patterns
        if not result["reasoning"]:
            # OpenAI often uses "Let's think step by step"
            sbs_match = re.search(r"Let's think step by step.(.*?)(?:Therefore|So|Thus|In conclusion)(.*)", 
                                 response_text, re.DOTALL)
            if sbs_match:
                reasoning_text = sbs_match.group(1).strip()
                result["answer"] = sbs_match.group(2).strip()
                
                # Split reasoning into bullet points or paragraphs
                reasoning_steps = re.split(r'\n\s*[-•*]\s*|\n\s*\d+[.)\s]\s*|\n{2,}', reasoning_text)
                result["reasoning"] = [step.strip() for step in reasoning_steps if step.strip()]
                return result
        
        # If still no reasoning found, try to split by paragraphs as a last resort
        if not result["reasoning"] and "\n\n" in response_text:
            paragraphs = [p.strip() for p in response_text.split("\n\n") if p.strip()]
            if len(paragraphs) >= 3:  # At least 3 paragraphs to consider it as reasoning + answer
                result["reasoning"] = paragraphs[:-1]  # All but last paragraph as reasoning
                result["answer"] = paragraphs[-1]  # Last paragraph as answer
        
        # If we found reasoning, return it; otherwise fall back to base implementation
        if result["reasoning"]:
            return result
        else:
            return super().extract_reasoning(response_text)

class AnthropicProvider(LLMProvider):
    """Provider implementation for Anthropic's API."""
    
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229", temperature: float = 0.3, max_tokens: int = 2000) -> None:
        super().__init__(ProviderType.ANTHROPIC)
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=api_key)
            self.model = model
            self.temperature = temperature
            self.max_tokens = max_tokens
        except ImportError as e:
            self._handle_error(e, "Anthropic package not installed")
        except Exception as e:
            self._handle_error(e, "Anthropic initialization")

    def generate_completion(self, messages: List[Message], stream: bool = False) -> ModelResponse:
        """Generate completion using Anthropic's API."""
        try:
            messages_dict = Message.message_list_to_dict_list(messages)
            
            # Separate system prompt from other messages
            system_message = next((msg for msg in messages_dict if msg['role'] == 'system'), None)
            other_messages = [msg for msg in messages_dict if msg['role'] != 'system']
            
            system_content = system_message['content'] if system_message else None

            if system_content is None:
                return self.client.messages.create(
                    model=self.model,
                    messages=other_messages,
                    stream=stream,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
            else:
                return self.client.messages.create(
                    model=self.model,
                    messages=other_messages,
                    system=system_content,
                    stream=stream,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
        except Exception as e:
            self._handle_error(e, "Anthropic completion")

    def _is_valid_response(self, response: ModelResponse) -> bool:
        return hasattr(response, 'content') and response.content

    def _extract_stream_content(self, response: ModelResponse) -> Optional[str]:
        if not hasattr(response, 'type'):
            return None
            
        if response.type in ('message_start', 'content_block_start'):
            return ''
        elif response.type in ('content_block_delta', 'message_delta'):
            return response.delta.text if hasattr(response.delta, 'text') else ''
        
        self.logger.debug(f"Unknown event type: {response.type}")
        return None

    def _extract_content(self, response: ModelResponse) -> str:
        return response.content[0].text

    def extract_token_counts(self, response: ModelResponse) -> Optional[Tuple[int, int]]:
        try:
            usage = response.usage
            if not usage:
                return None
            
            if not hasattr(usage, 'input_tokens') or not hasattr(usage, 'output_tokens'):
                return None
                
            if self.verbose:
                self.logger.debug(f"Extracted tokens - input: {usage.input_tokens}, output: {usage.output_tokens}")
            
            return usage.input_tokens, usage.output_tokens
            
        except AttributeError as e:
            if self.verbose:
                self.logger.warning(f"Failed to extract tokens from Anthropic response: {e}")
            return None

    def _handle_error(self, e: Exception, context: str) -> None:
        """Anthropic specific error handling"""
        # Only try to import anthropic-specific exceptions if anthropic is available
        try:
            import anthropic
            # Now we can safely import anthropic-specific exceptions
            from anthropic import (
                APIConnectionError as AnthropicConnectionError,
                APITimeoutError as AnthropicTimeoutError,
                APIError as AnthropicError
            )
            
            if isinstance(e, (AnthropicConnectionError, AnthropicTimeoutError)):
                raise ConnectionError(f"{context}: {str(e)}") from e
            elif isinstance(e, AnthropicError):
                raise ProviderError(f"{context}: {str(e)}") from e
        except ImportError:
            # If anthropic package is not installed, use base error handling
            pass
            
        super()._handle_error(e, context)

    def get_reasoning_prompt(self) -> str:
        """Get Anthropic-specific reasoning prompt."""
        return (
            "Think step by step to solve this problem.\n\n"
            "Step 1: Break down the problem into parts.\n"
            "Step 2: Work through each part systematically.\n"
            "Step 3: Show your reasoning for each step.\n"
            "Step 4: Provide your final answer clearly marked as 'Final answer:'"
        )
    
    def extract_reasoning(self, response_text: str) -> dict:
        """Extract reasoning using Anthropic-specific patterns."""
        import re
        
        result = {
            "reasoning": [],
            "answer": response_text,
            "full_response": response_text
        }
        
        # Anthropic typically uses numbered steps
        step_pattern = r"Step\s*(\d+)[:.]\s*(.*?)(?=Step\s*\d+[:.]\s*|\Z|Final answer:)"
        steps = re.findall(step_pattern, response_text, re.DOTALL)
        if steps:
            result["reasoning"] = [step.strip() for _, step in steps]
            
            # Extract final answer
            final_match = re.search(r"Final answer:(.*?)(?:\Z|$)", response_text, re.DOTALL)
            if final_match:
                result["answer"] = final_match.group(1).strip()
            return result
        
        # Fall back to base implementation
        return super().extract_reasoning(response_text)

class LlamaProvider(LLMProvider):
    """Provider implementation for local Llama models."""
    
    def __init__(self, model_path: str, temperature: float = 0.3, max_tokens: int = 2000) -> None:
        super().__init__(ProviderType.LLAMA)
        try:
            # Move import inside method
            from llama_cpp import Llama
            self.Llama = Llama
            
            # Rest of initialization
            self.model_path = model_path
            self.temperature = temperature
            self.max_tokens = max_tokens
            
            try:
                self.model = self.Llama(model_path=model_path)
            except Exception as e:
                self._handle_error(e, "Llama initialization")
            
        except ImportError as e:
            self._handle_error(e, "Llama CPP Python package not installed")

    def generate_completion(self, messages: List[Message], stream: bool = False) -> ModelResponse:
        """Generate completion using local Llama model."""
        try:
            messages_dict = Message.message_list_to_dict_list(messages)
            return self.model.create_chat_completion(
                messages=messages_dict,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=stream
            )
        except Exception as e:
            self._handle_error(e, "Llama completion")

    def _is_valid_response(self, response: ModelResponse) -> bool:
        return isinstance(response, dict) and 'choices' in response

    def _extract_stream_content(self, response: ModelResponse) -> Optional[str]:
        if not self._is_valid_response(response):
            return None
        return response['choices'][0].get('text', '')

    def _extract_content(self, response: ModelResponse) -> str:
        if not self._is_valid_response(response):
            raise ProviderError("Invalid response format from Llama")
        return response['choices'][0]['text']

    def get_reasoning_prompt(self) -> str:
        """Get Llama-specific reasoning prompt."""
        return (
            "I need to solve this step-by-step:\n\n"
            "1. First, understand what we're looking for\n"
            "2. Break down the problem into parts\n"
            "3. Work through each part systematically\n"
            "4. Provide the final answer\n\n"
            "Let me solve this problem:"
        )

    def extract_token_counts(self, response: ModelResponse) -> Optional[Tuple[int, int]]:
        """Llama typically doesn't provide token counts."""
        if self.verbose:
            self.logger.debug("Token count not available for Llama responses")
        return None

class DeepSeekProvider(LLMProvider):
    """Provider implementation for DeepSeek's API."""
    
    def __init__(self, api_key: str, model: str = "deepseek-chat", temperature: float = 0.3, max_tokens: int = 2000) -> None:
        super().__init__(ProviderType.DEEPSEEK)
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
            self.model = model
            self.temperature = temperature
            self.max_tokens = max_tokens
        except Exception as e:
            self._handle_error(e, "DeepSeek initialization")

    def generate_completion(self, messages: List[Message], stream: bool = False) -> ModelResponse:
        """Generate completion using DeepSeek's API."""
        try:
            messages_dict = Message.message_list_to_dict_list(messages)
            
            # Prepare parameters
            params = {
                "model": self.model,
                "messages": messages_dict,
                "stream": stream,
                "max_tokens": self.max_tokens
            }
            
            # Add temperature parameter if not using the reasoner model
            if not self.model.startswith("deepseek-reasoner"):
                params["temperature"] = self.temperature
                
            if self.verbose:
                self.logger.debug(f"DeepSeek API parameters: {params}")
                
            return self.client.chat.completions.create(**params)
        except Exception as e:
            self._handle_error(e, "DeepSeek completion")

    def _is_valid_response(self, response: ModelResponse) -> bool:
        return hasattr(response, 'choices') and response.choices

    def _extract_stream_content(self, response: ModelResponse) -> Optional[str]:
        if not self._is_valid_response(response):
            return None
        delta = response.choices[0].delta
        return delta.content if hasattr(delta, 'content') else None

    def _extract_content(self, response: ModelResponse) -> str:
        return response.choices[0].message.content

    def extract_token_counts(self, response: ModelResponse) -> Optional[Tuple[int, int]]:
        try:
            usage = response.usage
            if not usage:
                return None
            
            if not hasattr(usage, 'prompt_tokens') or not hasattr(usage, 'completion_tokens'):
                return None
                
            if self.verbose:
                self.logger.debug(f"Extracted tokens - input: {usage.prompt_tokens}, output: {usage.completion_tokens}")
            
            return usage.prompt_tokens, usage.completion_tokens
            
        except AttributeError as e:
            if self.verbose:
                self.logger.warning(f"Failed to extract tokens from DeepSeek response: {e}")
            return None

    def _handle_error(self, e: Exception, context: str) -> None:
        """DeepSeek specific error handling"""
        from openai import OpenAIError, APIConnectionError, APITimeoutError
        
        if isinstance(e, (APIConnectionError, APITimeoutError)):
            raise ConnectionError(f"{context}: {str(e)}") from e
        elif isinstance(e, OpenAIError):
            raise ProviderError(f"{context}: {str(e)}") from e
            
        super()._handle_error(e, context)

    def get_reasoning_prompt(self) -> str:
        """Get DeepSeek-specific reasoning prompt."""
        return (
            "Let's solve this problem step by step:\n\n"
            "1. First, I'll understand what the question is asking\n"
            "2. Then, I'll identify the key information and concepts needed\n"
            "3. Next, I'll work through the solution methodically\n"
            "4. Finally, I'll verify my answer and provide the final result\n\n"
            "Problem:"
        )
    
    def extract_reasoning(self, response_text: str) -> dict:
        """Extract reasoning steps from DeepSeek response."""
        import re
        
        result = {
            "reasoning": [],
            "answer": response_text,
            "full_response": response_text
        }
        
        # DeepSeek often uses numbered steps
        step_pattern = r"(\d+)[.:\)]\s*(.*?)(?=\d+[.:\)]|$)"
        steps = re.findall(step_pattern, response_text, re.DOTALL)
        
        if steps:
            result["reasoning"] = [step.strip() for _, step in steps if step.strip()]
            
            # Try to extract final answer
            answer_pattern = r"(?:Therefore|So|Thus|In conclusion|Final answer|The answer is)[:.](.*?)(?=$|\n\n)"
            answer_match = re.search(answer_pattern, response_text, re.DOTALL)
            if answer_match:
                result["answer"] = answer_match.group(1).strip()
        
        return result

class GeminiProvider(LLMProvider):
    """Provider implementation for Google's Gemini API."""
    
    def __init__(self, api_key: str, model: str = "gemini-pro", temperature: float = 0.3, max_tokens: int = 2000) -> None:
        super().__init__(ProviderType.GEMINI)
        try:
            # Move import inside method
            import google.generativeai as genai
            self.genai = genai
            
            # Rest of initialization
            self.genai.configure(api_key=api_key)
            self.model = model
            self.temperature = temperature
            self.max_tokens = max_tokens
        except ImportError as e:
            self._handle_error(e, "Google GenerativeAI package not installed")

    def generate_completion(self, messages: List[Message], stream: bool = False) -> ModelResponse:
        """Generate completion using Gemini's API."""
        try:
            # Convert our message format to Gemini's format
            gemini_messages = []
            
            for msg in messages:
                if msg.role == Role.SYSTEM:
                    # Gemini doesn't have a system role, so we'll add it as a user message
                    gemini_messages.append({"role": "user", "parts": [f"System instruction: {msg.content}"]})
                    # Add a model response acknowledging the system instruction
                    gemini_messages.append({"role": "model", "parts": ["I'll follow these instructions."]})
                elif msg.role == Role.USER:
                    gemini_messages.append({"role": "user", "parts": [msg.content]})
                elif msg.role == Role.ASSISTANT:
                    gemini_messages.append({"role": "model", "parts": [msg.content]})
            
            # Create generation config
            generation_config = {
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens,
            }
            
            if self.verbose:
                self.logger.debug(f"Gemini API parameters: {generation_config}")
                self.logger.debug(f"Gemini messages: {gemini_messages}")
            
            # Generate response
            if stream:
                return self.genai.GenerativeModel(model_name=self.model).generate_content(
                    gemini_messages,
                    generation_config=generation_config,
                    stream=True
                )
            else:
                return self.genai.GenerativeModel(model_name=self.model).generate_content(
                    gemini_messages,
                    generation_config=generation_config
                )
                
        except Exception as e:
            self._handle_error(e, "Gemini completion")

    def _is_valid_response(self, response: ModelResponse) -> bool:
        return hasattr(response, 'text')

    def _extract_stream_content(self, response: ModelResponse) -> Optional[str]:
        try:
            # For streaming responses in Gemini
            if hasattr(response, 'text'):
                return response.text
            return None
        except Exception:
            return None

    def _extract_content(self, response: ModelResponse) -> str:
        return response.text

    def extract_token_counts(self, response: ModelResponse) -> Optional[Tuple[int, int]]:
        # Gemini doesn't provide token counts directly
        return None

    def _handle_error(self, e: Exception, context: str) -> None:
        """Gemini specific error handling"""
        if "Connection" in str(e) or "timeout" in str(e).lower():
            raise ConnectionError(f"{context}: {str(e)}") from e
        raise ProviderError(f"{context}: {str(e)}") from e

    def get_reasoning_prompt(self) -> str:
        """Get Gemini-specific reasoning prompt."""
        return (
            "I need to solve this carefully and show my reasoning process.\n\n"
            "I'll follow these steps:\n"
            "1. Understand what the problem is asking\n"
            "2. Identify the relevant information\n"
            "3. Plan my approach\n"
            "4. Execute the solution step by step\n"
            "5. Verify my answer\n\n"
            "Let me work through this problem:"
        )
    
    def extract_reasoning(self, response_text: str) -> dict:
        """Extract reasoning steps from Gemini response."""
        import re
        
        result = {
            "reasoning": [],
            "answer": response_text,
            "full_response": response_text
        }
        
        # Gemini often uses a mix of numbered steps and paragraphs
        # Try numbered steps first
        step_pattern = r"(?:Step\s*)?(\d+)[.:\)]\s*(.*?)(?=(?:Step\s*)?(?:\d+)[.:\)]|$)"
        steps = re.findall(step_pattern, response_text, re.DOTALL)
        
        if steps:
            result["reasoning"] = [step.strip() for _, step in steps if step.strip()]
        else:
            # Try paragraphs if no numbered steps
            paragraphs = [p.strip() for p in response_text.split("\n\n") if p.strip()]
            if len(paragraphs) >= 3:  # Need at least a few paragraphs to consider it reasoning
                result["reasoning"] = paragraphs[:-1]
                result["answer"] = paragraphs[-1]
                return result
        
        # Try to extract final answer if we found reasoning steps
        if result["reasoning"]:
            answer_patterns = [
                r"(?:Therefore|So|Thus|In conclusion|Final answer|The answer is)[:.](.*?)(?=$|\n\n)",
                r"(?:To summarize|In summary)[:.](.*?)(?=$|\n\n)",
                r"(?:My answer is|The result is|The solution is)[:.](.*?)(?=$|\n\n)"
            ]
            
            for pattern in answer_patterns:
                answer_match = re.search(pattern, response_text, re.DOTALL)
                if answer_match:
                    result["answer"] = answer_match.group(1).strip()
                    break
        
        return result

class ProviderBuilder:
    """Builder for creating configured LLM providers."""
    
    def __init__(self, provider_type: ProviderType) -> None:
        self.provider_type: ProviderType = provider_type
        self.api_key: Optional[str] = None
        self.model: Optional[str] = None
        self.temperature: float = 0.3
        self.max_tokens: int = 2000
        self.model_path: Optional[str] = None
    
    def set_api_key(self, api_key: str) -> 'ProviderBuilder':
        self.api_key = api_key
        return self
    
    def set_model(self, model: str) -> 'ProviderBuilder':
        self.model = model
        return self
    
    def set_temperature(self, temperature: float) -> 'ProviderBuilder':
        if not 0 <= temperature <= 1:
            raise ValidationError("Temperature must be between 0 and 1")
        self.temperature = temperature
        return self
    
    def set_max_tokens(self, max_tokens: int) -> 'ProviderBuilder':
        if max_tokens <= 0:
            raise ValidationError("max_tokens must be positive")
        self.max_tokens = max_tokens
        return self
    
    def set_model_path(self, path: str) -> 'ProviderBuilder':
        self.model_path = path
        return self
    
    def build(self) -> LLMProvider:
        """
        Build and return a configured LLM provider.
        
        Returns:
            LLMProvider: The configured provider
            
        Raises:
            ValidationError: If required configuration is missing
            ValueError: If provider type is unknown
        """
        if self.provider_type == ProviderType.OPENAI:
            api_key = self.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValidationError("OpenAI API key is required")
            return OpenAIProvider(
                api_key=api_key, 
                model=self.model or "gpt-4o-mini",
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
        elif self.provider_type == ProviderType.ANTHROPIC:
            api_key = self.api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValidationError("Anthropic API key is required")
            return AnthropicProvider(
                api_key=api_key, 
                model=self.model or "claude-3-opus-20240229",
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
        elif self.provider_type == ProviderType.LLAMA:
            if not self.model_path:
                raise ValidationError("Model path required for Llama provider")
            return LlamaProvider(
                model_path=self.model_path,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
        elif self.provider_type == ProviderType.DEEPSEEK:
            api_key = self.api_key or os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValidationError("DeepSeek API key is required")
            return DeepSeekProvider(
                api_key=api_key, 
                model=self.model or "deepseek-chat",
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
        elif self.provider_type == ProviderType.GEMINI:
            api_key = self.api_key or os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValidationError("Gemini API key is required")
            return GeminiProvider(
                api_key=api_key, 
                model=self.model or "gemini-pro",
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
        raise ValueError(f"Unknown provider type: {self.provider_type}")

# Add more providers as needed... 