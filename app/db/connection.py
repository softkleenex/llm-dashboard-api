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
    """
    Get a connection from the pool with explicit transaction management.
    동시성 제어: Oracle의 기본 격리 수준인 READ COMMITTED를 사용하여
    Dirty Read를 방지하고 일관성 있는 데이터 읽기를 보장합니다.
    
    참고: Oracle은 READ COMMITTED(기본값)와 SERIALIZABLE만 지원합니다.
    READ COMMITTED는 명시적으로 설정하는 SQL이 없으며 기본값으로 동작합니다.
    """
    if pool is None:
        init_pool()
    conn = pool.acquire()
    try:
        # 동시성 제어: 명시적 트랜잭션 관리 활성화
        # autocommit=False로 설정하여 각 작업이 트랜잭션 내에서 수행되도록 함
        # Oracle의 기본 격리 수준인 READ COMMITTED 사용:
        #   - Dirty Read 방지: 커밋되지 않은 데이터는 읽을 수 없음
        #   - Phantom Read/Non-repeatable Read는 허용 (성능과 일관성의 균형)
        conn.autocommit = False
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
        import traceback
        print(f"Database connection failed: {e}")
        print(f"Settings - DSN: {settings.dsn}, Wallet: {settings.wallet_location}")
        traceback.print_exc()
        return False
