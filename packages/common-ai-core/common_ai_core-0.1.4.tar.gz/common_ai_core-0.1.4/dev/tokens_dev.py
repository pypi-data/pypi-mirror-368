import logging
from common_ai_core.tokens.token_counter import TokenCounterFactory
from common_ai_core.memory import TokenLimitedMemory
from common_ai_core.providers import ProviderBuilder, ProviderType
from common_ai_core.types import Message, Role

logging.basicConfig(level=logging.WARNING)
logging.getLogger("common_ai_core").setLevel(logging.DEBUG)


def dev_token_counter_factory():
    inp = input("Which provider?    1) Anthropic    2) OpenAI    3) Llama ")
    if inp == "1":
        provider = ProviderBuilder(ProviderType.ANTHROPIC).build()
    elif inp == "2":
        provider = ProviderBuilder(ProviderType.OPENAI).build()
    elif inp == "3":
        provider = ProviderBuilder(ProviderType.LLAMA).build()

    token_counter = TokenCounterFactory.from_provider(provider)
    text_tokens = token_counter.count_tokens_in_text("Hello world!")
    print(text_tokens)
    message = Message(Role.USER, "Hello world!")
    message_tokens = token_counter.count_tokens_in_messages([message])
    print(message)
    print(message_tokens)   


if __name__ == "__main__":
    dev_token_counter_factory()