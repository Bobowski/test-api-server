from typing import Annotated, AsyncGenerator, Generator, Self
from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    db_uri: str = "sqlite+aiosqlite:///database.db"

    @property
    def sync_database_uri(self) -> str:
        """Convert async SQLite URI to sync SQLite URI."""
        if not self.db_uri:
            raise ValueError("Database URI cannot be empty")

        if self.db_uri.startswith("sqlite+aiosqlite://"):
            return self.db_uri.replace("sqlite+aiosqlite://", "sqlite://")
        elif self.db_uri.startswith("sqlite://"):
            return self.db_uri
        else:
            raise ValueError(f"Unsupported database URI format: {self.db_uri}")

    @property
    def async_database_uri(self) -> str:
        """Convert sync SQLite URI to async SQLite URI."""
        if not self.db_uri:
            raise ValueError("Database URI cannot be empty")

        if self.db_uri.startswith("sqlite://"):
            return self.db_uri.replace("sqlite://", "sqlite+aiosqlite://")
        elif self.db_uri.startswith("sqlite+aiosqlite://"):
            return self.db_uri
        else:
            raise ValueError(f"Unsupported database URI format: {self.db_uri}")

    @classmethod
    def from_env(cls) -> Self:
        return cls()


def get_sync_sessionmaker(
    settings: Annotated[DatabaseSettings, Depends(DatabaseSettings.from_env)],
) -> sessionmaker[Session]:
    """
    Get a new database sync sessionmaker.
    """

    engine = create_engine(
        settings.sync_database_uri,
        echo=False,
        future=True,
    )
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=Session,
        expire_on_commit=False,
    )


def get_sync_session(
    sessionmaker: Annotated[sessionmaker[Session], Depends(get_sync_sessionmaker)],
) -> Generator[Session, None, None]:
    """
    Get a new database sync session.
    """

    with sessionmaker() as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


def get_sessionmaker(
    settings: Annotated[DatabaseSettings, Depends(DatabaseSettings.from_env)],
) -> async_sessionmaker[AsyncSession]:
    """
    Get a new database async sessionmaker.
    """

    print(f"Creating async engine with {settings.async_database_uri}")
    engine = create_async_engine(
        settings.async_database_uri,
        echo=False,  # Disable SQL query logging (for performance)
        future=True,  # Use the future-facing SQLAlchemy 2.0 style
    )

    sessionmaker = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    return sessionmaker


async def get_session(
    sessionmaker: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_sessionmaker)
    ],
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get a new database async session.
    """
    async with sessionmaker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


GetSessionmaker = Annotated[async_sessionmaker[AsyncSession], Depends(get_sessionmaker)]
GetSession = Annotated[AsyncSession, Depends(get_session)]
GetSyncSession = Annotated[Session, Depends(get_sync_session)]