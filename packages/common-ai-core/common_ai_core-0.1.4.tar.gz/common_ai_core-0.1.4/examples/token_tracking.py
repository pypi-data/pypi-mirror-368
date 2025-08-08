from common_ai_core import (
    ProviderBuilder, 
    ProviderType, 
    CompletionChat,
    TokenTracker
)

from common_ai_core.tokens.token_tracker import ModelPricing
def token_tracking_example():
    # Create provider and token tracker
    #provider = ProviderBuilder(ProviderType.ANTHROPIC).set_model("claude-3-opus-20240229").build()
    provider = ProviderBuilder(ProviderType.GEMINI).set_model("gemini-2.0-flash-lite").build()
    model_pricing = ModelPricing(input_price=0.0025, output_price=0.01)
    tracker = TokenTracker(pricing=model_pricing)
    
    # Create chat with token tracking
    chat = CompletionChat(
        llm_provider=provider,
        token_tracker=tracker
    )
    
    # Generate some responses
    prompts = [
        "Write a haiku about Python",
        "Explain what an API is",
        "Tell me about machine learning"
    ]
    
    for prompt in prompts:
        print(f"\nUser: {prompt}")
        response = chat.chat(prompt)
        print(f"Bot: {response}")
        
        # Print token usage after each interaction
        print("\nToken Usage:")
        print(f"Input tokens: {tracker.get_token_counts()[0]}")
        print(f"Output tokens: {tracker.get_token_counts()[-1]}")
        print(f"Total tokens: {tracker.get_token_counts()}")
        if tracker.pricing:
            print(f"Estimated cost: ${tracker.get_cost_estimate():.4f}")

if __name__ == "__main__":
    token_tracking_example() 