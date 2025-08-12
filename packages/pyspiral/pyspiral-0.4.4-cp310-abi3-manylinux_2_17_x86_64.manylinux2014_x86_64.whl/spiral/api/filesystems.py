from enum import Enum
from types import NoneType
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, Field

from .client import Paged, PagedResponse, ServiceBase
from .types import ProjectId


def _validate_directory_path(path: str) -> str:
    if not path.startswith("/"):
        raise ValueError("Directory path must start with a slash.")
    if not path.endswith("/"):
        raise ValueError("Directory path must not end with a slash.")
    return path


DirectoryPath = Annotated[str, AfterValidator(_validate_directory_path)]
FilePath = str  # Path or directory
FsLoc = str


class BuiltinFileSystem(BaseModel):
    """Spiral supports several builtin file systems in different cloud provider regions."""

    type: Literal["builtin"] = "builtin"
    provider: str


class UpstreamFileSystem(BaseModel):
    """File system that points to another project, usually a "file system" project.

    Upstream project must have an external file system configured,
    and not a builtin file system or another upstream file system.
    """

    type: Literal["upstream"] = "upstream"
    project_id: ProjectId


class S3FileSystem(BaseModel):
    """File system backed by an S3-compatible bucket."""

    type: Literal["s3"] = "s3"
    endpoint: str = "https://s3.amazonaws.com"
    region: str = "auto"
    bucket: str
    directory: DirectoryPath | None


class GCSFileSystem(BaseModel):
    """File system backed by a Google Cloud Storage bucket."""

    type: Literal["gcs"] = "gcs"
    region: str
    bucket: str
    directory: DirectoryPath | None


FileSystem = Annotated[
    BuiltinFileSystem | UpstreamFileSystem | S3FileSystem | GCSFileSystem, Field(discriminator="type")
]


class Mode(str, Enum):
    READ_ONLY = "ro"
    READ_WRITE = "rw"


class Mount(BaseModel):
    """Mount grants permission to a Spiral resource to use a specific directory within the file system."""

    id: str
    project_id: ProjectId
    directory: DirectoryPath
    mode: Mode
    principal: str


class AWSSecretAccessKey(BaseModel):
    """AWS secret access key credentials to be used with an S3 file system.
    The access key must have read/write access to the bucket specified in the file system.
    """

    access_key_id: str
    secret_access_key: str


class UpdateS3FileSystem(S3FileSystem):
    credentials: AWSSecretAccessKey


class GCPServiceAccount(BaseModel):
    """Google Cloud Platform service account credentials to be used with a GCS file system.
    The service account must have read/write access to the bucket specified in the file system.
    """

    service_account: str


class UpdateGCSFileSystem(GCSFileSystem):
    credentials: GCPServiceAccount


UpdateFileSystemRequest = Annotated[
    BuiltinFileSystem | UpstreamFileSystem | UpdateS3FileSystem | UpdateGCSFileSystem, Field(discriminator="type")
]


class UpdateFileSystemResponse(BaseModel):
    file_system: FileSystem


class CreateMountRequest(BaseModel):
    directory: DirectoryPath
    mode: Mode
    principal: str


class CreateMountResponse(BaseModel):
    mount: Mount


class GetMountAndFileSystemResponse(BaseModel):
    mount: Mount
    file_system: FileSystem
    fs_loc: FsLoc


class FileSystemService(ServiceBase):
    """Service for file system operations."""

    def list_providers(self) -> list[str]:
        """List builtin providers."""
        response = self.client.get("/v1/file-systems/builtin-providers", dict)
        return response.get("providers", [])

    def update_file_system(self, project_id: ProjectId, request: UpdateFileSystemRequest) -> UpdateFileSystemResponse:
        """Update project's default file system."""
        return self.client.post(f"/v1/file-systems/{project_id}", request, UpdateFileSystemResponse)

    def get_file_system(self, project_id: ProjectId) -> FileSystem:
        """Get project's default file system."""
        return self.client.get(f"/v1/file-systems/{project_id}", FileSystem)

    def create_mount(self, project_id: ProjectId, request: CreateMountRequest) -> CreateMountResponse:
        """Create a mount."""
        return self.client.post(f"/v1/file-systems/{project_id}/mounts", request, CreateMountResponse)

    def list_mounts(self, project_id: ProjectId) -> Paged[Mount]:
        """List active mounts in project's file system."""
        return self.client.paged(f"/v1/file-systems/{project_id}/mounts", PagedResponse[Mount])

    def get_mount(self, mount_id: str) -> Mount:
        """Get a mount."""
        return self.client.get(f"/v1/mounts/{mount_id}", Mount)

    def get_mount_and_file_system(self, mount_id: str) -> GetMountAndFileSystemResponse:
        """Get the mount and its associated file system."""
        return self.client.get(f"/v1/mounts/{mount_id}/with-filesystem", GetMountAndFileSystemResponse)

    def remove_mount(self, mount_id: str) -> None:
        """Remove mount."""
        return self.client.delete(f"/v1/mounts/{mount_id}", NoneType)
