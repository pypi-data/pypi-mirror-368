import sys
import os
import json
# Add the project root directory to Python's module search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common_ai_core.chat import CompletionChat, StreamingChat
from common_ai_core.providers import ProviderBuilder, ProviderType
from common_ai_core.memory import TokenLimitedMemory, SystemPromptLimitedMemory
from common_ai_core.tokens.token_tracker import TokenTracker
import logging

logging.basicConfig(level=logging.WARNING)
logging.getLogger("common_ai_core").setLevel(logging.DEBUG)


def test_chat_completion():
    inp = input("Vilken provider vill du testa? (openai (1), anthropic (2), llama (3)")
    if inp == "1":
        provider = ProviderBuilder(ProviderType.OPENAI).set_model("gpt-4o-mini").build()
    elif inp == "2":
        model1 = "claude-3-sonnet-20240229" # OBS!! FINNS EJ!!
        model2 = "claude-3-5-sonnet-20241022"
        model3 = "claude-3-7-sonnet-20250219"
        provider = ProviderBuilder(ProviderType.ANTHROPIC).set_model(model1).build()
    elif inp == "3":
        print("NO LLAMA MODEL YET")
        #model = "/Users/helgemoden/Programming/AI/_Models/llama-2-7b-chat.Q4_K_M.gguf"
       # provider = ProviderBuilder(ProviderType.LLAMA).set_model_path(model).build()
    
    token_tracker = TokenTracker()
    token_tracker_none = None
    memory = TokenLimitedMemory.from_provider(provider, max_tokens=500, verbose=True)
    memorynew = SystemPromptLimitedMemory("Du är en hjälpsam assistent som svarar på frågor.", 5, verbose=True)
    chatbot = CompletionChat(provider, memory, token_tracker, verbose=True)

    while True:
        prompt = input(">  ")
        response = chatbot.chat(prompt)
        print("")
        print(f"Response> {response}")
        print(memory.pretty_print())
        print(f"token_tracker.get_token_counts(): {token_tracker.get_token_counts()}")

def test_chat_streaming():
    inp = input("Vilken provider vill du testa? (openai (1), anthropic (2), llama (3)")
    if inp == "1":
        provider = ProviderBuilder(ProviderType.OPENAI).set_model("gpt-4o-mini").build()
    elif inp == "2":
        provider = ProviderBuilder(ProviderType.ANTHROPIC).set_model("claude-3-5-sonnet-20241022").build()
    elif inp == "3":
        print("NO LLAMA MODEL YET")
        return
        #model = "/Users/helgemoden/Programming/AI/_Models/llama-2-7b-chat.Q4_K_M.gguf"
       # provider = ProviderBuilder(ProviderType.LLAMA).set_model_path(model).build()

    system_promptold = """
    Du faktagranskar alltid dina svar. Om du är osäker på någon fakta, så svara det och be om mer information. 
    Svara alltid på svenska. Och svara alltid i kortfattat språk.
    """
    system_prompt = """
    Du är en clown och ska alltid skoja. Du ger aldrig seriösa svar. 
    """

    
    memoryold = TokenLimitedMemory.from_provider(provider, max_tokens=2048, verbose=True)
    memory = SystemPromptLimitedMemory(system_prompt, 10, verbose=True)
    chatbot = StreamingChat(provider, memory, verbose=True) 

    while True:
        prompt = input(">  ")
        for chunk in chatbot.chat(prompt):
            print(chunk, end="", flush=True)
        print() 
        print(memory.pretty_print())
        

if __name__ == "__main__":
    test_chat_completion()
    #test_chat_streaming()
