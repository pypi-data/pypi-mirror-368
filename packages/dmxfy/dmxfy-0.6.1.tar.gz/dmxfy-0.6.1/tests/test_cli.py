import pytest
from unittest.mock import Mock, patch

from dmxfy.cli.cli import CLI


class TestCLI:
    """Tests for the CLI class"""

    @patch('dmxfy.cli.cli.TranslationClient')
    def test_init(self, mock_translation_client):
        """Test that the CLI initializes correctly"""
        mock_client_instance = Mock()
        mock_translation_client.return_value = mock_client_instance

        cli = CLI()

        assert cli.client == mock_client_instance
        assert cli.target_lang == "英语"
        assert cli.source_lang == "简体中文"
        assert cli.prompt_str == "汉译英> "

    @patch('dmxfy.cli.cli.TranslationClient')
    def test_switch_to_en_to_ch(self, mock_translation_client):
        """Test switching to English-to-Chinese translation mode"""
        mock_translation_client.return_value = Mock()

        cli = CLI()
        cli._switch_to_en_to_ch()

        assert cli.target_lang == "简体中文"
        assert cli.source_lang == "英语"
        assert cli.prompt_str == "En2Ch> "

    @patch('dmxfy.cli.cli.TranslationClient')
    def test_switch_to_ch_to_en(self, mock_translation_client):
        """Test switching to Chinese-to-English translation mode"""
        mock_translation_client.return_value = Mock()

        cli = CLI()
        cli._switch_to_ch_to_en()

        assert cli.target_lang == "英语"
        assert cli.source_lang == "简体中文"
        assert cli.prompt_str == "汉译英> "
