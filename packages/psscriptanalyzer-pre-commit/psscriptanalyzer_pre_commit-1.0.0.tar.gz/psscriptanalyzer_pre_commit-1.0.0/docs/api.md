# API Reference

## PSScriptAnalyzer Hook Module

The `psscriptanalyzer_hook` module provides the core functionality for integrating PSScriptAnalyzer with pre-commit hooks.

### Module Functions

#### `main(argv=None)`

Main entry point for the PSScriptAnalyzer pre-commit hook.

**Parameters:**

- `argv` (list, optional): Command line arguments. If None, uses `sys.argv[1:]`

**Returns:****Compatibility:**

- Python 3.9+
- PowerShell Core 7.0+
- Windows PowerShell 5.1+
- Pre-commit 2.0+

**Returns:**
- `int`: Exit code (0 for success, non-zero for failure)

**Example:**

```python
from psscriptanalyzer_hook import main

# Run with default arguments
exit_code = main()

# Run with custom arguments
exit_code = main(['--severity', 'Error', 'script.ps1'])
```

#### `find_powershell_executable()`

Locates the PowerShell executable on the system.

**Returns:**

- `str`: Path to PowerShell executable

**Raises:**

- `RuntimeError`: If no PowerShell executable is found

**Search Order:**

1. `pwsh` (PowerShell Core)
2. `pwsh-lts` (PowerShell LTS - macOS Homebrew)
3. `powershell` (Windows PowerShell)

**Example:**

```python
from psscriptanalyzer_hook import find_powershell_executable

try:
    pwsh_path = find_powershell_executable()
    print(f"Found PowerShell at: {pwsh_path}")
except RuntimeError as e:
    print(f"PowerShell not found: {e}")
```

#### `run_psscriptanalyzer(files, severity='Warning', format_output=False)`

Executes PSScriptAnalyzer on the specified files.

**Parameters:**

- `files` (list): List of PowerShell file paths to analyze
- `severity` (str, optional): Minimum severity level ('Error', 'Warning', 'Information'). Default: 'Warning'
- `format_output` (bool, optional): Whether to format output for consistency. Default: False

**Returns:**

- `tuple`: (exit_code, stdout, stderr)
  - `exit_code` (int): Process exit code
  - `stdout` (str): Standard output from PSScriptAnalyzer
  - `stderr` (str): Standard error from PSScriptAnalyzer

**Example:**

```python
from psscriptanalyzer_hook import run_psscriptanalyzer

files = ['script1.ps1', 'module.psm1']
exit_code, stdout, stderr = run_psscriptanalyzer(
    files,
    severity='Error',
    format_output=True
)

if exit_code == 0:
    print("Analysis passed!")
else:
    print(f"Issues found:\n{stdout}")
```

#### `format_psscriptanalyzer_output(output)`

Formats PSScriptAnalyzer output for cross-platform consistency.

**Parameters:**

- `output` (str): Raw PSScriptAnalyzer output

**Returns:**

- `str`: Formatted output with consistent column widths

**Example:**

```python
from psscriptanalyzer_hook import format_psscriptanalyzer_output

raw_output = """
RuleName                            Severity     ScriptName                   Line  Message
--------                            --------     ----------                   ----  -------
PSAvoidUsingCmdletAliases          Warning      test.ps1                        5  'ls' is an alias...
"""

formatted = format_psscriptanalyzer_output(raw_output)
print(formatted)
```

## Command Line Interface

### PSScriptAnalyzer Hook

```bash
psscriptanalyzer-hook [OPTIONS] [FILES...]
```

**Options:**

- `--severity LEVEL`: Set minimum severity level (Error, Warning, Information)
- `-h, --help`: Show help message

**Examples:**

```bash
# Analyze with default warning level
psscriptanalyzer-hook script.ps1 module.psm1

# Only show errors
psscriptanalyzer-hook --severity Error *.ps1

# Analyze all PowerShell files
psscriptanalyzer-hook --severity Information **/*.ps*
```

### PSScriptAnalyzer Format Hook

```bash
psscriptanalyzer-format-hook [FILES...]
```

**Examples:**

```bash
# Format PowerShell files
psscriptanalyzer-format-hook script.ps1

# Format all PowerShell files
psscriptanalyzer-format-hook **/*.ps*
```

## Pre-commit Hook Configuration

### Hook Definitions

The package provides two pre-commit hooks:

#### `psscriptanalyzer`

Static analysis hook for PowerShell files.

**Configuration:**

```yaml
- id: psscriptanalyzer
  name: PSScriptAnalyzer
  description: Run PSScriptAnalyzer on PowerShell files
  entry: psscriptanalyzer-hook
  language: python
  files: \.(ps1|psm1|psd1)$
  args: ["--severity", "Warning"]
```

#### `psscriptanalyzer-format`

Code formatting hook for PowerShell files.

**Configuration:**

```yaml
- id: psscriptanalyzer-format
  name: PSScriptAnalyzer Format
  description: Format PowerShell files using PSScriptAnalyzer
  entry: psscriptanalyzer-format-hook
  language: python
  files: \.(ps1|psm1|psd1)$
```

## Error Handling

### Common Exceptions

#### `RuntimeError`

Raised when PowerShell executable cannot be found.

```python
try:
    from psscriptanalyzer_hook import find_powershell_executable
    pwsh = find_powershell_executable()
except RuntimeError as e:
    print(f"PowerShell installation required: {e}")
```

#### `subprocess.CalledProcessError`

Raised when PowerShell command execution fails.

```python
import subprocess
from psscriptanalyzer_hook import run_psscriptanalyzer

try:
    exit_code, stdout, stderr = run_psscriptanalyzer(['bad-file.ps1'])
except subprocess.CalledProcessError as e:
    print(f"Command failed: {e}")
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - no issues found |
| 1 | Analysis found issues |
| 2 | PowerShell not found |
| 3 | Invalid arguments |
| 4 | File not found |
| 5 | PowerShell execution error |

## Environment Variables

### `PSSCRIPTANALYZER_PWSH_PATH`

Override the PowerShell executable path.

```bash
export PSSCRIPTANALYZER_PWSH_PATH="/opt/microsoft/powershell/7/pwsh"
```

### `PSSCRIPTANALYZER_DEBUG`

Enable debug output.

```bash
export PSSCRIPTANALYZER_DEBUG=1
```

## PowerShell Integration

### PSScriptAnalyzer Commands

The hooks execute these PowerShell commands:

#### Analysis Command

```powershell
Invoke-ScriptAnalyzer -Path @($files) -Severity $severity |
Format-Table -Property RuleName, Severity, ScriptName, Line, Message -AutoSize |
Out-String -Width 4096
```

#### Formatting Command

```powershell
Invoke-Formatter -ScriptDefinition (Get-Content -Path $file -Raw) |
Set-Content -Path $file -NoNewline
```

### Custom PSScriptAnalyzer Settings

The hooks respect PSScriptAnalyzer configuration files:

```powershell
# PSScriptAnalyzerSettings.psd1
@{
    Severity = @('Error', 'Warning')
    Rules = @{
        PSPlaceOpenBrace = @{
            Enable = $true
            OnSameLine = $true
        }
    }
}
```

## Extension Points

### Custom Severity Mapping

```python
# Custom severity levels
SEVERITY_MAPPING = {
    'error': 'Error',
    'warn': 'Warning',
    'info': 'Information'
}
```

### Custom Output Formatting

```python
def custom_formatter(output):
    """Custom output formatter"""
    lines = output.strip().split('\n')
    # Custom formatting logic here
    return '\n'.join(formatted_lines)
```

### Custom PowerShell Detection

```python
def find_custom_powershell():
    """Custom PowerShell detection logic"""
    custom_paths = [
        '/custom/path/to/pwsh',
        '/another/path/powershell'
    ]

    for path in custom_paths:
        if shutil.which(path):
            return path

    # Fallback to default detection
    return find_powershell_executable()
```

## Testing

### Unit Tests

```python
import pytest
from psscriptanalyzer_hook import main, find_powershell_executable

def test_find_powershell():
    """Test PowerShell detection"""
    pwsh = find_powershell_executable()
    assert pwsh is not None
    assert os.path.isfile(pwsh)

def test_main_with_valid_file():
    """Test main function with valid PowerShell file"""
    exit_code = main(['valid-script.ps1'])
    assert exit_code in [0, 1]  # 0 for clean, 1 for issues found
```

### Integration Tests

```python
def test_full_integration():
    """Test complete hook integration"""
    # Create test PowerShell file
    test_file = 'test.ps1'
    with open(test_file, 'w') as f:
        f.write('Get-ChildItem | where Name -like "*.txt"')  # Alias usage

    try:
        exit_code = main(['--severity', 'Warning', test_file])
        assert exit_code == 1  # Should find alias issue
    finally:
        os.unlink(test_file)
```

## Version History

### Current Version: 1.0.6

**Features:**

- Cross-platform PowerShell support (Windows, macOS, Linux)
- Consistent output formatting across platforms
- Configurable severity levels
- Pre-commit hook integration
- Comprehensive error handling

**Compatibility:**

- Python 3.9+
- PowerShell Core 7.0+
- Windows PowerShell 5.1+
- Pre-commit 2.0+

For detailed changelog, see [CHANGELOG.md](../CHANGELOG.md).
