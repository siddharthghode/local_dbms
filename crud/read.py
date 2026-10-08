"""Backward-compatible shim — delegates to services."""
from services.record_service import view_records  # noqa: F401
from services.table_service import describe_table, show_tables  # noqa: F401
