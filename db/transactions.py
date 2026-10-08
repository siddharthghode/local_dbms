"""
Transaction management for local_dbms.

Usage:
    with transaction() as (conn, cur):
        cur.execute(...)
        cur.execute(...)
    # auto-commits on clean exit, auto-rollbacks on exception
"""
import logging
from collections.abc import Generator
from contextlib import contextmanager

import psycopg

from db.pool import get_pool

logger = logging.getLogger(__name__)


@contextmanager
def transaction() -> Generator[tuple[psycopg.Connection, psycopg.Cursor], None, None]:
    """
    Acquire a connection from the pool and yield (conn, cursor).
    Commits on success, rolls back on any exception, always returns
    the connection to the pool.
    """
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            try:
                yield conn, cur
                conn.commit()
                logger.debug("Transaction committed.")
            except Exception:
                conn.rollback()
                logger.warning("Transaction rolled back.")
                raise


@contextmanager
def readonly_cursor() -> Generator[psycopg.Cursor, None, None]:
    """
    Acquire a read-only cursor (no commit needed).
    Suitable for SELECT queries.
    """
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            yield cur
