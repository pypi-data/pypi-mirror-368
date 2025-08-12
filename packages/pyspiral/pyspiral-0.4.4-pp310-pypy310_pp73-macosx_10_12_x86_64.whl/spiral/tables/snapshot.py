from typing import TYPE_CHECKING

from spiral.core.table import TableSnapshot
from spiral.expressions import ExprLike
from spiral.tables.scan import Scan
from spiral.types_ import Timestamp

if TYPE_CHECKING:
    import duckdb
    import polars as pl
    import pyarrow.dataset

    from spiral.tables import Tables
    from spiral.tables.table import Table


class Snapshot:
    """Spiral table snapshot.

    A snapshot represents a point-in-time view of a table.
    """

    def __init__(self, tables: "Tables", snapshot: TableSnapshot):
        self._tables = tables
        self._snapshot = snapshot

    @property
    def asof(self) -> Timestamp:
        """Returns the asof timestamp of the snapshot."""
        return self._snapshot.asof

    @property
    def client(self) -> "Tables":
        """Returns the client used by the snapshot."""
        return self._tables

    @property
    def table(self) -> "Table":
        """Returns the table associated with the snapshot."""
        from spiral.tables.table import Table

        return Table(self._tables, self._snapshot.table)

    def to_dataset(self) -> "pyarrow.dataset.Dataset":
        """Returns a PyArrow Dataset representing the table."""
        from .dataset import TableDataset

        return TableDataset(self)

    def to_polars(self) -> "pl.LazyFrame":
        """Returns a Polars LazyFrame for the Spiral table."""
        import polars as pl

        return pl.scan_pyarrow_dataset(self.to_dataset())

    def to_duckdb(self) -> "duckdb.DuckDBPyRelation":
        """Returns a DuckDB relation for the Spiral table."""
        import duckdb

        return duckdb.from_arrow(self.to_dataset())

    def scan(
        self,
        *projections: ExprLike,
        where: ExprLike | None = None,
        exclude_keys: bool = False,
    ) -> Scan:
        """Reads the snapshot. If projections are not provided, the entire table is read."""
        if not projections:
            # Use table as the default projection.
            projections = [self._snapshot.table.__expr__]

        return self._tables.scan(
            *projections,
            where=where,
            asof=self._snapshot.asof,
            exclude_keys=exclude_keys,
        )
