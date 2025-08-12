from datetime import datetime
from typing import Any

import pyarrow as pa

from spiral.api import SpiralAPI
from spiral.api.projects import TableResource
from spiral.core.client import Spiral as CoreSpiral
from spiral.core.table.spec import Schema
from spiral.datetime_ import timestamp_micros
from spiral.expressions import ExprLike
from spiral.tables.scan import Scan
from spiral.tables.table import Table
from spiral.types_ import Uri


class Tables:
    """
    Spiral Tables a powerful and flexible way for storing, analyzing,
    and querying massive and/or multimodal datasets.

    The data model will feel familiar to users of SQL- or DataFrame-style systems,
    yet is designed to be more flexible, more powerful, and more useful in the context
    of modern data processing. Tables are stored and queried directly from object storage.
    """

    def __init__(self, api: SpiralAPI, spiral: CoreSpiral, *, project_id: str | None = None):
        self._api = api
        self._spiral = spiral
        self._project_id = project_id

    def table(self, identifier: str) -> Table:
        """Open a table with a `dataset.table` identifier, or `table` name using the `default` dataset."""
        project_id, dataset, table = self._parse_identifier(identifier)
        if project_id is None:
            raise ValueError("Must provide a fully qualified table identifier.")

        res = list(self._api.project.list_tables(project_id, dataset=dataset, table=table))
        if len(res) == 0:
            raise ValueError(f"Table not found: {project_id}.{dataset}.{table}")

        res = res[0]
        return Table(self, self._spiral.get_table(res.id), identifier=f"{res.project_id}.{res.dataset}.{res.table}")

    def list_tables(self) -> list[TableResource]:
        project_id = self._project_id
        if project_id is None:
            raise ValueError("Must provide a project ID to list tables.")
        return list(self._api.project.list_tables(project_id))

    def create_table(
        self,
        identifier: str,
        *,
        key_schema: pa.Schema | Any,
        root_uri: Uri | None = None,
        exist_ok: bool = False,
    ) -> Table:
        """Create a new table in the project.

        Args:
            identifier: The table identifier, in the form `project.dataset.table`, `dataset.table` or `table`.
            key_schema: The schema of the table's keys.
            root_uri: The root URI for the table.
            exist_ok: If True, do not raise an error if the table already exists.
        """
        project_id, dataset, table = self._parse_identifier(identifier)
        if project_id is None:
            raise ValueError("Must provide a fully qualified table identifier.")

        if not isinstance(key_schema, pa.Schema):
            key_schema = pa.schema(key_schema)
        key_schema = Schema.from_arrow(key_schema)

        core_table = self._spiral.create_table(
            project_id,
            dataset=dataset,
            table=table,
            key_schema=key_schema,
            root_uri=root_uri,
            exist_ok=exist_ok,
        )

        return Table(self, core_table, identifier=f"{project_id}.{dataset}.{table}")

    def _parse_identifier(self, identifier: str) -> tuple[str | None, str, str]:
        parts = identifier.split(".")
        if len(parts) == 1:
            return self._project_id, "default", parts[0]
        elif len(parts) == 2:
            return self._project_id, parts[0], parts[1]
        elif len(parts) == 3:
            return parts[0], parts[1], parts[2]
        else:
            raise ValueError(f"Invalid table identifier: {identifier}")

    def scan(
        self,
        *projections: ExprLike,
        where: ExprLike | None = None,
        asof: datetime | int | None = None,
        exclude_keys: bool = False,
    ) -> Scan:
        """Starts a read transaction on the Spiral.

        Args:
            projections: a set of expressions that return struct arrays.
            where: a query expression to apply to the data.
            asof: only data written before the given timestamp will be returned, caveats around compaction.
            exclude_keys: whether to exclude the key columns in the scan result, defaults to False.
                Note that if a projection includes a key column, it will be included in the result.
        """
        from spiral import expressions as se

        if isinstance(asof, datetime):
            asof = timestamp_micros(asof)

        # Combine all projections into a single struct.
        projection = se.merge(*projections)
        if where is not None:
            where = se.lift(where)

        return Scan(
            self._spiral.open_table_scan(
                projection.__expr__,
                filter=where.__expr__ if where else None,
                asof=asof,
                exclude_keys=exclude_keys,
            ),
        )
