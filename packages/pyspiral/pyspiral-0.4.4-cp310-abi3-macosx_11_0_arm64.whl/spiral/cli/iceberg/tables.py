import sys
from typing import Annotated

import pyiceberg.exceptions
import rich
import typer
from typer import Argument

from spiral.cli import AsyncTyper, state
from spiral.cli.types import ProjectArg

app = AsyncTyper(short_help="Apache Iceberg Tables.")


@app.command(help="List tables.")
def ls(
    project: ProjectArg,
    namespace: Annotated[str | None, Argument(help="Show only tables in the given namespace.")] = None,
):
    catalog = state.spiral.iceberg.catalog()

    try:
        if namespace is None:
            tables = catalog.list_tables(project)
        else:
            tables = catalog.list_tables((project, namespace))
    except pyiceberg.exceptions.ForbiddenError:
        print(
            f"The namespace, {repr(project)}.{repr(namespace)}, does not exist or you lack the "
            f"`iceberg:view` permission to list tables in it.",
            file=sys.stderr,
        )
        raise typer.Exit(code=1)

    rich_table = rich.table.Table("table id", title="Iceberg tables")
    for table in tables:
        rich_table.add_row(".".join(table))
    rich.print(rich_table)


@app.command(help="Show the table schema.")
def schema(
    project: ProjectArg,
    namespace: Annotated[str, Argument(help="Table namespace.")],
    table: Annotated[str, Argument(help="Table name.")],
):
    catalog = state.spiral.iceberg.catalog()

    try:
        tbl = catalog.load_table((project, namespace, table))
    except pyiceberg.exceptions.NoSuchTableError:
        print(f"No table {repr(table)} found in {repr(project)}.{repr(namespace)}", file=sys.stderr)
        raise typer.Exit(code=1)

    rich_table = rich.table.Table(
        "Field ID", "Field name", "Type", "Required", "Doc", title=f"{project}.{namespace}.{table}"
    )
    for col in tbl.schema().columns:
        rich_table.add_row(str(col.field_id), col.name, str(col.field_type), str(col.required), col.doc)
    rich.print(rich_table)
