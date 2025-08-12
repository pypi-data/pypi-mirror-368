from spiral import _lib
from spiral.tables.client import Tables
from spiral.tables.maintenance import Maintenance
from spiral.tables.scan import Scan
from spiral.tables.snapshot import Snapshot
from spiral.tables.table import Table
from spiral.tables.transaction import Transaction

# Eagerly import the Spiral library
assert _lib, "Spiral library"

__all__ = ["Tables", "Table", "Snapshot", "Scan", "Transaction", "Maintenance"]
