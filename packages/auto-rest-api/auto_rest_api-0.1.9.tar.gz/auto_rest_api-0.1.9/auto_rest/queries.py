"""
The `queries` module provides asynchronous wrapper functions around operations
involving SQLAlchemy sessions. These utilities automatically account for
variations in behavior between synchronous and asynchronous session types
(i.e., `Session` and `AsyncSession` instances). This ensures consistent query
handling and provides a streamlined interface for database interactions.

!!! example "Example: Query Execution"

    Query utilities seamlessly support synchronous and asynchronous session types.

    ```python
    query = select(SomeTable).where(SomeTable.id == item_id)

    with Session(...) as sync_session:
        result = await execute_session_query(sync_session, query)

    with AsyncSession(...) as async_session:
        result = await execute_session_query(async_session, query)
    ```
"""

import logging

from fastapi import HTTPException
from sqlalchemy import Executable, Result
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auto_rest.models import DBSession

__all__ = [
    "commit_session",
    "delete_session_record",
    "execute_session_query",
    "get_record_or_404"
]

logger = logging.getLogger("auto_rest.query")


async def commit_session(session: DBSession) -> None:
    """Commit a SQLAlchemy session.

    Supports synchronous and asynchronous sessions.

    Args:
        session: The session to commit.
    """

    if isinstance(session, AsyncSession):
        await session.commit()

    else:
        session.commit()


async def delete_session_record(session: DBSession, record: Result) -> None:
    """Delete a record from the database using an existing session.

    Does not automatically commit the session.
    Supports synchronous and asynchronous sessions.

    Args:
        session: The session to use for deletion.
        record: The record to be deleted.
    """

    logger.debug("Deleting record.")
    if isinstance(session, AsyncSession):
        await session.delete(record)

    else:
        session.delete(record)


async def execute_session_query(session: DBSession, query: Executable) -> Result:
    """Execute a query in the given session and return the result.

    Supports synchronous and asynchronous sessions.

    Args:
        session: The SQLAlchemy session to use for executing the query.
        query: The query to be executed.

    Returns:
        The result of the executed query.
    """

    logger.debug(str(query).replace("\n", " "))
    if isinstance(session, AsyncSession):
        return await session.execute(query)

    return session.execute(query)


def get_record_or_404(result: Result) -> any:
    """Retrieve a scalar record from a query result or raise a 404 error.

    Args:
        result: The query result to extract the scalar record from.

    Returns:
        The scalar record if it exists.

    Raises:
        HTTPException: If the record is not found.
    """

    if record := result.fetchone():
        return record

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
