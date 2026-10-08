"""Integration tests for CRUD operations."""
import pytest

from db.metadata import get_column_names
from db.transactions import readonly_cursor, transaction
from tests.conftest import TEST_TABLE


def _insert(name: str, email: str = None, age: int = None):
    with transaction() as (_, cur):
        cur.execute(
            f"INSERT INTO {TEST_TABLE} (name, email, age) VALUES (%s, %s, %s)",
            (name, email, age),
        )


def _count() -> int:
    with readonly_cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM {TEST_TABLE}")
        return cur.fetchone()[0]


def _fetch_all():
    with readonly_cursor() as cur:
        cur.execute(f"SELECT * FROM {TEST_TABLE} ORDER BY id")
        return cur.fetchall()


# ── INSERT ─────────────────────────────────────────────────────────────────────

def test_insert_single():
    _insert("Alice", "alice@example.com", 30)
    assert _count() == 1


def test_insert_multiple():
    for i in range(5):
        _insert(f"User{i}", f"user{i}@example.com", 20 + i)
    assert _count() == 5


# ── READ ───────────────────────────────────────────────────────────────────────

def test_read_returns_inserted_data():
    _insert("Bob", "bob@example.com", 25)
    rows = _fetch_all()
    assert len(rows) == 1
    assert rows[0][1] == "Bob"


def test_column_names():
    with readonly_cursor() as cur:
        cols = get_column_names(cur, TEST_TABLE)
    assert "name" in cols
    assert "email" in cols


# ── UPDATE ─────────────────────────────────────────────────────────────────────

def test_update_record():
    _insert("Carol", "carol@example.com", 28)
    with readonly_cursor() as cur:
        cur.execute(f"SELECT id FROM {TEST_TABLE} WHERE name='Carol'")
        row_id = cur.fetchone()[0]

    with transaction() as (_, cur):
        cur.execute(
            f"UPDATE {TEST_TABLE} SET name=%s, updated_at=CURRENT_TIMESTAMP WHERE id=%s",
            ("Carol Updated", row_id),
        )

    with readonly_cursor() as cur:
        cur.execute(f"SELECT name FROM {TEST_TABLE} WHERE id=%s", (row_id,))
        assert cur.fetchone()[0] == "Carol Updated"


# ── DELETE ─────────────────────────────────────────────────────────────────────

def test_delete_record():
    _insert("Dave", "dave@example.com")
    with readonly_cursor() as cur:
        cur.execute(f"SELECT id FROM {TEST_TABLE} WHERE name='Dave'")
        row_id = cur.fetchone()[0]

    with transaction() as (_, cur):
        cur.execute(f"DELETE FROM {TEST_TABLE} WHERE id=%s", (row_id,))

    assert _count() == 0


# ── SEARCH ─────────────────────────────────────────────────────────────────────

def test_search_ilike():
    _insert("Eve Smith", "eve@example.com")
    _insert("Frank Jones", "frank@example.com")

    with readonly_cursor() as cur:
        cur.execute(
            f"SELECT * FROM {TEST_TABLE} WHERE name::text ILIKE %s",
            ("%smith%",),
        )
        rows = cur.fetchall()
    assert len(rows) == 1
    assert rows[0][1] == "Eve Smith"


def test_search_no_results():
    _insert("Grace", "grace@example.com")
    with readonly_cursor() as cur:
        cur.execute(
            f"SELECT * FROM {TEST_TABLE} WHERE name::text ILIKE %s",
            ("%zzznomatch%",),
        )
        rows = cur.fetchall()
    assert rows == []


# ── PAGINATION ─────────────────────────────────────────────────────────────────

def test_pagination_limit_offset():
    for i in range(10):
        _insert(f"Page{i}", f"page{i}@example.com")

    with readonly_cursor() as cur:
        cur.execute(f"SELECT * FROM {TEST_TABLE} ORDER BY id LIMIT 3 OFFSET 0")
        page1 = cur.fetchall()
        cur.execute(f"SELECT * FROM {TEST_TABLE} ORDER BY id LIMIT 3 OFFSET 3")
        page2 = cur.fetchall()

    assert len(page1) == 3
    assert len(page2) == 3
    assert page1[0][0] != page2[0][0]


# ── UNIQUE CONSTRAINT ──────────────────────────────────────────────────────────

def test_unique_email_constraint():
    _insert("Heidi", "heidi@example.com")
    with pytest.raises(Exception):
        _insert("Heidi2", "heidi@example.com")
