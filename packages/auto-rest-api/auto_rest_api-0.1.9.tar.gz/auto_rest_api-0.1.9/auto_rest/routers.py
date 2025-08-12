"""
API routers are responsible for redirecting incoming HTTP requests to the
appropriate handling logic. Router objects are created using a factory
pattern, with each router being responsible for a single application
resource. Each factory returns an `APIRouter` instance preconfigured
with request handling logic for the relevant resource. This allows
routers to be added directly to an API application instance.

!!! example "Example: Creating and Adding a Router"

    Care should be taken to avoid path conflicts when adding routers
    to an API application instance. Using a unique `prefix` value
    ensures that each router's endpoints are properly namespaced and
    unique.

    ```python
    from fastapi import FastAPI
    from auto_rest.routers import create_welcome_router

    app = FastAPI()
    welcome_router = create_welcome_router()
    app.include_router(welcome_router, prefix="/welcome")
    ```
"""

import logging

from fastapi import APIRouter
from sqlalchemy import MetaData, Table
from starlette import status

from auto_rest.handlers import *
from auto_rest.models import DBEngine

__all__ = [
    "create_meta_router",
    "create_table_router",
    "create_welcome_router",
]

logger = logging.getLogger("auto_rest")


def create_welcome_router() -> APIRouter:
    """Create an API router for returning a welcome message.

    Returns:
        An `APIRouter` with a single route for retrieving a welcome message.
    """

    logger.debug("Creating welcome endpoint.")

    router = APIRouter()
    router.add_api_route(
        path="/",
        methods=["GET"],
        endpoint=create_welcome_handler(),
        include_in_schema=False
    )

    return router


def create_meta_router(engine: DBEngine, metadata: MetaData, name: str, version: str) -> APIRouter:
    """Create an API router for returning database metadata.

    Includes routes for retrieving the database driver, database schema,
    and application/schema version.

    Args:
        engine: The database engine used to facilitate database interactions.
        metadata: The metadata object containing the database schema.
        name: The application name.
        version: The application versionnumber.

    Returns:
        An `APIRouter` with a routes for retrieving application metadata.
    """

    logger.debug("Creating metadata endpoints.")

    router = APIRouter()
    tags = ["Application Metadata"]

    router.add_api_route(
        path="/app/",
        methods=["GET"],
        endpoint=create_about_handler(name, version),
        summary="Fetch application metadata.",
        tags=tags
    )

    router.add_api_route(
        path="/engine/",
        methods=["GET"],
        endpoint=create_engine_handler(engine),
        summary="Fetch database metadata.",
        tags=tags
    )

    router.add_api_route(
        path="/schema/",
        methods=["GET"],
        endpoint=create_schema_handler(metadata),
        summary="Fetch the database schema.",
        tags=tags
    )

    return router


def create_table_router(engine: DBEngine, table: Table) -> APIRouter:
    """Create an API router with endpoint handlers for a given database table.

    Args:
        engine: The SQLAlchemy engine connected to the database.
        table: The database table to create API endpoints for.

    Returns:
        An APIRouter instance with routes for database operations on the table.
    """

    logger.debug(f"Creating endpoints for table `{table.name}`.")
    router = APIRouter()

    # Construct path parameters from primary key columns
    pk_columns = sorted(column.name for column in table.primary_key.columns)
    path_params_url = "/".join(f"{{{col_name}}}" for col_name in pk_columns)

    # Add routes for operations against the table
    router.add_api_route(
        path="/",
        methods=["GET"],
        endpoint=create_list_records_handler(engine, table),
        status_code=status.HTTP_200_OK,
        summary="Fetch multiple records from the table.",
        tags=[table.name],
    )

    router.add_api_route(
        path="/",
        methods=["POST"],
        endpoint=create_post_record_handler(engine, table),
        status_code=status.HTTP_201_CREATED,
        summary="Create a new record.",
        tags=[table.name],
    )

    # Add route for read operations against individual records
    if pk_columns:
        router.add_api_route(
            path=f"/{path_params_url}/",
            methods=["GET"],
            endpoint=create_get_record_handler(engine, table),
            status_code=status.HTTP_200_OK,
            summary="Fetch a single record from the table.",
            tags=[table.name],
        )

        router.add_api_route(
            path=f"/{path_params_url}/",
            methods=["PUT"],
            endpoint=create_put_record_handler(engine, table),
            status_code=status.HTTP_200_OK,
            summary="Replace a single record in the table.",
            tags=[table.name],
        )

        router.add_api_route(
            path=f"/{path_params_url}/",
            methods=["PATCH"],
            endpoint=create_patch_record_handler(engine, table),
            status_code=status.HTTP_200_OK,
            summary="Update a single record in the table.",
            tags=[table.name],
        )

        router.add_api_route(
            path=f"/{path_params_url}/",
            methods=["DELETE"],
            endpoint=create_delete_record_handler(engine, table),
            status_code=status.HTTP_200_OK,
            summary="Delete a single record from the table.",
            tags=[table.name],
        )

    return router
