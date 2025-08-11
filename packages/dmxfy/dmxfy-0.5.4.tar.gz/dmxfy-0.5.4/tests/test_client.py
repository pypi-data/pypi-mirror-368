import pytest
from unittest.mock import Mock, patch

from dmxfy.client.client import TranslationClient
from dmxfy.exceptions.exceptions import TranslationError, ConfigurationError


class TestTranslationClient:
    """Tests for the TranslationClient class"""

    @patch('dmxfy.client.client.Config')
    def test_init(self, mock_config):
        """Test that the client initializes correctly"""
        mock_config_instance = Mock()
        mock_config_instance.api_key = "test_key"
        mock_config.return_value = mock_config_instance

        client = TranslationClient()

        assert client.config == mock_config_instance
        mock_config.assert_called_once()

    def test_translate_empty_text(self):
        """Test translating empty text"""
        with patch('dmxfy.config.config.Config'):
            client = TranslationClient()
            result = client.translate("", "英语", "简体中文")
            assert result == "请输入要翻译的文本"

    @patch('dmxfy.client.client.Config')
    @patch('dmxfy.client.client.http.client.HTTPSConnection')
    def test_translate_success(self, mock_conn_class, mock_config):
        """Test successful translation"""
        # Setup mocks
        mock_config_instance = Mock()
        mock_config_instance.headers = {"Authorization": "Bearer test_key", "Content-Type": "application/json"}
        mock_config.return_value = mock_config_instance

        mock_conn = Mock()
        mock_conn_class.return_value = mock_conn

        mock_response = Mock()
        mock_response.read.return_value.decode.return_value = '{"choices": [{"message": {"content": "Hello"}}]}'
        mock_conn.getresponse.return_value = mock_response

        # Run test
        client = TranslationClient()
        result = client.translate("你好", "简体中文", "英语")

        # Assertions
        assert result == "Hello"
        mock_conn.request.assert_called_once()

    @patch('dmxfy.client.client.Config')
    @patch('dmxfy.client.client.http.client.HTTPSConnection')
    def test_translate_api_error(self, mock_conn_class, mock_config):
        """Test translation when API returns an error"""
        # Setup mocks
        mock_config_instance = Mock()
        mock_config_instance.headers = {"Authorization": "Bearer test_key", "Content-Type": "application/json"}
        mock_config.return_value = mock_config_instance

        mock_conn = Mock()
        mock_conn_class.return_value = mock_conn
        mock_conn.request.side_effect = Exception("API error")

        # Run test
        client = TranslationClient()

        with pytest.raises(TranslationError):
            client.translate("你好", "简体中文", "英语")
