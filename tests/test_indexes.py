"""Integration tests for index management."""
from db.metadata import list_indexes, quote_ident
from db.transactions import readonly_cursor, transaction
from tests.conftest import TEST_TABLE

IDX_NAME = f"idx_{TEST_TABLE}_name"


def _create_idx():
    with transaction() as (_, cur):
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS {quote_ident(IDX_NAME)} "
            f"ON {quote_ident(TEST_TABLE)} (name);"
        )


def _drop_idx():
    with transaction() as (_, cur):
        cur.execute(f"DROP INDEX IF EXISTS {quote_ident(IDX_NAME)};")


def test_create_index():
    _create_idx()
    with readonly_cursor() as cur:
        idxs = list_indexes(cur, TEST_TABLE)
    assert any(i["index_name"] == IDX_NAME for i in idxs)
    _drop_idx()


def test_drop_index():
    _create_idx()
    _drop_idx()
    with readonly_cursor() as cur:
        idxs = list_indexes(cur, TEST_TABLE)
    assert not any(i["index_name"] == IDX_NAME for i in idxs)


def test_primary_key_index_exists():
    with readonly_cursor() as cur:
        idxs = list_indexes(cur, TEST_TABLE)
    assert any(i["is_primary"] for i in idxs)
