import datetime
from typing import TYPE_CHECKING

from spiral.core.index import TextIndex as CoreTextIndex
from spiral.expressions import Expr

if TYPE_CHECKING:
    from spiral.indexes import Indexes


class TextIndex(Expr):
    def __init__(self, indexes: "Indexes", index: CoreTextIndex, name: str):
        super().__init__(index.__expr__)

        self._indexes = indexes
        self._index = index
        self._name = name

    @property
    def client(self) -> "Indexes":
        return self._indexes

    @property
    def index_id(self) -> str:
        return self._index.id

    @property
    def name(self) -> str:
        return self._name

    def status(self) -> (str, datetime.timedelta | None):
        """Fetch the status of the index. If status is ready, returns the staleness of the index."""
        status = self._index.status()
        return status.status, datetime.timedelta(seconds=status.staleness_s) if status.staleness_s is not None else None
