# PSScriptAnalyzer Pre-commit Hook

A pre-commit hook for running [PSScriptAnalyzer](https://github.com/PowerShell/PSScriptAnalyzer) on PowerShell files to ensure code quality and consistency.

## Features

- **Cross-platform support**: Works on Windows, macOS, and Linux
- **Automatic installation**: Installs PSScriptAnalyzer if not present
- **Two modes**: Linting and formatting
- **Configurable severity**: Choose severity levels for issues (All, Information, Warning, Error)
- **PowerShell detection**: Automatically finds PowerShell Core (pwsh) or Windows PowerShell
- **Color-coded output**: Different colors for Error (red), Warning (orange), Information (cyan)
- **GitHub Actions integration**: Automatic annotations for GitHub Actions workflows
- **Improved output format**: Severity-first display for easy scanning

## Supported File Types

- `.ps1` - PowerShell scripts
- `.psm1` - PowerShell modules
- `.psd1` - PowerShell data files

## Prerequisites

- Python 3.9 or later
- PowerShell Core (pwsh) or Windows PowerShell
- pre-commit

### Installing PowerShell

If you don't have PowerShell installed:

- **Windows**: PowerShell is usually pre-installed. For PowerShell Core, visit [PowerShell releases](https://github.com/PowerShell/PowerShell/releases)
- **macOS**: `brew install powershell`
- **Linux**: Follow the [PowerShell installation guide](https://docs.microsoft.com/en-us/powershell/scripting/install/installing-powershell-on-linux)

## Usage

Add this to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/thetestlabs/psscriptanalyzer-pre-commit
    rev: v1.0.0 # Use the ref you want to point at
    hooks:
      - id: psscriptanalyzer
      - id: psscriptanalyzer-format
```

### Available Hooks

#### `psscriptanalyzer`

Runs PSScriptAnalyzer to check for issues in your PowerShell files.

**Configuration options:**

```yaml
- id: psscriptanalyzer
  args: ["--severity", "Warning"] # Default: Warning
  # Available options: All, Information, Warning, Error
```

**Severity levels:**

- `All`: Shows Error, Warning, and Information issues (most comprehensive)
- `Information`: Shows only Information level issues
- `Warning`: Shows only Warning level issues (default)
- `Error`: Shows only Error level issues (most critical)

#### `psscriptanalyzer-format`

Formats your PowerShell files using PSScriptAnalyzer's formatter.

```yaml
- id: psscriptanalyzer-format
```

### Command Line Options

- `--format`: Format files instead of just analyzing them
- `--severity`: Set severity level:
  - `All`: Show all issues (Error, Warning, Information)
  - `Information`: Show only Information level issues
  - `Warning`: Show only Warning level issues (default)
  - `Error`: Show only Error level issues

### Output Format

The hook displays issues with color-coded severity levels:

**Local Terminal:**

- **Error**: Red text - `Error: filename: Line X:1: RuleName`
- **Warning**: Orange text - `Warning: filename: Line X:1: RuleName`
- **Information**: Cyan text - `Information: filename: Line X:1: RuleName`

**GitHub Actions:**

- **Error**: `::error` annotation - `Error: filename: Line X:1: RuleName`
- **Warning**: `::warning` annotation - `Warning: filename: Line X:1: RuleName`
- **Information**: `::notice` annotation - `Notice: filename: Line X:1: RuleName`

The severity-first format makes it easy to quickly scan and prioritize issues.

## Example Configuration

```yaml
repos:
  - repo: https://github.com/thetestlabs/psscriptanalyzer-pre-commit
    rev: v1.0.0
    hooks:
      # Check for issues (show all severity levels)
      - id: psscriptanalyzer
        args: ["--severity", "All"]

      # Format files
      - id: psscriptanalyzer-format

      # Example: Only show critical errors
      - id: psscriptanalyzer
        name: psscriptanalyzer-errors-only
        args: ["--severity", "Error"]
```

## How It Works

1. The hook detects PowerShell files in your commit
2. Finds PowerShell executable (pwsh or powershell)
3. Checks if PSScriptAnalyzer is installed, installs it if needed
4. Runs the appropriate PSScriptAnalyzer command
5. Reports issues or applies formatting

## Development

### Development Prerequisites

- Python 3.9+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- PowerShell Core (pwsh) or Windows PowerShell

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/thetestlabs/psscriptanalyzer-pre-commit.git
cd psscriptanalyzer-pre-commit

# Install uv (if not already installed)
# On macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh
# On Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install dependencies using uv
uv sync --dev

# Install pre-commit hooks
uv run pre-commit install
```

To test the hook locally:

```bash
# Run on files directly
uv run psscriptanalyzer-hook --help
uv run psscriptanalyzer-hook script.ps1
uv run psscriptanalyzer-hook --format script.ps1
uv run psscriptanalyzer-hook --severity Error script.ps1

# Alternative: using Python module execution
uv run python -m psscriptanalyzer_hook script.ps1

# Run code quality checks
uv run ruff check .
uv run ruff format .
uv run mypy psscriptanalyzer_hook.py

# Run tests
uv run pytest

# Run all pre-commit hooks
uv run pre-commit run --all-files
```

To build the package:

```bash
# Build wheel and source distribution
uv build

# Check package integrity
uv run twine check dist/*
```

### Alternative: Traditional Python Setup

If you prefer not to use uv:

```bash
# Install dependencies
pip install -e ".[dev]"

# Run commands without uv prefix
python -m psscriptanalyzer_hook --help
pre-commit run --all-files
pytest
ruff check .
mypy psscriptanalyzer_hook.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [PSScriptAnalyzer](https://github.com/PowerShell/PSScriptAnalyzer) - The PowerShell static code checker
- [pre-commit](https://pre-commit.com/) - A framework for managing multi-language pre-commit hooks
