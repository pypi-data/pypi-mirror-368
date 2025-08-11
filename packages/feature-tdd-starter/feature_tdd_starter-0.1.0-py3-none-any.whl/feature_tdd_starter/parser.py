import re
from pathlib import Path

from .models import Feature, Scenario, Step
from .exceptions import InvalidGherkinSyntaxError

def parse_feature_file(file_path: Path) -> Feature:
    """Parses a Gherkin .feature file into a Feature dataclass."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    feature = None
    current_scenario = None
    step_keywords = ['Given', 'When', 'Then', 'And', 'But']
    
    parsing_feature_description = False

    for i, line in enumerate(lines, start=1):
        stripped_line = line.strip()

        if not stripped_line or stripped_line.startswith('#'):
            continue

        if stripped_line.startswith('Feature:'):
            if feature:
                raise InvalidGherkinSyntaxError(f"Multiple Feature definitions found at line {i}.")
            title = stripped_line.replace('Feature:', '', 1).strip()
            feature = Feature(title=title, line_number=i)
            parsing_feature_description = True
            
        elif stripped_line.startswith('Scenario:'):
            if not feature:
                raise InvalidGherkinSyntaxError(f"Scenario found before Feature at line {i}.")
            title = stripped_line.replace('Scenario:', '', 1).strip()
            current_scenario = Scenario(title=title, line_number=i)
            feature.scenarios.append(current_scenario)
            parsing_feature_description = False
        
        elif any(stripped_line.startswith(keyword) for keyword in step_keywords):
            if not current_scenario:
                raise InvalidGherkinSyntaxError(f"Step found outside of a Scenario at line {i}.")
            
            keyword_match = re.match(r'^(Given|When|Then|And|But)\s+', stripped_line)
            if keyword_match:
                keyword = keyword_match.group(1)
                text = stripped_line[len(keyword):].strip()
                current_scenario.steps.append(Step(keyword=keyword, text=text, line_number=i))
            else:
                raise InvalidGherkinSyntaxError(f"Invalid step format at line {i}.")
        
        elif feature and parsing_feature_description:
            feature.description.append(stripped_line)
        
        elif current_scenario:
            raise InvalidGherkinSyntaxError(f"Unrecognized line '{stripped_line}' at line {i}.")

    if not feature:
        raise InvalidGherkinSyntaxError("No Feature found in the file.")
    
    return feature