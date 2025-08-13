import yaml
from typing import Dict, List, Any
from dbt_yamer.exceptions import ValidationError

class MyDumper(yaml.Dumper):
    """
    A custom YAML dumper that overrides the increase_indent and write_line_break methods
    to produce extra line breaks after top-level items.
    """

    def increase_indent(self, flow=False, indentless=False):
        """Always set 'indentless' to False to ensure proper indentation of nested blocks."""
        return super(MyDumper, self).increase_indent(flow, False)

    def write_line_break(self, data=None):
        """
        Override to add an extra line break after the top-level indentation.
        (Here, we check if len(self.indents) == 4 to control when to add the extra line.)
        """
        super(MyDumper, self).write_line_break(data)
        if len(self.indents) == 4:
            super(MyDumper, self).write_line_break()

def format_columns(columns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Apply specific formatting to the columns list.
    
    Args:
        columns: List of column dictionaries
        
    Returns:
        Formatted list of column dictionaries
        
    Raises:
        ValidationError: If column data is invalid
    """
    if not isinstance(columns, list):
        raise ValidationError("Columns must be a list")
    
    formatted = []
    for i, column in enumerate(columns):
        if not isinstance(column, dict):
            raise ValidationError(f"Column {i} must be a dictionary")
        
        if 'name' not in column:
            raise ValidationError(f"Column {i} missing 'name' field")
        
        formatted_column = {
            'name': str(column['name']),
            'data_type': str(column.get('data_type', '')),
            'description': str(column.get('description', ''))
        }
        formatted.append(formatted_column)
    
    return formatted

def format_yaml2(input_yaml: str) -> str:
    """
    Alternate version of format function, demonstrating a second approach.
    Loads the YAML, applies column formatting, dumps with custom indentation,
    then adds a blank line after 'version: 2' if present.
    
    Args:
        input_yaml: Raw YAML string to format
        
    Returns:
        Formatted YAML string
        
    Raises:
        ValidationError: If YAML is invalid
    """
    if not input_yaml or not isinstance(input_yaml, str):
        raise ValidationError("Input YAML must be a non-empty string")
    
    try:
        data = yaml.safe_load(input_yaml)
    except yaml.YAMLError as e:
        raise ValidationError(f"Invalid YAML: {e}")
    
    if not isinstance(data, dict):
        raise ValidationError("YAML must contain a dictionary at root level")

    for model in data.get('models', []):
        if 'columns' in model:
            model['columns'] = format_columns(model['columns'])

    try:
        formatted = yaml.dump(data, Dumper=MyDumper, sort_keys=False, allow_unicode=True)
        formatted = formatted.replace("version: 2\n", "version: 2\n\n")
        return formatted
    except yaml.YAMLError as e:
        raise ValidationError(f"Error formatting YAML: {e}")


def format_yaml(input_yaml: str) -> str:
    """
    Reformats the input YAML to match the desired structure with separate formatting
    for headers and columns, using a custom dumper to handle indentation and spacing.
    
    Args:
        input_yaml: Raw YAML string to format
        
    Returns:
        Formatted YAML string
        
    Raises:
        ValidationError: If YAML is invalid
    """
    if not input_yaml or not isinstance(input_yaml, str):
        raise ValidationError("Input YAML must be a non-empty string")
    
    try:
        data = yaml.safe_load(input_yaml)
    except yaml.YAMLError as e:
        raise ValidationError(f"Invalid YAML: {e}")
    
    if not isinstance(data, dict):
        raise ValidationError("YAML must contain a dictionary at root level")

    for model in data.get('models', []):
        if 'columns' in model:
            model['columns'] = format_columns(model['columns'])

    try:
        formatted_yaml = yaml.dump(data, Dumper=MyDumper, sort_keys=False, allow_unicode=True)
        formatted_yaml = formatted_yaml.replace("  config:\n\n", "  config:\n")
        formatted_yaml = formatted_yaml.replace("version: 2\n", "version: 2\n\n")
        formatted_yaml = formatted_yaml.replace("columns:\n", "columns:")
        return formatted_yaml
    except yaml.YAMLError as e:
        raise ValidationError(f"Error formatting YAML: {e}")
