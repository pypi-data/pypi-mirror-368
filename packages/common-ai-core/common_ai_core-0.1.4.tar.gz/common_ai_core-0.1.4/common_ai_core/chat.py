import logging
from typing import Optional, Any, List, Iterator, Union
from common_ai_core.providers import LLMProvider, ProviderError
from common_ai_core.memory import MemoryBase, TokenLimitedMemory
from common_ai_core.tokens.token_tracker import TokenTracker
from common_ai_core.types import Message, Role
from common_ai_core.tokens.token_counter import TokenCounterFactory
from .exceptions import ChatError, ValidationError, ProviderError, ConnectionError

logger = logging.getLogger('common_ai_core')

class BaseChat:
    """Base class for chat implementations.
    
    Provides common functionality for handling chat interactions with LLM providers.
    Supports memory management and token tracking.
    
    Attributes:
        llm_provider: Provider for LLM interactions
        memory: Memory system for chat history
        token_tracker: Optional token usage tracker
        verbose: Enable verbose logging
    """
    
    def __init__(self, 
                 llm_provider: LLMProvider,
                 memory: Optional[MemoryBase] = None,
                 token_tracker: Optional[TokenTracker] = None,
                 verbose: bool = False) -> None:
        """
        Initialize chat.
        
        Args:
            llm_provider: Provider for LLM interactions
            memory: Memory system for chat history
            token_tracker: Optional token usage tracker
            verbose: Enable verbose logging
            
        Raises:
            ValidationError: If llm_provider is invalid
        """
        if not isinstance(llm_provider, LLMProvider):
            raise ValidationError("llm_provider must be an instance of LLMProvider")
        if memory is not None and not isinstance(memory, MemoryBase):
            raise ValidationError("memory must be an instance of MemoryBase")
        if token_tracker is not None and not isinstance(token_tracker, TokenTracker):
            raise ValidationError("token_tracker must be an instance of TokenTracker")
            
        self.logger = logging.getLogger(f'common_ai_core.{self.__class__.__name__}')
        if verbose:
            self.logger.setLevel(logging.DEBUG)
        self.llm_provider = llm_provider
        self.memory = memory if memory else TokenLimitedMemory(500, verbose=verbose)
        self.token_tracker = token_tracker
        self.verbose = verbose

    def _prepare_messages(self, prompt: str) -> List[Message]:
        """
        Prepare messages for the provider.
        
        Args:
            prompt: User input prompt
            
        Returns:
            List[Message]: Prepared message list
            
        Raises:
            ValidationError: If prompt is invalid
        """
        if not prompt or not isinstance(prompt, str):
            raise ValidationError("Invalid prompt: Must be a non-empty string")
            
        if self.verbose:
            self.logger.debug(f"Processing prompt: {prompt[:50]}...")
        
        user_message = Message(Role.USER, prompt)
        self.memory.add(user_message)
        messages = self.memory.get_history()
        
        if self.verbose:
            self.logger.debug(f"Messages to send to provider: {messages}")
            
        return messages
    
    def _generate_response(self, messages: List[Message], stream: bool = False) -> Any:
        """
        Generate response from the provider.
        
        Args:
            messages: List of messages to send
            stream: Whether to stream the response
            
        Returns:
            Any: Provider response
            
        Raises:
            ProviderError: If provider fails
            ConnectionError: If connection fails
        """
        try:
            return self.llm_provider.generate_completion(messages=messages, stream=stream)
        except (ProviderError, ConnectionError) as e:
            if self.verbose:
                self.logger.error(f"Error generating response: {str(e)}")
            raise
    
    def _process_response(self, full_response: Any, messages: List[Message]) -> str:
        """
        Process and store the provider's response.
        
        Args:
            full_response: Provider's response
            messages: List of messages sent
            
        Returns:
            str: Processed response text
            
        Raises:
            ProviderError: If response processing fails
        """
        chat_response = self.llm_provider.get_message_content(full_response, stream=False)
        if not chat_response:
            raise ProviderError("No response content from provider")
        
        # Store response in memory
        assistant_message = Message(Role.ASSISTANT, chat_response)
        self.memory.add(assistant_message)
        
        # Handle token tracking if enabled
        if self.token_tracker:
            self._track_tokens(full_response, messages, chat_response)
            
        return chat_response

    def _track_tokens(self, full_response: Any, messages: List[Message], chat_response: str) -> None:
        """
        Track token usage.
        
        Args:
            full_response: Provider's response
            messages: List of messages sent
            chat_response: Processed response text
        """
        try:
            token_counts = self.llm_provider.extract_token_counts(full_response)
            if token_counts:
                input_tokens, output_tokens = token_counts
            else:
                token_counter = TokenCounterFactory.from_provider(self.llm_provider, verbose=self.verbose)
                input_tokens = token_counter.count_tokens_in_messages(messages)
                output_tokens = token_counter.count_tokens_in_text(chat_response)
            
            self.token_tracker.add(input_tokens, output_tokens)
            
            if self.verbose:
                self.logger.debug(f"Tracked tokens - Input: {input_tokens}, Output: {output_tokens}")
                
        except Exception as e:
            self.logger.warning(f"Failed to track tokens: {str(e)}")

class CompletionChat(BaseChat):
    """Chat implementation for standard completion responses."""
    
    def chat(self, prompt: str) -> str:
        """
        Generate a chat response for the given prompt.
        
        Args:
            prompt: The user's input prompt
            
        Returns:
            str: The generated response
            
        Raises:
            ValidationError: If prompt is invalid
            ProviderError: If the provider encounters an error
            ConnectionError: If connection to provider fails
            ChatError: For other chat-related errors
        """
        if not prompt or not isinstance(prompt, str):
            raise ValidationError("Invalid prompt: Must be a non-empty string")

        try:
            messages = self._prepare_messages(prompt)
            full_response = self._generate_response(messages, stream=False)
            chat_response = self._process_response(full_response, messages)
            return chat_response
            
        except (ValidationError, ProviderError, ConnectionError) as e:
            raise
        except Exception as e:
            raise ChatError(f"Unexpected error in chat: {str(e)}") from e

class StreamingChat(BaseChat):
    """Chat implementation for streaming responses."""
    
    def chat(self, prompt: str) -> Iterator[str]:
        """
        Generate a streaming chat response for the given prompt.
        
        Args:
            prompt: The user's input prompt
            
        Yields:
            str: Response chunks as they become available
            
        Raises:
            ValidationError: If prompt is invalid
            ProviderError: If the provider encounters an error
            ConnectionError: If connection to provider fails
            ChatError: For other chat-related errors
        """
        if not prompt or not isinstance(prompt, str):
            raise ValidationError("Invalid prompt: Must be a non-empty string")

        try:
            messages = self._prepare_messages(prompt)
            stream = self._generate_response(messages, stream=True)
            chunks = []

            for chunk in stream:
                content = self.llm_provider.get_message_content(chunk, stream=True)
                if content is not None:
                    chunks.append(content)
                    yield content

            complete_response = "".join(chunks)
            if complete_response:
                if self.token_tracker:
                    self._track_tokens(messages, complete_response)
                
                assistant_message = Message(Role.ASSISTANT, complete_response)
                self.memory.add(assistant_message)
                
        except (ValidationError, ProviderError, ConnectionError) as e:
            raise
        except Exception as e:
            raise ChatError(f"Unexpected error in streaming chat: {str(e)}") from e

    def _track_tokens(self, messages: List[Message], response_text: str) -> None:
        """
        Track token usage for streaming responses.
        
        Args:
            messages: List of messages sent
            response_text: Complete response text
        """
        try:
            token_counter = TokenCounterFactory.from_provider(
                self.llm_provider, 
                verbose=self.verbose
            )
            input_tokens = token_counter.count_tokens_in_messages(messages)
            output_tokens = token_counter.count_tokens_in_text(response_text)
            self.token_tracker.add(input_tokens, output_tokens)
            
            if self.verbose:
                self.logger.debug(f"Tracked streaming tokens - Input: {input_tokens}, Output: {output_tokens}")
                
        except Exception as e:
            self.logger.warning(f"Failed to track streaming tokens: {str(e)}")

class ReasoningChat(BaseChat):
    """Chat implementation for models that support reasoning steps."""
    
    def __init__(self, 
                 llm_provider: LLMProvider,
                 memory: Optional[MemoryBase] = None,
                 token_tracker: Optional[TokenTracker] = None,
                 verbose: bool = False,
                 reasoning_prompt: Optional[str] = None) -> None:
        """
        Initialize reasoning chat.
        
        Args:
            llm_provider: Provider for LLM interactions
            memory: Memory system for chat history
            token_tracker: Optional token usage tracker
            verbose: Enable verbose logging
            reasoning_prompt: Custom prompt to encourage reasoning (uses default if None)
        """
        super().__init__(llm_provider, memory, token_tracker, verbose)
        
        # Use provider's reasoning prompt if available, otherwise use default
        if reasoning_prompt is None:
            self.reasoning_prompt = getattr(llm_provider, 'get_reasoning_prompt', lambda: (
                "Think step by step to solve this problem. First, break down the problem "
                "into parts. Then, work through each part systematically. Show your reasoning "
                "for each step. Finally, provide your answer."
            ))()
        else:
            self.reasoning_prompt = reasoning_prompt
    
    def chat(self, prompt: str, stream: bool = False) -> Union[dict, Iterator[str]]:
        """
        Generate a chat response with reasoning steps for the given prompt.
        
        Args:
            prompt: The user's input prompt
            stream: Whether to stream the response
            
        Returns:
            If stream=False: dict with reasoning steps and final answer
            If stream=True: Iterator yielding response chunks
            
        Raises:
            ValidationError: If prompt is invalid
            ProviderError: If the provider encounters an error
            ConnectionError: If connection to provider fails
            ChatError: For other chat-related errors
        """
        # Enhance the prompt with reasoning instructions
        enhanced_prompt = f"{self.reasoning_prompt}\n\n{prompt}"
        
        try:
            messages = self._prepare_messages(enhanced_prompt)
            
            if stream:
                # For streaming, return a generator that handles memory and token tracking
                return self._stream_with_tracking(messages)
            else:
                # For non-streaming, process and extract reasoning
                full_response = self._generate_response(messages, stream=False)
                chat_response = self._process_response(full_response, messages)
                reasoning_data = self._extract_reasoning(chat_response)
                return reasoning_data
                
        except (ValidationError, ProviderError, ConnectionError) as e:
            raise
        except Exception as e:
            raise ChatError(f"Unexpected error in reasoning chat: {str(e)}") from e
    
    def _stream_with_tracking(self, messages: List[Message]) -> Iterator[str]:
        """
        Stream response with proper memory and token tracking.
        
        Args:
            messages: List of messages to send
            
        Yields:
            str: Response chunks
            
        Raises:
            ProviderError: If provider fails
            ConnectionError: If connection fails
        """
        stream_response = self._generate_response(messages, stream=True)
        accumulated_text = ""
        
        for chunk in stream_response:
            content = self.llm_provider.get_message_content(chunk, stream=True)
            if content is not None:
                accumulated_text += content
                yield content
        
        # Store the complete response in memory
        if accumulated_text:
            assistant_message = Message(Role.ASSISTANT, accumulated_text)
            self.memory.add(assistant_message)
            
            # Handle token tracking
            if self.token_tracker:
                self._track_tokens_for_streaming(messages, accumulated_text)
    
    def _track_tokens_for_streaming(self, messages: List[Message], response_text: str) -> None:
        """
        Track token usage for streaming responses.
        
        Args:
            messages: List of messages sent
            response_text: Complete response text
        """
        try:
            # Try to get token counts from provider first
            token_counts = None
            if hasattr(self.llm_provider, 'extract_token_counts_from_text'):
                token_counts = self.llm_provider.extract_token_counts_from_text(messages, response_text)
            
            # Fall back to token counter if provider doesn't provide counts
            if not token_counts:
                token_counter = TokenCounterFactory.from_provider(
                    self.llm_provider, 
                    verbose=self.verbose
                )
                input_tokens = token_counter.count_tokens_in_messages(messages)
                output_tokens = token_counter.count_tokens_in_text(response_text)
                token_counts = (input_tokens, output_tokens)
            
            # Add to token tracker
            if token_counts:
                input_tokens, output_tokens = token_counts
                self.token_tracker.add(input_tokens, output_tokens)
                
                if self.verbose:
                    self.logger.debug(f"Tracked streaming tokens - Input: {input_tokens}, Output: {output_tokens}")
                    
        except Exception as e:
            self.logger.warning(f"Failed to track streaming tokens: {str(e)}")
    
    def chat_with_reasoning_stream(self, prompt: str) -> Iterator[dict]:
        """
        Generate a streaming chat response with incremental reasoning extraction.
        
        This method streams the response and attempts to extract reasoning steps
        and answers from the accumulated text as it comes in.
        
        Args:
            prompt: The user's input prompt
            
        Returns:
            Iterator yielding dicts with current reasoning steps and answer
            
        Raises:
            ValidationError: If prompt is invalid
            ProviderError: If the provider encounters an error
            ConnectionError: If connection to provider fails
            ChatError: For other chat-related errors
        """
        # Enhance the prompt with reasoning instructions
        enhanced_prompt = f"{self.reasoning_prompt}\n\n{prompt}"
        
        try:
            messages = self._prepare_messages(enhanced_prompt)
            stream = self._generate_response(messages, stream=True)
            
            accumulated_text = ""
            current_reasoning = []
            current_answer = ""
            
            for chunk in stream:
                content = self.llm_provider.get_message_content(chunk, stream=True)
                if content:
                    accumulated_text += content
                    
                    # Try to extract reasoning from accumulated text
                    reasoning_data = self._extract_reasoning(accumulated_text)
                    
                    # Only yield if something has changed
                    if (reasoning_data["reasoning"] != current_reasoning or 
                        reasoning_data["answer"] != current_answer):
                        
                        current_reasoning = reasoning_data["reasoning"]
                        current_answer = reasoning_data["answer"]
                        
                        yield {
                            "reasoning": current_reasoning,
                            "answer": current_answer,
                            "chunk": content,
                            "full_response": accumulated_text
                        }
            
            # Store final response in memory
            assistant_message = Message(Role.ASSISTANT, accumulated_text)
            self.memory.add(assistant_message)
            
            # Handle token tracking if enabled
            if self.token_tracker:
                self._track_tokens_for_streaming(messages, accumulated_text)
                
            # Final yield with complete reasoning
            final_reasoning = self._extract_reasoning(accumulated_text)
            yield final_reasoning
            
        except (ValidationError, ProviderError, ConnectionError) as e:
            raise
        except Exception as e:
            raise ChatError(f"Unexpected error in reasoning chat stream: {str(e)}") from e
    
    def _extract_reasoning(self, response_text: str) -> dict:
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
        
        # Use provider-specific extraction if available
        if hasattr(self.llm_provider, 'extract_reasoning'):
            provider_result = self.llm_provider.extract_reasoning(response_text)
            if provider_result and provider_result.get("reasoning"):
                return provider_result
        
        # Enhanced extraction patterns
        reasoning_patterns = [
            # Pattern 1: Numbered steps with various formats
            r"(?:Step|)\s*(\d+)[:.]\s*(.*?)(?=(?:Step|)\s*\d+[:.]\s*|\Z)",
            r"(?:\d+\.|\(\d+\))\s*(.*?)(?=\d+\.|\(\d+\)|\Z)",
            
            # Pattern 2: "Let's think step by step" pattern with variations
            r"(?:Let's|I'll) think step by step:(.*?)(?:Therefore|So|Thus|In conclusion|Final answer)(.*)",
            r"(?:Let's|I'll) solve this step by step:(.*?)(?:Therefore|So|Thus|In conclusion|Final answer)(.*)",
            r"(?:Let's|I'll) break this down:(.*?)(?:Therefore|So|Thus|In conclusion|Final answer)(.*)",
            
            # Pattern 3: Thought/Action/Observation pattern
            r"(?:Thought|Reasoning):(.*?)(?=(?:Action|Observation):|$)",
            
            # Pattern 4: Bulleted lists
            r"(?:•|-|\*)\s*(.*?)(?=•|-|\*|\Z)",
            
            # Pattern 5: Paragraph-based reasoning
            r"(?<=\n\n)(.*?)(?=\n\n|\Z)"
        ]
        
        # Try each pattern until we find a match
        for pattern in reasoning_patterns:
            matches = re.findall(pattern, response_text, re.DOTALL)
            if matches:
                if isinstance(matches[0], tuple):
                    # For patterns with capture groups
                    if len(matches[0]) == 2:
                        # For patterns like "Step 1: ..."
                        reasoning_steps = [step.strip() for _, step in matches]
                    else:
                        # For other patterns
                        reasoning_steps = [match[0].strip() for match in matches]
                else:
                    # For simple patterns
                    reasoning_steps = [match.strip() for match in matches]
                
                # Filter out empty steps and limit to reasonable steps
                reasoning_steps = [step for step in reasoning_steps if step and len(step) > 10]
                
                if reasoning_steps:
                    result["reasoning"] = reasoning_steps
                    
                    # Try to extract the final answer with enhanced patterns
                    final_answer_patterns = [
                        r"(?:Therefore|So|Thus|In conclusion|Final answer)[:.](.*)",
                        r"(?:Answer|Result|Solution)[:.](.*)",
                        r"(?:The answer is|The result is|The solution is)[:.](.*)",
                        r"(?:To summarize|In summary)[:.](.*)"
                    ]
                    
                    for ans_pattern in final_answer_patterns:
                        ans_match = re.search(ans_pattern, response_text, re.DOTALL)
                        if ans_match:
                            result["answer"] = ans_match.group(1).strip()
                            break
                    
                    # If we found reasoning but no answer, use the last paragraph as the answer
                    if result["answer"] == response_text and "\n\n" in response_text:
                        paragraphs = response_text.split("\n\n")
                        result["answer"] = paragraphs[-1].strip()
                    
                    break
        
        # If we still don't have reasoning but have paragraphs, use them as reasoning
        if not result["reasoning"] and "\n\n" in response_text:
            paragraphs = [p.strip() for p in response_text.split("\n\n") if p.strip()]
            if len(paragraphs) >= 3:  # At least 3 paragraphs to consider it as reasoning + answer
                result["reasoning"] = paragraphs[:-1]  # All but last paragraph as reasoning
                result["answer"] = paragraphs[-1]  # Last paragraph as answer
        
        return result 