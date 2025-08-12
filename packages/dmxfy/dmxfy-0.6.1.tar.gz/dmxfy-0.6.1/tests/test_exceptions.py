from dmxfy.exceptions.exceptions import DMXFYException, TranslationError, ConfigurationError


class TestExceptions:
    """Tests for the exceptions module"""

    def test_dmxify_exception(self):
        """Test DMXFYException"""
        exception = DMXFYException("Test message")
        assert str(exception) == "Test message"

    def test_translation_error(self):
        """Test TranslationError"""
        exception = TranslationError("Test message")
        assert isinstance(exception, DMXFYException)
        assert str(exception) == "Test message"

    def test_configuration_error(self):
        """Test ConfigurationError"""
        exception = ConfigurationError("Test message")
        assert isinstance(exception, DMXFYException)
        assert str(exception) == "Test message"
