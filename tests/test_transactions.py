"""Integration tests for db/transactions.py."""
import pytest

from db.transactions import readonly_cursor, transaction
from tests.conftest import TEST_TABLE


def test_transaction_commits(pg_conn):
    with transaction() as (_, cur):
        cur.execute(
            f"INSERT INTO {TEST_TABLE} (name, email) VALUES (%s, %s)",
            ("Alice", "alice@example.com"),
        )
    with pg_conn.cursor() as c:
        c.execute(f"SELECT name FROM {TEST_TABLE} WHERE email = 'alice@example.com'")
        row = c.fetchone()
    assert row is not None
    assert row[0] == "Alice"


def test_transaction_rollback_on_error(pg_conn):
    with pytest.raises(Exception):
        with transaction() as (_, cur):
            cur.execute(
                f"INSERT INTO {TEST_TABLE} (name, email) VALUES (%s, %s)",
                ("Bob", "bob@example.com"),
            )
            # Force an error — duplicate primary key
            cur.execute("SELECT 1/0")

    with pg_conn.cursor() as c:
        c.execute(f"SELECT COUNT(*) FROM {TEST_TABLE} WHERE email = 'bob@example.com'")
        count = c.fetchone()[0]
    assert count == 0


def test_readonly_cursor_select(pg_conn):
    with pg_conn.cursor() as c:
        c.execute(f"INSERT INTO {TEST_TABLE} (name) VALUES ('Charlie')")
    pg_conn.commit()

    with readonly_cursor() as cur:
        cur.execute(f"SELECT name FROM {TEST_TABLE}")
        rows = cur.fetchall()
    assert any(r[0] == "Charlie" for r in rows)
