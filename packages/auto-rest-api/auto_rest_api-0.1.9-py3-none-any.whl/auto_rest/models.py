"""
The `models` module facilitates communication with relational databases
via dynamically generated object relational mappers (ORMs). Building
on the popular SQLAlchemy package, it natively supports multiple
Database Management Systems (DBMS) without requiring custom configuration
or setup.

!!! example "Example: Mapping Database Metadata"

    Utility functions are provided for connecting to the database
    and mapping the underlying schema.

    ```python
    connection_args = dict(...)
    db_url = create_db_url(**connection_args)
    db_conn = create_db_engine(db_url)
    db_meta = create_db_metadata(db_conn)
    ```

Support for asynchronous operations is automatically determined based on
the chosen database. If the driver supports asynchronous operations, the
connection and session handling are configured accordingly.

!!! important "Developer Note"

    When working with database objects, the returned object type may vary
    depending on whether the underlying driver is synchronous or asynchronous.
    Of particular note are database engines (`Engine` / `AsyncEngine`) and
    sessions (`Session` / `AsyncSession`).
"""

import asyncio
import logging
from pathlib import Path
from typing import AsyncGenerator, Callable, Generator

import yaml
from sqlalchemy import create_engine, Engine, MetaData, URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import Session

__all__ = [
    "DBEngine",
    "DBSession",
    "create_db_engine",
    "create_db_metadata",
    "create_db_url",
    "create_session_iterator",
    "parse_db_settings"
]

logger = logging.getLogger("auto_rest")

# Base classes and typing objects.
DBEngine = Engine | AsyncEngine
DBSession = Session | AsyncSession


def parse_db_settings(path: Path | None) -> dict[str, any]:
    """Parse engine configuration settings from a given file path.

    Args:
        path: Path to the configuration file.

    Returns:
        Engine configuration settings.
    """

    if path is not None:
        logger.debug(f"Parsing engine configuration from {path}.")
        return yaml.safe_load(path.read_text()) or dict()

    logger.debug("No configuration file specified.")
    return {}


def create_db_url(
    driver: str,
    database: str,
    host: str | None = None,
    port: int | None = None,
    username: str | None = None,
    password: str | None = None,
) -> URL:
    """Create a database URL from the provided parameters.

    Args:
        driver: The SQLAlchemy-compatible database driver.
        database: The database name or file path (for SQLite).
        host: The database server hostname or IP address.
        port: The database server port number.
        username: The username for authentication.
        password: The password for the database user.

    Returns:
        A fully qualified database URL.
    """

    # Handle special case where SQLite uses file paths.
    if "sqlite" in driver:
        path = Path(database).resolve()
        url = URL.create(drivername=driver, database=str(path))

    else:
        url = URL.create(
            drivername=driver,
            username=username,
            password=password,
            host=host,
            port=port,
            database=database,
        )

    logger.debug(f"Resolved URL: {url}")
    return url


def create_db_engine(url: URL, **kwargs: dict[str: any]) -> DBEngine:
    """Initialize a new database engine.

    Instantiates and returns an `Engine` or `AsyncEngine` instance depending
    on whether the database URL uses a driver with support for async operations.

    Args:
        url: A fully qualified database URL.
        **kwargs: Keyword arguments passed to `create_engine`.

    Returns:
        A SQLAlchemy `Engine` or `AsyncEngine` instance.
    """

    if url.get_dialect().is_async:
        engine = create_async_engine(url, **kwargs)
        logger.debug("Asynchronous connection established.")
        return engine

    else:
        engine = create_engine(url, **kwargs)
        logger.debug("Synchronous connection established.")
        return engine


async def _async_reflect_metadata(engine: AsyncEngine, metadata: MetaData) -> None:
    """Helper function used to reflect database metadata using an async engine."""

    async with engine.connect() as connection:
        await connection.run_sync(metadata.reflect, views=True)


def create_db_metadata(engine: DBEngine) -> MetaData:
    """Create and reflect metadata for the database connection.

    Args:
        engine: The database engine to use for reflection.

    Returns:
        A MetaData object reflecting the database schema.
    """

    logger.debug("Loading database metadata.")
    metadata = MetaData()

    if isinstance(engine, AsyncEngine):
        asyncio.run(_async_reflect_metadata(engine, metadata))

    else:
        metadata.reflect(bind=engine, views=True)

    return metadata


def create_session_iterator(engine: DBEngine) -> Callable[[], Generator[Session, None, None] | AsyncGenerator[AsyncSession, None]]:
    """Create a generator for database sessions.

    Returns a synchronous or asynchronous function depending on whether
    the database engine supports async operations. The type of session
    returned also depends on the underlying database engine, and will
    either be a `Session` or `AsyncSession` instance.

    Args:
        engine: Database engine to use when generating new sessions.

    Returns:
        A function that yields a single new database session.
    """

    if isinstance(engine, AsyncEngine):
        async def session_iterator() -> AsyncGenerator[AsyncSession, None]:
            async with AsyncSession(bind=engine, autocommit=False, autoflush=True) as session:
                yield session

    else:
        def session_iterator() -> Generator[Session, None, None]:
            with Session(bind=engine, autocommit=False, autoflush=True) as session:
                yield session

    return session_iterator
