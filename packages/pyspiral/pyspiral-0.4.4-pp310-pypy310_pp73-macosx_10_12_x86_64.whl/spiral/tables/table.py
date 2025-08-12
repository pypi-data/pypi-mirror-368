from datetime import datetime
from typing import TYPE_CHECKING

from spiral.core.table import Table as CoreTable
from spiral.core.table.spec import Schema
from spiral.expressions.base import Expr, ExprLike
from spiral.settings import settings
from spiral.tables.maintenance import Maintenance
from spiral.tables.scan import Scan
from spiral.tables.snapshot import Snapshot
from spiral.tables.transaction import Transaction

if TYPE_CHECKING:
    from spiral.tables import Tables


class Table(Expr):
    """API for interacting with a SpiralDB's Table.

    Different catalog implementations should ultimately construct a Table object.
    """

    # TODO(marko): Make identifier required.
    def __init__(self, tables: "Tables", table: CoreTable, *, identifier: str | None = None):
        super().__init__(table.__expr__)

        self._tables = tables
        self._table = table
        self._identifier = identifier
        self._key_schema = self._table.key_schema
        self._key_columns = set(self._key_schema.names)

    @property
    def client(self) -> "Tables":
        """Returns the client used by the table."""
        return self._tables

    @property
    def table_id(self) -> str:
        return self._table.id

    @property
    def identifier(self) -> str:
        """Returns the fully qualified identifier of the table."""
        return self._identifier or self._table.id

    @property
    def dataset(self) -> str | None:
        """Returns the dataset of the table."""
        if self._identifier is None:
            return None
        _, dataset, _ = self._identifier.split(".")
        return dataset

    @property
    def name(self) -> str | None:
        """Returns the name of the table."""
        if self._identifier is None:
            return None
        _, _, name = self._identifier.split(".")
        return name

    @property
    def last_modified_at(self) -> int:
        return self._table.get_wal(asof=None).last_modified_at

    def __str__(self):
        return self.identifier

    def __repr__(self):
        return f'Table("{self.identifier}")'

    def __getitem__(self, item: str) -> Expr:
        return super().__getitem__(item)

    def select(self, *paths: str, exclude: list[str] = None) -> "Expr":
        # Override an expression select in the root column group to split between keys and columns.
        if exclude is not None:
            if set(exclude) & self._key_columns:
                raise ValueError(
                    "Cannot use 'exclude' arg with key columns. Use 'exclude_keys' and an explicit select of keys."
                )

        return super().select(*paths, exclude=exclude)

    @property
    def key_schema(self) -> Schema:
        """Returns the key schema of the table."""
        return self._key_schema

    @property
    def schema(self) -> Schema:
        """Returns the FULL schema of the table.

        NOTE: This can be expensive for large tables.
        """
        return self._table.get_schema(asof=None)

    def scan(
        self,
        *projections: ExprLike,
        where: ExprLike | None = None,
        asof: datetime | int | None = None,
        exclude_keys: bool = False,
    ) -> Scan:
        """Reads the table. If projections are not provided, the entire table is read."""
        if not projections:
            projections = [self]

        return self._tables.scan(*projections, where=where, asof=asof, exclude_keys=exclude_keys)

    def write(
        self,
        expr: ExprLike,
        *,
        partition_size_bytes: int | None = None,
    ) -> None:
        """Write an item to the table inside a single transaction.

        :param expr: The expression to write. Must evaluate to a struct array.
        :param partition_size_bytes: The maximum partition size in bytes.
        """
        with self.txn() as txn:
            txn.write(
                expr,
                partition_size_bytes=partition_size_bytes,
            )

    def snapshot(self, asof: datetime | int | None = None) -> Snapshot:
        """Returns a snapshot of the table at the given timestamp."""
        if isinstance(asof, datetime):
            asof = int(asof.timestamp() * 1_000_000)
        return Snapshot(self._tables, self._table.get_snapshot(asof=asof))

    def txn(self) -> Transaction:
        """Begins a new transaction. Transaction must be committed for writes to become visible.

        IMPORTANT: While transaction can be used to atomically write data to the table,
             it is important that the primary key columns are unique within the transaction.
        """
        return Transaction(self._tables._spiral.open_transaction(self._table, settings().file_format))

    def maintenance(self) -> Maintenance:
        """Access maintenance operations for a table."""
        return Maintenance(self._tables._spiral.open_maintenance(self._table, settings().file_format))
