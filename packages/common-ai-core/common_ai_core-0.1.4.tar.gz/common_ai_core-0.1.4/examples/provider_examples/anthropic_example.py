from common_ai_core import (
    ProviderBuilder, 
    ProviderType, 
    StreamingChat,
    SystemTokenLimitedMemory
)

def anthropic_example():
    # Create Anthropic provider
    provider = (ProviderBuilder(ProviderType.ANTHROPIC)
               .set_model("claude-3-opus-20240229")
               .set_temperature(0.7)
               .build())
    
    # Create memory with system prompt
    memory = SystemTokenLimitedMemory.from_provider(
        provider=provider,
        system_prompt="You are Claude, a helpful AI assistant with expertise in science.",
        max_tokens=2000
    )
    
    # Create streaming chat
    chat = StreamingChat(provider, memory)
    
    # Example of scientific explanation
    prompt = "Explain quantum entanglement in simple terms"
    print("Bot: ", end="", flush=True)
    for chunk in chat.chat(prompt):
        print(chunk, end="", flush=True)
    print("\n")

if __name__ == "__main__":
    anthropic_example() 