"""Configuration management for Baynext CLI."""

import json
import os
from pathlib import Path
from typing import Any

import typer
from dotenv import find_dotenv, load_dotenv

# Load environment variables from .env.local if it exists
load_dotenv(find_dotenv(".env.local", raise_error_if_not_found=False))
# Load environment variables from .env if it exists
# This allows overriding .env.local with .env if both are present
# Useful for production vs development configurations
load_dotenv(find_dotenv(".env", raise_error_if_not_found=False))

CONFIG_DIR = Path.home() / ".config" / "baynext"
CONFIG_FILE = CONFIG_DIR / "config.json"

BAYNEXT_API_URL = "https://api.baynext.tech"
BAYNEXT_API_BASE_URL = os.getenv("BAYNEXT_API_URL", BAYNEXT_API_URL) + "/v1"
"""Default API URL for Baynext CLI."""


def ensure_config_dir() -> None:
    """Ensure the config directory exists."""
    if not CONFIG_DIR.exists():
        typer.echo("Creating config files....")
    CONFIG_DIR.mkdir(exist_ok=True)


def get_config() -> dict[str, Any]:
    """Get current configuration."""
    ensure_config_dir()
    try:
        with CONFIG_FILE.open("r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def set_config(key: str, value: str) -> None:
    """Set a configuration value."""
    ensure_config_dir()
    config = get_config()
    config[key] = value

    with CONFIG_FILE.open("w") as f:
        json.dump(config, f, indent=2)


def get_config_value(key: str) -> str | None:
    """Get a specific configuration value."""
    config = get_config()
    return config.get(key)


def get_api_url() -> str:
    """Get API URL from config or default."""
    return get_config_value("api_url") or BAYNEXT_API_BASE_URL


def get_token() -> str | None:
    """Get access token from config."""
    return get_config_value("access_token")


def save_token(token: str) -> None:
    """Save access token to config."""
    set_config("access_token", token)
