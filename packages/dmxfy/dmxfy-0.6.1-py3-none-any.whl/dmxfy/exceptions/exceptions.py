class DMXFYException(Exception):
    """Base exception for DMXFY package"""

    pass


class TranslationError(DMXFYException):
    """Raised when there's an error during translation"""

    pass


class ConfigurationError(DMXFYException):
    """Raised when there's a configuration error"""

    pass
