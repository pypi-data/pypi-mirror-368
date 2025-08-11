from dataclasses import dataclass, field
from typing import List, Any

@dataclass
class Step:
    """Represents a single Gherkin step (Given, When, Then)."""
    keyword: str
    text: str
    line_number: int

@dataclass
class Scenario:
    """Represents a Gherkin Scenario."""
    title: str
    line_number: int
    steps: List[Step] = field(default_factory=list)

@dataclass
class Feature:
    """Represents the entire Gherkin Feature file."""
    title: str
    line_number: int
    description: List[str] = field(default_factory=list)
    scenarios: List[Scenario] = field(default_factory=list)