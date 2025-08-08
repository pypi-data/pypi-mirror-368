import os
from common_ai_core.providers import ProviderBuilder, ProviderType
from common_ai_core.chat import CompletionChat
from common_ai_core.memory import SystemTokenLimitedMemory

# DeepSeek example
provider = (
    ProviderBuilder(ProviderType.DEEPSEEK)
    .set_api_key(os.getenv("DEEPSEEK_API_KEY"))
    .set_model("deepseek-chat")  # or "deepseek-reasoner" for the reasoning model
    .build()
)
#deepseek-reasoner
#deepseek-chat

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