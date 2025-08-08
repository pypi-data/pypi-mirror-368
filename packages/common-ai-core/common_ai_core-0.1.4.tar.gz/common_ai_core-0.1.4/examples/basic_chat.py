from common_ai_core import ProviderBuilder, ProviderType, CompletionChat

def basic_chat_example():
    # Create a provider (using OpenAI as default)
    provider = (ProviderBuilder(ProviderType.ANTHROPIC)
               .set_model("claude-3-5-sonnet-20240620")
               .set_temperature(0.7)
               .build())
    
    # Create chat interface
    chat = CompletionChat(provider)
    
    # Single interaction
    response = chat.chat("What is Python?")
    print("Bot:", response)
    
    # Multiple interactions
    questions = [
        "What are Python's main features?",
        "How does Python handle memory management?",
        "What is the difference between Python 2 and 3?"
    ]
    
    for question in questions:
        print("\nUser:", question)
        response = chat.chat(question)
        print("Bot:", response)

if __name__ == "__main__":
    basic_chat_example() 