# Examples

## Test Files Overview

The `examples/` directory contains PowerShell files with intentional errors that demonstrate various PSScriptAnalyzer rules and violations. These examples serve multiple purposes:

- **Learning Tool**: Understand what PSScriptAnalyzer detects
- **Testing**: Verify the pre-commit hooks work correctly
- **Reference**: See examples of common PowerShell issues

## File Structure

```text
examples/
├── README.md                    # This file
├── basic-script-errors.ps1      # Common scripting mistakes
├── advanced-errors.ps1          # Complex rule violations
├── module-errors.psm1          # Module-specific issues
├── manifest-errors.psd1        # Manifest validation errors
├── formatting-issues.ps1       # Code style violations
├── security-issues.ps1         # Security-related problems
└── performance-issues.ps1      # Performance anti-patterns
```

## Error Categories Covered

### 1. Basic Script Errors (`basic-script-errors.ps1`)

Common mistakes in PowerShell scripts:

- **PSAvoidUsingCmdletAliases**: Using aliases instead of full cmdlet names
- **PSUseSingularNouns**: Plural nouns in function names
- **PSAvoidDefaultValueSwitchParameter**: Default values on switch parameters
- **PSUseApprovedVerbs**: Non-approved verbs in function names
- **PSUseDeclaredVarsMoreThanAssignments**: Variables that are assigned but never used

### 2. Advanced Errors (`advanced-errors.ps1`)

More complex rule violations:

- **PSAvoidUsingPositionalParameters**: Relying on parameter positions
- **PSAvoidGlobalVars**: Using global variables inappropriately
- **PSUseShouldProcessForStateChangingFunctions**: Missing ShouldProcess support
- **PSAvoidUsingWMICmdlet**: Using deprecated WMI cmdlets
- **PSUsePSCredentialType**: Incorrect credential parameter types

### 3. Module Errors (`module-errors.psm1`)

Module-specific issues:

- **PSMissingModuleManifestField**: Missing required manifest fields
- **PSUseToExportFieldsInManifest**: Incorrect export definitions
- **PSAvoidUsingWriteHost**: Using Write-Host in modules
- **PSProvideCommentHelp**: Missing comment-based help

### 4. Manifest Errors (`manifest-errors.psd1`)

PowerShell manifest validation:

- **PSMissingModuleManifestField**: Required fields missing
- **PSInvalidModuleManifestField**: Invalid field values
- **PSAvoidTrailingWhitespace**: Whitespace issues
- **PSUseBOMForUnicodeEncodedFile**: Encoding problems

### 5. Formatting Issues (`formatting-issues.ps1`)

Code style and formatting:

- **PSPlaceOpenBrace**: Brace placement inconsistencies
- **PSPlaceCloseBrace**: Closing brace issues
- **PSUseConsistentIndentation**: Inconsistent indentation
- **PSUseConsistentWhitespace**: Whitespace inconsistencies
- **PSAlignAssignmentStatement**: Assignment alignment

### 6. Security Issues (`security-issues.ps1`)

Security-related concerns:

- **PSAvoidUsingPlainTextForPassword**: Plain text passwords
- **PSAvoidUsingConvertToSecureStringWithPlainText**: Insecure string conversion
- **PSUsePSCredentialType**: Credential handling
- **PSAvoidUsingUsernameAndPasswordParams**: Separate username/password parameters
- **PSAvoidHardcodedCredentials**: Hardcoded credentials

### 7. Performance Issues (`performance-issues.ps1`)

Performance anti-patterns:

- **PSUseSingularNouns**: Inefficient patterns
- **PSAvoidUsingWMICmdlet**: Deprecated slow cmdlets
- **PSUseProcessBlockForPipelineCommand**: Missing process blocks
- **PSReviewUnusedParameter**: Unused parameters
- **PSAvoidLongLines**: Overly long lines

## Running Examples

### Test All Examples

Run PSScriptAnalyzer on all example files:

```bash
# Using pre-commit (will fail as expected)
pre-commit run psscriptanalyzer --files examples/*.ps*

# Direct PowerShell analysis
pwsh -Command "Invoke-ScriptAnalyzer -Path ./examples/ -Recurse"
```

### Test Specific Categories

Run analysis on specific file types:

```bash
# Test basic script errors
pre-commit run psscriptanalyzer --files examples/basic-script-errors.ps1

# Test module issues
pre-commit run psscriptanalyzer --files examples/module-errors.psm1

# Test manifest problems
pre-commit run psscriptanalyzer --files examples/manifest-errors.psd1
```

### Test with Different Severity Levels

```bash
# Only show errors
pwsh -Command "Invoke-ScriptAnalyzer -Path ./examples/ -Severity Error"

# Show warnings and errors
pwsh -Command "Invoke-ScriptAnalyzer -Path ./examples/ -Severity Warning"

# Show all issues including information
pwsh -Command "Invoke-ScriptAnalyzer -Path ./examples/ -Severity Information"
```

## Expected Output

When running PSScriptAnalyzer on these examples, you should see output similar to:

```text
examples/basic-script-errors.ps1:5:1: PSAvoidUsingCmdletAliases: 'ls' is an alias of 'Get-ChildItem'. Alias can introduce possible problems and make scripts hard to maintain. Please consider changing alias to its full content.

examples/basic-script-errors.ps1:10:10: PSUseSingularNouns: The cmdlet 'Get-Users' uses a plural noun. A singular noun should be used instead.

examples/security-issues.ps1:3:1: PSAvoidUsingPlainTextForPassword: Parameter 'Password' should use SecureString, otherwise this will expose passwords. Please consider changing the type to SecureString.
```

## Using Examples for Development

### Pre-commit Hook Testing

These examples are perfect for testing pre-commit hook functionality:

```bash
# Install hooks
pre-commit install

# Test on examples (should fail)
git add examples/
git commit -m "Test commit"  # Will be blocked by hooks

# Run formatting (may fix some issues)
pre-commit run psscriptanalyzer-format --files examples/*.ps1
```

### CI/CD Pipeline Testing

Use examples in continuous integration:

```yaml
# GitHub Actions example
- name: Test PSScriptAnalyzer Examples
  run: |
    # Should find violations
    pwsh -Command "
      $results = Invoke-ScriptAnalyzer -Path ./examples/ -Recurse
      if ($results.Count -eq 0) {
        Write-Error 'Expected violations in examples but found none'
        exit 1
      }
      Write-Host 'Found expected violations:' $results.Count
    "
```

### Learning PowerShell Best Practices

Each file demonstrates what NOT to do:

1. **Read the comments**: Each violation is documented
2. **Run analysis**: See what PSScriptAnalyzer reports
3. **Fix the issues**: Practice correcting common problems
4. **Compare results**: See how the analysis output changes

## Contributing New Examples

To add new example violations:

1. **Identify the rule**: Find a PSScriptAnalyzer rule not covered
2. **Create minimal reproduction**: Write the smallest code that triggers the rule
3. **Add comments**: Explain what the violation demonstrates
4. **Test thoroughly**: Ensure PSScriptAnalyzer detects the issue
5. **Document**: Add to this README under the appropriate category

### Example Template

```powershell
# Example: Rule Name (PSRuleName)
# This demonstrates [what the violation is]
# PSScriptAnalyzer should report: [expected message]

# Violating code here
function Bad-Example {
    # This violates PSRuleName because...
    Write-Host "This is problematic"
}

# Correct version (commented)
# function Good-Example {
#     Write-Output "This is better"
# }
```

## Integration with Documentation

These examples are referenced throughout the documentation:

- **Installation Guide**: Used to verify hook installation
- **Usage Examples**: Demonstrate hook behavior
- **Configuration**: Show how different settings affect output
- **Troubleshooting**: Help diagnose hook issues

## Maintenance

The examples are maintained to:

- **Stay current**: Updated when new PSScriptAnalyzer rules are added
- **Remain comprehensive**: Cover all major rule categories
- **Be educational**: Clear comments explaining each violation
- **Test thoroughly**: Verified against multiple PowerShell versions

## Summary

These intentionally flawed PowerShell files provide a comprehensive test suite for the PSScriptAnalyzer pre-commit hooks. They serve as both a learning resource for PowerShell best practices and a validation tool for the hook implementation across different platforms and PowerShell versions.
