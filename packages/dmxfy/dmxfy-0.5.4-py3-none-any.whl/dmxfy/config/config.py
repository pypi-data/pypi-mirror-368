import os

from dmxfy.exceptions.exceptions import ConfigurationError


class Config:
    """Configuration management for DMXFY"""

    def __init__(self) -> None:
        self._api_key: str | None = None
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from environment variables"""
        self._api_key = os.getenv("DMXFY_API_KEY")

    @property
    def api_key(self) -> str:
        """Get the API key"""
        if not self._api_key:
            raise ConfigurationError(
                "API key not found. Please set the DMXFY_API_KEY environment variable."
            )
        return self._api_key

    @property
    def headers(self) -> dict[str, str]:
        """Get the headers for API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
