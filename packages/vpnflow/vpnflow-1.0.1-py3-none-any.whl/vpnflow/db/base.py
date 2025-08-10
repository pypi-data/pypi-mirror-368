# -*- coding: utf-8 -*-
from contextlib import asynccontextmanager
from logging import getLogger

from sqlalchemy import MetaData
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (AsyncAttrs, AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.orm import DeclarativeBase

from vpnflow.settings import settings

logger = getLogger(__name__)
db_settings = settings.database


class Base(AsyncAttrs, DeclarativeBase):
    """⭐"""

    metadata: MetaData = MetaData()

    __abstract__ = True

    @classmethod
    def build_tablename(cls) -> str:
        """⭐"""
        return cls.__name__.lower() + 's'

    def __repr__(self) -> str:
        cols = [
            f"{col}={getattr(self, col)}"
            for idx, col in enumerate(self.__table__.columns.keys())
        ]
        return f"{self.__class__.__name__}({', '.join(cols)})"


def create_engine(
    url: str = db_settings.sqlalchemy_url.get_secret_value(),
    params = db_settings.sqlalchemy_engine_params
    ) -> AsyncEngine:
    """⭐"""
    return create_async_engine(url, **params)


def create_session_pool(
    engine: AsyncEngine,
    **kwargs: dict
    ) -> async_sessionmaker[AsyncSession]:
    """⭐"""
    expire_on_commit = kwargs.get("expire_on_commit", False)
    return async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=expire_on_commit
        )


@asynccontextmanager
async def run_session(engine, **kwargs):
    """⭐"""
    session_runner = create_session_pool(engine)
    async with session_runner() as session:
        try:
            yield session
            if kwargs.get("commit", False):
                await session.commit()
        except (SQLAlchemyError, Exception) as exc:
            logger.error(exc)
            await session.rollback()
        finally:
            await session.close()


engine_r = create_engine()
engine_w = engine_r.execution_options(isolation_level="AUTOCOMMIT")

if settings.marzban.sqlalchemy_url:
    engine_mrzbn = create_engine(settings.marzban.sqlalchemy_url.get_secret_value())
else:
    engine_mrzbn = None
