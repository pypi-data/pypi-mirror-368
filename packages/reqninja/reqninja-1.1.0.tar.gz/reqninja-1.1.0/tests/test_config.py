"""Test cases for ReqNinja configuration."""

import pytest
import tempfile
from pathlib import Path
import yaml

from reqninja.config import Config
from reqninja.exceptions import ConfigError, ProfileNotFoundError


class TestConfig:
    """Test configuration management."""
    
    def test_default_config(self):
        """Test default configuration creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'config.yml'
            config = Config(config_path)
            
            assert config.get('default_retries') == 3
            assert config.get('default_timeout') == 30
            assert 'User-Agent' in config.get('default_headers', {})
    
    def test_load_existing_config(self, temp_config_dir, sample_config):
        """Test loading existing configuration."""
        config_file = temp_config_dir / 'config.yml'
        with open(config_file, 'w') as f:
            yaml.dump(sample_config, f)
        
        config = Config(config_file)
        
        assert config.get('default_retries') == 3
        assert len(config.get('profiles', {})) == 2
    
    def test_get_nested_config(self, config_with_file):
        """Test getting nested configuration values."""
        config = config_with_file
        
        assert config.get('retry_policy.total') == 3
        assert config.get('retry_policy.backoff_factor') == 0.5
        assert config.get('nonexistent.key', 'default') == 'default'
    
    def test_get_profile(self, config_with_file):
        """Test getting profile configuration."""
        config = config_with_file
        
        profile = config.get_profile('test')
        assert profile['base_url'] == 'https://api.test.com'
        assert 'Authorization' in profile['headers']
    
    def test_get_nonexistent_profile(self, config_with_file):
        """Test getting non-existent profile."""
        config = config_with_file
        
        with pytest.raises(ProfileNotFoundError):
            config.get_profile('nonexistent')
    
    def test_list_profiles(self, config_with_file):
        """Test listing profiles."""
        config = config_with_file
        
        profiles = config.list_profiles()
        assert 'test' in profiles
        assert 'prod' in profiles
        assert len(profiles) == 2
    
    def test_add_profile(self, temp_config_dir):
        """Test adding a new profile."""
        config_file = temp_config_dir / 'config.yml'
        config = Config(config_file)
        
        new_profile = {
            'base_url': 'https://api.new.com',
            'headers': {'X-API-Key': 'new-key'}
        }
        
        config.add_profile('new', new_profile)
        
        # Verify profile was added
        profiles = config.list_profiles()
        assert 'new' in profiles
        
        # Verify profile content
        profile = config.get_profile('new')
        assert profile['base_url'] == 'https://api.new.com'
    
    def test_remove_profile(self, config_with_file):
        """Test removing a profile."""
        config = config_with_file
        
        # Initially should have test profile
        assert 'test' in config.list_profiles()
        
        # Remove profile
        config.remove_profile('test')
        
        # Should no longer exist
        assert 'test' not in config.list_profiles()
    
    def test_remove_nonexistent_profile(self, config_with_file):
        """Test removing non-existent profile."""
        config = config_with_file
        
        with pytest.raises(ProfileNotFoundError):
            config.remove_profile('nonexistent')
    
    def test_merge_profile_config(self, config_with_file):
        """Test merging profile with base configuration."""
        config = config_with_file
        
        merged = config.merge_profile_config('test')
        
        # Should have base settings
        assert merged['retries'] == 3
        assert merged['timeout'] == 30
        
        # Should have profile-specific settings
        assert merged['base_url'] == 'https://api.test.com'
        
        # Should merge headers
        assert 'User-Agent' in merged['headers']
        assert 'Authorization' in merged['headers']
    
    def test_env_var_expansion(self, temp_config_dir):
        """Test environment variable expansion."""
        import os
        
        # Set test environment variable
        os.environ['TEST_TOKEN'] = 'secret-token'
        
        try:
            config_data = {
                'profiles': {
                    'test': {
                        'headers': {
                            'Authorization': 'Bearer ${TEST_TOKEN}'
                        }
                    }
                }
            }
            
            config_file = temp_config_dir / 'config.yml'
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f)
            
            config = Config(config_file)
            profile = config.get_profile('test')
            
            assert profile['headers']['Authorization'] == 'Bearer secret-token'
        finally:
            # Clean up
            if 'TEST_TOKEN' in os.environ:
                del os.environ['TEST_TOKEN']
    
    def test_invalid_yaml(self, temp_config_dir):
        """Test handling of invalid YAML."""
        config_file = temp_config_dir / 'config.yml'
        with open(config_file, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        with pytest.raises(ConfigError):
            Config(config_file)
