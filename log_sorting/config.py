# -*- coding: utf-8 -*-

"""Config utility functions."""

import os
import string
import yaml
from collections import defaultdict
from typing import Dict, List

from box import Box

from log_sorting.constants import YAML_EXTENSION


def _resolve_env_vars(dictionary: dict) -> None:
    """Expand environment variables in the dictionary values, format: ${ENV_VAR}.

    If the environment variable is not set, it is expanded as empty string.
    
    :param dictionary: Dictionary to expand values on.
    """
    # Build a default dict with env vars, but that gives empty string
    # if env var does not exist
    env_vars = defaultdict(lambda: "", os.environ)
    for key, value in dictionary.items():
        if type(value) == dict:
            _resolve_env_vars(value)
        elif type(value) == list:
            dictionary[key] = [
                string.Template(item).substitute(env_vars)
                if "${" in str(item)
                else item
                for item in value
            ]
        elif type(value) == str and "${" in value:
            dictionary[key] = string.Template(value).substitute(env_vars)


def _update_config(source: Dict, target: Dict) -> Dict:
    """Update nested dictionaries recursively.

    This happens in an append-overwrite manner:
    - Append if full key is unseen (e.g. parent.child).
    - Override if full key already exists in target.

    :param source: Source of new keys and values.
    :param target: Existing mapping to update with source.
    :return: Combination of both source and target.
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # Recurse if the value in source is a nested dictionary.
            # Required to prevent overriding a key in full.
            # Instead go down the nesting, add the new keys,
            # and override the overlapping ones.
            target[key] = _update_config(value, target.get(key, {}))
        else:
            # Reached lowest level in recursion, set key to value.
            target[key] = value
    
    return target


def load_config(
    config_file_names: List[str],
    config_dir: str,
) -> Box:
    """Load entire configuration.
    
    :param config_files: Names of configuration files to load.
    :type config_files: List[str]
    :config_dir: Directory for configuration files.
    :type config_dir: str
    :return: Loaded configuration.
    :type return: Box
    """
    config: Dict = {}
    file_paths = [
        config_dir / f"{file_name}.{YAML_EXTENSION}"
        for file_name in config_file_names
    ]
    for file_path in file_paths:
        with open(file_path, "r") as f:
            config = _update_config(yaml.safe_load(f.read()), config)
    _resolve_env_vars(config)
    
    return Box(config)
