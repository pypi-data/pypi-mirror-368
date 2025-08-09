# MarkThat

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/markthat.svg)](https://badge.fury.io/py/markthat)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A  Python library for converting images and PDFs to Markdown or generating rich image descriptions using state-of-the-art multimodal LLMs.

## 🚀 Features

- **Multiple Provider Support**: OpenAI, Anthropic, Google Gemini, Mistral, and OpenRouter
- **Dual Mode Operation**: Convert to Markdown or generate detailed descriptions
- **Advanced Figure Extraction**: Automatically detect, extract, and process figures from PDFs
- **Robust Retry Logic**: Intelligent retry with fallback models and failure feedback
 - **Async Support**: Concurrent processing for improved performance
 - **Clean architecture**: Type-safe, well-documented, and thoroughly tested
 - **Easy Integration**: Simple API with comprehensive configuration options

## 📦 Option 1: Install from PyPI

```bash
pip install markthat
```

### Option 2: Development Installation

```bash
git clone https://github.com/Flopsky/markthat.git
cd markthat
pip install -e .
pre-commit install
```

## 🏃 Quick Start

### Basic Usage

```python
from markthat import MarkThat

# Initialize with your preferred model
converter = MarkThat(
    model="gemini-2.0-flash-001",
    provider="gemini",
    api_key="YOUR_API_KEY"
)

# Convert image to markdown
result = converter.convert("path/to/image.jpg")
print(result[0])

# Generate image description
description = converter.convert(
    "path/to/image.jpg", 
    description_mode=True
)
print(description[0])
```

### Updated Examples from `examples/basic_usage.py`

```python
from markthat import MarkThat
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

def test_markthat_with_figure_extraction():
    """Test MarkThat with advanced figure extraction capabilities."""
    try:
        client = MarkThat(
            provider="gemini",
            model="gemini-2.0-flash-001",
            api_key=os.getenv("GEMINI_API_KEY"),
            api_key_figure_detector=os.getenv("GEMINI_API_KEY"),
            api_key_figure_extractor=os.getenv("GEMINI_API_KEY"),
            api_key_figure_parser=os.getenv("GEMINI_API_KEY"),
        )

        result = asyncio.run(
            client.async_convert(
                "path/to/document.pdf",
                extract_figure=True,
                coordinate_model="gemini-2.0-flash-001",
                parsing_model="gemini-2.5-flash-lite",
            )
        )
        return result
    except Exception as e:
        print("Figure extraction failed:", e)
        return None

def test_markthat_without_figure_extraction():
    """Test standard MarkThat conversion without figure extraction."""
    try:
        client = MarkThat(
            provider="gemini",
            model="gemini-2.0-flash-001",
            api_key=os.getenv("GEMINI_API_KEY"),
        )

        result = asyncio.run(
            client.async_convert(
                "path/to/document.pdf",
                extract_figure=False,
            )
        )
        return result
    except Exception as e:
        print("Standard conversion failed:", e)
        return None

if __name__ == "__main__":
    # Test both approaches
    with_figures = test_markthat_with_figure_extraction()
    without_figures = test_markthat_without_figure_extraction()
    
    print("With figure extraction:", with_figures)
    print("Without figure extraction:", without_figures)
```

## 🖥️ Gradio UI (Visual App)

Quickly try MarkThat in your browser.

```bash
pip install -r requirements.txt  # ensures gradio is installed
python gradio_ui.py
```

Then open `http://localhost:7861` in your browser.

- Supports multiple providers with per-step model overrides
- Lets you pass provider-specific API keys (auto-fills from env when available)
- Exports results as Markdown or JSON with detected figure paths

## 🔧 Advanced Configuration

### Provider-Specific Setup

```python
from markthat import MarkThat, RetryPolicy

# Custom retry policy
retry_policy = RetryPolicy(
    max_attempts=5,
    timeout_seconds=30,
    backoff_factor=1.5
)

# Multi-provider setup with fallbacks
converter = MarkThat(
    model="gpt-4o",
    provider="openai",
    fallback_models=["claude-3-5-sonnet-20241022", "gemini-2.0-flash-001"],
    retry_policy=retry_policy,
    api_key="YOUR_OPENAI_KEY"
)
```

### OpenRouter Integration

```python
# Access 300+ models through OpenRouter
converter = MarkThat(
    model="anthropic/claude-3.5-sonnet",
    provider="openrouter",
    api_key="YOUR_OPENROUTER_KEY"
)

# Or use model path auto-detection
converter = MarkThat(
    model="openai/gpt-4o",  # Automatically uses OpenRouter
    api_key="YOUR_OPENROUTER_KEY"
)
```

## 🎯 Figure Extraction Pipeline

MarkThat includes a sophisticated figure extraction system for PDFs:

```python
converter = MarkThat(
    model="gemini-2.0-flash-001",
    api_key_figure_detector="DETECTOR_KEY",
    api_key_figure_extractor="EXTRACTOR_KEY", 
    api_key_figure_parser="PARSER_KEY"
)

results = await converter.async_convert(
    "research_paper.pdf",
    extract_figure=True,
    figure_detector_model="gemini-2.0-flash",
    coordinate_model="gemini-2.0-flash-001",
    parsing_model="gemini-2.5-flash-lite"
)
```

### How Figure Extraction Works

1. **Detection**: Analyzes document content to identify pages with figures
2. **Coordinate Mapping**: Overlays coordinate grids and identifies figure boundaries  
3. **Extraction**: Crops figures using precise coordinate mapping
4. **Integration**: Embeds figure paths into the final markdown output

## ⚡ Async Processing

For optimal performance with multi-page documents:

```python
import asyncio
from markthat import MarkThat

async def process_document():
    converter = MarkThat(model="gemini-2.0-flash-001")
    
    # Process pages concurrently
    results = await converter.async_convert("large_document.pdf")
    
    for i, page_content in enumerate(results):
        print(f"Page {i+1}: {len(page_content)} characters")

asyncio.run(process_document())
```

## 🔑 Environment Variables

```bash
# Primary providers (used automatically if constructor api_key is not provided)
export OPENAI_API_KEY="your_openai_key"
export ANTHROPIC_API_KEY="your_anthropic_key"
export GEMINI_API_KEY="your_google_key"
export MISTRAL_API_KEY="your_mistral_key"

# Unified access via OpenRouter
export OPENROUTER_API_KEY="your_openrouter_key"
```

Note: For figure extraction you can pass separate keys via the constructor
parameters `api_key_figure_detector`, `api_key_figure_extractor`, and
`api_key_figure_parser`. If omitted, they default to the main `api_key`.

## 🧪 Testing

```bash
# Run the test suite
pytest

# Run with coverage
pytest --cov=markthat

# Run a specific test file
pytest tests/test_validation.py
```

## 📁 Project Structure

```
markthat/
├── markthat/
│   ├── __init__.py          # Public API
│   ├── client.py            # Main MarkThat class
│   ├── providers.py         # LLM provider abstractions
│   ├── file_processor.py    # PDF/image loading
│   ├── image_processing.py  # Image manipulation
│   ├── figure_extraction.py # Figure detection & extraction
│   ├── prompts/             # Prompt templates & utilities
│   ├── utils/               # Validation & helpers
│   ├── exceptions.py        # Custom exceptions
│   └── logging_config.py    # Logging setup
├── gradio_ui.py             # Visual demo app
├── tests/                   # Test suite
├── examples/                # Usage examples
├── pyproject.toml          # Project metadata
└── README.md               # This file
```

## 🛠️ Development

### Code Quality

This project uses modern Python development practices:

- **Type Hints**: Full type annotations with mypy validation
- **Code Formatting**: Black for consistent code style
- **Linting**: Ruff for fast, comprehensive linting
- **Import Sorting**: isort for organized imports
- **Pre-commit Hooks**: Automated quality checks

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes with proper tests
4. Run quality checks: `pre-commit run --all-files`
5. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -e .[dev]

# Set up pre-commit hooks
pre-commit install

# Run quality checks
black .
ruff check .
isort .
mypy markthat
```

## 📄 API Reference

### MarkThat Class

```python
class MarkThat:
    def __init__(
        self,
        model: str,
        *,
        provider: Optional[str] = None,
        fallback_models: Optional[Sequence[str]] = None,
        retry_policy: Optional[RetryPolicy] = None,
        api_key: Optional[str] = None,
        api_key_figure_detector: Optional[str] = None,
        api_key_figure_extractor: Optional[str] = None,
        api_key_figure_parser: Optional[str] = None,
        max_retry: int = 3,
    ) -> None: ...

    def convert(
        self,
        file_path: str,
        *,
        format_options: Optional[Dict[str, Any]] = None,
        additional_instructions: Optional[str] = None,
        description_mode: bool = False,
        extract_figure: bool = False,
        figure_detector_model: str = "gemini-2.0-flash",
        coordinate_model: str = "gemini-2.0-flash",
        parsing_model: str = "gemini-2.5-flash-lite",
        max_retry: Optional[int] = None,
        clean_output: bool = True,
    ) -> List[str]: ...

    async def async_convert(
        self,
        file_path: str,
        *,
        format_options: Optional[Dict[str, Any]] = None,
        additional_instructions: Optional[str] = None,
        description_mode: bool = False,
        extract_figure: bool = False,
        figure_detector_model: str = "gemini-2.0-flash",
        coordinate_model: str = "gemini-2.0-flash",
        parsing_model: str = "gemini-2.5-flash-lite",
        max_retry: Optional[int] = None,
        clean_output: bool = True,
    ) -> List[str]: ...
```

### RetryPolicy Configuration

```python
@dataclass
class RetryPolicy:
    max_attempts: int = 3
    timeout_seconds: int = 30
    backoff_factor: float = 1.0
```

## 🏆 Supported Models

### Direct Provider Access
- **OpenAI**: gpt-4o, gpt-4-turbo, gpt-4o-mini
- **Anthropic**: claude-3-5-sonnet-20241022, claude-3-opus, claude-3-haiku
- **Google**: gemini-2.0-flash-001, gemini-1.5-pro, gemini-1.5-flash
- **Mistral**: mistral-large-latest, mistral-medium, mistral-small

### OpenRouter Models (300+)
- **Meta**: meta-llama/llama-3.2-90b-vision
- **Qwen**: qwen/qwen-2-vl-72b-instruct  
- **Many more**: Access the full catalog at [OpenRouter](https://openrouter.ai)

## 🐛 Error Handling

MarkThat provides comprehensive error handling:

```python
from markthat import MarkThat
from markthat.exceptions import ProviderInitializationError, ConversionError

try:
    converter = MarkThat(model="invalid-model")
except ProviderInitializationError as e:
    print(f"Provider setup failed: {e}")

try:
    result = converter.convert("image.jpg")
except ConversionError as e:
    print(f"Conversion failed: {e}")
```

## 📊 Performance Tips

1. **Use Async for Multiple Pages**: `async_convert()` processes pages concurrently
2. **Configure Appropriate Timeouts**: Balance speed vs. reliability
3. **Choose the Right Model**: Faster models for simple tasks, powerful models for complex content
4. **Leverage Fallbacks**: Set up model hierarchies for reliability

## 📈 Roadmap

- [x] ✅ Multi-provider LLM support
- [x] ✅ PDF processing with figure extraction
- [x] ✅ Async processing capabilities
- [x] ✅ Comprehensive retry logic
- [x] ✅ Type-safe, clean architecture
- [ ] 🔄 Additional file format support (TIFF, WEBP)
- [ ] 🔄 Cost tracking and optimization
- [ ] 🔄 Batch processing API
- [ ] 🔄 Custom prompt template system

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern Python best practices
- Leverages state-of-the-art multimodal LLMs
- Inspired by the need for robust document processing tools

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/Flopsky/markthat/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Flopsky/markthat/discussions)
- **Documentation**: See `docs/` for Sphinx sources

---

**MarkThat** - Transform visual content into structured text with the power of AI 🚀