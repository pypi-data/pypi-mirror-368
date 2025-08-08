from common_ai_core import (
    ProviderBuilder, 
    ProviderType, 
    CompletionChat,
    PromptLimitedMemory
)
import os

def llama_example():
    # Create Llama provider with local model
    model_path = os.getenv("LLAMA_MODEL_PATH", "path/to/your/model.gguf")
    provider = (ProviderBuilder(ProviderType.LLAMA)
               .set_model_path(model_path)
               .set_temperature(0.7)
               .build())
    
    # Use prompt-limited memory for local model
    memory = PromptLimitedMemory(max_prompts=5)
    
    chat = CompletionChat(provider, memory)
    
    # Example conversation
    prompts = [
        "What is your favorite programming language?",
        "Why do you like it?",
        "What are its main features?"
    ]
    
    for prompt in prompts:
        print(f"\nUser: {prompt}")
        response = chat.chat(prompt)
        print(f"Bot: {response}")

if __name__ == "__main__":
    llama_example() 