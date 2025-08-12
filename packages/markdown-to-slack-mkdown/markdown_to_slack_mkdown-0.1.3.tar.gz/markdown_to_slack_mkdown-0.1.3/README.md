# markdown-to-slack-mkdown

Convert GitHub markdown to Slack markdown format.

This is a Python port of [githubmarkdownconvertergo](https://github.com/eritikass/githubmarkdownconvertergo) (Go package). 

## Installation

```bash
pip install markdown-to-slack-mkdown
```

## Usage

```python
from markdown_to_slack_mkdown import slack_convert, SlackConvertOptions

# Basic conversion
markdown_text = "**bold** and ~~strikethrough~~ with [link](https://example.com)"
slack_text = slack_convert(markdown_text)
print(slack_text)  # *bold* and ~strikethrough~ with <https://example.com|link>

# With options
options = SlackConvertOptions(
    headlines=True,  # Convert markdown headers to bold text
    repo_name="owner/repo",  # Link issue references to GitHub
    github_url="https://github.com",  # Custom GitHub URL
    custom_ref_patterns={  # Custom reference patterns
        r'JIRA-(?P<ID>\d+)': "https://jira.example.com/browse/JIRA-${ID}"
    }
)

markdown_text = "## Features\n- Fix #123\n- JIRA-456"
slack_text = slack_convert(markdown_text, options)
```

## Features

- **Bold text**: `**text**` → `*text*`
- **Strikethrough**: `~~text~~` → `~text~`
- **Links**: `[text](url)` → `<url|text>`
- **User mentions**: `@username` → `<https://github.com/username|@username>`
- **Issue/PR references**: `#123` → `<https://github.com/owner/repo/pull/123|#123>` (when repo_name is set)
- **Lists**: `* item` → `• item`
- **Headlines**: `## Header` → `*Header*` (when headlines option is enabled)
- **Custom patterns**: Define your own pattern replacements (e.g., JIRA tickets)

## Development

### Prerequisites

Install [uv](https://github.com/astral-sh/uv) package manager:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Makefile Commands

```bash
# Show available commands
make help

# Install development dependencies
make install

# Run linting (flake8 and mypy)
make lint

# Format code with black
make format

# Run tests
make test

# Run tests with coverage
make coverage

# Build the package
make build

# Clean build artifacts
make clean
```

### Manual Commands

If you prefer to run commands directly:
```bash
# Install dependencies
uv sync --group dev

# Run tests
uv run pytest

# Format code
uv run black .

# Lint code
uv run flake8 markdown_to_slack_mkdown tests
uv run mypy markdown_to_slack_mkdown
```

## License

MIT
