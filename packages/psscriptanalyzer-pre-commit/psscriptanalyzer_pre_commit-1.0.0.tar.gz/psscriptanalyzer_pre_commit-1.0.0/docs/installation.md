# Installation

## Prerequisites

Before installing the PSScriptAnalyzer pre-commit hook, ensure you have the following prerequisites:

### PowerShell

The hook requires PowerShell Core (pwsh) to be installed and available in your system PATH.

#### Windows

##### Option 1: Microsoft Store (Recommended)

```bash
# Install from Microsoft Store
winget install Microsoft.PowerShell
```

##### Option 2: Direct Download (Windows)

Download from the [PowerShell GitHub releases page](https://github.com/PowerShell/PowerShell/releases).

#### macOS

##### Option 1: Homebrew (Recommended)

```bash
brew install --cask powershell
```

##### Option 2: Direct Download (macOS)

Download from the [PowerShell GitHub releases page](https://github.com/PowerShell/PowerShell/releases).

#### Linux

##### Ubuntu/Debian

```bash
# Update package index
sudo apt update

# Install dependencies
sudo apt install -y wget apt-transport-https software-properties-common

# Download Microsoft signing key and repository
wget -q "https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/packages-microsoft-prod.deb"
sudo dpkg -i packages-microsoft-prod.deb

# Update package index after adding Microsoft repository
sudo apt update

# Install PowerShell
sudo apt install -y powershell
```

##### CentOS/RHEL/Fedora

```bash
# Register Microsoft signature key
sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc

# Register Microsoft repository
curl https://packages.microsoft.com/config/rhel/8/prod.repo | sudo tee /etc/yum.repos.d/microsoft.repo

# Install PowerShell
sudo dnf install -y powershell
```

### Verify PowerShell Installation

After installation, verify PowerShell is working:

```bash
pwsh --version
```

You should see output similar to:

```text
PowerShell 7.4.0
```

### PSScriptAnalyzer Module

The PSScriptAnalyzer PowerShell module will be automatically installed when the hook first runs. However, you can install it manually if needed:

```powershell
pwsh -Command "Install-Module -Name PSScriptAnalyzer -Force -Scope CurrentUser"
```

## Installing the Pre-commit Hook

### Method 1: Add to Existing .pre-commit-config.yaml

If you already have a `.pre-commit-config.yaml` file in your repository, add the PSScriptAnalyzer hooks:

```yaml
repos:
  # ... your existing hooks ...

  - repo: https://github.com/thetestlabs/psscriptanalyzer-pre-commit
    rev: v1.0.0  # Use the latest version
    hooks:
      # Lint PowerShell files
      - id: psscriptanalyzer
        args: ["--severity", "Warning"]

      # Format PowerShell files
      - id: psscriptanalyzer-format
```

### Method 2: Create New .pre-commit-config.yaml

If you don't have a pre-commit configuration file, create one:

```yaml
repos:
  - repo: https://github.com/thetestlabs/psscriptanalyzer-pre-commit
    rev: v1.0.0  # Use the latest version
    hooks:
      # Lint PowerShell files (show warnings and errors)
      - id: psscriptanalyzer
        args: ["--severity", "Warning"]

      # Format PowerShell files
      - id: psscriptanalyzer-format
```

### Install Pre-commit

If you haven't already, install pre-commit:

```bash
pip install pre-commit
```

### Install the Hooks

Install the pre-commit hooks in your repository:

```bash
pre-commit install
```

## Verification

Test that everything is working:

```bash
# Run on all PowerShell files
pre-commit run --all-files

# Run only PSScriptAnalyzer hooks
pre-commit run psscriptanalyzer --all-files
pre-commit run psscriptanalyzer-format --all-files
```

## Troubleshooting

### PowerShell Not Found

If you see an error about PowerShell not being found:

1. Verify PowerShell is installed: `pwsh --version`
2. Ensure PowerShell is in your PATH
3. On macOS, try installing via Homebrew: `brew install --cask powershell`

### Assembly Loading Errors (macOS)

If you encounter assembly loading errors on macOS:

```bash
# Clear PowerShell module cache
rm -rf ~/.local/share/powershell/Modules/PSScriptAnalyzer

# Reinstall PSScriptAnalyzer
pwsh -Command 'Uninstall-Module PSScriptAnalyzer -Force; Install-Module PSScriptAnalyzer -Force'
```

### Permission Issues

If you encounter permission issues during PSScriptAnalyzer installation:

```powershell
# Install with elevated permissions
pwsh -Command "Install-Module -Name PSScriptAnalyzer -Force -Scope CurrentUser"
```

For more troubleshooting tips, see the [GitHub Issues](https://github.com/thetestlabs/psscriptanalyzer-pre-commit/issues) page.
