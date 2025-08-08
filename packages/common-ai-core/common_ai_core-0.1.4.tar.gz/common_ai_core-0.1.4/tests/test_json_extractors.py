from common_ai_core.parsers.json_parser import JsonParser
from common_ai_core.parsers.json_validator import JsonTemplateValidator


class TestJsonParser:
    def test_extract_json_from_plain_text(self):
        parser = JsonParser()
        text = 'Here is a JSON object: {"name": "John", "age": 30}'
        result = parser.extract_json_structures(text)
        
        assert len(result) == 1
        assert result[0] == {"name": "John", "age": 30}
    
    def test_extract_json_from_markdown(self):
        parser = JsonParser()
        text = '''Here is a JSON object in markdown:
        json
        {
        "name": "John",
        "age": 30
        }
        '''
        result = parser.extract_json_structures(text)
        
        assert len(result) == 1
        assert result[0] == {"name": "John", "age": 30}
    
    def test_extract_multiple_json_objects(self):
        parser = JsonParser()
        text = '''Two JSON objects:
{"name": "John", "age": 30}
{"name": "Jane", "age": 25}'''
        result = parser.extract_json_structures(text)
        
        assert len(result) == 2
        assert {"name": "John", "age": 30} in result
        assert {"name": "Jane", "age": 25} in result
    
    def test_extract_nested_json(self):
        parser = JsonParser()
        text = '''Complex JSON:
{
  "people": [
    {"name": "John", "age": 30},
    {"name": "Jane", "age": 25}
  ]
}'''
        result = parser.extract_json_structures(text)
        
        assert len(result) == 1
        assert result[0] == {
            "people": [
                {"name": "John", "age": 30},
                {"name": "Jane", "age": 25}
            ]
        }

    def test_extract_json_array(self):
        parser = JsonParser()
        text = '''JSON array:
[
  {"name": "John", "age": 30},
  {"name": "Jane", "age": 25}
]'''
        result = parser.extract_json_structures(text)
        
        assert len(result) == 1
        assert result[0] == [
            {"name": "John", "age": 30},
            {"name": "Jane", "age": 25}
        ]
    
    def test_invalid_json(self):
        parser = JsonParser()
        text = '''Invalid JSON:
{
  "name": "John",
  "age": 30,
}'''  # Extra comma makes this invalid
        result = parser.extract_json_structures(text)
        
        assert len(result) == 0

    
class TestJsonTemplateValidator:
    def test_basic_template_validation(self):
        template = {
            "name": "string_value",
            "age": 0
        }
        validator = JsonTemplateValidator(template)
        
        valid_obj = {"name": "John", "age": 30}
        invalid_obj1 = {"name": "John"}  # Missing age
        invalid_obj2 = {"name": "John", "age": "30"}  # Age is string, not int
        
        assert validator.validate_against_template(valid_obj) is True
        assert validator.validate_against_template(invalid_obj1) is False
        assert validator.validate_against_template(invalid_obj2) is False
    
    def test_nested_template_validation(self):
        template = {
            "person": {
                "name": "string_value",
                "age": 0
            }
        }
        validator = JsonTemplateValidator(template)
        
        valid_obj = {"person": {"name": "John", "age": 30}}
        invalid_obj = {"person": {"name": "John"}}  # Missing age
        
        assert validator.validate_against_template(valid_obj) is True
        assert validator.validate_against_template(invalid_obj) is False
    
    def test_array_template_validation(self):
        template = {
            "people": [
                {
                    "name": "string_value",
                    "age": 0
                }
            ]
        }
        validator = JsonTemplateValidator(template)
        
        valid_obj = {
            "people": [
                {"name": "John", "age": 30},
                {"name": "Jane", "age": 25}
            ]
        }
        invalid_obj = {
            "people": [
                {"name": "John", "age": 30},
                {"name": "Jane"}  # Missing age
            ]
        }
        
        assert validator.validate_against_template(valid_obj) is True
        assert validator.validate_against_template(invalid_obj) is False
    
    def test_extract_matching_objects_simple(self):
        template = {
            "name": "string_value",
            "age": 0
        }
        validator = JsonTemplateValidator(template)
        
        text = '''Here are some people:
{"name": "John", "age": 30}
{"name": "Jane", "age": 25}
{"name": "Bob"}  # This one is missing age
'''
        result = validator.extract_matching_objects(text)
        
        assert len(result) == 2
        assert {"name": "John", "age": 30} in result
        assert {"name": "Jane", "age": 25} in result
    
    def test_extract_matching_objects_nested(self):
        template = {
            "name": "string_value",
            "age": 0,
            "city": "string_value"
        }
        validator = JsonTemplateValidator(template)
        
        text = '''Here is a complex structure:
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
        }
    ],
    "cats": [
        {
            "catname": "Mia",
            "catage": 3,
            "catcolor": "black"
        }
    ]
}'''
        result = validator.extract_matching_objects(text)
        
        assert len(result) == 2
        assert {"name": "Helge", "age": 52, "city": "Stockholm"} in result
        assert {"name": "Emma", "age": 45, "city": "Göteborg"} in result
    
    def test_template_from_string(self):
        template_str = '{"name": "string_value", "age": 0}'
        validator = JsonTemplateValidator(template_str)
        
        valid_obj = {"name": "John", "age": 30}
        
        assert validator.validate_against_template(valid_obj) is True
    
    def test_custom_parser(self):
        template = {"name": "string_value", "age": 0}
        
        # Create a custom parser that always returns a specific result
        class MockParser:
            def extract_json_structures(self, text):
                return [{"name": "Mock", "age": 99}]
        
        validator = JsonTemplateValidator(template, parser=MockParser())
        result = validator.extract_matching_objects("any text")
        
        assert len(result) == 1
        assert result[0] == {"name": "Mock", "age": 99}