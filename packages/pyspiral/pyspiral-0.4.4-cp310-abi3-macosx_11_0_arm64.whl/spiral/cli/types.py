from typing import Annotated

import questionary
import rich
import typer
from questionary import Choice
from typer import Argument

from spiral.api.types import OrgId, ProjectId
from spiral.cli import state


def ask_project(title="Select a project"):
    projects = list(state.settings.api.project.list())

    if not projects:
        rich.print("[red]No projects found[/red]")
        raise typer.Exit(1)

    return questionary.select(
        title,
        choices=[
            Choice(title=f"{project.id} - {project.name}" if project.name else project.id, value=project.id)
            for project in projects
        ],
    ).ask()


ProjectArg = Annotated[ProjectId, Argument(help="Project ID", show_default=False, default_factory=ask_project)]


def _org_default():
    memberships = list(state.settings.api.organization.list_memberships())

    if not memberships:
        rich.print("[red]No organizations found[/red]")
        raise typer.Exit(1)

    return questionary.select(
        "Select an organization",
        choices=[
            Choice(
                title=f"{m.org.id} - {m.org.name}" if m.org.name else m.org.id,
                value=m.org.id,
            )
            for m in memberships
        ],
    ).ask()


OrganizationArg = Annotated[OrgId, Argument(help="Organization ID", show_default=False, default_factory=_org_default)]
