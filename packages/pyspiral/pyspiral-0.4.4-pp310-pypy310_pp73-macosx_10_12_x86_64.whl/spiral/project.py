from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from spiral.client import Spiral
    from spiral.iceberg import Iceberg
    from spiral.indexes import Indexes
    from spiral.tables import Tables


class Project:
    def __init__(self, spiral: "Spiral", id: str, name: str | None = None):
        self._spiral = spiral
        self._id = id
        self._name = name

    def __str__(self):
        return self._id

    def __repr__(self):
        return f"Project(id={self._id}{', name=' + self._name if self._name else ''})"

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name or self._id

    @property
    def tables(self) -> "Tables":
        from spiral.tables import Tables

        return Tables(self._spiral._api, self._spiral._core, project_id=self.id)

    @property
    def indexes(self) -> "Indexes":
        from spiral.indexes.client import Indexes

        return Indexes(self._spiral._api, self._spiral._core, project_id=self._id)

    @property
    def iceberg(self) -> "Iceberg":
        from spiral.iceberg import Iceberg

        return Iceberg(self._spiral, project_id=self._id)
