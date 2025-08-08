from common_ai_core.parsers.json_parser import JsonParser

# Test case 1: Single valid JSON structure
def test_single_valid_json():
    text = 'Here is a JSON: {"key": "value"}'
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == [{"key": "value"}]

# Test case 2: Multiple valid JSON structures
def test_multiple_valid_json():
    text = 'JSON1: {"key1": "value1"} and JSON2: {"key2": "value2"}'
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == [{"key1": "value1"}, {"key2": "value2"}]

# Test case 3: No JSON structures
def test_no_json():
    text = 'This text has no JSON.'
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == []

# Test case 4: Invalid JSON structure
def test_invalid_json():
    text = 'Invalid JSON: {"key": "value" and {"key2": "value2"}'
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == []

# Test case 5: Nested JSON structures
def test_nested_json():
    text = 'Nested JSON: {"outer": {"inner": "value"}}'
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == [{"outer": {"inner": "value"}}]

# Test case 6: JSON with special characters
def test_json_with_special_characters():
    text = 'JSON with special chars: {"key": "value@#!$%^&*()"}'
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == [{"key": "value@#!$%^&*()"}]

# Test case 7: JSON with escaped characters
def test_json_with_escaped_characters():
    text = 'JSON with escaped chars: {"key": "value\\"\\n\\t"}'
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == [{"key": "value\"\n\t"}]

# Test case 8: JSON with numbers and booleans
def test_json_with_numbers_and_booleans():
    text = 'JSON with numbers and booleans: {"number": 123, "boolean": true}'
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == [{"number": 123, "boolean": True}]

# Test case 9: JSON with arrays
def test_json_with_arrays():
    text = 'JSON with arrays: {"array": [1, 2, 3, {"inner": "value"}]}'
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == [{"array": [1, 2, 3, {"inner": "value"}]}]

# Test case 10: JSON with null values
def test_json_with_null_values():
    text = 'JSON with null values: {"key": null}'
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == [{"key": None}]

# Test case 11: Empty input
def test_empty_input():
    text = ''
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == []

# Test case 12: JSON with Unicode characters
def test_json_with_unicode_characters():
    text = 'JSON with Unicode: {"key": "value\\u2122"}'
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == [{"key": "value™"}]

# Test case 13: JSON with floating-point numbers
def test_json_with_floating_point_numbers():
    text = 'JSON with floats: {"key": 123.45}'
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == [{"key": 123.45}]

# Test case 14: JSON with multiple levels of nesting
def test_json_with_multiple_levels_of_nesting():
    text = 'Deeply nested JSON: {"level1": {"level2": {"level3": "value"}}}'
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == [{"level1": {"level2": {"level3": "value"}}}]

# Test case 15: JSON with trailing commas (invalid JSON)
def test_json_with_trailing_commas():
    text = 'Invalid JSON with trailing comma: {"key": "value",}'
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == []

# Test case 16: JSON with comments (invalid JSON)
def test_json_with_comments():
    text = 'Invalid JSON with comment: {"key": "value" /* comment */}'
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == []

# Test case 17: JSON with embedded quotes
def test_json_with_embedded_quotes():
    text = 'JSON with embedded quotes: {"key": "value \\"with quotes\\""}'
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == [{"key": 'value "with quotes"'}]

# Test case 18: JSON with mixed data types
def test_json_with_mixed_data_types():
    text = 'JSON with mixed types: {"string": "value", "number": 123, "boolean": true, "null": null, "array": [1, 2], "object": {"key": "value"}}'
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == [{"string": "value", "number": 123, "boolean": True, "null": None, "array": [1, 2], "object": {"key": "value"}}]

# Test case 19: JSON within markdown code block
def test_json_in_markdown_code_block():
    text = 'Here is the JSON structure you requested:\n\n```json\n{\n  "key": "value"\n}\n```'
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == [{"key": "value"}]

# Test case 20: Multiple JSON structures within markdown code blocks
def test_multiple_json_in_markdown_code_blocks():
    text = 'First JSON:\n\n```json\n{\n  "key1": "value1"\n}\n```\n\nSecond JSON:\n\n```json\n{\n  "key2": "value2"\n}\n```'
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == [{"key1": "value1"}, {"key2": "value2"}]

# Test case 21: JSON with nested structure within markdown code block
def test_nested_json_in_markdown_code_block():
    text = 'Nested JSON structure:\n\n```json\n{\n  "outer": {\n    "inner": "value"\n  }\n}\n```'
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == [{"outer": {"inner": "value"}}]

# Test case 22: JSON with special characters within markdown code block
def test_json_with_special_characters_in_markdown_code_block():
    text = '''JSON with special characters:

```json
{
  "key": "value@#!$%^&*()"
}
```'''
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == [{"key": "value@#!$%^&*()"}]

# Test case 23: JSON with arrays within markdown code block
def test_json_with_arrays_in_markdown_code_block():
    text = 'JSON with arrays:\n\n```json\n{\n  "array": [1, 2, 3, {\n    "inner": "value"\n  }]\n}\n```'
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == [{"array": [1, 2, 3, {"inner": "value"}]}]

# Test case 24: JSON array within markdown code block
def test_json_array_in_markdown_code_block():
    text = '''Here's an array of people:

```json
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
```'''
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == [
        [
            {"name": "Helge", "age": 52, "city": "Stockholm"},
            {"name": "Emma", "age": 45, "city": "Göteborg"},
            {"name": "Inez", "age": 22, "city": "Malmö"}
        ]
    ]

# Test case 25: Markdown code block with language but invalid JSON
def test_invalid_json_in_markdown_code_block():
    text = '''This JSON has a syntax error:

```json
{
  "key": "value",
}
```'''
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == []

# Test case 26: Mixed regular JSON and markdown JSON blocks
def test_mixed_regular_and_markdown_json():
    text = '''Here's a regular JSON object: {"regular": "json"}

And here's one in a markdown block:

```json
{
  "markdown": "json"
}
```'''
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    print(result)
    assert result == [{"markdown": "json"}, {"regular": "json"}]

# Test case 27: Markdown code blocks with other languages
def test_other_language_code_blocks():
    text = '''Python code:

```python
print({"key": "value"})
{
  "key": "value"
}
```'''
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    print(result)
    assert result == [{"key": "value"}, {"key": "value"}]

# Test case 28: Nested objects in array within markdown code block
def test_nested_objects_in_array_markdown():
    text = '''Complex nested structure:

```json
[
  {"id": 1, "data": {"name": "Item 1", "tags": ["tag1", "tag2"]}},
  {"id": 2, "data": {"name": "Item 2", "tags": ["tag3", "tag4"]}}
]
```'''
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == [
        [
            {"id": 1, "data": {"name": "Item 1", "tags": ["tag1", "tag2"]}},
            {"id": 2, "data": {"name": "Item 2", "tags": ["tag3", "tag4"]}}
        ]
    ]

# Test case 29: Markdown block with whitespace variations
def test_markdown_block_with_whitespace_variations():
    text = '''Variations in whitespace:

```json    
  {
    "key": "value"
  }  
```'''
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == [{"key": "value"}]

# Test case 30: Multiple JSON objects in a single markdown block
def test_multiple_objects_in_single_markdown_block():
    text = '''Multiple objects in one block:

```json
{"first": "object"}
{"second": "object"}
```'''
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    # Should parse the whole block as one, and if that fails, extract individual JSONs
    assert result == [{"first": "object"}, {"second": "object"}]

# Test case 31: Non-English text in JSON within markdown
def test_non_english_text_in_markdown_json():
    text = '''JSON with non-English characters:

```json
{
  "swedish": "Här är en text på svenska",
  "russian": "Текст на русском",
  "japanese": "日本語のテキスト"
}
```'''
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == [{"swedish": "Här är en text på svenska", 
                      "russian": "Текст на русском", 
                      "japanese": "日本語のテキスト"}]

# Test case 32: Real-world LLM response example
def test_real_world_llm_response():
    text = '''Här är ett JSON-objekt som beskriver de tre personerna Helge, Emma och Inez:
```json
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
```
Jag har skapat en array med tre objekt där varje objekt representerar en person med attributen name (string), age (int) och city (string), precis enligt specifikationen.
'''
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    assert result == [
    [
    {"name": "Helge", "age": 52, "city": "Stockholm"},
    {"name": "Emma", "age": 45, "city": "Göteborg"},
    {"name": "Inez", "age": 22, "city": "Malmö"}
    ]
    ]

# Test case 32: Real-world LLM response example
def test_multiple_json_objects_in_llm_response():
    text = '''Här är ett JSON-objekt som beskriver de tre personerna Helge, Emma och Inez:
```json

  {
    "name": "Helge",
    "age": 52,
    "city": "Stockholm"
  }
```
Och här kommer en till
```json

  {
    "name": "Emma",
    "age": 45,
    "city": "Göteborg"
  }

```
```json

  {
    "name": "Inez",
    "age": 22,
    "city": "Malmö"
  }

```
Jag har skapat en array med tre objekt där varje objekt representerar en person med attributen name (string), age (int) och city (string), precis enligt specifikationen.
'''
    parser = JsonParser()
    result = parser.extract_json_structures(text)
    print(result)
    assert result == [
        {"name": "Helge", "age": 52, "city": "Stockholm"},
     {"name": "Emma", "age": 45, "city": "Göteborg"},
     {"name": "Inez", "age": 22, "city": "Malmö"}
     ]
    