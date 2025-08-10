"""Test click-based CLI"""
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from termcap.cli import main, config, template

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_version(self):
        """Test --version flag"""
        result = self.runner.invoke(main, ['--version'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('termcap', result.output)
        
    def test_config_show(self):
        """Test config show command"""
        with patch('termcap.cli.show_config') as mock_show:
            result = self.runner.invoke(config, ['show'])
            self.assertEqual(result.exit_code, 0)
            mock_show.assert_called_once()
            
    def test_config_templates(self):
        """Test config templates command"""
        with patch('termcap.cli.list_templates') as mock_list:
            result = self.runner.invoke(config, ['templates'])
            self.assertEqual(result.exit_code, 0)
            mock_list.assert_called_once()
            
    def test_config_reset(self):
        """Test config reset command"""
        with patch('termcap.cli.reset_config') as mock_reset:
            # Test with confirmation
            result = self.runner.invoke(config, ['reset'], input='y')
            self.assertEqual(result.exit_code, 0)
            mock_reset.assert_called_once()
            
            # Test without confirmation
            mock_reset.reset_mock()
            result = self.runner.invoke(config, ['reset'], input='n')
            self.assertEqual(result.exit_code, 0)
            mock_reset.assert_not_called()
            
    def test_config_set(self):
        """Test config set command"""
        with patch('termcap.cli.get_config_manager') as mock_get_manager:
            mock_manager = MagicMock()
            mock_get_manager.return_value = mock_manager
            
            # Test setting string value
            result = self.runner.invoke(config, ['set', 'general', 'default_template', 'my_template'])
            self.assertEqual(result.exit_code, 0)
            mock_manager.set_setting.assert_called_with('general', 'default_template', 'my_template')
            
            # Test setting integer value
            result = self.runner.invoke(config, ['set', 'general', 'default_min_duration', '100'])
            self.assertEqual(result.exit_code, 0)
            mock_manager.set_setting.assert_called_with('general', 'default_min_duration', 100)
            
            # Test setting boolean value
            result = self.runner.invoke(config, ['set', 'templates', 'custom_templates_enabled', 'true'])
            self.assertEqual(result.exit_code, 0)
            mock_manager.set_setting.assert_called_with('templates', 'custom_templates_enabled', True)
            
    def test_config_get(self):
        """Test config get command"""
        with patch('termcap.cli.get_config_manager') as mock_get_manager:
            mock_manager = MagicMock()
            mock_get_manager.return_value = mock_manager
            
            # Test existing value
            mock_manager.get_setting.return_value = 'test_value'
            result = self.runner.invoke(config, ['get', 'general', 'default_template'])
            self.assertEqual(result.exit_code, 0)
            self.assertIn('general.default_template = test_value', result.output)
            
            # Test non-existing value
            mock_manager.get_setting.return_value = None
            result = self.runner.invoke(config, ['get', 'general', 'non_existing'])
            self.assertEqual(result.exit_code, 0)
            self.assertIn('not found', result.output)
            
    def test_template_install(self):
        """Test template install command"""
        # Create a test template file
        template_file = self.temp_dir / "test_template.svg"
        template_file.write_text("<svg>test</svg>")
        
        with patch('termcap.cli.get_config_manager') as mock_get_manager:
            mock_manager = MagicMock()
            mock_get_manager.return_value = mock_manager
            
            result = self.runner.invoke(template, ['install', 'test_template', str(template_file)])
            self.assertEqual(result.exit_code, 0)
            mock_manager.install_custom_template.assert_called_once()
            self.assertIn('installed successfully', result.output)
            
    def test_template_install_error(self):
        """Test template install command with error"""
        template_file = self.temp_dir / "test_template.svg"
        template_file.write_text("<svg>test</svg>")
        
        with patch('termcap.cli.get_config_manager') as mock_get_manager:
            mock_manager = MagicMock()
            mock_manager.install_custom_template.side_effect = Exception("Test error")
            mock_get_manager.return_value = mock_manager
            
            result = self.runner.invoke(template, ['install', 'test_template', str(template_file)])
            self.assertEqual(result.exit_code, 1)
            self.assertIn('Error installing template', result.output)
            
    def test_template_remove(self):
        """Test template remove command"""
        with patch('termcap.cli.get_config_manager') as mock_get_manager:
            mock_manager = MagicMock()
            mock_get_manager.return_value = mock_manager
            
            # Test with confirmation
            result = self.runner.invoke(template, ['remove', 'test_template'], input='y')
            self.assertEqual(result.exit_code, 0)
            mock_manager.remove_custom_template.assert_called_with('test_template')
            
            # Test without confirmation
            mock_manager.reset_mock()
            result = self.runner.invoke(template, ['remove', 'test_template'], input='n')
            self.assertEqual(result.exit_code, 0)
            mock_manager.remove_custom_template.assert_not_called()
            
    def test_template_list(self):
        """Test template list command"""
        with patch('termcap.cli.list_templates') as mock_list:
            result = self.runner.invoke(template, ['list'])
            self.assertEqual(result.exit_code, 0)
            mock_list.assert_called_once()
            
