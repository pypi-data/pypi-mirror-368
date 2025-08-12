from spiral.cli import AsyncTyper

from . import namespaces, tables

app = AsyncTyper(short_help="Apache Iceberg Catalog.")
app.add_typer(tables.app, name="tables")
app.add_typer(namespaces.app, name="namespaces")
