from common_ai_core.parsers.json_validator import JsonTemplateValidator
from common_ai_core.parsers.json_parser import JsonParser
# Define your template
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
    print(obj)# Output: [
#   {"name": "Helge", "age": 52, "city": "Stockholm"},
#   {"name": "Emma", "age": 45, "city": "Göteborg"},
#   {"name": "Inez", "age": 22, "city": "Malmö"}
# ]
