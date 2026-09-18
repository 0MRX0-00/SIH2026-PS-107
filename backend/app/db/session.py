import logging
from typing import AsyncGenerator
from app.core.config import settings

logger = logging.getLogger("ebis.db")

engine = None
AsyncSessionLocal = None

try:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    try:
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            future=True,
            pool_pre_ping=True
        )
        AsyncSessionLocal = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
    except Exception as e:
        logger.warning(f"Failed to create primary async engine ({e}).")
        # Try sqlite if aiosqlite exists
        try:
            engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False, future=True)
            AsyncSessionLocal = async_sessionmaker(
                bind=engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False
            )
        except Exception:
            # Fallback mock for environments without asyncpg/aiosqlite
            class DummyAsyncSession:
                async def __aenter__(self):
                    return self
                async def __aexit__(self, exc_type, exc_val, exc_tb):
                    pass
                async def execute(self, *args, **kwargs):
                    raise RuntimeError("No active database driver (asyncpg/aiosqlite) installed")
                async def close(self):
                    pass

            def dummy_session_maker():
                return DummyAsyncSession()

            AsyncSessionLocal = dummy_session_maker

except Exception as ex:
    logger.warning(f"SQLAlchemy async setup fallback: {ex}")
    class DummyAsyncSession:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def execute(self, *args, **kwargs):
            raise RuntimeError("No active database driver")
        async def close(self):
            pass

    def dummy_session_maker():
        return DummyAsyncSession()

    AsyncSessionLocal = dummy_session_maker


async def get_db() -> AsyncGenerator:
    if AsyncSessionLocal:
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()
    else:
        yield None
