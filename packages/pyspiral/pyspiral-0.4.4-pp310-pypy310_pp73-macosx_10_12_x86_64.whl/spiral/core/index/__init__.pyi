import pyarrow as pa

class IndexStatus:
    status: str
    staleness_s: int | None
    # An extent of keys that are indexed.
    # key_extent: KeyExtent | None

class TextIndex:
    id: str

    def status(self) -> IndexStatus: ...

class SearchScan:
    def to_record_batches(self) -> pa.RecordBatchReader: ...
