# DMXFY - 大语言模型翻译器

DMXFY is a terminal-based translation tool powered by Alibaba Cloud's Qwen-MT-Turbo model. It provides a simple command-line interface for translating text between multiple languages.

## Features

- Interactive terminal interface
- Support for 40+ languages
- Switch between translation directions (Chinese to English / English to Chinese)
- Powered by Alibaba Cloud's Qwen-MT-Turbo model

## Installation

```bash
pip install dmxfy
```

## Configuration

Before using DMXFY, you need to set your Alibaba Cloud API key as an environment variable:

```bash
export DMXFY_API_KEY=your_api_key_here
```

## Usage

Run the tool with:

```bash
dmxfy
```

### Commands

- `\\e` - Switch to English-to-Chinese translation mode
- `\\c` - Switch to Chinese-to-English translation mode
- `Ctrl+C` - Exit the program

## Development

### Setup

1. Clone the repository
2. Install dependencies with `pip install -e .`
3. Set the `DMXFY_API_KEY` environment variable

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Run linter
ruff check .

# Run type checker
mypy src/

# Format code
black src/
```

## License

MIT
