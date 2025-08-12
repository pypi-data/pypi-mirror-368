import pyarrow as pa

from spiral.core.index import SearchScan as CoreSearchScan
from spiral.settings import CI, DEV


class SearchScan:
    def __init__(self, scan: CoreSearchScan):
        self._scan = scan

    def to_record_batches(self) -> pa.RecordBatchReader:
        """Read all results as a record batch reader."""
        return self._scan.to_record_batches()

    def to_table(self) -> pa.Table:
        """Read all results as a table."""
        # NOTE: Evaluates fully on Rust side which improved debuggability.
        if DEV and not CI:
            rb = self._scan.to_record_batch()
            return pa.Table.from_batches([rb])

        return self.to_record_batches().read_all()
