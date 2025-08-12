import pyperclip
import rich

from spiral.api.telemetry import IssueExportTokenResponse
from spiral.cli import AsyncTyper, state

app = AsyncTyper(short_help="Client-side telemetry.")


@app.command(help="Issue new telemetry export token.")
def export():
    res: IssueExportTokenResponse = state.settings.api.telemetry.issue_export_token()

    command = f"export SPIRAL_OTEL_TOKEN={res.token}"
    pyperclip.copy(command)

    rich.print("Export command copied to clipboard! Paste and run to set [green]SPIRAL_OTEL_TOKEN[/green].")
    rich.print("[dim]Token is valid for 1h.[/dim]")
