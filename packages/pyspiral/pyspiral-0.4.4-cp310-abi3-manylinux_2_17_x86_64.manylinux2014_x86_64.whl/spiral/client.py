from typing import TYPE_CHECKING

import jwt

from spiral.api import SpiralAPI
from spiral.api.projects import CreateProjectRequest, CreateProjectResponse
from spiral.core.client import Spiral as CoreSpiral
from spiral.settings import Settings, settings

if TYPE_CHECKING:
    from spiral.iceberg import Iceberg
    from spiral.project import Project


class Spiral:
    def __init__(self, config: Settings | None = None):
        self._config = config or settings()
        self._api = self._config.api
        self._core = CoreSpiral(
            api_url=self._config.spiraldb.uri, spfs_url=self._config.spfs.uri, authn=self._config.authn
        )
        self._org = None

    @property
    def config(self) -> Settings:
        return self._config

    @property
    def api(self) -> SpiralAPI:
        return self._api

    @property
    def organization(self) -> str:
        if self._org is None:
            token = self._config.authn.token()
            if token is None:
                raise ValueError("Authentication failed.")
            token_payload = jwt.decode(token.expose_secret(), options={"verify_signature": False})
            if "org_id" not in token_payload:
                raise ValueError("Please create an organization.")
            self._org = token_payload["org_id"]
        return self._org

    def list_projects(self) -> list["Project"]:
        """List project IDs."""
        from .project import Project

        return [Project(self, id=p.id, name=p.name) for p in self.api.project.list()]

    def create_project(
        self,
        id_prefix: str | None = None,
        *,
        name: str | None = None,
    ) -> "Project":
        """Create a project in the current, or given, organization."""
        from .project import Project

        res: CreateProjectResponse = self.api.project.create(CreateProjectRequest(id_prefix=id_prefix, name=name))
        return Project(self, res.project.id, name=res.project.name)

    def project(self, project_id: str) -> "Project":
        """Open an existing project."""
        from spiral.project import Project

        # We avoid an API call since we'd just be fetching a human-readable name. Seems a waste in most cases.
        return Project(self, id=project_id, name=project_id)

    @property
    def iceberg(self) -> "Iceberg":
        """
        Apache Iceberg is a powerful open-source table format designed for high-performance data lakes.
        Iceberg brings reliability, scalability, and advanced features like time travel, schema evolution,
        and ACID transactions to your warehouse.

        """
        from spiral.iceberg import Iceberg

        return Iceberg(self)
