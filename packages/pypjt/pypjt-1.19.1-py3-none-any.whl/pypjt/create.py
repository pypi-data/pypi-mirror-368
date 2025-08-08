#!/usr/bin/env python3
"""Create a new python project."""

import os
import shutil
from pathlib import Path

import click
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel

load_dotenv()
PACKAGE_DIR = Path(__file__).parent.absolute()
RC_DIR = PACKAGE_DIR / "resources"
__VERSION__ = "1.19.1"


class Project(BaseModel):
    """Pydantic model for project data."""

    project_dir: Path
    project_name: str
    version: str = "0.0.1"
    author: str = ""
    email: str = ""
    description: str = ""


class Renderer:
    """A class to render templates."""

    def __init__(self, searchpath: str | os.PathLike[str]) -> None:
        """Initialize the Renderer.

        Args:
            searchpath: The path to search for templates.

        """
        self.searchpath = searchpath
        self.env = Environment(
            loader=FileSystemLoader(self.searchpath),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=select_autoescape(),
        )

    def render(
        self,
        template: str | os.PathLike[str],
        output_file: str | os.PathLike[str] = "",
        kwargs: dict | None = None,
    ) -> str:
        """Render a template.

        Args:
            template: The name of the template to render.
            output_file: The path to write the rendered output to. If not
              provided, the output is not written to a file.
            kwargs: A dictionary of keyword arguments to pass to the template.

        Returns:
            The rendered template as a string.

        """
        t = self.env.get_template(str(template))
        output = t.render(**(kwargs or {}))
        if output_file:
            Path(output_file).write_text(output, encoding="utf-8")
        return output


def process(project: Project) -> None:
    """Process the project creation.

    Args:
        project: A Project object containing project details.

    """
    shutil.copytree(RC_DIR, project.project_dir)

    (project.project_dir / "CHANGELOG.md").touch()

    src_dir = project.project_dir / project.project_name
    src_dir.mkdir()
    (src_dir / "__init__.py").touch()
    shutil.copy2(RC_DIR / ".env.template", project.project_dir / ".env")

    r = Renderer(searchpath=RC_DIR)
    render_kwargs = project.model_dump()
    r.render("compose.yml", project.project_dir / "compose.yml", render_kwargs)
    r.render("MANIFEST.in", project.project_dir / "MANIFEST.in", render_kwargs)
    r.render(
        "pyproject.toml",
        project.project_dir / "pyproject.toml",
        {**render_kwargs, "pypjt_version": __VERSION__},
    )
    r.render("README.rst", project.project_dir / "README.rst", render_kwargs)
    r.render(".releaserc", project.project_dir / ".releaserc", render_kwargs)
    r.render(
        "docs/source/conf.py",
        project.project_dir / "docs/source/conf.py",
        render_kwargs,
    )
    r.render(
        "docs/source/index.rst",
        project.project_dir / "docs/source/index.rst",
        render_kwargs,
    )


@click.command()
def main() -> None:
    """Run the command-line interface for creating a new project."""
    project_name = click.prompt("Project name", type=str)
    click.echo(f"Project will create at '{Path.cwd() / project_name}'")
    project_dir = Path.cwd() / project_name
    if project_dir.exists():
        msg = (
            f"Project dir '{project_dir}' already exists, "
            f"please choose another name or delete it first."
        )
        raise click.ClickException(
            msg,
        )
    version = click.prompt("Version", type=str, default="0.0.1")
    author = click.prompt("Author", type=str, default="")
    email = click.prompt("Email", type=str, default="")
    description = click.prompt("Description", type=str, default="")

    project = Project(
        project_dir=project_dir,
        project_name=project_name,
        version=version,
        author=author,
        email=email,
        description=description,
    )
    process(project)


if __name__ == "__main__":
    main()
