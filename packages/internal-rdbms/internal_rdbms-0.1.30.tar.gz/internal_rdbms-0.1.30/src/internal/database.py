import contextlib
from typing import AsyncIterator

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncConnection
from sqlalchemy.orm import sessionmaker

from .exception.internal_exception import DatabaseInitializeFailureException, DatabaseConnectFailureException


class MariaDB:

    def __init__(self, user_name: str, password: str, host: str, port: int, db_name: str):
        self._connection_url = URL.create("mysql+aiomysql",
                                          username=user_name,
                                          password=password,
                                          host=host,
                                          port=port,
                                          database=db_name)
        self._engine = create_async_engine(self._connection_url, echo=True, future=True, pool_pre_ping=True)
        self._session_local = sessionmaker(class_=AsyncSession, autocommit=False, autoflush=False, bind=self._engine,
                                           expire_on_commit=False)

    async def close(self):
        if self._engine:
            await self._engine.dispose()

            self._engine = None
            self._session_local = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise DatabaseInitializeFailureException()

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise DatabaseConnectFailureException()

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._session_local is None:
            raise DatabaseConnectFailureException()

        session = self._session_local()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
