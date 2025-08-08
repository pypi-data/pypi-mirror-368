
import sys
import os
import json
# Add the project root directory to Python's module search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common_ai_core.parsers.json_parser import JsonParser

def test_json_parser():
    ans = """
    {"approved": true, "comment": "Den angivna korrekta lösningen 'Astrid Lindgren' är korrekt. Astrid Lindgren är en internationellt känd svensk barnboksförfattare som skapade karaktärer som Pippi Långstrump, Emil i Lönneberga och många fler. Även om Barbro Lindgren och Per Gustavsson också är svenska barnboksförfattare, är Astrid Lindgren utan tvekan den mest kända av de tre alternativen. Frågan är tydlig och svarsalternativen är rimliga."}
    """
    json_parser = JsonParser()
    json_obj = json_parser.extract_json_structures(ans)
    print(json_obj)

if __name__ == "__main__":
    test_json_parser()