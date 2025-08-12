import logging
import os
from logging.handlers import RotatingFileHandler

from spiral.cli import (
    AsyncTyper,
    admin,
    console,
    fs,
    iceberg,
    indexes,
    login,
    orgs,
    projects,
    state,
    tables,
    telemetry,
    workloads,
)
from spiral.settings import LOG_DIR, Settings

app = AsyncTyper(name="spiral")


@app.callback()
def _callback(verbose: bool = False):
    if verbose:
        logging.getLogger().setLevel(level=logging.INFO)

    # Load the settings (we reload in the callback to support testing under different env vars)
    state.settings = Settings()


app.add_typer(fs.app, name="fs")
app.add_typer(orgs.app, name="orgs")
app.add_typer(projects.app, name="projects")
app.add_typer(iceberg.app, name="iceberg")
app.add_typer(tables.app, name="tables")
app.add_typer(indexes.app, name="indexes")
app.add_typer(telemetry.app, name="telemetry")
app.command("console")(console.command)
app.command("login")(login.command)
app.command("whoami")(login.whoami)

# Register unless we're building docs. Because Typer docs command does not skip hidden commands...
if not bool(os.environ.get("SPIRAL_DOCS", False)):
    app.add_typer(workloads.app, name="workloads", hidden=True)
    app.add_typer(admin.app, name="admin", hidden=True)
    app.command("logout", hidden=True)(login.logout)


def main():
    # Setup rotating CLI logging.
    # NOTE(ngates): we should do the same for the Spiral client? Maybe move this logic elsewhere?
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[RotatingFileHandler(LOG_DIR / "cli.log", maxBytes=2**20, backupCount=10)],
    )

    app()


if __name__ == "__main__":
    main()
