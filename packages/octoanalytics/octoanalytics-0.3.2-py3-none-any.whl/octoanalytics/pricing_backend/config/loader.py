"""Configuration loader for the pricing module."""

import yaml
import os
from typing import Dict, Any

_FILE_DIR = os.path.dirname(__file__)
_CONFIG_PATH = os.path.join(
    _FILE_DIR,
    "config.yaml"
)


def load_config(filepath: str = _CONFIG_PATH) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        filepath: Path to the configuration file. Defaults to config.yaml in this directory.
        
    Returns:
        Dictionary containing configuration settings.
        
    Raises:
        FileNotFoundError: If the configuration file is not found.
        yaml.YAMLError: If there's an error parsing the YAML file.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {filepath}")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing configuration file {filepath}: {e}")


def get_config_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Get a configuration value using dot notation.
    
    Args:
        config: Configuration dictionary
        key_path: Dot-separated path to the configuration value (e.g., 'app.name')
        default: Default value to return if key is not found
        
    Returns:
        Configuration value or default if not found
        
    Example:
        >>> config = load_config()
        >>> app_name = get_config_value(config, 'app.name', 'Unknown')
    """
    keys = key_path.split('.')
    value = config
    
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default