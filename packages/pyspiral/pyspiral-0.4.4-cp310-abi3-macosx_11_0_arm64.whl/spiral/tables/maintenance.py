from spiral.core.table import TableMaintenance


class Maintenance:
    """Spiral table maintenance."""

    def __init__(self, maintenance: TableMaintenance):
        self._maintenance = maintenance

    def flush_wal(self):
        """Flush the write-ahead log."""
        self._maintenance.flush_wal()
