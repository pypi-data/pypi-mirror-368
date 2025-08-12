import datetime

from spiral.api import SpiralAPI
from spiral.api.projects import TextIndexResource
from spiral.core.client import Spiral as CoreSpiral
from spiral.expressions.base import ExprLike
from spiral.indexes.index import TextIndex
from spiral.indexes.scan import SearchScan
from spiral.types_ import Uri


class Indexes:
    def __init__(self, api: SpiralAPI, spiral: CoreSpiral, *, project_id: str | None = None):
        self._api = api
        self._spiral = spiral
        self._project_id = project_id

    def index(self, identifier: str) -> TextIndex:
        """Returns the index with the given identifier."""
        project_id, index_name = self._parse_identifier(identifier)
        if project_id is None:
            raise ValueError("Must provide a fully qualified index identifier.")

        res = list(self._api.project.list_text_indexes(project_id, name=index_name))
        if len(res) == 0:
            raise ValueError(f"Index not found: {project_id}.{index_name}")
        res = res[0]

        return TextIndex(self, self._spiral.get_text_index(res.id), index_name)

    def list_indexes(self) -> list[TextIndexResource]:
        project_id = self._project_id
        if project_id is None:
            raise ValueError("Must provide a project ID to list indexes.")
        return list(self._api.project.list_text_indexes(project_id))

    def create_text_index(
        self,
        identifier: str,
        # At least one projection is required. All projections must reference the same table!
        # NOTE(marko): Indexes are currently independent of tables.
        #   That will likely change with the new root resource such as documents.
        *projections: ExprLike,
        where: ExprLike | None = None,
        root_uri: Uri | None = None,
        exist_ok: bool = False,
    ) -> TextIndex:
        """Creates a text index over the table projection.

        See `se.text.field` for how to create and configure indexable fields.

        Args:
            identifier: The index identifier, in the form `project.index` or `index`.
            projections: At least one projection expression is required.
                All projections must reference the same table.
            where: An optional filter expression to apply to the index.
            root_uri: The root URI for the index.
            exist_ok: If True, do not raise an error if the index already exists.
        """
        from spiral import expressions as se

        project_id, index_name = self._parse_identifier(identifier)
        if project_id is None:
            raise ValueError("Must provide a fully qualified index identifier.")

        if not projections:
            raise ValueError("At least one projection is required.")
        projection = se.merge(*projections)
        if where is not None:
            where = se.lift(where)

        core_index = self._spiral.create_text_index(
            project_id,
            index_name,
            projection.__expr__,
            where.__expr__ if where else None,
            root_uri=root_uri,
            # TODO(marko): Validate that if an index exists, it's the same?
            exist_ok=exist_ok,
        )

        return TextIndex(self, core_index, index_name)

    def _parse_identifier(self, identifier: str) -> tuple[str | None, str]:
        parts = identifier.split(".")
        if len(parts) == 1:
            return self._project_id, parts[0]
        elif len(parts) == 2:
            return parts[0], parts[1]
        else:
            raise ValueError(f"Invalid index identifier: {identifier}")

    def search(
        self,
        *rank_by: ExprLike,
        where: ExprLike | None = None,
        top_k: int = 10,
        # Do not refresh the index if freshness does not exceed the freshness window.
        # NOTE(marko): The current implementation fails the query if the index is stale.
        freshness_window: datetime.timedelta | None = None,
    ) -> SearchScan:
        """Queries the index with the given rank by and where clauses.

        Rank by expressions are combined for scoring.
            See `se.text.find` and `se.text.boost` for scoring expressions.
        The `where` expression is used to filter the results.
            It must return a boolean value and use only conjunctions (ANDs). Expressions in where statement
            are considered either a `must` or `must_not` clause in search terminology.

        Args:
            rank_by: At least one rank by expression is required.
                These expressions are used to score the results.
            where: An optional filter expression to apply to the index.
                It must return a boolean value and use only conjunctions (ANDs).
            top_k: The number of top results to return.
            freshness_window: If provided, the index will not be refreshed if its freshness does not exceed this window.
        """
        from spiral import expressions as se

        if not rank_by:
            raise ValueError("At least one rank by expression is required.")
        rank_by = se.or_(*rank_by)
        if where is not None:
            where = se.lift(where)

        if freshness_window is None:
            freshness_window = datetime.timedelta(seconds=0)
        freshness_window_s = int(freshness_window.total_seconds())

        return SearchScan(
            self._spiral.open_search_scan(
                rank_by.__expr__,
                top_k=top_k,
                freshness_window_s=freshness_window_s,
                filter=where.__expr__ if where else None,
            )
        )
