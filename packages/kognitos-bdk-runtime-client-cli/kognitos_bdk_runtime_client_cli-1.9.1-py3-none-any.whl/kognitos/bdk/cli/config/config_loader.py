import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH_USER = Path.home() / ".bdkctl" / "config.yaml"
DEFAULT_CONFIG_PATH_XDG = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "bdkctl" / "config.yaml"


def find_config_file() -> Optional[Path]:
    """Searches for bdkctl.yaml or bdkctl.yml in current dir and parent dirs."""
    current_dir = Path.cwd()
    for directory in [current_dir] + list(current_dir.parents):
        for filename in ["bdkctl.yaml", "bdkctl.yml"]:
            config_file = directory / filename
            if config_file.is_file():
                return config_file
    return None


def load_config() -> Dict[str, Any]:
    config_file = find_config_file()
    if config_file:
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.warning("Configuration file not found: %s. Using default configuration.", config_file)
            return {}
        except yaml.YAMLError as e:
            logger.warning("Error parsing configuration file %s: %s", config_file, e)
            return {}
        except Exception as e:  # pylint: disable=broad-except
            logger.warning("An unexpected error occurred while loading config %s: %s", config_file, e)
            return {}
    return {}


def get_command_config(command_name: Optional[str], config_data: Dict[str, Any], cli_columns: Optional[List[str]], cli_column_styles: Optional[Dict[str, str]]) -> Dict[str, Any]:
    resolved_config = {"columns": None, "column_styles": {}}

    all_commands_defaults = config_data.get("defaults", {}).get("all_commands", {})
    if "columns" in all_commands_defaults:
        resolved_config["columns"] = all_commands_defaults["columns"]
    if "column_styles" in all_commands_defaults:
        resolved_config["column_styles"].update(all_commands_defaults["column_styles"])

    if command_name:
        command_specific_defaults = config_data.get("defaults", {}).get(command_name, {})
        if "columns" in command_specific_defaults:
            resolved_config["columns"] = command_specific_defaults["columns"]
        if "column_styles" in command_specific_defaults:
            resolved_config["column_styles"].update(command_specific_defaults["column_styles"])

    if cli_columns is not None:
        resolved_config["columns"] = cli_columns

    if cli_column_styles:
        resolved_config["column_styles"].update(cli_column_styles)

    return resolved_config
