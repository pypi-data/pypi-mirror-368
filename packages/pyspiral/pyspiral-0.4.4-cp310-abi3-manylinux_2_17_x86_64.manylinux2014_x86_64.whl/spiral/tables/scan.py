from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

import pyarrow as pa
from datasets import DatasetInfo, Features

from spiral.core.table import KeyRange, TableScan
from spiral.core.table.spec import Schema
from spiral.settings import CI, DEV

if TYPE_CHECKING:
    import dask.dataframe as dd
    import pandas as pd
    import polars as pl
    from datasets import iterable_dataset


class Scan:
    """Scan object."""

    def __init__(
        self,
        scan: TableScan,
    ):
        # NOTE(ngates): this API is a little weird. e.g. if the query doesn't define an asof, it is resolved
        #  when we wrap it into a core.Scan. Should we expose a Query object in the Python API that's reusable
        #  and will re-resolve the asof? Or should we just expose a scan that fixes the asof at construction time?
        self._scan = scan

    @property
    def metrics(self) -> dict[str, Any]:
        """Returns metrics about the scan."""
        return self._scan.metrics()

    @property
    def schema(self) -> Schema:
        """Returns the schema of the scan."""
        return self._scan.schema()

    def is_empty(self) -> bool:
        """Check if the Spiral is empty for the given key range.

        **IMPORTANT**: False negatives are possible, but false positives are not,
            i.e. is_empty can return False and scan can return zero rows.
        """
        return self._scan.is_empty()

    def to_record_batches(
        self,
        key_table: pa.Table | pa.RecordBatchReader | None = None,
        batch_size: int | None = None,
        batch_readahead: int | None = None,
    ) -> pa.RecordBatchReader:
        """Read as a stream of RecordBatches.

        Args:
            key_table: a table of keys to "take" (including aux columns for cell-push-down).
                If None, the scan will be executed without a key table.
            batch_size: the maximum number of rows per returned batch.
                IMPORTANT: This is currently only respected when the key_table is used. If key table is a
                    RecordBatchReader, the batch_size argument must be None, and the existing batching is respected.
            batch_readahead: the number of batches to prefetch in the background.
        """
        if isinstance(key_table, pa.RecordBatchReader):
            if batch_size is not None:
                raise ValueError(
                    "batch_size must be None when key_table is a RecordBatchReader, the existing batching is respected."
                )
        elif isinstance(key_table, pa.Table):
            key_table = key_table.to_reader(max_chunksize=batch_size)

        return self._scan.to_record_batches(key_table=key_table, batch_readahead=batch_readahead)

    def to_table(
        self,
        key_table: pa.Table | pa.RecordBatchReader | None = None,
    ) -> pa.Table:
        """Read into a single PyArrow Table.

        Args:
            key_table: a table of keys to "take" (including aux columns for cell-push-down).
                If None, the scan will be executed without a key table.
        """
        # NOTE: Evaluates fully on Rust side which improved debuggability.
        if DEV and not CI and key_table is None:
            rb = self._scan.to_record_batch()
            return pa.Table.from_batches([rb])

        return self.to_record_batches(key_table=key_table).read_all()

    def to_dask(self) -> "dd.DataFrame":
        """Read into a Dask DataFrame.

        Requires the `dask` package to be installed.
        """
        import dask.dataframe as dd
        import pandas as pd

        def _read_key_range(key_range: KeyRange) -> pd.DataFrame:
            # TODO(ngates): we need a way to preserve the existing asofs? Should we copy CoreScan instead of Query?
            raise NotImplementedError()

        # Fetch a set of partition ranges
        return dd.from_map(_read_key_range, self.split())

    def to_pandas(self) -> "pd.DataFrame":
        """Read into a Pandas DataFrame.

        Requires the `pandas` package to be installed.
        """
        return self.to_table().to_pandas()

    def to_polars(self) -> "pl.DataFrame":
        """Read into a Polars DataFrame.

        Requires the `polars` package to be installed.
        """
        import polars as pl

        # TODO(marko): This should support lazy dataframe.
        return pl.from_arrow(self.to_record_batches())

    def to_pytorch(
        self,
        batch_readahead: int | None = None,
        shuffle_batch_size: int | None = None,
        shuffle_pool_num_rows: int | None = None,
    ) -> "iterable_dataset.IterableDataset":
        """Returns an iterable dataset that can be used to build a PyTorch DataLoader.

        Args:
            batch_readahead: Number of batches to prefetch in the background.
            shuffle_batch_size: read granularity of number of rows for a shuffled scan. If left as
            None along with shuffle_pool_num_rows=None, shuffling is disabled.
            shuffle_pool_num_rows: Pool size for shuffling batches.
        """
        from datasets.iterable_dataset import ArrowExamplesIterable, IterableDataset

        def _generate_tables(**kwargs) -> Iterator[tuple[int, pa.Table]]:
            if shuffle_batch_size is None and shuffle_pool_num_rows is None:
                stream = self.to_record_batches(
                    batch_readahead=batch_readahead,
                )
            else:
                stream = self._scan.to_shuffled_record_batches(
                    batch_readahead, shuffle_batch_size, shuffle_pool_num_rows
                )

            # This key is unused when training with IterableDataset.
            # Default implementation returns shard id, e.g. parquet row group id.
            for i, rb in enumerate(stream):
                yield i, pa.Table.from_batches([rb], stream.schema)

        def _hf_compatible_schema(schema: pa.Schema) -> pa.Schema:
            """
            Replace string-view columns in the schema with strings. We do use this converted schema
            as Features in the returned Dataset.
            Remove this method once we have https://github.com/huggingface/datasets/pull/7718
            """
            new_fields = [
                pa.field(field.name, pa.string(), nullable=field.nullable, metadata=field.metadata)
                if field.type == pa.string_view()
                else field
                for field in schema
            ]
            return pa.schema(new_fields)

        # NOTE: generate_tables_fn type annotations are wrong, return type must be an iterable of tuples.
        ex_iterable = ArrowExamplesIterable(generate_tables_fn=_generate_tables, kwargs={})
        info = DatasetInfo(features=Features.from_arrow_schema(_hf_compatible_schema(self.schema.to_arrow())))
        return IterableDataset(ex_iterable=ex_iterable, info=info)

    def _split(self) -> list[KeyRange]:
        # Splits the scan into a set of key ranges.
        return self._scan.split()

    def _debug(self):
        # Visualizes the scan, mainly for debugging purposes.
        from spiral.tables.debug.scan import show_scan

        show_scan(self._scan)

    def _dump_manifests(self):
        # Print manifests in a human-readable format.
        from spiral.tables.debug.manifests import display_manifests

        display_manifests(self._scan)

    def _dump_metrics(self):
        # Print metrics in a human-readable format.
        from spiral.tables.debug.metrics import display_metrics

        display_metrics(self.metrics)
