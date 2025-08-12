from spiral.api.types import DatasetName, IndexName, OrgId, ProjectId, RootUri, TableName
from spiral.core.index import SearchScan, TextIndex
from spiral.core.table import Table, TableMaintenance, TableScan, TableSnapshot, TableTransaction
from spiral.core.table.spec import Schema
from spiral.expressions import Expr

class Token:
    def __init__(self, value: str): ...
    def expose_secret(self) -> str: ...

class Authn:
    @staticmethod
    def from_token(token: Token) -> Authn: ...
    @staticmethod
    def from_fallback() -> Authn: ...
    @staticmethod
    def from_device() -> Authn: ...
    def token(self) -> Token | None: ...

class DeviceCodeAuth:
    @staticmethod
    def default() -> DeviceCodeAuth:
        """Return the static device code instance."""
        ...
    def authenticate(self, force: bool = False, org_id: OrgId | None = None) -> Token:
        """Authenticate using device code flow."""
        ...

    def logout(self) -> None:
        """Logout from the device authentication session."""
        ...

class Spiral:
    """A client for Spiral database"""
    def __init__(
        self,
        api_url: str | None = None,
        spfs_url: str | None = None,
        authn: Authn | None = None,
    ):
        """Initialize the Spiral client."""
        ...
    def authn(self) -> Authn:
        """Get the current authentication context."""
        ...
    def create_table(
        self,
        project_id: ProjectId,
        dataset: DatasetName,
        table: TableName,
        key_schema: Schema,
        *,
        root_uri: RootUri | None = None,
        exist_ok: bool = False,
    ) -> Table:
        """Create a new table in the specified project."""
        ...

    def get_table(self, table_id: str) -> Table:
        """Get and open table."""

    def open_table(self, table_id: str, key_schema: Schema, root_uri: RootUri) -> Table:
        """Open a table. This does not make any network calls."""
        ...

    def open_table_scan(
        self,
        projection: Expr,
        filter: Expr | None = None,
        asof: int | None = None,
        exclude_keys: bool = False,
    ) -> TableScan:
        """Construct a table scan."""
        ...

    def open_transaction(self, table: Table, format: str | None = None) -> TableTransaction:
        """Being transaction."""
        ...

    def open_maintenance(self, table: Table, format: str | None = None) -> TableMaintenance:
        """Access maintenance operations for a table."""
        ...
    def create_text_index(
        self,
        project_id: ProjectId,
        name: IndexName,
        projection: Expr,
        filter: Expr | None = None,
        *,
        root_uri: RootUri | None = None,
        exist_ok: bool = False,
    ) -> TextIndex:
        """Create a new index in the specified project."""
        ...

    def get_text_index(self, index_id: str) -> TextIndex:
        """Get a text-based index."""
        ...

    def open_search_scan(
        self,
        rank_by: Expr,
        top_k: int,
        # NOTE(marko): Required for now.
        freshness_window_s: int,
        *,
        filter: Expr | None = None,
    ) -> SearchScan:
        """Query an index."""
        ...

    def _sync_snapshot(self, index_id: str, snapshot: TableSnapshot) -> None:
        """
        Synchronize an index with a table snapshot.

        IMPORTANT: This is only exposed for testing purposes and should not be used.
        """
        ...
