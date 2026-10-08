"""Integration tests for db/metadata.py."""
import pytest

from db.metadata import (
    get_column_names,
    get_columns,
    get_foreign_keys,
    list_indexes,
    list_tables,
    quote_ident,
    validate_identifier,
)
from tests.conftest import TEST_TABLE


def test_list_tables_contains_test_table(cur):
    tables = list_tables(cur)
    assert TEST_TABLE in tables


def test_get_column_names(cur):
    cols = get_column_names(cur, TEST_TABLE)
    assert "id" in cols
    assert "name" in cols
    assert "email" in cols


def test_get_columns_returns_metadata(cur):
    cols = get_columns(cur, TEST_TABLE)
    names = [c["name"] for c in cols]
    assert "id" in names
    pk_col = next(c for c in cols if c["name"] == "id")
    assert pk_col["primary_key"] == "YES"


def test_get_foreign_keys_empty(cur):
    fks = get_foreign_keys(cur, TEST_TABLE)
    assert isinstance(fks, list)


def test_list_indexes(cur):
    idxs = list_indexes(cur, TEST_TABLE)
    assert any(i["is_primary"] for i in idxs)


def test_quote_ident_basic():
    assert quote_ident("users") == '"users"'


def test_quote_ident_escapes_double_quotes():
    assert quote_ident('say"hello') == '"say""hello"'


def test_quote_ident_null_byte_raises():
    with pytest.raises(ValueError):
        quote_ident("bad\x00name")


def test_validate_identifier_valid():
    assert validate_identifier("my_table") == "my_table"


def test_validate_identifier_invalid():
    with pytest.raises(ValueError):
        validate_identifier("bad name!")
