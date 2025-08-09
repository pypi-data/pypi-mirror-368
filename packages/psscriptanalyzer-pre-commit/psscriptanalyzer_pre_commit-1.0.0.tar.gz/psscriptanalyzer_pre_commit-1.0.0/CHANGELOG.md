# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.12] - 2025-08-07

### Added

- Color-coded output for different severity levels in local terminal
- GitHub Actions integration with proper annotations (::error, ::warning, ::notice)
- "All" severity option to display all issue types (Error, Warning, Information)
- Improved output format with severity-first display for easy scanning
- Environment-aware output formatting (different terminology for GitHub Actions vs local)

### Changed

- Enhanced output format: `Severity: filename: Line X:1: RuleName` (severity displayed first)
- Updated severity parameter to accept "All" option for comprehensive analysis
- GitHub Actions displays "Notice" instead of "Information" to match platform conventions
- Improved color scheme: Error (red), Warning (orange/dark yellow), Information (cyan)

### Fixed

- Resolved issues with severity level filtering - "All" now properly shows all issue types
- Fixed PowerShell command generation to conditionally include severity parameter
- Corrected argument parser to handle new "All" severity option

## [1.0.6] - 2024-01-XX

### Added

- Comprehensive Sphinx documentation with ReadTheDocs integration
- Complete PyPI package metadata with proper classifiers and keywords
- Cross-platform installation instructions for all supported systems
- Detailed API reference documentation with function signatures and examples
- Configuration guide with advanced pre-commit hook scenarios and customization
- Examples directory with intentionally flawed PowerShell files covering all PSScriptAnalyzer rules

### Changed

- Enhanced pyproject.toml with professional PyPI metadata including 15+ classifiers
- Improved documentation structure with MyST markdown parser for Sphinx
- Updated installation guide with platform-specific PowerShell setup instructions
- Refined package discovery configuration for consistent PyPI distribution

### Documentation

- Added comprehensive installation guide (docs/installation.md) with troubleshooting
- Created detailed usage documentation (docs/usage.md) with CLI and CI/CD examples
- Built complete configuration reference (docs/configuration.md) with advanced scenarios
- Developed API documentation (docs/api.md) with function signatures and examples
- Established examples documentation (examples/README.md) with comprehensive test coverage
- Configured Sphinx with ReadTheDocs theme (docs/conf.py) for professional documentation

### Package Management

- Prepared package for PyPI publication with comprehensive metadata
- Added documentation URLs for PyPI package page
- Enhanced project description and keywords for better discoverability
- Configured Sphinx dependencies for ReadTheDocs hosting

## [Unreleased]

### Development Changes

- Modernized package configuration by migrating from `setup.py` and `requirements.txt` to `pyproject.toml`
- Replaced `black` and `isort` with `ruff` for faster, unified linting and formatting
- Updated GitHub Actions workflows to use latest actions and Python 3.12 support
- Improved development workflow with better tooling configuration
- Updated license format to use SPDX identifier
- Enhanced `.gitignore` for modern Python packaging artifacts
- **Made code more Pythonic** with significant improvements:
  - Added type hints and constants for better maintainability
  - Improved error handling with proper stderr output
  - Enhanced PowerShell command generation with path escaping
  - Added explicit `check=False` parameters for subprocess calls
  - Used constants for timeouts, file extensions, and severity levels
  - Better separation of concerns with helper functions

### Development Features

- Development dependencies configuration in `pyproject.toml`
- Modern build system using `python -m build`
- Additional GitHub Actions workflow for code quality checks
- **Comprehensive test suite** with pytest covering core functionality
- Enhanced Ruff configuration with additional linting rules
- Constants for improved code maintainability

## [1.0.0] - 2025-08-04

### Initial Release

- Initial release of PSScriptAnalyzer pre-commit hook
- Cross-platform support (Windows, macOS, Linux)
- Automatic PSScriptAnalyzer installation
- Two hook modes: linting and formatting
- Configurable severity levels
- Support for .ps1, .psm1, and .psd1 files
- GitHub Actions workflow for testing
- Comprehensive documentation
