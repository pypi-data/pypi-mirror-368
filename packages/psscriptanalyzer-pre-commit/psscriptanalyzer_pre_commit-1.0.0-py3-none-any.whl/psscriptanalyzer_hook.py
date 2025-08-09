#!/usr/bin/env python3
"""
Pre-commit hook for PSScriptAnalyzer.

This script runs PSScriptAnalyzer on PowerShell files to check for issues
            if ($issues.Count -gt 0) {
                Write-Host ""
                foreach ($issue in $issues) {
                    $fileName = Split-Path -Leaf $issue.ScriptName
                    $location = "$($fileName): Line $($issue.Line):1"

                    # Set color based on severity
                    $severityColor = switch ($issue.Severity) {
                        "Error" { "Red" }
                        "Warning" { "DarkYellow" }
                        "Information" { "Cyan" }
                        default { "Red" }
                    }

                    $header = "$($location): $($issue.Severity): $($issue.RuleName)"
                    Write-Host $header -ForegroundColor $severityColor
                    Write-Host "  $($issue.Message)" -ForegroundColor Gray
                    Write-Host ""
                }
"""

import argparse
import subprocess
import sys
from collections.abc import Sequence
from typing import Final, Optional

# Constants
POWERSHELL_EXECUTABLES: Final[list[str]] = ["pwsh", "pwsh-lts", "powershell"]
POWERSHELL_FILE_EXTENSIONS: Final[tuple[str, ...]] = (".ps1", ".psm1", ".psd1")
SEVERITY_LEVELS: Final[list[str]] = ["All", "Information", "Warning", "Error"]

# Timeouts (in seconds)
POWERSHELL_CHECK_TIMEOUT: Final[int] = 10
MODULE_CHECK_TIMEOUT: Final[int] = 30
INSTALL_TIMEOUT: Final[int] = 120
ANALYSIS_TIMEOUT: Final[int] = 300


def find_powershell() -> Optional[str]:
    """Find PowerShell executable on the system."""
    for name in POWERSHELL_EXECUTABLES:
        try:
            result = subprocess.run(
                [name, "-Command", "$PSVersionTable.PSVersion"],
                capture_output=True,
                text=True,
                timeout=POWERSHELL_CHECK_TIMEOUT,
                check=False,
            )
            if result.returncode == 0:
                return name
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue

    return None


def check_psscriptanalyzer_installed(powershell_cmd: str) -> bool:
    """Check if PSScriptAnalyzer module is available."""
    try:
        result = subprocess.run(
            [
                powershell_cmd,
                "-Command",
                "Get-Module -ListAvailable -Name PSScriptAnalyzer",
            ],
            capture_output=True,
            text=True,
            timeout=MODULE_CHECK_TIMEOUT,
            check=False,
        )
        return result.returncode == 0 and "PSScriptAnalyzer" in result.stdout
    except subprocess.TimeoutExpired:
        return False


def install_psscriptanalyzer(powershell_cmd: str) -> bool:
    """Install PSScriptAnalyzer module."""
    print("PSScriptAnalyzer not found. Installing...")
    try:
        result = subprocess.run(
            [
                powershell_cmd,
                "-Command",
                "Install-Module -Name PSScriptAnalyzer -Force -Scope CurrentUser",
            ],
            capture_output=True,
            text=True,
            timeout=INSTALL_TIMEOUT,
            check=False,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("Timeout while installing PSScriptAnalyzer")
        return False


def _escape_powershell_path(path: str) -> str:
    """Escape a file path for use in PowerShell."""
    return path.replace("'", "''")


def _build_powershell_file_array(files: list[str]) -> str:
    """Build a PowerShell array string from a list of files."""
    escaped_files = [f"'{_escape_powershell_path(f)}'" for f in files]
    return ",".join(escaped_files)


def run_script_analyzer(
    powershell_cmd: str,
    files: list[str],
    format_files: bool = False,
    severity: str = "Warning",
) -> int:
    """Run PSScriptAnalyzer on the given files."""
    if not files:
        return 0

    files_param = _build_powershell_file_array(files)

    if format_files:
        # Format files using Invoke-Formatter
        ps_command = f"""
        $files = @({files_param})
        $exitCode = 0
        foreach ($file in $files) {{
            try {{
                $originalContent = Get-Content -Path $file -Raw
                $formatted = Invoke-Formatter -ScriptDefinition $originalContent
                if ($formatted -ne $originalContent) {{
                    Set-Content -Path $file -Value $formatted -NoNewline
                    Write-Host "Formatted: $file"
                }}
            }} catch {{
                Write-Error "Failed to format $file`: $($_.Exception.Message)"
                $exitCode = 1
            }}
        }}
        exit $exitCode
        """
    else:
        # Analyze files using Invoke-ScriptAnalyzer
        # Conditionally add Severity parameter - if "All" is selected, omit it to get all severities
        severity_param = f"-Severity {severity}" if severity != "All" else ""

        ps_command = f"""
        try {{
            $files = @({files_param})
            $issues = @()
            foreach ($file in $files) {{
                $result = Invoke-ScriptAnalyzer -Path $file {severity_param}
                if ($result) {{
                    $issues += $result
                }}
            }}
            if ($issues.Count -gt 0) {{
                Write-Host ""

                # Check if running in GitHub Actions
                $isGitHubActions = $env:GITHUB_ACTIONS -eq "true"

                foreach ($issue in $issues) {{
                    $fileName = Split-Path -Leaf $issue.ScriptName
                    $location = "$($fileName): Line $($issue.Line):1"

                    if ($isGitHubActions) {{
                        # Use GitHub Actions annotations
                        $annotationType = switch ($issue.Severity) {{
                            "Error" {{ "error" }}
                            "Warning" {{ "warning" }}
                            "Information" {{ "notice" }}
                            default {{ "error" }}
                        }}

                        # Map severity for GitHub Actions display
                        $displaySeverity = switch ($issue.Severity) {{
                            "Error" {{ "Error" }}
                            "Warning" {{ "Warning" }}
                            "Information" {{ "Notice" }}
                            default {{ "Error" }}
                        }}

                        # GitHub Actions annotation format
                        $annotation = "::" + $annotationType + " file=" + $issue.ScriptName + `
                            ",line=" + $issue.Line + ",title=" + $issue.RuleName + "::" + $issue.Message
                        Write-Host $annotation

                        # Also show regular output for readability with GitHub Actions terminology
                        $header = "$($displaySeverity): $($location): $($issue.RuleName)"
                        Write-Host $header
                        Write-Host "  $($issue.Message)"
                        Write-Host ""
                    }} else {{
                        # Set color based on severity for local terminal
                        $severityColor = switch ($issue.Severity) {{
                            "Error" {{ "Red" }}
                            "Warning" {{ "DarkYellow" }}
                            "Information" {{ "Cyan" }}
                            default {{ "Red" }}
                        }}

                        $header = "$($issue.Severity): $($location): $($issue.RuleName)"
                        Write-Host $header -ForegroundColor $severityColor
                        Write-Host "  $($issue.Message)" -ForegroundColor Gray
                        Write-Host ""
                    }}
                }}
                Write-Host "Found $($issues.Count) issue(s)" -ForegroundColor Yellow
                exit 1
            }} else {{
                Write-Host "No issues found" -ForegroundColor Green
                exit 0
            }}
        }} catch [System.IO.FileLoadException] {{
            Write-Error "Assembly loading error: $($_.Exception.Message)"
            Write-Error "This may be due to .NET runtime compatibility issues."
            Write-Error "Try updating PowerShell or reinstalling PSScriptAnalyzer."
            exit 250
        }} catch {{
            Write-Error "Unexpected error: $($_.Exception.Message)"
            exit 250
        }}
        """

    try:
        result = subprocess.run(
            [powershell_cmd, "-Command", ps_command],
            text=True,
            timeout=ANALYSIS_TIMEOUT,
            check=False,
        )
        return result.returncode
    except subprocess.TimeoutExpired:
        print("Timeout while running PSScriptAnalyzer")
        return 1


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="PSScriptAnalyzer pre-commit hook")
    parser.add_argument(
        "--format",
        action="store_true",
        help="Format files instead of just analyzing them",
    )
    parser.add_argument(
        "--severity",
        choices=SEVERITY_LEVELS,
        default="Warning",
        help="Severity level to report: All (shows all levels), Information, Warning, Error (default: Warning)",
    )
    parser.add_argument("files", nargs="*", help="Files to check")

    args = parser.parse_args(argv)

    # Filter for PowerShell files
    ps_files = [f for f in args.files if f.endswith(POWERSHELL_FILE_EXTENSIONS)]

    if not ps_files:
        return 0

    # Find PowerShell
    powershell_cmd = find_powershell()
    if not powershell_cmd:
        print(
            "Error: PowerShell not found. Please install PowerShell Core (pwsh) or Windows PowerShell.",
            file=sys.stderr,
        )
        print(
            "Visit: https://github.com/PowerShell/PowerShell#get-powershell",
            file=sys.stderr,
        )
        return 1

    print(f"Using PowerShell: {powershell_cmd}")

    # Check if PSScriptAnalyzer is installed
    if not check_psscriptanalyzer_installed(powershell_cmd):
        if not install_psscriptanalyzer(powershell_cmd):
            print("Error: Failed to install PSScriptAnalyzer", file=sys.stderr)
            return 1
        print("PSScriptAnalyzer installed successfully")

    # Run the analysis or formatting
    action = "Formatting" if args.format else "Analyzing"
    print(f"{action} {len(ps_files)} PowerShell file(s)...")

    return run_script_analyzer(powershell_cmd, ps_files, format_files=args.format, severity=args.severity)


if __name__ == "__main__":
    sys.exit(main())
