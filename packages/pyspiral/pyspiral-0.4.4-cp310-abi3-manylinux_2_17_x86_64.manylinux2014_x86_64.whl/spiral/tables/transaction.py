from typing import TYPE_CHECKING

from spiral.core.table import TableTransaction

if TYPE_CHECKING:
    from spiral.expressions.base import ExprLike


class Transaction:
    """Spiral table transaction.

    IMPORTANT: While transaction can be used to atomically write data to the table,
            it is important that the primary key columns are unique within the transaction.
    """

    def __init__(self, transaction: TableTransaction):
        self._transaction = transaction

    @property
    def status(self) -> str:
        """The status of the transaction."""
        return self._transaction.status

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self._transaction.commit()
        else:
            self._transaction.abort()

    def write(self, expr: "ExprLike", *, partition_size_bytes: int | None = None):
        """Write an item to the table inside a single transaction.

        :param expr: The expression to write. Must evaluate to a struct array.
        :param partition_size_bytes: The maximum partition size in bytes.
            If not provided, the default partition size is used.
        """
        from spiral import expressions as se

        expr = se.lift(expr)

        self._transaction.write(expr.__expr__, partition_size_bytes=partition_size_bytes)

    def commit(self):
        """Commit the transaction."""
        self._transaction.commit()

    def abort(self):
        """Abort the transaction."""
        self._transaction.abort()
