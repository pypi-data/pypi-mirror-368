"""Pydantic models are used to facilitate data validation and to define
interfaces for FastAPI endpoint handlers. The `interfaces` module
provides utility functions for converting SQLAlchemy models into
Pydantic interfaces. Interfaces can be created using different modes
which force interface fields to be optional or read only.

!!! example "Example: Creating an Interface"

    The `create_interface_default` method creates an interface class
    based on a SQLAlchemy table.

    ```python
    default_interface = create_interface(database_model)
    required_interface = create_interface(database_model, mode="required")
    optional_interface = create_interface(database_model, mode="optional")
    ```
"""

from typing import Any, Iterator, Literal

from pydantic import BaseModel as PydanticModel, create_model
from sqlalchemy import Column, Table

__all__ = ["create_interface"]

MODE_TYPE = Literal["default", "required", "optional"]


def iter_columns(table: Table, pk_only: bool = False) -> Iterator[Column]:
    """Iterate over the columns of a SQLAlchemy model.

    Args:
        table: The table to iterate columns over.
        pk_only: If True, only iterate over primary key columns.

    Yields:
        A column of the SQLAlchemy model.
    """

    for column in table.columns.values():
        if column.primary_key or not pk_only:
            yield column


def create_field_definition(col: Column, mode: MODE_TYPE = "default") -> tuple[type[any], any]:
    """Return a tuple with the type and default value for a database table column.

    The returned tuple is compatible for use with Pydantic as a field definition
    during dynamic model generation. The `mode` argument modifies returned
    values to enforce different behavior in the generated Pydantic interface.

    Modes:
        default: Values are marked as (not)required based on the column schema.
        required: Values are always marked required.
        optional: Values are always marked optional.

    Args:
        col: The column to return values for.
        mode: The mode to use when determining the default value.

    Returns:
        The default value for the column.
    """

    try:
        col_type = col.type.python_type

    except NotImplementedError:
        col_type = Any

    col_default = getattr(col.default, "arg", col.default)

    if mode == "required":
        return col_type, ...

    elif mode == "optional":
        return col_type | None, col_default

    elif mode == "default" and (col.nullable or col.default):
        return col_type | None, col_default

    elif mode == "default":
        return col_type, ...

    raise RuntimeError(f"Unknown mode: {mode}")


def create_interface(table: Table, pk_only: bool = False, mode: MODE_TYPE = "default") -> type[PydanticModel]:
    """Create a Pydantic interface for a SQLAlchemy model where all fields are required.

    Modes:
        default: Values are marked as (not)required based on the column schema.
        required: Values are always marked required.
        optional: Values are always marked optional.

    Args:
        table: The SQLAlchemy table to create an interface for.
        pk_only: If True, only include primary key columns.
        mode: Whether to force fields to all be optional or required.

    Returns:
        A dynamically generated Pydantic model with all fields required.
    """

    # Map field names to the column type and default value.
    fields = {
        col.name: create_field_definition(col, mode) for col in iter_columns(table, pk_only)
    }

    # Create a unique name for the interface
    name = f"{table.name}-{mode.title()}"
    if pk_only:
        name += '-PK'

    return create_model(name, __config__={'arbitrary_types_allowed': True}, **fields)
