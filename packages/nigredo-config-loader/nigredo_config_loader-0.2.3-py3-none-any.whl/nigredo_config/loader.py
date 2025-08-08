import re
import ast

# -- Module-level "private" variables to store the loaded state --
# This dictionary will hold the parsed configuration data.
_config_data = {}
# This flag indicates whether the configuration has been loaded.
_is_loaded = False


class Template:
    """A special object to store and format text templates."""
    def __init__(self, raw_text=""):
        """Initializes the Template object with the raw template string."""
        self.text = raw_text

    def format(self, **kwargs):
        """
        Replaces placeholders like {{key}} with values from kwargs.
        Example: template.format(name="World") -> "Hello, World!"
        """
        result = self.text
        for key, value in kwargs.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result

    def __str__(self):
        """Allows casting the object directly to a string."""
        return self.text


def _parse_config_file(file_path):
    """
    Internal function to parse the .nigredo configuration file.
    It reads the file and returns a dictionary containing the variable
    name, its declared type, and its parsed value.
    """
    parsed_data = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        # This error is handled by the calling function.
        raise

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        line_number = i + 1
        i += 1  # Increment the line counter immediately

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
            
        # Regex to capture: (type) (name) = (value)
        # Now includes the 'template' type.
        match = re.match(r'^(string|int|bool|list|dict|template)\s+([a-zA-Z_]\w*)\s*=\s*(.*)$', line)
        if not match:
            print(f"Warning: Could not parse line {line_number}: '{line}'")
            continue

        var_type, var_name, var_value_str = match.groups()
        var_value_str = var_value_str.strip()
        
        # --- Handle multiline 'template' type ---
        if var_type == 'template' and var_value_str == '"""':
            block_content = []
            # Read subsequent lines until a closing '"""' is found
            while i < len(lines):
                line_in_block = lines[i]
                i += 1
                if line_in_block.strip().endswith('"""'):
                    # Append the content of the line before the closing quotes
                    block_content.append(line_in_block.rsplit('"""', 1)[0])
                    break
                block_content.append(line_in_block)
            
            # Join the lines and remove any trailing whitespace
            var_value_str = "".join(block_content).rstrip()

        # --- Handle multiline 'list' and 'dict' types ---
        elif var_type in ['list', 'dict'] and var_value_str in ['[', '{']:
            block_content = [var_value_str]
            closing_char = ']' if var_type == 'list' else '}'
            # Read subsequent lines until the closing character is found
            while i < len(lines):
                line_in_block = lines[i].strip()
                i += 1
                block_content.append(line_in_block)
                if line_in_block.endswith(closing_char):
                    break
            
            var_value_str = " ".join(block_content)

        # --- Parse the value string into a Python object ---
        value = None
        try:
            if var_type in ['string', 'template']:
                if var_type == 'string' and var_value_str.startswith('"') and var_value_str.endswith('"'):
                    text_content = var_value_str[1:-1]
                else:
                    text_content = var_value_str
                
                value = Template(text_content)
            
            elif var_type == 'int':
                value = int(var_value_str)
            elif var_type == 'bool':
                value = var_value_str.lower() == 'true'
            elif var_type == 'list':
                value = ast.literal_eval(var_value_str)
            elif var_type == 'dict':
                dict_str = re.sub(r'([a-zA-Z_]\w*)\s*:', r'"\1":', var_value_str)
                value = ast.literal_eval(dict_str)

            parsed_data[var_name] = {'type': var_type, 'value': value}
        except Exception as e:
            print(f"Error parsing value for variable '{var_name}': {e}")
    
    return parsed_data


# --- Public API Functions ---

def load(file_path="config.nigredo"):
    """
    Loads and parses the specified configuration file.
    This function must be called once before using get(), items(), or get_template().
    """
    global _config_data, _is_loaded
    _config_data = _parse_config_file(file_path)
    _is_loaded = True
    print(f"Nigredo Config: Loaded {len(_config_data)} variables from '{file_path}'")


def get(variable_name, default=None):
    """
    Gets the value of a variable from the loaded configuration.

    Args:
        variable_name (str): The name of the variable to retrieve.
        default (any, optional): The value to return if the variable is not found. Defaults to None.

    Returns:
        The variable's value or the default value.
    """
    if not _is_loaded:
        raise RuntimeError("Configuration not loaded. Call nigredo_config.load() before using get().")
    
    variable_data = _config_data.get(variable_name)
    
    if variable_data:
        # Return the actual value, not the Template object for templates
        if isinstance(variable_data['value'], Template):
            return str(variable_data['value'])
        return variable_data['value']
    else:
        return default


def items():
    """
    Returns all loaded variables and their metadata (type, value).

    Returns:
        A dict_items object containing (name, {'type': ..., 'value': ...}) pairs.
    """
    if not _is_loaded:
        raise RuntimeError("Configuration not loaded. Call nigredo_config.load() before using items().")
    
    return _config_data.items()


def get_template(template_name, default_text=""):
    """
    Retrieves a template variable as a formattable Template object.

    Args:
        template_name (str): The name of the template variable.
        default_text (str, optional): A fallback text if the template is not found.

    Returns:
        A Template object that can be formatted using .format().
    """
    if not _is_loaded:
        raise RuntimeError("Configuration not loaded. Call nigredo_config.load() before using get_template().")
    
    variable_data = _config_data.get(template_name)
    
    # Ensure the retrieved variable is actually a Template instance
    if variable_data and isinstance(variable_data['value'], Template):
        return variable_data['value']
    
    # If not found or not a template, return a default Template object
    return Template(default_text)