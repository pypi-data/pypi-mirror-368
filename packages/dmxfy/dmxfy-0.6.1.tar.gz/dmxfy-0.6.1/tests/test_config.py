import pytest
import os
from unittest.mock import patch

from dmxfy.config.config import Config
from dmxfy.exceptions.exceptions import ConfigurationError


class TestConfig:
    """Tests for the Config class"""

    def test_init_with_api_key(self):
        """Test initialization with API key"""
        with patch.dict(os.environ, {"DMXFY_API_KEY": "test_key"}):
            config = Config()
            assert config.api_key == "test_key"

    def test_init_without_api_key(self):
        """Test initialization without API key"""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            with pytest.raises(ConfigurationError):
                _ = config.api_key

    def test_headers(self):
        """Test headers property"""
        with patch.dict(os.environ, {"DMXFY_API_KEY": "test_key"}):
            config = Config()
            headers = config.headers
            assert headers == {
                "Authorization": "Bearer test_key",
                "Content-Type": "application/json",
            }
