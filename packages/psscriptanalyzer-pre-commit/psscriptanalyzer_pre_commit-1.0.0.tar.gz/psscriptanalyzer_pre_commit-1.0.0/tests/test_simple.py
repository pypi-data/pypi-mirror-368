"""Simple tests for psscriptanalyzer_hook module."""

from unittest.mock import patch

from psscriptanalyzer_hook import find_powershell, main


def test_find_powershell_success() -> None:
    """Test finding PowerShell when it's available."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        result = find_powershell()
        assert result in ["pwsh", "powershell"]


def test_find_powershell_not_found() -> None:
    """Test when PowerShell is not found."""
    with patch("subprocess.run", side_effect=FileNotFoundError):
        result = find_powershell()
        assert result is None


def test_main_no_ps_files() -> None:
    """Test main function with no PowerShell files."""
    result = main(["test.txt", "test.py"])
    assert result == 0


def test_main_no_powershell() -> None:
    """Test main function when PowerShell is not found."""
    with patch("psscriptanalyzer_hook.find_powershell", return_value=None):
        result = main(["test.ps1"])
        assert result == 1


def test_main_success() -> None:
    """Test successful execution of main function."""
    with (
        patch("psscriptanalyzer_hook.find_powershell", return_value="pwsh"),
        patch("psscriptanalyzer_hook.check_psscriptanalyzer_installed", return_value=True),
        patch("psscriptanalyzer_hook.run_script_analyzer", return_value=0),
    ):
        result = main(["test.ps1"])
        assert result == 0
