import sys
from typing import NoReturn

from dmxfy.client.client import TranslationClient
from dmxfy.exceptions.exceptions import DMXFYException


class CLI:
    """Command-line interface for DMXFY"""

    def __init__(self) -> None:
        self.client = TranslationClient()
        self.target_lang = "英语"
        self.source_lang = "简体中文"
        self.prompt_str = "汉译英> "

    def run(self) -> NoReturn:
        """Run the CLI interface"""
        print("Welcome to DMXFY - 大语言模型翻译器")
        print("Type '\\e' to switch to English-to-Chinese translation")
        print("Type '\\c' to switch to Chinese-to-English translation")
        print("Press Ctrl+C to exit")

        while True:
            try:
                text = input(self.prompt_str)
            except KeyboardInterrupt:
                print("\nGoodbye!")
                sys.exit(0)
            except EOFError:
                print("Goodbye!")
                sys.exit(0)

            if text.startswith("\\e"):
                self._switch_to_en_to_ch()
            elif text.startswith("\\c"):
                self._switch_to_ch_to_en()
            else:
                self._translate(text)

    def _switch_to_en_to_ch(self) -> None:
        """Switch to English-to-Chinese translation mode"""
        self.target_lang = "简体中文"
        self.source_lang = "英语"
        self.prompt_str = "En2Ch> "
        print("Translate English to Chinese")

    def _switch_to_ch_to_en(self) -> None:
        """Switch to Chinese-to-English translation mode"""
        self.target_lang = "英语"
        self.source_lang = "简体中文"
        self.prompt_str = "汉译英> "
        print("翻译成英文")

    def _translate(self, text: str) -> None:
        """Translate text and print the result"""
        try:
            result = self.client.translate(
                text, source_lang=self.source_lang, target_lang=self.target_lang
            )
            print(result)
        except DMXFYException as e:
            print(f"Error: {e}", file=sys.stderr)
