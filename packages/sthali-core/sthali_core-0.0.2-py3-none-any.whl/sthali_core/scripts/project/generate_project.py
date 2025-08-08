"""Script to generate a new project using the Sthali Core cookiecutter template.

This script clones the template, applies the project name and year, copies the generated content, and cleans up the
temporary directory.
"""

import datetime
import subprocess

import cookiecutter.main  # type: ignore
import typer


def main(project_name: str) -> None:
    """Generate a new project using the Sthali Core cookiecutter template.

    Args:
        project_name: The name of the new project to generate.
    """
    typer.echo(f"Generating project with name: {project_name}")

    typer.echo("Cloning template")
    cookiecutter.main.cookiecutter(  # type: ignore
        "https://github.com/project-sthali/sthali-core",
        no_input=True,
        overwrite_if_exists=True,
        extra_context={"project_name": project_name, "year": datetime.datetime.now(datetime.timezone.utc).year},
    )

    typer.echo("Copying content from temp directory")
    subprocess.call(["cp", "-r", f"./{project_name}/", "."])

    typer.echo("Deleting temp directory")
    subprocess.call(["rm", "-rf", f"./{project_name}"])
