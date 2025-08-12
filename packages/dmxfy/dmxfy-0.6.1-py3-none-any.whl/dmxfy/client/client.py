import http.client
import json
import socket
from typing import Any

from dmxfy.config.config import Config
from dmxfy.exceptions.exceptions import TranslationError
from dmxfy.languages.languages import LANGUAGES


class TranslationClient:
    """Client for handling translations with the DashScope API"""

    def __init__(self) -> None:
        self.config = Config()

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text using the DashScope API

        Args:
            text: The text to translate
            source_lang: The source language name (in Chinese)
            target_lang: The target language name (in Chinese)

        Returns:
            The translated text

        Raises:
            TranslationError: If there's an error during translation
        """
        if not text.strip():
            return "请输入要翻译的文本"

        try:
            # Create a new connection for each request to avoid connection issues
            conn: http.client.HTTPSConnection = http.client.HTTPSConnection(
                "dashscope.aliyuncs.com"
            )

            # Prepare the request data
            json_data = {
                "model": "qwen-mt-turbo",
                "messages": [
                    {
                        "role": "user",
                        "content": text,
                    },
                ],
                "translation_options": {
                    "source_lang": LANGUAGES.get(source_lang, "auto"),
                    "target_lang": LANGUAGES.get(target_lang, "English"),
                },
            }

            # Make the request
            conn.request(
                "POST",
                "/compatible-mode/v1/chat/completions",
                json.dumps(json_data),
                self.config.headers,
            )

            # Get and parse the response
            response = conn.getresponse()
            resp_str = response.read().decode("utf-8")

            # Check if response is valid
            if not resp_str:
                raise TranslationError("Received empty response from server")

            resp_json: dict[str, Any] = json.loads(resp_str)

            # Close the connection
            conn.close()

            # Check if we have a valid response structure
            if "choices" not in resp_json or not resp_json["choices"]:
                raise TranslationError(f"Invalid response format: {resp_json}")

            return str(resp_json["choices"][0]["message"]["content"])

        except (socket.gaierror, TimeoutError, ConnectionRefusedError) as e:
            raise TranslationError(f"Network connection error: {str(e)}") from e
        except http.client.RemoteDisconnected as e:
            raise TranslationError(
                "Remote server disconnected unexpectedly. Please try again."
            ) from e
        except http.client.ResponseNotReady as e:
            raise TranslationError(
                "Server not ready to respond. Please try again."
            ) from e
        except json.JSONDecodeError as e:
            raise TranslationError(f"Failed to parse server response: {str(e)}") from e
        except Exception as e:
            raise TranslationError(f"Translation failed: {str(e)}") from e
