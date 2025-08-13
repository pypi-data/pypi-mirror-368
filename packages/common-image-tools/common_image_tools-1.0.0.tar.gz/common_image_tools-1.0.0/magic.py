# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "toml",
#     "typer",
#     "rich",
#     "genbadge[coverage]",
# ]
# ///

import subprocess
from enum import Enum

import toml
import typer
from genbadge import Badge
from rich import print

app = typer.Typer(help="Utility script for project management")
version_app = typer.Typer(help="Version management")
app.add_typer(version_app, name="version")


class VersionPart(str, Enum):
    patch = "patch"
    minor = "minor"
    major = "major"


def get_version() -> str:
    """Get the current version from pyproject.toml"""
    with open("pyproject.toml", "r") as f:
        pyproject = toml.load(f)
    return pyproject["project"]["version"]


def bump(part: VersionPart = VersionPart.patch) -> None:
    """Bump the version number"""
    with open("pyproject.toml", "r") as f:
        pyproject = toml.load(f)

    version = pyproject["project"]["version"]
    major, minor, patch = map(int, version.split("."))

    if part == VersionPart.major:
        major += 1
        minor = 0
        patch = 0
    elif part == VersionPart.minor:
        minor += 1
        patch = 0
    elif part == VersionPart.patch:
        patch += 1

    pyproject["project"]["version"] = f"{major}.{minor}.{patch}"

    with open("pyproject.toml", "w") as f:
        toml.dump(pyproject, f)

    try:
        subprocess.check_call(
            ["uv", "run", "pre-commit", "run", "end-of-file-fixer", "--files", "pyproject.toml"]
        )
    except subprocess.CalledProcessError as e:
        typer.echo("pre-commit fixed pyproject.toml")

    print(f"Version bumped to {major}.{minor}.{patch}")


def run_tests():
    try:
        subprocess.check_call(["uv", "run", "pytest", "--cov=src"])

    except subprocess.CalledProcessError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


def generate_coverage_badge():
    try:
        subprocess.check_call(["uv", "run", "coverage", "xml"])
        subprocess.check_call(
            [
                "genbadge",
                "coverage",
                "-i",
                "coverage.xml",
                "-o",
                "reports/coverage-badge.svg",
            ]
        )

    except subprocess.CalledProcessError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


def generate_version_badge():
    version = get_version()
    b = Badge(left_txt="release", right_txt=f"v{version}", color="#0e7fc0")
    b.write_to("reports/version-badge.svg", use_shields=False)


@version_app.callback(invoke_without_command=True)
def version_callback(ctx: typer.Context) -> None:
    """Show version info"""
    if ctx.invoked_subcommand is None:
        # No subcommand provided, just display the version
        print(get_version())


@version_app.command(name="bump")
def bump_command(
    part: VersionPart = typer.Argument(VersionPart.patch, help="Which part of the version to bump"),
) -> None:
    """Bump version in pyproject.toml"""
    bump(part)


@app.command(name="check")
def check_command() -> None:
    """
    Run pre-release checks
    """

    # Check if we're on the main branch
    try:
        # Install pre-commit hooks
        subprocess.check_call(["uv", "run", "pre-commit", "install"])

        current_branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.STDOUT, text=True
        ).strip()

        if current_branch != "main":
            typer.echo(
                f"Error: You must be on the main branch to release. Current branch: {current_branch}",
                err=True,
            )
            raise typer.Exit(code=1)

        # Check for uncommitted files
        uncommitted_files = subprocess.check_output(
            ["git", "status", "--porcelain"], stderr=subprocess.STDOUT, text=True
        ).strip()
        if uncommitted_files:
            typer.echo(
                "Error: There are uncommitted changes. Please commit all changes before continuing.",
                err=True,
            )
            raise typer.Exit(code=1)

        typer.echo("All checks passed successfully!")
    except subprocess.CalledProcessError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command(name="release")
def release_command(
    part: VersionPart = typer.Argument(VersionPart.patch, help="Which part of the version to bump"),
    skip_tests: bool = typer.Option(
        False, "--skip-tests", help="Skip running tests during release"
    ),
) -> None:
    """
    Prepare a release: run checks and bump version
    """
    # First run checks
    check_command()

    # Run tests if not skipped
    if not skip_tests:
        typer.echo("Running tests...")
        run_tests()
        generate_coverage_badge()
    else:
        typer.echo("Tests skipped as requested.")

    # Bump the version
    bump(part)

    generate_version_badge()

    try:
        # Get the old version for reporting
        old_version = get_version()

        # Get the new version
        new_version = get_version()

        typer.echo(f"Releasing version {old_version} → {new_version}")

        # Build
        typer.echo(f"Building version: {new_version}")
        subprocess.check_call(["uv", "lock"])
        subprocess.check_call(["uv", "build"])

        # Git operations
        # Add files to git
        subprocess.check_call(["git", "add", "."])

        # Commit
        subprocess.check_call(["git", "commit", "-m", f"Release version {new_version}"])

        # Tag
        subprocess.check_call(["git", "tag", f"{new_version}"])

        # Push
        subprocess.check_call(["git", "push", "origin", "main", "--tags"])

    except subprocess.CalledProcessError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    print(f"[green]Successfully released version[/green] [bold green]{new_version}[/bold green]")


@app.command(name="test")
def run_test_command():
    run_tests()


@app.command(name="generate-badges")
def generate_badges():
    generate_coverage_badge()
    generate_version_badge()


if __name__ == "__main__":
    app()
