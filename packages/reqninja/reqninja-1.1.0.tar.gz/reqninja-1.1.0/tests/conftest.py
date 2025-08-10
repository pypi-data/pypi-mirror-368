"""Test configuration for ReqNinja."""

import pytest
import responses
from pathlib import Path
import tempfile
import os

from reqninja import Config, ReqNinjaClient


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        'default_retries': 3,
        'default_timeout': 30,
        'default_headers': {
            'User-Agent': 'ReqNinja/1.0'
        },
        'retry_policy': {
            'total': 3,
            'status_forcelist': [429, 500, 502, 503, 504],
            'backoff_factor': 0.5
        },
        'profiles': {
            'test': {
                'base_url': 'https://api.test.com',
                'headers': {
                    'Authorization': 'Bearer test-token'
                }
            },
            'prod': {
                'base_url': 'https://api.prod.com',
                'headers': {
                    'Authorization': 'Bearer ${PROD_TOKEN}'
                }
            }
        }
    }


@pytest.fixture
def mock_responses():
    """Mock HTTP responses for testing."""
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def client():
    """Create a test client."""
    return ReqNinjaClient()


@pytest.fixture
def config_with_file(temp_config_dir, sample_config):
    """Create a config with a temporary file."""
    import yaml
    
    config_file = temp_config_dir / 'config.yml'
    with open(config_file, 'w') as f:
        yaml.dump(sample_config, f)
    
    return Config(config_file)
