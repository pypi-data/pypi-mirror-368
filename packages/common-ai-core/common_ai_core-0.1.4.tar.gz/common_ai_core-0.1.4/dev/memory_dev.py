from common_ai_core.memory import TokenLimitedMemory, PromptLimitedMemory, SystemTokenLimitedMemory, SystemPromptLimitedMemory
from common_ai_core.providers import ProviderBuilder, ProviderType
from common_ai_core.types import Message, Role
from common_ai_core.chat import CompletionChat
import logging

logging.basicConfig(level=logging.WARNING)
logging.getLogger("common_ai_core").setLevel(logging.DEBUG)

def dev_token_memory():
    provider = ProviderBuilder(ProviderType.ANTHROPIC).build()
    memory = TokenLimitedMemory.from_provider(provider, 10)
    while True:
        user_input = input("Enter a user message (exit to quit): ")
        if user_input.lower() == "exit":
            break
        message = Message(Role.USER, user_input)
        memory.add(message)
        memory.pretty_print()

def dev_system_memory_token_limited():
    provider = ProviderBuilder(ProviderType.ANTHROPIC).build()
    sysPrompt = """
    You are a helpful assistant.
    """
    memory = SystemTokenLimitedMemory.from_provider(provider, sysPrompt, 50, 10, True)
    while True:
        user_input = input("Enter a user message (exit to quit): ")
        if user_input.lower() == "exit":
            break
        message = Message(Role.USER, user_input)
        memory.add(message)
        memory.pretty_print()
        assistant_input = input("Enter a assistant message (exit to quit): ")
        if user_input.lower() == "exit":
            break
        message = Message(Role.ASSISTANT, assistant_input)
        memory.add(message)
        memory.pretty_print()

def dev_system_memory_prompt_limited():
    sysPrompt = """
    You are a helpful assistant. You always answer in Swedish. 
    You always use a joke in your answers. 
    Then you answer the question.
    """
    memory = SystemPromptLimitedMemory(sysPrompt, 5)
    while True:
        user_input = input("Enter a user message (exit to quit): ")
        if user_input.lower() == "exit":
            break
        message = Message(Role.USER, user_input)
        memory.add(message)
        memory.pretty_print()
        assistant_input = input("Enter a assistant message (exit to quit): ")
        message = Message(Role.ASSISTANT, assistant_input)
        memory.add(message)
        memory.pretty_print()

def test_system_prompt_chat():
    provider = ProviderBuilder(ProviderType.ANTHROPIC).set_model("claude-3-5-sonnet-20241022").build()
    sysPrompt2 = """
    Du ska skriva quizzfrågor. Jag ger dig ett ämne och du skapar en fråga och svar. 
    En fråga ska ha tre svarsalternativ var av endast ett ska vara rätt. 
    Du ska skriva ut frågan och tre svarsalternativ. Svaret ska vara en bokstav A, B eller C.
    Packa frågan i lämpligt json-format.
    """
    sysPrompt = """
    You are a helpful assistant. You always answer in Swedish. 
    You always use a joke in your answers. 
    Then you answer the question.
    """
    memory = SystemPromptLimitedMemory(sysPrompt, 5)
    chatbot = CompletionChat(provider, memory)
    while True:
        user_input = input("Enter a user message (exit to quit): ")
        if user_input.lower() == "exit":
            break
        full_ans = chatbot.chat(user_input)
        print(full_ans)
        memory.pretty_print()

if __name__ == "__main__":
    test_system_prompt_chat()
