import os
from common_ai_core import ProviderBuilder, ProviderType, CompletionChat
from common_ai_core.memory import SystemTokenLimitedMemory

# Create Gemini provider
provider = (ProviderBuilder(ProviderType.GEMINI)
           .set_api_key(os.getenv("GEMINI_API_KEY"))
           .set_model("gemini-2.0-flash-lite")
           .build())

# Create memory with system prompt - automatically handles Gemini's limitations
memory = SystemTokenLimitedMemory.from_provider(
    provider=provider,
    system_prompt="Du är en quizmaster som skapar quiz-frågor utifrån ämne, kategori och subkategori. En fråga, tre svarsalternativ varav endast ett ska vara rätt. ",
    max_tokens=1000
)

# Create chat interface
chatbot = CompletionChat(provider, memory)

# Chat!
while True:
    inp = input("You: (exit to quit)")
    if inp == "exit":
        break
    response = chatbot.chat(inp)
    print(response) 