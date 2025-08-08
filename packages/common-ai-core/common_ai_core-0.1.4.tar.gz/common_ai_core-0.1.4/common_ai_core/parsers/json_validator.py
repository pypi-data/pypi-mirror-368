import json
import re
from typing import Dict, List, Any, Union, Optional

from .json_parser import JsonParser

class JsonTemplateValidator:
    """Validates and extracts JSON objects that match a specified template."""
    
    def __init__(self, template: Union[str, Dict], parser: Optional[JsonParser] = None):
        """
        Initialize with a JSON template and optional parser.
        
        Args:
            template: A JSON template string or dictionary
            parser: A JsonParser instance (creates a new one if None)
        """
        self.parser = parser or JsonParser()
        
        if isinstance(template, str):
            # Try to parse the template string
            try:
                self.template = json.loads(template)
            except json.JSONDecodeError:
                # If it's not valid JSON, try to extract JSON from the string
                extracted = self.parser.extract_json_structures(template)
                if extracted:
                    self.template = extracted[0]
                else:
                    raise ValueError("Could not parse template as valid JSON")
        else:
            self.template = template
    
    def validate_against_template(self, data: Any, template: Any = None) -> bool:
        """
        Recursively validate if data matches the template structure.
        
        Args:
            data: The data to validate
            template: The template to validate against (uses self.template if None)
            
        Returns:
            bool: True if data matches template structure, False otherwise
        """
        if template is None:
            template = self.template
            
        # Check basic type compatibility
        if isinstance(template, dict):
            if not isinstance(data, dict):
                return False
                
            # Check if all required keys from template exist in data
            for key in template:
                if key not in data:
                    return False
                
                # Recursively validate nested structures
                if not self.validate_against_template(data[key], template[key]):
                    return False
                    
            return True
            
        elif isinstance(template, list):
            if not isinstance(data, list):
                return False
                
            # If template list has items, validate each data item against template item
            if template:
                template_item = template[0]
                return all(self.validate_against_template(item, template_item) for item in data)
            return True
            
        # For primitive types, check type compatibility only, not exact values
        elif isinstance(template, int):
            return isinstance(data, int)
        elif isinstance(template, float):
            return isinstance(data, (int, float))  # Allow integers where floats are expected
        elif isinstance(template, str):
            # Special case: if template is "string_value" or starts with "<" and ends with ">", 
            # it's a placeholder for any string
            if template == "string_value" or (template.startswith("<") and template.endswith(">")):
                return isinstance(data, str)
            else:
                # For other strings, check exact match
                return data == template
        elif isinstance(template, bool):
            return isinstance(data, bool)
        elif template is None:
            return data is None
            
        return False
    
    def extract_matching_objects(self, text: str) -> List[Dict]:
        """
        Extract JSON objects from text that match the template.
        
        Args:
            text: Text containing JSON objects
            
        Returns:
            List of JSON objects that match the template
        """
        json_objects = self.parser.extract_json_structures(text)
        return self.find_matching_objects(json_objects)
    
    def find_matching_objects(self, json_objects: List[Dict]) -> List[Dict]:
        """
        Find objects in the provided JSON that match the template.
        
        Args:
            json_objects: List of parsed JSON objects
            
        Returns:
            List of JSON objects that match the template
        """
        matching_objects = []
        
        for obj in json_objects:
            # If the object directly matches our template
            if self.validate_against_template(obj):
                matching_objects.append(obj)
                continue
                
            # Check if the object contains arrays or nested objects that match
            self._find_matching_structures(obj, matching_objects)
                
        return matching_objects
    
    def _find_matching_structures(self, obj: Any, matching_objects: List[Dict], path: Optional[List] = None):
        """
        Recursively search for structures matching the template within a JSON object.
        
        Args:
            obj: The object to search within
            matching_objects: List to collect matching objects
            path: Current path in the object (for debugging)
        """
        if path is None:
            path = []
            
        if isinstance(obj, dict):
            # Check if this dictionary matches our template
            if self.validate_against_template(obj):
                matching_objects.append(obj)
                
            # Recursively check all values
            for key, value in obj.items():
                self._find_matching_structures(value, matching_objects, path + [key])
                
        elif isinstance(obj, list):
            # Check each item in the list
            for i, item in enumerate(obj):
                self._find_matching_structures(item, matching_objects, path + [i]) 