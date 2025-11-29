import oracledb
from contextlib import contextmanager
from typing import Generator
from app.config import get_settings

settings = get_settings()

# Connection pool
pool = None


def init_pool():
    """Initialize Oracle connection pool for Oracle Cloud Autonomous DB"""
    global pool
    if pool is None:
        pool = oracledb.create_pool(
            user=settings.db_user,
            password=settings.db_password,
            dsn=settings.dsn,
            config_dir=settings.wallet_location,
            wallet_location=settings.wallet_location,
            wallet_password=settings.db_wallet_password,
            min=2,
            max=10,
            increment=1,
        )
    return pool


def close_pool():
    """Close the connection pool"""
    global pool
    if pool:
        pool.close()
        pool = None


@contextmanager
def get_connection() -> Generator[oracledb.Connection, None, None]:
    """Get a connection from the pool"""
    if pool is None:
        init_pool()
    conn = pool.acquire()
    try:
        yield conn
    finally:
        pool.release(conn)


@contextmanager
def get_cursor() -> Generator[oracledb.Cursor, None, None]:
    """Get a cursor with automatic connection management"""
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()


def test_connection() -> bool:
    """Test database connection"""
    try:
        with get_cursor() as cursor:
            cursor.execute("SELECT 1 FROM DUAL")
            result = cursor.fetchone()
            return result is not None and result[0] == 1
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
