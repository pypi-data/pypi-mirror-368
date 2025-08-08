import ast
import re

_config_data = {}
_is_loaded = False


def _parse_config_file(file_path):
    """Internal function to parse the config file. Returns a dictionary."""
    parsed_data = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"ERROR: Configuration file not found at path: {file_path}")
        raise

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        line_number = i + 1
        i += 1

        if not line or line.startswith('#'):
            continue

        match = re.match(r'^(string|int|bool|list|dict)\s+([a-zA-Z_]\w*)\s*=\s*(.*)$', line)
        if not match:
            print(f"Warning: Failed to parse line {line_number}: '{line}'")
            continue

        var_type, var_name, var_value_str = match.groups()
        var_value_str = var_value_str.strip()

        if var_type in ['list', 'dict'] and var_value_str in ['[', '{']:
            block_content = [var_value_str]
            closing_char = ']' if var_type == 'list' else '}'
            start_line = line_number
            
            is_closed = False
            while i < len(lines):
                line_in_block = lines[i].strip()
                i += 1
                block_content.append(line_in_block)
                if line_in_block.endswith(closing_char):
                    is_closed = True
                    break
            
            if not is_closed:
                print(f"ERROR: Multiline block for '{var_name}', started at line {start_line}, was not closed.")
                continue

            var_value_str = " ".join(block_content)

        value = None
        try:
            if var_type == 'string':
                if var_value_str.startswith('"') and var_value_str.endswith('"'):
                    value = var_value_str[1:-1]
                else:
                    # Allow strings without quotes if they contain no spaces
                    # and are not keywords (true, false, numbers)
                    if ' ' in var_value_str or var_value_str.isdigit() or var_value_str in ['true', 'false']:
                        raise ValueError(f"String '{var_value_str}' must be enclosed in double quotes.")
                    value = var_value_str
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
            print(f"Value error for variable '{var_name}': {e}")
    
    return parsed_data


def load(file_path="config.nigredo"):
    """
    Loads and parses the specified configuration file.
    This function should be called once at the start of the program.
    """
    global _config_data, _is_loaded
    _config_data = _parse_config_file(file_path)
    _is_loaded = True
    # Here is the corrected line:
    print(f"Nigredo Config: Loaded {len(_config_data)} variables from '{file_path}'")


def get(variable_name, default=None):
    """
    Retrieves the value of a variable from the loaded configuration.

    Args:
        variable_name (str): The name of the variable to retrieve.
        default (any, optional): Default value if the variable is not found. Defaults to None.

    Returns:
        The value of the variable or the default value.
    """
    if not _is_loaded:
        raise RuntimeError("Error: Configuration not loaded. Call nigredo_config.load() before using get().")
    
    variable_data = _config_data.get(variable_name)
    
    if variable_data:
        return variable_data['value']
    else:
        return default
    

def items():
    """
    Возвращает все загруженные переменные и их метаданные (тип, значение).

    Returns:
        dict_items: Объект, содержащий пары (имя_переменной, {'type': ..., 'value': ...})
    """
    if not _is_loaded:
        raise RuntimeError("Ошибка: Конфигурация не загружена. Вызовите nigredo_config.load() перед использованием items().")
    
    return _config_data.items()
