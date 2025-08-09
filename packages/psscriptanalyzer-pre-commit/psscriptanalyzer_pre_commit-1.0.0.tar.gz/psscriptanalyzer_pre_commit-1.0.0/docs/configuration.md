# Configuration

## Basic Configuration

The PSScriptAnalyzer pre-commit hooks can be configured through your `.pre-commit-config.yaml` file.

### Minimal Configuration

```yaml
repos:
  - repo: https://github.com/thetestlabs/psscriptanalyzer-pre-commit
    rev: v1.0.0
    hooks:
      - id: psscriptanalyzer
      - id: psscriptanalyzer-format
```

### Complete Configuration

```yaml
repos:
  - repo: https://github.com/thetestlabs/psscriptanalyzer-pre-commit
    rev: v1.0.0  # Use the latest version
    hooks:
      # Static analysis with custom severity
      - id: psscriptanalyzer
        name: PowerShell Analysis
        description: Run PSScriptAnalyzer on PowerShell files
        args: ["--severity", "All"]
        files: \.(ps1|psm1|psd1)$

      # Code formatting
      - id: psscriptanalyzer-format
        name: PowerShell Formatting
        description: Format PowerShell files with PSScriptAnalyzer
        files: \.(ps1|psm1|psd1)$
```

## Hook Parameters

### PSScriptAnalyzer Hook Options

#### Severity Levels

Control which issues are reported:

```yaml
hooks:
  - id: psscriptanalyzer
    args: ["--severity", "All"]          # All issues (comprehensive)

  - id: psscriptanalyzer
    args: ["--severity", "Error"]        # Only critical errors

  - id: psscriptanalyzer
    args: ["--severity", "Warning"]      # Only warnings (default)

  - id: psscriptanalyzer
    args: ["--severity", "Information"]  # Only informational issues
```

**Severity Level Details:**

- **All**: Shows Error, Warning, and Information issues (most comprehensive analysis)
- **Error**: Critical issues that will likely cause runtime errors
- **Warning**: Code that may cause issues but isn't necessarily wrong (default)
- **Information**: Style suggestions and best practices

## Output Format

### Local Terminal Output

Issues are displayed with color-coded severity levels:

- **Error**: Red text - `Error: filename: Line X:1: RuleName`
- **Warning**: Orange text - `Warning: filename: Line X:1: RuleName`
- **Information**: Cyan text - `Information: filename: Line X:1: RuleName`

### GitHub Actions Integration

When running in GitHub Actions, the hook automatically:

- Creates GitHub Actions annotations for each issue
- Maps severity levels: Error → `::error`, Warning → `::warning`, Information → `::notice`
- Displays "Notice" instead of "Information" to match GitHub terminology

  - id: psscriptanalyzer
    args: ["--severity", "Warning"]   # Warnings and errors (default)

  - id: psscriptanalyzer
    args: ["--severity", "Information"]  # All issues

```

### File Filtering

#### Default File Pattern

Both hooks automatically target:

- `.ps1` files (PowerShell scripts)
- `.psm1` files (PowerShell modules)
- `.psd1` files (PowerShell data/manifests)

#### Custom File Patterns

Override the default file selection:

```yaml
hooks:
  - id: psscriptanalyzer
    files: \.(ps1)$  # Only .ps1 files

  - id: psscriptanalyzer
    files: \.(ps1|psm1)$  # Only scripts and modules

  - id: psscriptanalyzer
    files: ^scripts/.*\.ps1$  # Only .ps1 files in scripts/ directory
```

#### Exclude Patterns

Exclude specific files or directories:

```yaml
hooks:
  - id: psscriptanalyzer
    exclude: ^(tests/|vendor/|\.vscode/).*$

  - id: psscriptanalyzer
    exclude: |
      (?x)^(
        tests/.*|
        vendor/.*|
        legacy/.*\.ps1
      )$
```

## Advanced Configuration

### Hook Stages

Control when hooks run:

```yaml
hooks:
  - id: psscriptanalyzer
    stages: [commit, push]  # Run on commit and push

  - id: psscriptanalyzer-format
    stages: [commit]  # Only run on commit
```

### Language Override

Force language detection:

```yaml
hooks:
  - id: psscriptanalyzer
    language: python
    entry: psscriptanalyzer-hook
    args: ["--severity", "Warning"]
```

### Custom Entry Points

Override the default entry point:

```yaml
hooks:
  - id: psscriptanalyzer
    entry: python -m psscriptanalyzer_hook
    args: ["--severity", "Error"]
```

## Repository-Specific Configuration

### Multiple Configurations

Different rules for different directories:

```yaml
repos:
  - repo: https://github.com/thetestlabs/psscriptanalyzer-pre-commit
    rev: v1.0.0
    hooks:
      # Strict checking for production code
      - id: psscriptanalyzer
        name: Production Code Analysis
        files: ^src/.*\.(ps1|psm1)$
        args: ["--severity", "Error"]

      # Relaxed checking for tests
      - id: psscriptanalyzer
        name: Test Code Analysis
        files: ^tests/.*\.ps1$
        args: ["--severity", "Warning"]

      # Format all PowerShell files
      - id: psscriptanalyzer-format
```

### Conditional Hooks

Enable hooks based on file changes:

```yaml
hooks:
  - id: psscriptanalyzer
    files: \.(ps1|psm1|psd1)$
    types_or: [powershell]  # Only run if PowerShell files changed
```

## PSScriptAnalyzer Configuration

### PowerShell Profile Configuration

The hooks respect PSScriptAnalyzer settings in your PowerShell profile or configuration files.

#### Global Settings

Create a PSScriptAnalyzer settings file:

```powershell
# PSScriptAnalyzerSettings.psd1
@{
    Severity = @('Error', 'Warning')
    IncludeRules = @(
        'PSAvoidUsingCmdletAliases',
        'PSAvoidUsingWMICmdlet',
        'PSUseSingularNouns'
    )
    ExcludeRules = @(
        'PSAvoidUsingWriteHost'  # Allow Write-Host for scripts
    )
}
```

#### Rule Customization

Customize which rules are applied:

```powershell
# In PowerShell profile or settings file
$PSScriptAnalyzerSettings = @{
    Rules = @{
        PSAvoidUsingCmdletAliases = @{
            Whitelist = @('where', 'foreach', 'select')
        }
        PSPlaceOpenBrace = @{
            Enable = $true
            OnSameLine = $true
        }
        PSProvideCommentHelp = @{
            Enable = $true
            ExportedOnly = $false
            BlockComment = $true
            VSCodeSnippetCorrection = $false
            Placement = "before"
        }
    }
}
```

## Environment Variables

### PowerShell Detection

The hook automatically detects PowerShell in this order:

1. `pwsh` (PowerShell Core)
2. `pwsh-lts` (PowerShell LTS on macOS Homebrew)
3. `powershell` (Windows PowerShell)

### Override PowerShell Path

```bash
# Force specific PowerShell executable
export PSSCRIPTANALYZER_PWSH_PATH="/usr/local/bin/pwsh"
```

### Debug Mode

Enable verbose output:

```bash
# Enable debug output
export PSSCRIPTANALYZER_DEBUG=1
```

## Integration Examples

### With Other Hooks

Combine with other pre-commit hooks:

```yaml
repos:
  # PowerShell hooks
  - repo: https://github.com/thetestlabs/psscriptanalyzer-pre-commit
    rev: v1.0.0
    hooks:
      - id: psscriptanalyzer
      - id: psscriptanalyzer-format

  # General hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json

  # Python hooks (if you have Python code too)
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
```

### Monorepo Configuration

For repositories with multiple languages:

```yaml
repos:
  # PowerShell in src/powershell/
  - repo: https://github.com/thetestlabs/psscriptanalyzer-pre-commit
    rev: v1.0.0
    hooks:
      - id: psscriptanalyzer
        files: ^src/powershell/.*\.(ps1|psm1)$
        args: ["--severity", "Warning"]
      - id: psscriptanalyzer-format
        files: ^src/powershell/.*\.(ps1|psm1)$

  # Other language hooks...
```

## Troubleshooting Configuration

### Hook Not Running

If hooks aren't running on your files:

1. Check file extensions match the pattern
2. Verify files aren't excluded by patterns
3. Ensure PowerShell is installed and accessible

### Performance Optimization

For large repositories:

```yaml
hooks:
  - id: psscriptanalyzer
    # Only run on changed files (default)
    pass_filenames: true

  - id: psscriptanalyzer
    # Skip files larger than 1MB
    exclude: '^.*\.(ps1|psm1)$'
    files: '^(?!.*/(large-file\.ps1)).*\.(ps1|psm1)$'
```

### Custom Timeout

For long-running analysis:

```yaml
hooks:
  - id: psscriptanalyzer
    # Extend timeout for large files
    timeout: 300  # 5 minutes
```
