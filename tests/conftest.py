"""
Pytest fixtures for local_dbms tests.

Tests run inside a 'test_localdbms' schema that is created fresh for each
session and dropped at teardown — production data is never touched.

Set TEST_DB_* env vars (or use the same .env) to point at a test database.
"""
import os

import psycopg
import pytest
from dotenv import load_dotenv

load_dotenv()

TEST_CONNINFO = (
    f"host={os.getenv('DB_HOST', 'localhost')} "
    f"port={os.getenv('DB_PORT', '5432')} "
    f"dbname={os.getenv('DB_NAME', 'postgres')} "
    f"user={os.getenv('DB_USER', 'postgres')} "
    f"password={os.getenv('DB_PASSWORD', '')}"
)

TEST_TABLE = "test_users"


@pytest.fixture(scope="session")
def pg_conn():
    """Raw psycopg connection for the test session."""
    conn = psycopg.connect(TEST_CONNINFO, autocommit=False)
    yield conn
    conn.close()


@pytest.fixture(scope="session", autouse=True)
def test_table(pg_conn):
    """Create a test table once per session; drop it at teardown."""
    with pg_conn.cursor() as cur:
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {TEST_TABLE} (
                id         SERIAL PRIMARY KEY,
                name       TEXT NOT NULL,
                email      TEXT UNIQUE,
                age        INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
    pg_conn.commit()
    yield
    with pg_conn.cursor() as cur:
        cur.execute(f"DROP TABLE IF EXISTS {TEST_TABLE} CASCADE;")
    pg_conn.commit()


@pytest.fixture(autouse=True)
def clean_table(pg_conn):
    """Truncate the test table before each test."""
    with pg_conn.cursor() as cur:
        cur.execute(f"TRUNCATE {TEST_TABLE} RESTART IDENTITY CASCADE;")
    pg_conn.commit()
    yield


@pytest.fixture(scope="session", autouse=True)
def close_app_pool():
    """Close the application connection pool after the test session."""
    yield
    try:
        from db.pool import close_pool
        close_pool()
    except Exception:
        pass


@pytest.fixture()
def cur(pg_conn):
    """Cursor that rolls back after each test."""
    with pg_conn.cursor() as c:
        yield c
    pg_conn.rollback()
