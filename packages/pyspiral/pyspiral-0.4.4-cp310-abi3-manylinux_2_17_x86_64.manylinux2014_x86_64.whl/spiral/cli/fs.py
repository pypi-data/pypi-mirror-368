from typing import Annotated

import questionary
import rich
from pydantic import SecretStr
from typer import Option

from spiral.api.filesystems import (
    AWSSecretAccessKey,
    BuiltinFileSystem,
    GCPServiceAccount,
    UpdateGCSFileSystem,
    UpdateS3FileSystem,
    UpstreamFileSystem,
)
from spiral.cli import AsyncTyper, state
from spiral.cli.types import ProjectArg, ask_project

app = AsyncTyper(short_help="File Systems.")


@app.command(help="Show the file system configured for project.")
def show(project: ProjectArg):
    file_system = state.settings.api.file_system.get_file_system(project)
    match file_system:
        case BuiltinFileSystem(provider=provider):
            rich.print(f"provider: {provider}")
        case _:
            rich.print(file_system)


def ask_provider():
    res = state.settings.api.file_system.list_providers()
    return questionary.select("Select a file system provider", choices=res).ask()


BuiltinProviderOpt = Annotated[
    str,
    Option(help="Built-in provider to use for the file system.", show_default=False, default_factory=ask_provider),
]


@app.command(help="Update a project's default file system.")
def update(
    project: ProjectArg,
    builtin: bool = Option(False, help="Use a built-in file system provider."),
    upstream: bool = Option(
        False, help="Use another project as default file system. Only if another project is an external provider."
    ),
    s3: bool = Option(False, help="Use S3 compatible provider."),
    gcs: bool = Option(False, help="Use GCS provider."),
    provider: str = Option(None, help="Built-in provider to use for the file system."),
    endpoint: str = Option(None, help="Endpoint for S3 provider."),
    region: str = Option(None, help="Region for S3 or GCS provider. Required for GCS."),
    bucket: str = Option(None, help="Bucket name for S3 or GCS provider."),
    directory: str = Option(None, help="Directory for S3 or GCS provider."),
    access_key_id: str = Option(None, help="Access key ID for S3 provider. Required for S3."),
    secret_access_key: str = Option(None, help="Secret access key for S3 provider. Required for S3."),
    credentials_path: str = Option(
        None, help="Path to service account credentials file for GCS provider. Required for GCS."
    ),
):
    if not any([builtin, s3, gcs, upstream]):
        raise ValueError("Must specify one of --builtin, --upstream, --s3, or --gcs.")

    if builtin:
        provider = provider or ask_provider()
        file_system = BuiltinFileSystem(provider=provider)

    elif upstream:
        upstream_project = ask_project(title="Select a project to use as file system.")
        file_system = UpstreamFileSystem(project_id=upstream_project)

    elif s3:
        if access_key_id is None or secret_access_key is None:
            raise ValueError("--access-key-id and --secret-access-key are required for S3 provider.")
        credentials = AWSSecretAccessKey(access_key_id=access_key_id, secret_access_key=secret_access_key)

        if bucket is None:
            raise ValueError("--bucket is required for S3 provider.")
        file_system = UpdateS3FileSystem(bucket=bucket, credentials=credentials)
        if endpoint:
            file_system.endpoint = endpoint
        if region:
            file_system.region = region
        if directory:
            file_system.directory = directory

    elif gcs:
        if credentials_path is None:
            raise ValueError("--credentials-path is required for GCS provider.")
        with open(credentials_path) as f:
            service_account = f.read()
        credentials = GCPServiceAccount(credentials=SecretStr(service_account))

        if region is None or bucket is None:
            raise ValueError("--region and --bucket is required for GCS provider.")
        file_system = UpdateGCSFileSystem(bucket=bucket, region=region, credentials=credentials)
        if directory:
            file_system.directory = directory

    else:
        raise ValueError("Must specify either --s3 or --gcs.")

    res = state.settings.api.file_system.update_file_system(project, file_system)
    rich.print(res.file_system)


@app.command(help="Lists the available built-in file system providers.")
def list_providers():
    for provider in state.settings.api.file_system.list_providers():
        rich.print(provider)
