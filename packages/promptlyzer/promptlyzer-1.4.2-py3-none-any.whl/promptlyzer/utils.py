import json
from typing import Dict, Any, Union


def format_prompt(prompt_template: str, values: Dict[str, Any]) -> str:
    """
    Simple formatter for prompt templates. Uses format string syntax.
    This is a fallback if Jinja2 is not available.
    
    Args:
        prompt_template: The template string.
        values: Dict of values to insert into the template.
        
    Returns:
        str: The formatted prompt.
    """
    try:
        return prompt_template.format(**values)
    except KeyError as e:
        missing_key = str(e).strip("'")
        raise ValueError(f"Missing required value: {missing_key}")


def prettify_json(obj: Union[Dict, list]) -> str:
    """
    Format a JSON object for nice display.
    
    Args:
        obj: The object to format.
        
    Returns:
        str: Formatted JSON string.
    """
    return json.dumps(obj, indent=2)