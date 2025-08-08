from common_ai_core import (
    ProviderBuilder, 
    ProviderType, 
    CompletionChat,
    SystemTokenLimitedMemory
)

def system_prompt_example():
    # Create a provider
    provider = (ProviderBuilder(ProviderType.DEEPSEEK)
               .set_model("deepseek-chat")
               .build())
    
    # Create memory with system prompt
    memory = SystemTokenLimitedMemory.from_provider(
        provider=provider,
        system_prompt="You are a Python coding assistant. Always provide code examples in your explanations.",
        max_tokens=2000
    )
    
    # Create chat interface with memory
    chat = CompletionChat(provider, memory)
    
    # The assistant will now include code examples
    response = chat.chat("How do I read a file in Python?")
    print(response)
    
    # Follow-up question - memory maintains context
    response = chat.chat("How would I modify that to read CSV files?")
    print(response)

if __name__ == "__main__":
    system_prompt_example() 