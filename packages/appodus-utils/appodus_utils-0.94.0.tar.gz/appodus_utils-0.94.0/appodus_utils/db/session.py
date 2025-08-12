import os
from contextlib import asynccontextmanager
from contextvars import ContextVar, Token
from logging import Logger
from typing import AsyncGenerator

from kink import di

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from appodus_utils import Utils
from appodus_utils.exception.exceptions import AppodusBaseException

logger: Logger = di['logger']

db_url = Utils.get_from_env_fail_if_not_exists('SQLALCHEMY_DATABASE_URI')
db_log_enabled = bool(Utils.get_from_env('DB_ENABLE_LOGS') or True)
engine = create_async_engine(
    db_url,
    echo=db_log_enabled,
    query_cache_size=500,
    future=True,
    pool_pre_ping=True,
    echo_pool=True,
    pool_size=5,
    max_overflow=10
)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
db_session_ctx: ContextVar[AsyncSession] = ContextVar("db_session_ctx")


async def close_db_engine():
    logger.info("Disposing DB engine.")
    await engine.dispose()
    logger.info("...done disposing DB engine.")


# Add to dependency injector
def get_async_session_for_di(_):
    return get_db_session_from_context()


di[AsyncSession] = get_async_session_for_di


@asynccontextmanager
async def create_new_db_session() -> AsyncGenerator[AsyncSession, None]:
    logger.debug("Creating async database session.")
    async with AsyncSessionLocal() as session:
        token = set_db_session_context(session)
        logger.debug("Database session context set.")
        try:
            yield session
            logger.debug("Database session yielded successfully.")
        except Exception as e:
            error_msg = f"Exception during DB session usage: {e}"
            logger.exception(error_msg)
            raise AppodusBaseException(error_msg)
        finally:
            db_session_ctx.reset(token)
            logger.debug("Database session context reset.")


def set_db_session_context(session: AsyncSession) -> Token[AsyncSession]:
    return db_session_ctx.set(session)


def get_db_session_from_context() -> AsyncSession:
    error_msg = (
        "No database session found in context. "
        "Make sure to call this function within @transactional or a request context using get_db_session."
    )
    try:
        session = db_session_ctx.get()
    except LookupError:
        raise AppodusBaseException(error_msg)
    if session is None:
        raise AppodusBaseException(error_msg)
    return session
