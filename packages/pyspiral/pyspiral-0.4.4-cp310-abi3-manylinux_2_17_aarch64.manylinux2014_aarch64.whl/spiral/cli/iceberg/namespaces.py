import sys
from typing import Annotated

import pyiceberg.exceptions
import rich
import typer
from typer import Argument

from spiral.cli import AsyncTyper, state
from spiral.cli.types import ProjectArg

app = AsyncTyper(short_help="Apache Iceberg Namespaces.")


@app.command(help="List namespaces.")
def ls(
    project: ProjectArg,
    namespace: Annotated[str | None, Argument(help="List only namespaces under this namespace.")] = None,
):
    """List Iceberg namespaces."""
    catalog = state.spiral.iceberg.catalog()

    if namespace is None:
        try:
            namespaces = catalog.list_namespaces(project)
        except pyiceberg.exceptions.ForbiddenError:
            print(
                f"The project, {repr(project)}, does not exist or you lack the "
                f"`iceberg:view` permission to list namespaces in it.",
                file=sys.stderr,
            )
            raise typer.Exit(code=1)
    else:
        try:
            namespaces = catalog.list_namespaces((project, namespace))
        except pyiceberg.exceptions.ForbiddenError:
            print(
                f"The namespace, {repr(project)}.{repr(namespace)}, does not exist or you lack the "
                f"`iceberg:view` permission to list namespaces in it.",
                file=sys.stderr,
            )
            raise typer.Exit(code=1)

    table = rich.table.Table("Namespace ID", title="Iceberg namespaces")
    for ns in namespaces:
        table.add_row(".".join(ns))
    rich.print(table)
