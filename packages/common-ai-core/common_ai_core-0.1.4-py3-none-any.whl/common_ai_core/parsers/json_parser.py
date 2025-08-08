import json
import re
import ast

class JsonParser:
    def __init__(self):
        pass
    
    def extract_json_structures(self, text):
        """Extract complete and valid JSON structures from text.
        
        Returns:
            list: List of parsed JSON objects
        """
        json_structures = []
        
        # Extract JSON from markdown code blocks
        markdown_pattern = r'```json\s*([\s\S]*?)\s*```'
        markdown_matches = re.findall(markdown_pattern, text)
        
        for json_text in markdown_matches:
            try:
                json_obj = json.loads(json_text)
                json_structures.append(json_obj)
            except json.JSONDecodeError:
                # If the entire block doesn't parse as JSON, try to find JSON objects within it
                self._extract_json_objects(json_text, json_structures)
        
        # Always extract JSON from the entire text as well
        # First, create a version of the text with markdown blocks removed to avoid duplicates
        text_without_markdown = re.sub(markdown_pattern, '', text)
        self._extract_json_objects(text_without_markdown, json_structures)
            
        return json_structures
    
    def _extract_json_objects(self, text, json_structures):
        """Extract JSON objects from text based on brace matching."""
        start_idx = 0
        
        while start_idx < len(text):
            try:
                # Find the start of a JSON object or array
                start_char_idx = text.find('{', start_idx)
                start_array_idx = text.find('[', start_idx)
                
                # Determine which comes first, array or object
                if start_char_idx == -1 and start_array_idx == -1:
                    break
                elif start_char_idx == -1:
                    start_idx = start_array_idx
                    open_char, close_char = '[', ']'
                elif start_array_idx == -1:
                    start_idx = start_char_idx
                    open_char, close_char = '{', '}'
                else:
                    if start_array_idx < start_char_idx:
                        start_idx = start_array_idx
                        open_char, close_char = '[', ']'
                    else:
                        start_idx = start_char_idx
                        open_char, close_char = '{', '}'
                
                balance = 0
                
                # Find the end of the JSON structure
                for end_idx in range(start_idx, len(text)):
                    if text[end_idx] == open_char:
                        balance += 1
                    elif text[end_idx] == close_char:
                        balance -= 1
                    
                    if balance == 0:
                        # Extract and validate the JSON substring
                        json_substring = text[start_idx:end_idx + 1]
                        try:
                            # First try standard JSON parsing
                            json_obj = json.loads(json_substring)
                            json_structures.append(json_obj)
                        except json.JSONDecodeError as e:
                            # Check for trailing comma error specifically
                            if "Expecting property name enclosed in double quotes" in str(e) or "Expecting ',' delimiter" in str(e):
                                # Trailing comma detected, skip this structure
                                pass
                            else:
                                try:
                                    # If that fails, try using ast.literal_eval which can handle Python literals
                                    # including dictionaries with single quotes
                                    json_obj = ast.literal_eval(json_substring)
                                    json_structures.append(json_obj)
                                except (SyntaxError, ValueError):
                                    pass  # Invalid JSON/Python literal, skip it
                        break
                
                # Move to next potential JSON object
                start_idx = end_idx + 1 if 'end_idx' in locals() else start_idx + 1
                
            except (ValueError, IndexError):
                break