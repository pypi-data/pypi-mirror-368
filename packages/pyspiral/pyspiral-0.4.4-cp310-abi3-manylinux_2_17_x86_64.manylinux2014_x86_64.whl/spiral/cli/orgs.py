import webbrowser
from typing import Annotated

import jwt
import rich
import typer
from rich.table import Table
from typer import Option

from spiral.api.organizations import CreateOrgRequest, InviteUserRequest, OrgRole, PortalLinkIntent, PortalLinkRequest
from spiral.cli import AsyncTyper, state
from spiral.cli.types import OrganizationArg

app = AsyncTyper(short_help="Org admin.")


@app.command(help="Switch the active organization.")
def switch(org_id: OrganizationArg):
    state.settings.device_code_auth.authenticate(org_id=org_id)
    rich.print(f"Switched to organization: {org_id}")


@app.command(help="Create a new organization.")
def create(
    name: Annotated[str | None, Option(help="The human-readable name of the organization.")] = None,
):
    res = state.settings.api.organization.create(CreateOrgRequest(name=name))

    # Authenticate to the new organization
    state.settings.device_code_auth.authenticate(org_id=res.org.id)

    rich.print(f"{res.org.name} [dim]{res.org.id}[/dim]")


@app.command(help="List organizations.")
def ls():
    org_id = current_org_id()

    table = Table("", "id", "name", "role", title="Organizations")
    for m in state.settings.api.organization.list_memberships():
        table.add_row("👉" if m.org.id == org_id else "", m.org.id, m.org.name, m.role)

    rich.print(table)


@app.command(help="Invite a user to the organization.")
def invite(email: str, role: OrgRole = OrgRole.MEMBER, expires_in_days: int = 7):
    state.settings.api.organization.invite_user(
        InviteUserRequest(email=email, role=role, expires_in_days=expires_in_days)
    )
    rich.print(f"Invited {email} as a {role.value}.")


@app.command(help="Configure single sign-on for your organization.")
def sso():
    _do_action(PortalLinkIntent.SSO)


@app.command(help="Configure directory services for your organization.")
def directory():
    _do_action(PortalLinkIntent.DIRECTORY_SYNC)


@app.command(help="Configure audit logs for your organization.")
def audit_logs():
    _do_action(PortalLinkIntent.AUDIT_LOGS)


@app.command(help="Configure log streams for your organization.")
def log_streams():
    _do_action(PortalLinkIntent.LOG_STREAMS)


@app.command(help="Configure domains for your organization.")
def domains():
    _do_action(PortalLinkIntent.DOMAIN_VERIFICATION)


def _do_action(intent: PortalLinkIntent):
    res = state.settings.api.organization.portal_link(PortalLinkRequest(intent=intent))
    rich.print(f"Opening the configuration portal:\n{res.url}")
    webbrowser.open(res.url)


def current_org_id():
    if token := state.settings.authn.token():
        if org_id := jwt.decode(token.expose_secret(), options={"verify_signature": False}).get("org_id"):
            return org_id
    rich.print("[red]You are not logged in to an organization.[/red]")
    raise typer.Exit(1)
