"""Integration tests for statistics and connection pool."""
from db.config import DB_CONFIG
from db.metadata import get_db_size, get_table_stats
from db.pool import get_pool
from db.transactions import readonly_cursor
from tests.conftest import TEST_TABLE


def test_pool_is_open():
    pool = get_pool()
    assert pool is not None
    assert not pool.closed


def test_pool_provides_working_connections():
    """Pool connections should be functional (can execute queries)."""
    pool = get_pool()
    results = []
    for _ in range(3):
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                results.append(cur.fetchone()[0])
    assert results == [1, 1, 1]


def test_get_table_stats_contains_test_table():
    with readonly_cursor() as cur:
        stats = get_table_stats(cur)
    tables = [s["table"] for s in stats]
    assert TEST_TABLE in tables


def test_get_db_size():
    with readonly_cursor() as cur:
        size = get_db_size(cur, DB_CONFIG["dbname"])
    assert size  # non-empty string like "8192 bytes"
