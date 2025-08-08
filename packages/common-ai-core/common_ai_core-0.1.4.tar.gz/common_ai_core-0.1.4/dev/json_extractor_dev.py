
import sys
import os
import json
# Add the project root directory to Python's module search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common_ai_core.parsers.json_validator import JsonTemplateValidator
from common_ai_core.parsers.json_parser import JsonParser
from common_ai_core.providers import ProviderBuilder, ProviderType
from common_ai_core.chat import CompletionChat
from common_ai_core.memory import SystemPromptLimitedMemory
def test1():# Define your template
    template = {
        "name": "string_value",
        "age": 0,  # Using 0 as a placeholder for any integer
        "city": "string_value"
    }

    # Create validator
    validator = JsonTemplateValidator(template, JsonParser())

    # LLM response
    llm_response = """Here is JSON-objektet with three persons:

    {
        "persons": [
            {
                "name": "Helge",
                "age": 52,
                "city": "Stockholm"
            },
            {
                "name": "Emma",
                "age": 45,
                "city": "Göteborg"
            },
            {
                "name": "Inez",
                "age": 22,
                "city": "Malmö"
            }
        ],
        "cats": [
            {
                "catname": "Mia",
                "catage": 3,
                "catcolor": "black"
            }
        ]
    }"""

    # Extract objects matching the template
    matching_objects = validator.extract_matching_objects(llm_response)
    #print(matching_objects)
    for obj in matching_objects:
        print(obj)
    # Output: [
    #   {"name": "Helge", "age": 52, "city": "Stockholm"},
    #   {"name": "Emma", "age": 45, "city": "Göteborg"},
    #   {"name": "Inez", "age": 22, "city": "Malmö"}
    # ]

def test2():
    template = {
        "name": "string_value",
        "age": 0,  # Using 0 as a placeholder for any integer
        "city": "string_value"
    }
    provider = (
        ProviderBuilder(ProviderType.ANTHROPIC)
        .set_model("claude-3-5-sonnet-20240620")
        .build()
    )

    chat = CompletionChat(provider)
    prompt = f"""
    Make up three persons and answer in the following JSON format:

    {json.dumps(template, indent=4)}
    """
    ans = chat.chat(prompt)
    print(ans)
    validator = JsonTemplateValidator(template, JsonParser())
    matching_objects = validator.extract_matching_objects(ans)
    for obj in matching_objects:
        print(obj)

def test3():
    template = {
        "question": "string_value",
        "answer_alternatives": ["string_value", "string_value", "string_value"],
        "correct_answer": "string_value"
    }
    provider = (
        ProviderBuilder(ProviderType.ANTHROPIC)
        .set_model("claude-3-5-sonnet-20240620")
        .build()
    )
    
    sysPrompt = f"""
    Du är en quizmaster som skapar frågor och svar. Du får ett ämne (topic) och ett underämne (subtopic).
    Du får även en region (region) som frågorna ska vara relaterade till.
    Du skapar frågor och för varje fråga tre olika svarsalternativ på givna frågan.
    Frågan och svaren ska vara lättlästa och förståeliga för en människa.
    Svaren ska vara lättlästa och förståeliga för en människa.
    Du ska svara på följande format:
    {json.dumps(template, indent=4)}
    """
    memory = SystemPromptLimitedMemory(sysPrompt, 10)
    chat = CompletionChat(provider, memory=memory)

    topic = "Konst"
    subtopic = "Kända konstnärer"
    region = "Australien"
    num_questions = 5

    prompt = f"""
    Skapa {num_questions} frågor med följande ämne, subämne och region:
    Ämne: {topic} subämne: {subtopic} region: {region}
    """
    ans = chat.chat(prompt)
    print(ans)
    validator = JsonTemplateValidator(template, JsonParser())
    matching_objects = validator.extract_matching_objects(ans)
    for obj in matching_objects:
        print(obj)

def test4():
    
    template = {
        "name": "<name of the person>",
        "age": 0,
        "city": "<city of the person>"
    }
    """
    template = {
        "name": "string_value",
        "age": 0,
        "city": "string_value"
    }
    """
    ans = """
    Här är JSON-objektet med de tre personerna enligt mallen:

[
    {
        "name": "Helge",
        "age": 52,
        "city": "Stockholm"
    },
    {
        "name": "Emma",
        "age": 45,
        "city": "Göteborg"
    },
    {
        "name": "Inez",
        "age": 22,
        "city": "Malmö"
    }
]
    """
    ansSingleQ = """
    Här är JSON-objektet med de tre personerna enligt mallen:

[
    {
        'name': 'Helge',
        'age': 52,
        'city': 'Stockholm'
    },
    {
        'name': 'Emma',
        'age': 45,
        'city': 'Göteborg'
    },
    {
        'name': 'Inez',
        'age': 22,
        'city': 'Malmö'
    }
]
    """
    print(ans)
    validator = JsonTemplateValidator(template, JsonParser())
    matching_objects = validator.extract_matching_objects(ans)
    matching_objectsSingleQ = validator.extract_matching_objects(ansSingleQ)
    for obj in matching_objects:
        print(obj)
    print("--------------------------------")
    for obj in matching_objectsSingleQ:
        print(obj)

def test5():
    template = {
        "approved": True,
        "comment": "string_value"
    }
    ans = """
    {"approved": true, "comment": "Den angivna korrekta lösningen 'Astrid Lindgren' är korrekt. Astrid Lindgren är en internationellt känd svensk barnboksförfattare som skapade karaktärer som Pippi Långstrump, Emil i Lönneberga och många fler. Även om Barbro Lindgren och Per Gustavsson också är svenska barnboksförfattare, är Astrid Lindgren utan tvekan den mest kända av de tre alternativen. Frågan är tydlig och svarsalternativen är rimliga."}
    """
    validator = JsonTemplateValidator(template, JsonParser())
    matching_objects = validator.extract_matching_objects(ans)
    for obj in matching_objects:
        print(obj)

if __name__ == "__main__":
    test5()