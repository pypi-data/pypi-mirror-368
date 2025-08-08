from common_ai_core.providers import ProviderBuilder, ProviderType, Message

def test_providers_openai():
    provider = ProviderBuilder(ProviderType.OPENAI).set_model("gpt-4o-mini").build()
    messages = {"role": "user", "content": "hej hej"}
    resp = provider.generate_completion([messages], stream=False)
    resptext = provider.get_message_content(resp, stream=False)
    print(resptext)


def test_providers_anthropic():
    provider = ProviderBuilder(ProviderType.ANTHROPIC).set_model("claude-3-5-sonnet-20241022").build()
    messages = [{"role": "user", "content": "hej hej"}]
    resp = provider.generate_completion(messages, stream=False)
    resptext = provider.get_message_content(resp, stream=False)
    print(resptext)

def test_providers_llama():
    print("NO LLAMA MODEL YET")

if __name__ == "__main__":
    inp = input("Vilken provider vill du testa? (openai (1), anthropic (2), llama (3)")
    if inp == "1":
        test_providers_openai()
    elif inp == "2":
        test_providers_anthropic()
    elif inp == "3":
        test_providers_llama()
