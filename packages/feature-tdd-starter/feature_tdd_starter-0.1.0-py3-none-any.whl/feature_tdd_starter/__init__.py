from pathlib import Path

from .parser import parse_feature_file
from .generator import generate_json_output
from .exceptions import InvalidGherkinSyntaxError

def parse_and_generate(file_path: str | Path) -> str:
    """
    Parses a Gherkin .feature file, validates it, and generates a JSON string.
    
    Args:
        file_path: The path to the .feature file. Can be a string or Path object.
        
    Returns:
        A JSON string of the parsed feature file structure.
        
    Raises:
        FileNotFoundError: If the file does not exist.
        InvalidGherkinSyntaxError: If the file content violates Gherkin syntax.
    """
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"File not found at '{file_path}'")
        
    feature_model = parse_feature_file(path)
    json_output = generate_json_output(feature_model)
    
    return json_output