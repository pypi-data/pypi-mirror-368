"""Test config_dirs module"""
import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

from termcap.config_dirs import (
    get_config_dir, get_data_dir, get_templates_dir, 
    get_config_file, ensure_config_directories,
    APP_NAME, APP_AUTHOR
)

class TestConfigDirs(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    @patch('termcap.config_dirs.platformdirs.user_config_dir')
    @patch('termcap.config_dirs.platformdirs.user_data_dir')
    def test_ensure_config_directories(self, mock_data_dir, mock_config_dir):
        """Test that configuration directories are created"""
        config_path = Path(self.temp_dir) / "config"
        data_path = Path(self.temp_dir) / "data"
        
        mock_config_dir.return_value = str(config_path)
        mock_data_dir.return_value = str(data_path)
        
        ensure_config_directories()
        
        # Check that directories were created
        self.assertTrue(config_path.exists())
        self.assertTrue(data_path.exists())
        self.assertTrue((config_path / "templates").exists())
        
    @patch('termcap.config_dirs.platformdirs.user_config_dir')
    def test_get_config_dir(self, mock_config_dir):
        """Test get_config_dir function"""
        config_path = Path(self.temp_dir) / "config"
        mock_config_dir.return_value = str(config_path)
        
        result = get_config_dir()
        
        self.assertEqual(result, config_path)
        self.assertTrue(config_path.exists())
        
    @patch('termcap.config_dirs.platformdirs.user_data_dir')
    def test_get_data_dir(self, mock_data_dir):
        """Test get_data_dir function"""
        data_path = Path(self.temp_dir) / "data"
        mock_data_dir.return_value = str(data_path)
        
        result = get_data_dir()
        
        self.assertEqual(result, data_path)
        self.assertTrue(data_path.exists())
        
    @patch('termcap.config_dirs.platformdirs.user_config_dir')
    def test_get_templates_dir(self, mock_config_dir):
        """Test get_templates_dir function"""
        config_path = Path(self.temp_dir) / "config"
        mock_config_dir.return_value = str(config_path)
        
        result = get_templates_dir()
        
        expected = config_path / "templates"
        self.assertEqual(result, expected)
        self.assertTrue(expected.exists())
        
    @patch('termcap.config_dirs.platformdirs.user_config_dir')
    def test_get_config_file(self, mock_config_dir):
        """Test get_config_file function"""
        config_path = Path(self.temp_dir) / "config"
        mock_config_dir.return_value = str(config_path)
        
        result = get_config_file()
        
        expected = config_path / "config.toml"
        self.assertEqual(result, expected)
        # Config file should not be created automatically
        self.assertTrue(config_path.exists())  # Directory should exist
        
    def test_app_constants(self):
        """Test application constants"""
        self.assertEqual(APP_NAME, "termcap")
        self.assertEqual(APP_AUTHOR, "rexwzh")
