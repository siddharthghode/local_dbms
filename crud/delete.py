"""Backward-compatible shim."""
from services.record_service import delete_record  # noqa: F401
from services.table_service import drop_table  # noqa: F401
