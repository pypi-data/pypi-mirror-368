# Usage

## Basic Usage

Once installed, the PSScriptAnalyzer pre-commit hooks will automatically run on PowerShell files during git commits.

### Available Hooks

The package provides two main hooks:

1. **`psscriptanalyzer`** - Static analysis and linting
2. **`psscriptanalyzer-format`** - Code formatting

### Automatic Execution

When you commit PowerShell files (`.ps1`, `.psm1`, `.psd1`), the hooks will automatically:

1. **Analysis Hook**: Check for code quality issues, style violations, and potential bugs
2. **Format Hook**: Apply consistent formatting to your PowerShell code

```bash
git add MyScript.ps1
git commit -m "Add new PowerShell script"
# Hooks run automatically
```

### Manual Execution

You can also run the hooks manually:

#### Run All Hooks

```bash
# Run on all PowerShell files
pre-commit run --all-files

# Run on specific files
pre-commit run --files MyScript.ps1 MyModule.psm1
```

#### Run Specific Hooks

```bash
# Run only the analyzer
pre-commit run psscriptanalyzer --all-files

# Run only the formatter
pre-commit run psscriptanalyzer-format --all-files
```

## Hook Behavior

### PSScriptAnalyzer Hook

The analyzer hook will:

- Scan PowerShell files for issues based on PSScriptAnalyzer rules
- Report violations with rule name, severity, file, line number, and description
- Exit with code 1 if issues are found (blocking the commit)
- Exit with code 0 if no issues are found

**Example output:**

```text
RuleName                                 Severity ScriptName           Line Message
--------                                 -------- ----------           ---- -------
PSAvoidUsingWriteHost                    Warning  MyScript.ps1         15   File 'MyScript.ps1' uses Write-Host...
PSUseSingularNouns                       Warning  MyScript.ps1         8    The cmdlet 'Get-Files' uses a plural noun...
```

### PSScriptAnalyzer Format Hook

The formatter hook will:

- Apply consistent formatting to PowerShell code
- Automatically fix style issues when possible
- Modify files in-place with improved formatting
- Report which files were formatted

**Example output:**

```text
Using PowerShell: pwsh
Formatting 2 PowerShell file(s)...
Formatted: MyScript.ps1
Formatted: MyModule.psm1
```

## Integration with Git Workflow

### Pre-commit Integration

The hooks integrate seamlessly with your git workflow:

1. **Stage your changes**: `git add .`
2. **Attempt commit**: `git commit -m "Your message"`
3. **Hooks run automatically**:
   - If analysis finds issues → commit blocked, issues reported
   - If formatting changes files → commit blocked, files modified
   - If all checks pass → commit proceeds

### Handling Hook Failures

#### Analysis Failures

When the analyzer finds issues:

1. Review the reported violations
2. Fix the issues in your code
3. Stage the changes: `git add .`
4. Retry the commit: `git commit -m "Your message"`

#### Formatting Changes

When the formatter modifies files:

1. The modified files are automatically saved
2. Review the formatting changes: `git diff`
3. Stage the formatted files: `git add .`
4. Retry the commit: `git commit -m "Your message"`

## Command Line Options

### PSScriptAnalyzer Arguments

You can customize the analyzer behavior with arguments:

```yaml
hooks:
  - id: psscriptanalyzer
    args: ["--severity", "Error"]  # Only show errors
```

#### Available Severity Levels

- **`Information`** - All rules including informational suggestions
- **`Warning`** - Warnings and errors (default)
- **`Error`** - Only critical errors

### Examples

#### Strict Configuration (Errors Only)

```yaml
repos:
  - repo: https://github.com/thetestlabs/psscriptanalyzer-pre-commit
    rev: v1.0.0
    hooks:
      - id: psscriptanalyzer
        args: ["--severity", "Error"]
      - id: psscriptanalyzer-format
```

#### Comprehensive Configuration (All Issues)

```yaml
repos:
  - repo: https://github.com/thetestlabs/psscriptanalyzer-pre-commit
    rev: v1.0.0
    hooks:
      - id: psscriptanalyzer
        args: ["--severity", "Information"]
      - id: psscriptanalyzer-format
```

## File Selection

The hooks automatically target PowerShell files with these extensions:

- `.ps1` - PowerShell scripts
- `.psm1` - PowerShell modules
- `.psd1` - PowerShell data files/manifests

Other files are ignored by the hooks.

## Bypassing Hooks

### Skip All Hooks

```bash
git commit --no-verify -m "Skip all pre-commit hooks"
```

### Skip Specific Hooks

```bash
# Skip only PSScriptAnalyzer hooks
SKIP=psscriptanalyzer,psscriptanalyzer-format git commit -m "Skip PowerShell hooks"
```

## CI/CD Integration

The hooks work well in CI/CD environments:

```yaml
# GitHub Actions example
- name: Run pre-commit
  run: |
    pip install pre-commit
    pre-commit run --all-files
```
