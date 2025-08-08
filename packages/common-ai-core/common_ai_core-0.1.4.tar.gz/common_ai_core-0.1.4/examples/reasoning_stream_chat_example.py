import sys
import os
import time
# Add the project root directory to Python's module search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common_ai_core.providers import ProviderBuilder, ProviderType
from common_ai_core.chat import ReasoningChat

def test_simple_streaming(provider_type, model_name, prompt):
    """
    Test simple streaming mode for reasoning chat.
    
    Args:
        provider_type: The provider type (OPENAI, ANTHROPIC)
        model_name: The model name to evaluate
        prompt: The reasoning prompt to test
    """
    print(f"\n{'='*80}")
    print(f"Testing simple streaming with {provider_type.name} model: {model_name}")
    print(f"{'='*80}")
    
    # Create provider
    provider = (
        ProviderBuilder(provider_type)
        .set_model(model_name)
        .build()
    )
    
    # Create reasoning chat
    chat = ReasoningChat(provider)
    
    print(f"Prompt: {prompt}")
    print(f"{'-'*80}")
    
    # Stream the response
    print("Streaming response:")
    accumulated_text = ""
    for chunk in chat.chat(prompt, stream=True):
        accumulated_text += chunk
        print(chunk, end="", flush=True)
        time.sleep(0.01)  # Small delay to make streaming visible
    
    print("\n\n")
    
    # Extract reasoning from the full response
    reasoning_data = chat._extract_reasoning(accumulated_text)
    
    print("Extracted reasoning steps:")
    if reasoning_data["reasoning"]:
        for i, step in enumerate(reasoning_data["reasoning"], 1):
            print(f"Step {i}: {step}")
    else:
        print("No structured reasoning steps detected.")
    
    print(f"{'-'*40}")
    print("Extracted answer:")
    print(reasoning_data["answer"])
    print(f"{'-'*80}")

def test_reasoning_stream(provider_type, model_name, prompt):
    """
    Test reasoning-aware streaming mode.
    
    Args:
        provider_type: The provider type (OPENAI, ANTHROPIC)
        model_name: The model name to evaluate
        prompt: The reasoning prompt to test
    """
    print(f"\n{'='*80}")
    print(f"Testing reasoning-aware streaming with {provider_type.name} model: {model_name}")
    print(f"{'='*80}")
    
    # Create provider
    provider = (
        ProviderBuilder(provider_type)
        .set_model(model_name)
        .build()
    )
    
    # Create reasoning chat
    chat = ReasoningChat(provider)
    
    print(f"Prompt: {prompt}")
    print(f"{'-'*80}")
    
    # Stream with reasoning extraction
    print("Streaming with reasoning extraction:")
    
    last_reasoning_count = 0
    for update in chat.chat_with_reasoning_stream(prompt):
        # Print new reasoning steps if any
        if len(update["reasoning"]) > last_reasoning_count:
            print("\n\nNew reasoning steps detected:")
            for i in range(last_reasoning_count, len(update["reasoning"])):
                print(f"Step {i+1}: {update['reasoning'][i]}")
            last_reasoning_count = len(update["reasoning"])
        
        # Print chunk if available
        if "chunk" in update:
            print(update["chunk"], end="", flush=True)
            time.sleep(0.01)  # Small delay to make streaming visible
    
    print("\n\n")
    print("Final reasoning steps:")
    if update["reasoning"]:
        for i, step in enumerate(update["reasoning"], 1):
            print(f"Step {i}: {step}")
    else:
        print("No structured reasoning steps detected.")
    
    print(f"{'-'*40}")
    print("Final answer:")
    print(update["answer"])
    print(f"{'-'*80}")

def main():
    # Test prompt
    prompt = "If a train travels at 60 mph for 2 hours, then at 30 mph for 1 hour, what is the average speed for the entire journey?"
    
    # Define models to test
    models = [
        (ProviderType.OPENAI, "gpt-3.5-turbo"),
        (ProviderType.OPENAI, "gpt-4"),
        (ProviderType.OPENAI, "o3-mini"),
        (ProviderType.ANTHROPIC, "claude-3-5-haiku-20241022"),
        (ProviderType.ANTHROPIC, "claude-3-5-sonnet-20241022"),
        (ProviderType.ANTHROPIC, "claude-3-7-sonnet-20250219"),
    ]
    
    # Test each model with both streaming methods
    for provider_type, model_name in models:
        try:
            # Test simple streaming
            test_simple_streaming(provider_type, model_name, prompt)
            
            # Test reasoning-aware streaming
            test_reasoning_stream(provider_type, model_name, prompt)
            
        except Exception as e:
            print(f"Error testing {provider_type.name} {model_name}: {str(e)}")

if __name__ == "__main__":
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable not set. OpenAI models will fail.")
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Warning: ANTHROPIC_API_KEY environment variable not set. Anthropic models will fail.")
    
    # Run the tests
    main()