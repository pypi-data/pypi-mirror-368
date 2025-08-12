import rich

from spiral.cli import AsyncTyper, state
from spiral.cli.types import ProjectArg

app = AsyncTyper(short_help="Indexes.")


@app.command(help="List indexes.")
def ls(
    project: ProjectArg,
):
    """List indexes."""
    indexes = state.spiral.project(project).indexes.list_indexes()

    rich_table = rich.table.Table("id", "name", title="Indexes")
    for index in indexes:
        rich_table.add_row(index.id, index.name)
    rich.print(rich_table)
