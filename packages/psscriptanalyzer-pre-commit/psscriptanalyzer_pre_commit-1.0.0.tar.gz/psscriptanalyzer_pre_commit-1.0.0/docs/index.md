# PSScriptAnalyzer Pre-commit Hook

A pre-commit hook for PSScriptAnalyzer that provides PowerShell static analysis and formatting capabilities.

```{toctree}
:maxdepth: 2
:caption: Contents

installation
usage
configuration
api
changelog
```

## Quick Start

1. **Install the hook in your repository:**

   ```yaml
   # .pre-commit-config.yaml
   repos:
     - repo: https://github.com/thetestlabs/psscriptanalyzer-pre-commit
       rev: v1.0.0
       hooks:
         - id: psscriptanalyzer
         - id: psscriptanalyzer-format
   ```

2. **Install pre-commit:**

   ```bash
   pip install pre-commit
   pre-commit install
   ```

3. **Run on all files:**

   ```bash
   pre-commit run --all-files
   ```

## Features

- **Static Analysis**: Comprehensive PowerShell code analysis using PSScriptAnalyzer
- **Code Formatting**: Automatic PowerShell code formatting with Invoke-Formatter
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Configurable**: Customizable severity levels and rule selection
- **Fast**: Efficient processing with proper error handling
- **CI/CD Ready**: Tested across multiple Python versions and operating systems

## Requirements

- Python 3.9 or higher
- PowerShell Core (pwsh) installed and available in PATH
- PSScriptAnalyzer PowerShell module (auto-installed if missing)

## Supported Platforms

- **Windows**: PowerShell Core, Windows PowerShell
- **macOS**: PowerShell Core via Homebrew (`brew install --cask powershell`)
- **Linux**: PowerShell Core via package manager
