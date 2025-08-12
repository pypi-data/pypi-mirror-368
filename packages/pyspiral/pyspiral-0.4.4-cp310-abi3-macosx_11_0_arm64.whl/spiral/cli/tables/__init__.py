from typing import Annotated

import questionary
import rich
import typer
from questionary import Choice
from typer import Argument, Option

from spiral import Spiral
from spiral.cli import AsyncTyper, state
from spiral.cli.types import ProjectArg
from spiral.tables import Table

app = AsyncTyper(short_help="Spiral Tables.")


def ask_table(project_id, title="Select a table"):
    tables = list(state.spiral.project(project_id).tables.list_tables())

    if not tables:
        rich.print("[red]No tables found[/red]")
        raise typer.Exit(1)

    return questionary.select(
        title,
        choices=[
            Choice(title=f"{table.dataset}.{table.table}", value=f"{table.project_id}.{table.dataset}.{table.table}")
            for table in tables
        ],
    ).ask()


@app.command(help="List tables.")
def ls(
    project: ProjectArg,
):
    tables = Spiral().project(project).tables.list_tables()

    rich_table = rich.table.Table("id", "dataset", "name", title="Spiral tables")
    for table in tables:
        rich_table.add_row(table.id, table.dataset, table.table)
    rich.print(rich_table)


@app.command(help="Show the table key schema.")
def key_schema(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
):
    _, table = _get_table(project, table, dataset)
    rich.print(table.key_schema)


@app.command(help="Compute the full table schema.")
def schema(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
):
    _, table = _get_table(project, table, dataset)
    rich.print(table.schema)


@app.command(help="Flush Write-Ahead-Log.")
def flush(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
):
    identifier, table = _get_table(project, table, dataset)
    table.maintenance().flush_wal()
    print(f"Flushed WAL for table {identifier} in project {project}.")


@app.command(help="Display scan.")
def debug(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
    column_group: Annotated[str, Argument(help="Dot-separated column group path.")] = ".",
):
    _, table = _get_table(project, table, dataset)
    if column_group != ".":
        projection = table[column_group]
    else:
        projection = table
    scan = table.scan(projection)

    scan._debug()


@app.command(help="Display manifests.")
def manifests(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
    column_group: Annotated[str, Argument(help="Dot-separated column group path.")] = ".",
):
    _, table = _get_table(project, table, dataset)
    if column_group != ".":
        projection = table[column_group]
    else:
        projection = table
    scan = projection.scan()

    scan._dump_manifests()


def _get_table(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
) -> (str, Table):
    if table is None:
        identifier = ask_table(project)
    else:
        identifier = table
        if dataset is not None:
            identifier = f"{dataset}.{table}"
    return identifier, state.spiral.project(project).tables.table(identifier)
