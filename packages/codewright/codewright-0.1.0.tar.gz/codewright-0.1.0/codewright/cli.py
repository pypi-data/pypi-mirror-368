import click
from pathlib import Path


@click.group()
def cli():
    """Codewright: A CLI to accelerate Python development."""
    pass


@cli.command()
@click.argument("project_name")
def setup(project_name):
    """Creates a standard Python project directory structure."""
    click.echo(f"✨ Creating project structure for '{project_name}'...")

    base_path = Path(project_name)
    package_path = base_path / project_name.lower()

    try:
        # Create directories
        package_path.mkdir(parents=True, exist_ok=True)
        (base_path / "tests").mkdir(parents=True, exist_ok=True)

        # Create files
        (base_path / "pyproject.toml").touch()
        (base_path / "README.md").write_text(f"# {project_name}\n")
        (base_path / ".gitignore").write_text("__pycache__/\n.venv/\n*.pyc\n")
        (package_path / "__init__.py").write_text('__version__ = "0.1.0"\n')
        (base_path / "tests" / "__init__.py").touch()

        click.secho(
            f"\n🚀 Project '{project_name}' created successfully!",
            fg="green",
            bold=True,
        )
        click.echo("Created the following structure:")
        click.secho(f"  - {base_path}/", bold=True)
        click.secho(f"    - {package_path.name}/", bold=True)
        click.secho("    - tests/", bold=True)
        click.secho("    - .gitignore", bold=True)
        click.secho("    - pyproject.toml", bold=True)
        click.secho("    - README.md", bold=True)

    except Exception as e:
        click.secho(f"Error creating project: {e}", fg="red")


if __name__ == "__main__":
    cli()
