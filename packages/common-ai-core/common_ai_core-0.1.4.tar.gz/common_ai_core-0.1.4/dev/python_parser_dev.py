# Example usage with an LLM API
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common_ai_core.parsers.code_parser import CodeParser, CodeFileSaver
from common_ai_core.chat import CompletionChat
from common_ai_core.providers import ProviderBuilder, ProviderType

def ask_llm_for_code(prompt):
    provider = ProviderBuilder(ProviderType.OPENAI).set_model("gpt-4o-mini").build()
    chat = CompletionChat(provider)
    response = chat.chat(prompt)
    return response

# Get response from LLM
prompt = "Write a Python function that calculates the Fibonacci sequence"
llm_response = ask_llm_for_code(prompt)

# Create the parser with a custom output directory
extractor = CodeParser()
code_blocks = extractor.extract_code_blocks(llm_response)

# Process the response and save code blocks with a specific filename base
saver = CodeFileSaver(output_directory="llm_generated_code")
saved_files = saver.save_multiple_code_blocks(code_blocks, "fibonacci")