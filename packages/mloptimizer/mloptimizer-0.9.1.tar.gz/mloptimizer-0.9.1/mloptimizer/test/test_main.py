import pytest
from pathlib import Path
from mloptimizer.__main__ import main, get_version

def test_version_output(monkeypatch, capsys):
    # Read the version from the VERSION file directly for the expected output
    version_file = Path(__file__).resolve().parent.parent / "VERSION"
    with open(version_file) as f:
        expected_version = f.read().strip()

    # Use monkeypatch to simulate the command-line argument `--version`
    monkeypatch.setattr("sys.argv", ["mloptimizer", "--version"])

    # Run the main function, which should print the version
    main()

    # Capture the output
    captured = capsys.readouterr()

    # Verify that the output matches the expected version format
    assert captured.out.strip() == f"mloptimizer version: {expected_version}"
