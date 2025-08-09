"""
Configuration validation utilities for Stata-MCP web UI.

This module provides validation functions for all configuration fields
from the complete example.toml structure.
"""

import os
import platform
import re
import shutil
from typing import Any, Dict, Optional, Tuple


class ConfigValidationError(Exception):
    """Exception raised for configuration validation errors."""

    def __init__(self, field: str, message: str,
                 suggestion: Optional[str] = None):
        self.field = field
        self.message = message
        self.suggestion = suggestion
        super().__init__(f"{field}: {message}")


def validate_stata_cli_path(path: str) -> Tuple[bool, str, Optional[str]]:
    """Validate Stata CLI path."""
    if not path or not path.strip():
        return False, "Stata CLI path is required", None

    path = path.strip()

    # Check if path exists
    if not os.path.exists(path):
        return False, f"Path does not exist: {path}", get_stata_suggestion()

    # Check if it's a file (not directory)
    if not os.path.isfile(path):
        return False, f"Path is not a file: {path}", get_stata_suggestion()

    # Check if it's executable (Unix-like systems)
    if platform.system() != "Windows":
        if not os.access(path, os.X_OK):
            return False, f"File is not executable: {path}", f"Run: chmod +x {path}"

    # Check if it looks like a Stata executable
    path_lower = path.lower()
    stata_indicators = ["stata", "stata-mp", "stata-se", "stataic"]
    if not any(indicator in path_lower for indicator in stata_indicators):
        return False, "File does not appear to be a Stata executable", get_stata_suggestion()

    return True, "", None


def validate_output_base_path(path: str) -> Tuple[bool, str, Optional[str]]:
    """Validate output base directory path."""
    if not path or not path.strip():
        return False, "Output base path is required", get_default_output_suggestion()

    path = path.strip()

    # Expand user paths
    path = os.path.expanduser(path)

    try:
        # Check if path exists
        if os.path.exists(path):
            # Check if it's a directory
            if not os.path.isdir(path):
                return False, f"Path is not a directory: {path}", None

            # Check write permissions
            if not os.access(path, os.W_OK):
                return False, f"Directory is not writable: {path}", "Check directory permissions"
        else:
            # Try to create the directory
            try:
                os.makedirs(path, exist_ok=True)
                # Verify we can write to it
                test_file = os.path.join(path, ".stata-mcp-test")
                with open(test_file, "w") as f:
                    f.write("test")
                os.remove(test_file)
            except OSError as e:
                return False, f"Cannot create or write to directory: {path}", str(
                    e)

        return True, "", None

    except Exception as e:
        return False, f"Invalid path format: {str(e)}", None


def validate_llm_type(llm_type: str) -> Tuple[bool, str, Optional[str]]:
    """Validate LLM type."""
    valid_types = ["ollama", "openai"]
    if llm_type.lower() not in valid_types:
        return False, f"Invalid LLM type: {llm_type}", f"Must be one of: {', '.join(valid_types)}"
    return True, "", None


def validate_url(url: str) -> Tuple[bool, str, Optional[str]]:
    """Validate URL format."""
    if not url or not url.strip():
        return False, "URL is required", None

    url = url.strip()

    # Basic URL validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        # domain...
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if not url_pattern.match(url):
        return False, f"Invalid URL format: {url}", "Use format: http://host:port or https://host:port"

    return True, "", None


def validate_model_name(model: str) -> Tuple[bool, str, Optional[str]]:
    """Validate model name."""
    if not model or not model.strip():
        return False, "Model name is required", None

    model = model.strip()
    if len(model) < 3:
        return False, "Model name too short", "Use at least 3 characters"

    return True, "", None


def validate_api_key(api_key: str) -> Tuple[bool, str, Optional[str]]:
    """Validate API key format."""
    if not api_key or not api_key.strip():
        return False, "API key is required for OpenAI", None

    api_key = api_key.strip()
    if len(api_key) < 20:
        return False, "API key appears too short", "OpenAI API keys are typically longer"

    if not api_key.startswith('sk-'):
        return False, "Invalid OpenAI API key format", "Should start with 'sk-'"

    return True, "", None


def get_stata_suggestion() -> str:
    """Get platform-specific Stata executable suggestions."""
    system = platform.system()

    if system == "Darwin":  # macOS
        return "Common locations: /Applications/Stata/StataMP.app/Contents/MacOS/stata-mp"
    elif system == "Linux":
        return "Common locations: /usr/local/stata17/stata-mp, /opt/stata/stata"
    elif system == "Windows":
        return r"Common locations: C:\Program Files\Stata17\StataMP-64.exe"
    else:
        return "Please check your Stata installation directory"


def get_default_output_suggestion() -> str:
    """Get default output directory suggestion."""
    system = platform.system()

    if system in ["Darwin", "Linux"]:
        documents = os.path.expanduser("~/Documents")
    elif system == "Windows":
        documents = os.path.join(
            os.environ.get(
                "USERPROFILE",
                ""),
            "Documents")
    else:
        documents = os.path.expanduser("~/Documents")

    return f"Suggested: {os.path.join(documents, 'stata-mcp-output')}"


def validate_configuration(
        config_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Validate entire configuration structure from example.toml.

    Args:
        config_data: Complete configuration dictionary

    Returns:
        Nested dictionary with validation results for all fields
    """
    results = {}

    # Validate stata section
    stata_config = config_data.get('stata', {})
    results['stata'] = {}

    stata_cli = stata_config.get('stata_cli', '')
    is_valid, error, suggestion = validate_stata_cli_path(stata_cli)
    results['stata']['stata_cli'] = {
        "valid": is_valid,
        "error": error,
        "suggestion": suggestion
    }

    # Validate stata-mcp section
    stata_mcp_config = config_data.get('stata-mcp', {})
    results['stata-mcp'] = {}

    output_base_path = stata_mcp_config.get('output_base_path', '')
    is_valid, error, suggestion = validate_output_base_path(output_base_path)
    results['stata-mcp']['output_base_path'] = {
        "valid": is_valid,
        "error": error,
        "suggestion": suggestion
    }

    # Validate llm section
    llm_config = config_data.get('llm', {})
    results['llm'] = {}

    llm_type = llm_config.get('LLM_TYPE', 'ollama')
    is_valid, error, suggestion = validate_llm_type(llm_type)
    results['llm']['LLM_TYPE'] = {
        "valid": is_valid,
        "error": error,
        "suggestion": suggestion
    }

    # Validate llm.ollama section
    ollama_config = llm_config.get('ollama', {})
    results['llm']['ollama'] = {}

    ollama_model = ollama_config.get('MODEL', '')
    is_valid, error, suggestion = validate_model_name(ollama_model)
    results['llm']['ollama']['MODEL'] = {
        "valid": is_valid,
        "error": error,
        "suggestion": suggestion
    }

    ollama_url = ollama_config.get('BASE_URL', '')
    is_valid, error, suggestion = validate_url(ollama_url)
    results['llm']['ollama']['BASE_URL'] = {
        "valid": is_valid,
        "error": error,
        "suggestion": suggestion
    }

    # Validate llm.openai section
    openai_config = llm_config.get('openai', {})
    results['llm']['openai'] = {}

    openai_model = openai_config.get('MODEL', '')
    is_valid, error, suggestion = validate_model_name(openai_model)
    results['llm']['openai']['MODEL'] = {
        "valid": is_valid,
        "error": error,
        "suggestion": suggestion
    }

    openai_url = openai_config.get('BASE_URL', '')
    is_valid, error, suggestion = validate_url(openai_url)
    results['llm']['openai']['BASE_URL'] = {
        "valid": is_valid,
        "error": error,
        "suggestion": suggestion
    }

    openai_key = openai_config.get('API_KEY', '')
    is_valid, error, suggestion = validate_api_key(openai_key)
    results['llm']['openai']['API_KEY'] = {
        "valid": is_valid,
        "error": error,
        "suggestion": suggestion
    }

    return results


def create_configuration_backup(config_path: str) -> str:
    """Create a backup of the current configuration file."""
    import time
    if not os.path.exists(config_path):
        return ""

    timestamp = int(time.time())
    backup_path = f"{config_path}.backup.{timestamp}"
    shutil.copy2(config_path, backup_path)
    return backup_path
