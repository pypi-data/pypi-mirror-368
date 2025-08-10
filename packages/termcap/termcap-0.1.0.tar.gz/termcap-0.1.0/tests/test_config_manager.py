"""Test config_manager module"""
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, mock_open
import toml

from termcap.config_manager import (
    ConfigManager, DEFAULT_CONFIG, get_config_manager
)

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_file = self.temp_dir / "config.toml"
        self.templates_dir = self.temp_dir / "templates"
        
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def _create_config_manager(self):
        """Create a config manager with mocked paths"""
        with patch('termcap.config_manager.get_config_file', return_value=self.config_file), \
             patch('termcap.config_manager.get_templates_dir', return_value=self.templates_dir):
            return ConfigManager()
    
    def test_load_config_creates_default(self):
        """Test that load_config creates default config when file doesn't exist"""
        manager = self._create_config_manager()
        
        config = manager.load_config()
        
        self.assertEqual(config, DEFAULT_CONFIG)
        self.assertTrue(self.config_file.exists())
        
        # Verify file content
        with open(self.config_file, 'r') as f:
            saved_config = toml.load(f)
        self.assertEqual(saved_config, DEFAULT_CONFIG)
        
    def test_load_config_existing_file(self):
        """Test loading existing config file"""
        test_config = {
            "general": {
                "default_template": "custom_template",
                "default_geometry": "100x30"
            }
        }
        
        # Create config file
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            toml.dump(test_config, f)
            
        manager = self._create_config_manager()
        config = manager.load_config()
        
        # Should merge with defaults
        expected = DEFAULT_CONFIG.copy()
        expected["general"]["default_template"] = "custom_template"
        expected["general"]["default_geometry"] = "100x30"
        
        self.assertEqual(config, expected)
        
    def test_save_config(self):
        """Test saving config to file"""
        manager = self._create_config_manager()
        test_config = {
            "general": {
                "default_template": "test_template"
            }
        }
        
        manager.save_config(test_config)
        
        self.assertTrue(self.config_file.exists())
        with open(self.config_file, 'r') as f:
            saved_config = toml.load(f)
        self.assertEqual(saved_config, test_config)
        
    def test_get_setting(self):
        """Test getting specific settings"""
        manager = self._create_config_manager()
        manager.load_config()  # Load defaults
        
        # Test existing setting
        value = manager.get_setting("general", "default_template")
        self.assertEqual(value, "gjm8")
        
        # Test non-existing setting with default
        value = manager.get_setting("general", "non_existing", "default_value")
        self.assertEqual(value, "default_value")
        
        # Test non-existing section
        value = manager.get_setting("non_existing", "key", "default_value")
        self.assertEqual(value, "default_value")
        
    def test_set_setting(self):
        """Test setting specific settings"""
        manager = self._create_config_manager()
        
        # Set in existing section
        manager.set_setting("general", "default_template", "new_template")
        value = manager.get_setting("general", "default_template")
        self.assertEqual(value, "new_template")
        
        # Set in new section
        manager.set_setting("new_section", "new_key", "new_value")
        value = manager.get_setting("new_section", "new_key")
        self.assertEqual(value, "new_value")
        
    def test_get_available_templates_builtin_only(self):
        """Test getting available templates (builtin only)"""
        manager = self._create_config_manager()
        
        with patch('termcap.config_manager.default_templates') as mock_templates:
            mock_templates.return_value = {"template1": "content1", "template2": "content2"}
            
            templates = manager.get_available_templates()
            
            self.assertIn("template1", templates)
            self.assertIn("template2", templates)
            self.assertIsNone(templates["template1"])  # Builtin templates have no file path
            
    def test_get_available_templates_with_custom(self):
        """Test getting available templates (builtin + custom)"""
        manager = self._create_config_manager()
        
        # Create custom templates
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        (self.templates_dir / "custom1.svg").touch()
        (self.templates_dir / "custom2.svg").touch()
        
        with patch('termcap.config_manager.default_templates') as mock_templates:
            mock_templates.return_value = {"builtin1": "content1"}
            
            templates = manager.get_available_templates()
            
            self.assertIn("builtin1", templates)
            self.assertIn("custom1", templates)
            self.assertIn("custom2", templates)
            self.assertIsNone(templates["builtin1"])
            self.assertEqual(templates["custom1"], self.templates_dir / "custom1.svg")
            
    def test_install_custom_template(self):
        """Test installing custom template"""
        manager = self._create_config_manager()
        
        # Create source template file
        source_template = self.temp_dir / "source.svg"
        source_template.write_text("<svg>test content</svg>")
        
        manager.install_custom_template("my_template", source_template)
        
        dest_path = self.templates_dir / "my_template.svg"
        self.assertTrue(dest_path.exists())
        self.assertEqual(dest_path.read_text(), "<svg>test content</svg>")
        
    def test_install_custom_template_file_not_found(self):
        """Test installing custom template with non-existing file"""
        manager = self._create_config_manager()
        
        non_existing_file = self.temp_dir / "non_existing.svg"
        
        with self.assertRaises(FileNotFoundError):
            manager.install_custom_template("my_template", non_existing_file)
            
    def test_remove_custom_template(self):
        """Test removing custom template"""
        manager = self._create_config_manager()
        
        # Create template
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        template_file = self.templates_dir / "my_template.svg"
        template_file.write_text("content")
        
        manager.remove_custom_template("my_template")
        
        self.assertFalse(template_file.exists())
        
    def test_remove_custom_template_not_found(self):
        """Test removing non-existing custom template"""
        manager = self._create_config_manager()
        
        with self.assertRaises(FileNotFoundError):
            manager.remove_custom_template("non_existing")
            
    def test_reset_config(self):
        """Test resetting config to defaults"""
        manager = self._create_config_manager()
        
        # Modify config
        manager.set_setting("general", "default_template", "custom")
        
        # Reset
        manager.reset_config()
        
        # Verify reset
        config = manager.load_config()
        self.assertEqual(config, DEFAULT_CONFIG)
        
    def test_get_config_manager_singleton(self):
        """Test global config manager singleton"""
        manager1 = get_config_manager()
        manager2 = get_config_manager()
        
        self.assertIs(manager1, manager2)
