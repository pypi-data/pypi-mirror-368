from typer.testing import CliRunner
from upgrade_tool.main import app

# CliRunner is a utility from Typer for testing command-line applications
runner = CliRunner()

def test_app_shows_up_to_date_message(monkeypatch):
    """
    Tests that the correct message is shown when no packages are outdated.
    This test mocks `get_outdated_packages` to return an empty list.
    """
    # Create a mock function that returns an empty list
    def mock_get_outdated():
        return []

    # Use monkeypatch to replace the function *where it is used* in the main module
    monkeypatch.setattr("upgrade_tool.main.get_outdated_packages", mock_get_outdated)

    # Run the command
    result = runner.invoke(app)

    # Assert that the exit code is 0 (success) and the correct message is in the output
    assert result.exit_code == 0
    assert "All packages are up to date!" in result.stdout

def test_app_exclusion_logic(monkeypatch):
    """
    Tests the --exclude functionality.
    This test mocks a fixed list of outdated packages to verify that the
    exclusion logic works as intended.
    """
    # Create a mock function that returns a predefined list of packages
    def mock_get_outdated():
        return [
            {'name': 'requests', 'version': '2.25.0', 'latest_version': '2.28.0'},
            {'name': 'numpy', 'version': '1.20.0', 'latest_version': '1.23.0'}
        ]

    # Use monkeypatch to replace the function *where it is used* in the main module
    monkeypatch.setattr("upgrade_tool.main.get_outdated_packages", mock_get_outdated)

    # Run the command with the --exclude flag and --dry-run to prevent actual upgrades
    result = runner.invoke(app, ["--exclude", "requests", "--dry-run"])

    # Assertions
    assert result.exit_code == 0
    assert "requests" not in result.stdout  # The excluded package should NOT be in the output table
    assert "numpy" in result.stdout        # The other package should be present
    assert "1 packages selected" in result.stdout # The table caption should reflect the exclusion