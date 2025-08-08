from common_ai_core import ProviderBuilder, ProviderType, CompletionChat

def openai_example():
    # Create OpenAI provider with custom settings
    provider = (ProviderBuilder(ProviderType.OPENAI)
               .set_model("gpt-4")
               .set_temperature(0.8)
               .set_max_tokens(500)
               .build())
    
    chat = CompletionChat(provider)
    
    # Example of creative writing with higher temperature
    prompt = "Write a short, creative story about a robot learning to paint"
    response = chat.chat(prompt)
    print(response)

if __name__ == "__main__":
    openai_example() 