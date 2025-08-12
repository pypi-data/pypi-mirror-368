from typing import Annotated

import pyperclip
import questionary
import rich
from questionary import Choice
from typer import Argument, Option

from spiral.api.workloads import CreateWorkloadRequest, IssueWorkloadCredentialsResponse, Workload
from spiral.cli import AsyncTyper, printer, state
from spiral.cli.types import ProjectArg

app = AsyncTyper()


@app.command(help="Create a new workload.")
def create(
    project: ProjectArg,
    name: Annotated[str | None, Option(help="Friendly name for the workload.")] = None,
):
    res = state.settings.api.workload.create(project, CreateWorkloadRequest(name=name))
    rich.print(f"Created workload {res.workload.id}")


@app.command(help="List workloads.")
def ls(
    project: ProjectArg,
):
    workloads = list(state.settings.api.workload.list(project))
    rich.print(printer.table_of_models(Workload, workloads, fields=["id", "project_id", "name"]))


@app.command(help="Issue new workflow credentials.")
def issue_credentials(workload_id: Annotated[str, Argument(help="Workload ID.")]):
    res: IssueWorkloadCredentialsResponse = state.settings.api.workload.issue_credentials(workload_id)

    while True:
        choice = questionary.select(
            "What would you like to do with the secret? You will not be able to see this secret again!",
            choices=[
                Choice(title="Copy to clipboard", value=1),
                Choice(title="Print to console", value=2),
                Choice(title="Exit", value=3),
            ],
        ).ask()

        if choice == 1:
            pyperclip.copy(res.client_secret)
            rich.print("[green]Secret copied to clipboard![/green]")
            break
        elif choice == 2:
            rich.print(f"[green]Token Secret:[/green] {res.client_secret}")
            break
        elif choice == 3:
            break
        else:
            rich.print("[red]Invalid choice. Please try again.[/red]")

    rich.print(f"[green]Token ID:[/green] {res.client_id}")
