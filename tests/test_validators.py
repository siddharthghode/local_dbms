"""Unit tests for utils/validators.py — no database required."""
import pytest

from utils.validators import non_empty, positive_int, safe_identifier


class TestNonEmpty:
    def test_valid(self):
        assert non_empty("hello") == "hello"

    def test_strips_whitespace(self):
        assert non_empty("  hi  ") == "hi"

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            non_empty("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError):
            non_empty("   ")


class TestPositiveInt:
    def test_valid(self):
        assert positive_int("5") == 5

    def test_zero_raises(self):
        with pytest.raises(ValueError):
            positive_int("0")

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            positive_int("-3")

    def test_non_numeric_raises(self):
        with pytest.raises(ValueError):
            positive_int("abc")


class TestSafeIdentifier:
    def test_valid_simple(self):
        assert safe_identifier("users") == "users"

    def test_valid_with_underscore(self):
        assert safe_identifier("user_name") == "user_name"

    def test_lowercases(self):
        assert safe_identifier("Users") == "users"

    def test_sql_injection_raises(self):
        with pytest.raises(ValueError):
            safe_identifier("users; DROP TABLE users")

    def test_space_raises(self):
        with pytest.raises(ValueError):
            safe_identifier("my table")

    def test_hyphen_raises(self):
        with pytest.raises(ValueError):
            safe_identifier("my-table")

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            safe_identifier("")

    def test_too_long_raises(self):
        with pytest.raises(ValueError):
            safe_identifier("a" * 64)

    def test_starts_with_digit_raises(self):
        with pytest.raises(ValueError):
            safe_identifier("1table")
