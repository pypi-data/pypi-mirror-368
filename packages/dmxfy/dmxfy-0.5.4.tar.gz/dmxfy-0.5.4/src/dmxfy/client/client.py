import http.client
import json
from typing import Any

from dmxfy.config.config import Config
from dmxfy.exceptions.exceptions import TranslationError
from dmxfy.languages.languages import LANGUAGES


class TranslationClient:
    """Client for handling translations with the DashScope API"""

    def __init__(self) -> None:
        self.config = Config()
        self._conn: http.client.HTTPSConnection = http.client.HTTPSConnection(
            "dashscope.aliyuncs.com"
        )

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
            self._conn.request(
                "POST",
                "/compatible-mode/v1/chat/completions",
                json.dumps(json_data),
                self.config.headers,
            )

            # Get and parse the response
            response = self._conn.getresponse()
            resp_str = response.read().decode("utf-8")
            resp_json: dict[str, Any] = json.loads(resp_str)

            return str(resp_json["choices"][0]["message"]["content"])

        except Exception as e:
            raise TranslationError(f"Translation failed: {str(e)}") from e
