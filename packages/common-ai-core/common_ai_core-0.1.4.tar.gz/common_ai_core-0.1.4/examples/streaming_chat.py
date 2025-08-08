from common_ai_core import ProviderBuilder, ProviderType, StreamingChat
import time

def streaming_chat_example():
    # Create a provider
    provider = (ProviderBuilder(ProviderType.ANTHROPIC)
               .set_model("claude-3-opus-20240229")
               .build())
    
    # Create streaming chat interface
    chat = StreamingChat(provider)
    
    print("Bot is generating a story...")
    prompt = "Tell me a short story about a programmer who discovers AI"
    
    # Stream the response
    print("\nBot: ", end="", flush=True)
    for chunk in chat.chat(prompt):
        print(chunk, end="", flush=True)
        time.sleep(0.02)  # Optional: simulate realistic typing
    print("\n")

if __name__ == "__main__":
    streaming_chat_example() 