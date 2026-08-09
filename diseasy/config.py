"""
diseasy/config.py (v0.3.1)

Loads bot configuration from .env, config.json, config.yml/.yaml, or
config.py — with clear, specific errors instead of generic Python
exceptions (FileNotFoundError, JSONDecodeError, KeyError, etc.).

Usage:
    from diseasy.config import load_config, require_env

    config = load_config("config.json")
    token = require_env("DISCORD_TOKEN")  # reads from os.environ,
                                            # typically populated by
                                            # python-dotenv's load_dotenv()

    config = load_config("config.json", required_keys=["prefix", "intents"])
"""

import json
import os
import importlib.util

from .errors import (
    ConfigFileNotFound,
    ConfigParseError,
    MissingConfigKey,
    EnvVariableMissing,
)

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


def load_config(path: str, required_keys: list = None) -> dict:
    """
    Loads a config file, auto-detecting format from its extension:
    .json, .yml/.yaml, or .py (expects a dict-returning module, either
    via a MODULE-LEVEL dict of uppercase variables, or a CONFIG dict).

    Raises:
        ConfigFileNotFound — if the path doesn't exist
        ConfigParseError — if the file exists but can't be parsed
        MissingConfigKey — if required_keys are given and any are absent
    """
    if not os.path.exists(path):
        raise ConfigFileNotFound(path)

    ext = os.path.splitext(path)[1].lower()

    if ext == ".json":
        config = _load_json(path)
    elif ext in (".yml", ".yaml"):
        config = _load_yaml(path)
    elif ext == ".py":
        config = _load_python(path)
    else:
        raise ConfigParseError(
            path, ValueError(f"Unsupported config file extension: '{ext}' "
                              f"(expected .json, .yml, .yaml, or .py)")
        )

    if required_keys:
        for key in required_keys:
            if key not in config:
                raise MissingConfigKey(key, path)

    return config


def _load_json(path: str) -> dict:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigParseError(path, e) from e


def _load_yaml(path: str) -> dict:
    if not _YAML_AVAILABLE:
        raise ConfigParseError(
            path, ImportError("PyYAML is not installed — run "
                               "'pip install pyyaml' to load .yml/.yaml configs.")
        )
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise ConfigParseError(path, e) from e


def _load_python(path: str) -> dict:
    try:
        spec = importlib.util.spec_from_file_location("diseasy_config", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as e:
        raise ConfigParseError(path, e) from e

    if hasattr(module, "CONFIG") and isinstance(module.CONFIG, dict):
        return module.CONFIG

    # Fall back to collecting uppercase module-level variables as config
    return {
        name: value
        for name, value in vars(module).items()
        if name.isupper() and not name.startswith("_")
    }


def require_env(var_name: str) -> str:
    """
    Reads a required environment variable, raising EnvVariableMissing
    with a clear message instead of returning None silently.
    Typically used after python-dotenv's load_dotenv() has run.
    """
    value = os.environ.get(var_name)
    if value is None:
        raise EnvVariableMissing(var_name)
    return value
