from click.testing import CliRunner
from pathlib import Path
from codewright.cli import setup


def test_setup_command():
    runner = CliRunner()
    # Use the runner to invoke the command in an isolated filesystem
    with runner.isolated_filesystem() as temp_dir:
        result = runner.invoke(setup, ["my-test-app"])

        # Check that the command exited successfully
        assert result.exit_code == 0
        assert "Project 'my-test-app' created successfully!" in result.output

        # Check if directories and files were created
        base_path = Path(temp_dir) / "my-test-app"
        assert (base_path).is_dir()
        assert (base_path / "my-test-app").is_dir()
        assert (base_path / "tests").is_dir()
        assert (base_path / "README.md").is_file()
        assert (base_path / "pyproject.toml").is_file()
