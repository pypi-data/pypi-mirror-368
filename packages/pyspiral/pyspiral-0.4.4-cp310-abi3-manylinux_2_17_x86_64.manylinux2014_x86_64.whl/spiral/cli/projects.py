from typing import Annotated

import rich
import typer
from typer import Option

from spiral.api.organizations import OrgRole
from spiral.api.projects import (
    CreateProjectRequest,
    GCPPrincipalConditions,
    GitHubConditions,
    GitHubPrincipalConditions,
    Grant,
    GrantRoleRequest,
    ModalConditions,
    ModalPrincipalConditions,
    OrgRolePrincipalConditions,
    OrgUserPrincipalConditions,
    Project,
    WorkloadPrincipalConditions,
)
from spiral.cli import AsyncTyper, printer, state
from spiral.cli.types import ProjectArg

app = AsyncTyper(short_help="Projects and grants.")


@app.command(help="List projects.")
def ls():
    projects = list(state.settings.api.project.list())
    rich.print(printer.table_of_models(Project, projects))


@app.command(help="Create a new project.")
def create(
    id_prefix: Annotated[
        str | None, Option(help="An optional ID prefix to which a random number will be appended.")
    ] = None,
    name: Annotated[str | None, Option(help="Friendly name for the project.")] = None,
):
    res = state.settings.api.project.create(CreateProjectRequest(id_prefix=id_prefix, name=name))
    rich.print(f"Created project {res.project.id}")


@app.command(help="Grant a role on a project.")
def grant(
    project: ProjectArg,
    role: Annotated[str, Option(help="Role to grant.")],
    org_id: Annotated[
        str | None, Option(help="Pass an organization ID to grant a role to an organization user(s).")
    ] = None,
    user_id: Annotated[
        str | None, Option(help="Pass a user ID when using --org-id to grant a role to grant a role to a user.")
    ] = None,
    org_role: Annotated[
        str | None,
        Option(help="Pass an organization role when using --org-id to grant a role to all users with that role."),
    ] = None,
    workload_id: Annotated[str | None, Option(help="Pass a workload ID to grant a role to a workload.")] = None,
    github: Annotated[
        str | None, Option(help="Pass an `<org>/<repo>` string to grant a role to a job running in GitHub Actions.")
    ] = None,
    modal: Annotated[
        str | None,
        Option(help="Pass a `<workspace_id>/<env_name>` string to grant a role to a job running in Modal environment."),
    ] = None,
    gcp: Annotated[
        str | None,
        Option(help="Pass a `<service_account_email>/<unique_id>` to grant a role to a GCP service account."),
    ] = None,
    conditions: list[str] | None = Option(
        default=None,
        help="`<key>=<value>` token conditions to apply to the grant when using --github or --modal.",
    ),
):
    # Check mutual exclusion
    if sum(int(bool(opt)) for opt in {org_id, workload_id, github, modal, gcp}) != 1:
        raise typer.BadParameter("Only one of --org-id, --github or --modal may be specified.")

    if github:
        org, repo = github.split("/", 1)
        github_conditions = None
        if conditions is not None:
            github_conditions = GitHubConditions()
            for k, v in dict(c.split("=", 1) for c in conditions).items():
                github_conditions = github_conditions.model_copy(update={k: v})
        principal = GitHubPrincipalConditions(org=org, repo=repo, conditions=github_conditions)

    elif modal:
        workspace_id, environment_name = modal.split("/", 1)
        modal_conditions = None
        if conditions is not None:
            modal_conditions = ModalConditions()
            for k, v in dict(c.split("=", 1) for c in conditions).items():
                modal_conditions = modal_conditions.model_copy(update={k: v})
        principal = ModalPrincipalConditions(
            workspace_id=workspace_id, environment_name=environment_name, conditions=modal_conditions
        )

    elif org_id:
        # Check mutual exclusion
        if sum(int(bool(opt)) for opt in {user_id, org_role}) != 1:
            raise typer.BadParameter("Only one of --user-id or --org-role may be specified.")

        if user_id is not None:
            principal = OrgUserPrincipalConditions(org_id=org_id, user_id=user_id)
        elif org_role is not None:
            principal = OrgRolePrincipalConditions(org_id=org_id, role=OrgRole(org_role))
        else:
            raise NotImplementedError("Only user or role principal is supported at this time.")

    elif workload_id:
        principal = WorkloadPrincipalConditions(workload_id=workload_id)

    elif gcp:
        service_account, unique_id = gcp.split("/", 1)
        principal = GCPPrincipalConditions(service_account=service_account, unique_id=unique_id)

    else:
        raise ValueError("Invalid grant principal")

    state.settings.api.project.grant_role(
        project,
        GrantRoleRequest(
            role_id=role,
            principal=principal,
        ),
    )

    rich.print(f"Granted role {role} on project {project}")


@app.command(help="List project grants.")
def grants(project: ProjectArg):
    project_grants = list(state.settings.api.project.list_grants(project))
    rich.print(printer.table_of_models(Grant, project_grants, title="Project Grants"))
