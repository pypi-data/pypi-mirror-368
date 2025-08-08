import sys
import os
import json
# Add the project root directory to Python's module search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common_ai_core.providers import ProviderBuilder, ProviderType
from common_ai_core.chat import ReasoningChat

def evaluate_model(provider_type, model_name, prompt):
    """
    Evaluate a specific model's reasoning capabilities.
    
    Args:
        provider_type: The provider type (OPENAI, ANTHROPIC)
        model_name: The model name to evaluate
        prompt: The reasoning prompt to test
        
    Returns:
        dict: The model's response
    """
    print(f"\n{'='*80}")
    print(f"Evaluating {provider_type.name} model: {model_name}")
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
    
    # Get response with reasoning steps
    response = chat.chat(prompt)
    
    print("Reasoning steps:")
    if response["reasoning"]:
        for i, step in enumerate(response["reasoning"], 1):
            print(f"Step {i}: {step}")
    else:
        print("No structured reasoning steps detected.")
    
    print(f"{'-'*40}")
    print("Final answer:")
    print(response["answer"])
    print(f"{'-'*80}")
    
    return response

def main():
    # Test prompt
    prompt = "If a train travels at 60 mph for 2 hours, then at 30 mph for 1 hour, what is the average speed for the entire journey?"
    
    """
    import anthropic
    client = anthropic.Anthropic()
    models = client.models.list(limit=20)
    for m in models:
        print(m)
"""
    # Define models to evaluate
    """
    models = [
        (ProviderType.OPENAI, "gpt-3.5-turbo"),
        (ProviderType.OPENAI, "gpt-4"),
        (ProviderType.OPENAI, "o3-mini"),
        (ProviderType.ANTHROPIC, "claude-3-5-haiku-20241022"),
        (ProviderType.ANTHROPIC, "claude-3-5-sonnet-20241022"),
        (ProviderType.ANTHROPIC, "claude-3-7-sonnet-20250219"),
    ]
    """
    models = [
        (ProviderType.GEMINI, "gemini-2.0-flash"),
        (ProviderType.DEEPSEEK, "deepseek-reasoner"),
        #(ProviderType.ANTHROPIC, "claude-3-5-haiku-20241022"),
        #(ProviderType.ANTHROPIC, "claude-3-5-sonnet-20241022"),
        (ProviderType.ANTHROPIC, "claude-3-7-sonnet-20250219"),
    ]
    
    results = {}
    
    # Evaluate each model
    for provider_type, model_name in models:
        try:
            response = evaluate_model(provider_type, model_name, prompt)
            
            # Store results
            results[f"{provider_type.name}_{model_name}"] = {
                "has_reasoning": len(response["reasoning"]) > 0,
                "reasoning_steps": len(response["reasoning"]),
                "answer": response["answer"]
            }
        except Exception as e:
            print(f"Error evaluating {provider_type.name} {model_name}: {str(e)}")
            results[f"{provider_type.name}_{model_name}"] = {
                "error": str(e)
            }
    
    # Print summary
    print("\n\nSUMMARY OF RESULTS")
    print("=" * 80)
    print(f"{'Model':<30} | {'Has Reasoning':<15} | {'Steps':<8} | {'Answer Length':<15}")
    print("-" * 80)
    
    for model, data in results.items():
        if "error" in data:
            print(f"{model:<30} | {'ERROR':<15} | {'N/A':<8} | {data['error'][:30]}")
        else:
            print(f"{model:<30} | {str(data['has_reasoning']):<15} | {data['reasoning_steps']:<8} | {len(data['answer']):<15}")

if __name__ == "__main__":
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable not set. OpenAI models will fail.")
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Warning: ANTHROPIC_API_KEY environment variable not set. Anthropic models will fail.")
    
    # Run the evaluation
    main()