"""Configuration directory management using platformdirs"""
import os
from pathlib import Path
import platformdirs

# Application info
APP_NAME = "termcap"
APP_AUTHOR = "rexwzh"

def _get_config_dir_path() -> Path:
    """Get raw configuration directory path"""
    return Path(platformdirs.user_config_dir(APP_NAME, APP_AUTHOR))

def _get_data_dir_path() -> Path:
    """Get raw data directory path"""
    return Path(platformdirs.user_data_dir(APP_NAME, APP_AUTHOR))

def ensure_config_directories():
    """Ensure configuration directories exist"""
    config_dir = _get_config_dir_path()
    data_dir = _get_data_dir_path()
    templates_dir = config_dir / "templates"
    
    config_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    templates_dir.mkdir(parents=True, exist_ok=True)

def get_config_dir() -> Path:
    """Get configuration directory path"""
    ensure_config_directories()
    return _get_config_dir_path()

def get_data_dir() -> Path:
    """Get data directory path"""
    ensure_config_directories()
    return _get_data_dir_path()

def get_templates_dir() -> Path:
    """Get templates directory path"""
    ensure_config_directories()
    return _get_config_dir_path() / "templates"

def get_config_file() -> Path:
    """Get config file path"""
    ensure_config_directories()
    return _get_config_dir_path() / "config.toml"
