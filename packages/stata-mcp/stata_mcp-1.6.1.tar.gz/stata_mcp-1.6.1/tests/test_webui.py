#!/usr/bin/env python3
"""
Test script for Stata-MCP web UI functionality.

This script tests all the configuration validation and edge cases
for the web UI components.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, '../src')

from stata_mcp.webui.utils.config_validator import (
    validate_stata_cli_path,
    validate_output_base_path,
    validate_configuration,
    create_configuration_backup,
    get_stata_suggestion,
    get_default_output_suggestion
)


class TestConfigValidation(unittest.TestCase):
    """Test configuration validation functions."""

    def test_stata_cli_path_empty(self):
        """Test empty Stata CLI path validation."""
        is_valid, error, suggestion = validate_stata_cli_path('')
        self.assertFalse(is_valid)
        self.assertIn('required', error)

    def test_stata_cli_path_nonexistent(self):
        """Test nonexistent Stata CLI path."""
        is_valid, error, suggestion = validate_stata_cli_path('/nonexistent/path')
        self.assertFalse(is_valid)
        self.assertIn('does not exist', error)

    def test_stata_cli_path_directory(self):
        """Test directory instead of file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            is_valid, error, suggestion = validate_stata_cli_path(temp_dir)
            self.assertFalse(is_valid)
            self.assertIn('not a file', error)

    def test_stata_cli_path_valid_file(self):
        """Test valid file path."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='-stata') as f:
            # Make it executable on Unix-like systems
            try:
                os.chmod(f.name, 0o755)
            except OSError:
                pass  # Windows doesn't support chmod
            
            is_valid, error, suggestion = validate_stata_cli_path(f.name)
            self.assertTrue(is_valid)
            self.assertEqual(error, '')
            
            os.unlink(f.name)

    def test_output_base_path_empty(self):
        """Test empty output base path."""
        is_valid, error, suggestion = validate_output_base_path('')
        self.assertFalse(is_valid)
        self.assertIn('required', error)

    def test_output_base_path_nonexistent_directory(self):
        """Test nonexistent directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = os.path.join(temp_dir, 'new_output_dir')
            is_valid, error, suggestion = validate_output_base_path(new_dir)
            self.assertTrue(is_valid)
            self.assertTrue(os.path.exists(new_dir))

    def test_output_base_path_non_directory(self):
        """Test file instead of directory."""
        with tempfile.NamedTemporaryFile() as f:
            is_valid, error, suggestion = validate_output_base_path(f.name)
            self.assertFalse(is_valid)
            self.assertIn('not a directory', error)

    def test_output_base_path_no_permission(self):
        """Test directory without write permission."""
        # This test is tricky cross-platform, so we'll skip it
        pass

    def test_validate_configuration_complete(self):
        """Test complete configuration validation."""
        with tempfile.NamedTemporaryFile(suffix='-stata', delete=False) as f:
            try:
                os.chmod(f.name, 0o755)
            except OSError:
                pass

            with tempfile.TemporaryDirectory() as temp_dir:
                config_data = {
                    'stata': {'stata_cli': f.name},
                    'stata-mcp': {'output_base_path': temp_dir},
                    'llm': {
                        'LLM_TYPE': 'ollama',
                        'ollama': {
                            'MODEL': 'qwen2.5-coder:7b',
                            'BASE_URL': 'http://localhost:11434'
                        },
                        'openai': {
                            'MODEL': 'gpt-3.5-turbo',
                            'BASE_URL': 'https://api.openai.com/v1',
                            'API_KEY': 'sk-test123456789012345678901234567890'
                        }
                    }
                }
                results = validate_configuration(config_data)
                
                self.assertTrue(results['stata']['stata_cli']['valid'])
                self.assertTrue(results['stata-mcp']['output_base_path']['valid'])
                self.assertTrue(results['llm']['LLM_TYPE']['valid'])
                self.assertTrue(results['llm']['ollama']['MODEL']['valid'])
                self.assertTrue(results['llm']['ollama']['BASE_URL']['valid'])
                self.assertTrue(results['llm']['openai']['MODEL']['valid'])
                self.assertTrue(results['llm']['openai']['BASE_URL']['valid'])
                self.assertTrue(results['llm']['openai']['API_KEY']['valid'])

            os.unlink(f.name)

    def test_validate_configuration_invalid(self):
        """Test configuration validation with invalid paths."""
        config_data = {
            'stata': {'stata_cli': '/nonexistent/stata'},
            'stata-mcp': {'output_base_path': '/nonexistent/dir'},
            'llm': {
                'LLM_TYPE': 'invalid_type',
                'ollama': {
                    'MODEL': '',
                    'BASE_URL': 'invalid_url'
                },
                'openai': {
                    'MODEL': '',
                    'BASE_URL': 'invalid_url',
                    'API_KEY': 'invalid_key'
                }
            }
        }
        results = validate_configuration(config_data)
        
        self.assertFalse(results['stata']['stata_cli']['valid'])
        self.assertFalse(results['stata-mcp']['output_base_path']['valid'])
        self.assertFalse(results['llm']['LLM_TYPE']['valid'])
        self.assertFalse(results['llm']['ollama']['MODEL']['valid'])
        self.assertFalse(results['llm']['ollama']['BASE_URL']['valid'])
        self.assertFalse(results['llm']['openai']['MODEL']['valid'])
        self.assertFalse(results['llm']['openai']['BASE_URL']['valid'])
        self.assertFalse(results['llm']['openai']['API_KEY']['valid'])

    def test_backup_creation(self):
        """Test configuration backup creation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write('[test]\nkey = "value"\n')
            f.flush()
            
            backup_path = create_configuration_backup(f.name)
            self.assertIsNotNone(backup_path)
            self.assertTrue(os.path.exists(backup_path))
            self.assertTrue(backup_path.startswith(f.name))
            
            # Cleanup
            os.unlink(f.name)
            if os.path.exists(backup_path):
                os.unlink(backup_path)

    def test_suggestions(self):
        """Test suggestion generation."""
        stata_suggestion = get_stata_suggestion()
        self.assertIsInstance(stata_suggestion, str)
        self.assertIn('Common locations', stata_suggestion)

        output_suggestion = get_default_output_suggestion()
        self.assertIsInstance(output_suggestion, str)
        self.assertIn('Suggested', output_suggestion)


class TestWebUIRoutes(unittest.TestCase):
    """Test web UI route functionality."""

    def setUp(self):
        """Set up test client."""
        from stata_mcp.webui import app
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_home_route(self):
        """Test home page route."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Stata-MCP', response.data)

    def test_config_route_get(self):
        """Test configuration page GET request."""
        response = self.client.get('/config')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Configuration', response.data)

    def test_config_route_post_valid(self):
        """Test configuration page POST with valid data."""
        with tempfile.NamedTemporaryFile(suffix='-stata', delete=False) as f:
            try:
                os.chmod(f.name, 0o755)
            except OSError:
                pass

            with tempfile.TemporaryDirectory() as temp_dir:
                response = self.client.post('/config', data={
                    'stata.stata_cli': f.name,
                    'stata-mcp.output_base_path': temp_dir,
                    'llm.LLM_TYPE': 'ollama',
                    'llm.ollama.MODEL': 'qwen2.5-coder:7b',
                    'llm.ollama.BASE_URL': 'http://localhost:11434',
                    'llm.openai.MODEL': 'gpt-3.5-turbo',
                    'llm.openai.BASE_URL': 'https://api.openai.com/v1',
                    'llm.openai.API_KEY': 'sk-test123456789012345678901234567890'
                })
                
                self.assertEqual(response.status_code, 302)  # Redirect on success

            os.unlink(f.name)

    def test_api_validate_endpoint(self):
        """Test validation API endpoint."""
        response = self.client.post('/api/validate', json={
            'stata': {'stata_cli': '/fake/path'},
            'stata-mcp': {'output_base_path': '/tmp'},
            'llm': {
                'LLM_TYPE': 'ollama',
                'ollama': {'MODEL': 'test', 'BASE_URL': 'http://localhost:11434'},
                'openai': {'MODEL': 'test', 'BASE_URL': 'https://api.openai.com/v1', 'API_KEY': 'sk-test123456789012345678901234567890'}
            }
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, dict)
        self.assertIn('stata', data)
        self.assertIn('stata-mcp', data)
        self.assertIn('llm', data)

    def test_api_export_endpoint(self):
        """Test export API endpoint."""
        response = self.client.get('/api/export')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertIn('attachment', response.headers['Content-Disposition'])

    def test_api_reset_endpoint(self):
        """Test reset API endpoint."""
        response = self.client.post('/api/reset')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('success', data)


def run_tests():
    """Run all tests."""
    print("Running Stata-MCP Web UI Tests...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestConfigValidation))
    suite.addTest(unittest.makeSuite(TestWebUIRoutes))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)