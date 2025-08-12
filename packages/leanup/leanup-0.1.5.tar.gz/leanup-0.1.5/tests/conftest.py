import tempfile
import pytest
from pathlib import Path
from leanup.const import LEANUP_CACHE_DIR, LEANUP_CONFIG_DIR
from leanup.utils.config import ConfigManager

@pytest.fixture
def cache_dir():
    """Fixture to provide the LeanUp cache directory."""
    return LEANUP_CACHE_DIR

@pytest.fixture
def config_dir():
    """Fixture to provide the LeanUp config directory."""
    return LEANUP_CONFIG_DIR

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture
def mock_elan_home(temp_dir):
    """Create a mock elan home directory for testing"""
    elan_home = temp_dir / '.elan'
    elan_home.mkdir()
    (elan_home / 'bin').mkdir()
    return elan_home

@pytest.fixture
def mock_config_manager(temp_dir):
    """Create a mock config manager for testing"""
    config_dir = temp_dir / '.leanup'
    config_manager = ConfigManager(config_dir=config_dir)
    config_manager.init_config()
    return config_manager

@pytest.fixture
def mock_repo_cache(temp_dir):
    """Create a mock repository cache directory"""
    cache_dir = temp_dir / 'repos'
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir