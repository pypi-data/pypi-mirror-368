import json
from dataclasses import asdict
from .models import Feature

def generate_json_output(feature: Feature) -> str:
    """Converts a Feature object into a pretty-printed JSON string."""
    # asdict converts dataclasses into dictionaries recursively
    feature_dict = asdict(feature)
    return json.dumps(feature_dict, indent=4)