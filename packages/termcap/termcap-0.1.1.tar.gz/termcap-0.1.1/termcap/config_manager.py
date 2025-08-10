"""Configuration file management with TOML support"""
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import toml

from .config_dirs import get_config_file, get_templates_dir, get_config_dir
from .config import default_templates

# Default configuration
DEFAULT_CONFIG = {
    "general": {
        "default_template": "gjm8",
        "default_geometry": "82x19",
        "default_min_duration": 17,
        "default_max_duration": 3000,
        "default_loop_delay": 1000,
    },
    "templates": {
        "custom_templates_enabled": True,
        "builtin_templates_enabled": True,
    },
    "output": {
        "default_output_dir": "~/termcap_recordings",
        "auto_timestamp": True,
    }
}

class ConfigManager:
    """Manage termcap configuration files"""
    
    def __init__(self):
        self.config_file = get_config_file()
        self.templates_dir = get_templates_dir()
        self._config = None
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from config.toml"""
        if self._config is not None:
            return self._config
            
        if not self.config_file.exists():
            # Create default config file
            self.save_config(DEFAULT_CONFIG)
            self._config = DEFAULT_CONFIG.copy()
        else:
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = toml.load(f)
                # Merge with defaults for missing keys
                self._config = self._merge_with_defaults(self._config)
            except Exception as e:
                # If config file is corrupted, recreate it
                print(f"Warning: Config file corrupted, recreating: {e}")
                self.save_config(DEFAULT_CONFIG)
                self._config = DEFAULT_CONFIG.copy()
                
        return self._config
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to config.toml"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            toml.dump(config, f)
        self._config = config.copy()
        
    def get_setting(self, section: str, key: str, default: Any = None) -> Any:
        """Get a specific setting from config"""
        config = self.load_config()
        return config.get(section, {}).get(key, default)
        
    def set_setting(self, section: str, key: str, value: Any):
        """Set a specific setting in config"""
        config = self.load_config()
        if section not in config:
            config[section] = {}
        config[section][key] = value
        self.save_config(config)
        
    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user config with defaults"""
        merged = DEFAULT_CONFIG.copy()
        for section, settings in config.items():
            if section in merged:
                merged[section].update(settings)
            else:
                merged[section] = settings
        return merged
        
    def get_available_templates(self) -> Dict[str, Path]:
        """Get all available templates (builtin + custom)"""
        templates = {}
        
        # Add builtin templates if enabled
        config = self.load_config()
        if config.get("templates", {}).get("builtin_templates_enabled", True):
            builtin_templates = default_templates()
            for name in builtin_templates:
                templates[name] = None  # Builtin templates don't have file paths
                
        # Add custom templates if enabled
        if config.get("templates", {}).get("custom_templates_enabled", True):
            if self.templates_dir.exists():
                for template_file in self.templates_dir.glob("*.svg"):
                    name = template_file.stem
                    templates[name] = template_file
                    
        return templates
        
    def install_custom_template(self, name: str, template_path: Path):
        """Install a custom template"""
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")
            
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        dest_path = self.templates_dir / f"{name}.svg"
        shutil.copy2(template_path, dest_path)
        
    def remove_custom_template(self, name: str):
        """Remove a custom template"""
        template_path = self.templates_dir / f"{name}.svg"
        if template_path.exists():
            template_path.unlink()
        else:
            raise FileNotFoundError(f"Custom template not found: {name}")
            
    def reset_config(self):
        """Reset configuration to defaults"""
        self.save_config(DEFAULT_CONFIG)
        
# Global config manager instance
_config_manager = None

def get_config_manager() -> ConfigManager:
    """Get global config manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
