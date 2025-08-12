"""Application entrypoint triggered by calling the packaged CLI command."""

import logging

from .app import *
from .cli import *
from .models import *
from .routers import *

__all__ = ["main", "run_application"]

logger = logging.getLogger("auto_rest")


def main() -> None:  # pragma: no cover
    """Application entry point called when executing the command line interface.

    This is a wrapper around the `run_application` function used to provide
    graceful error handling.
    """

    try:
        run_application()

    except KeyboardInterrupt:
        pass

    except Exception as e:
        logger.critical(str(e), exc_info=True)


def run_application(cli_args: list[str] = None, /) -> None:  # pragma: no cover
    """Run an Auto-REST API server.

    This function is equivalent to launching an API server from the command line
    and accepts the same arguments as those provided in the CLI. Arguments are
    parsed from STDIN by default, unless specified in the function call.

    Args:
        A list of commandline arguments used to run the application.
    """

    # Parse application arguments
    args = create_cli_parser().parse_args(cli_args)
    configure_cli_logging(args.log_level)

    logger.info(f"Resolving database connection settings.")
    db_kwargs = parse_db_settings(args.db_config)
    db_url = create_db_url(
        driver=args.db_driver,
        host=args.db_host,
        port=args.db_port,
        database=args.db_name,
        username=args.db_user,
        password=args.db_pass
    )

    logger.info("Mapping database schema.")
    db_conn = create_db_engine(db_url, **db_kwargs)
    db_meta = create_db_metadata(db_conn)

    logger.info("Creating application.")
    app = create_app(args.app_title, args.app_version)
    app.include_router(create_welcome_router(), prefix="")
    app.include_router(create_meta_router(db_conn, db_meta, args.app_title, args.app_version), prefix="/meta")
    for table_name, table in db_meta.tables.items():
        app.include_router(create_table_router(db_conn, table), prefix=f"/db/{table_name}")

    logger.info(f"Launching server on http://{args.server_host}:{args.server_port}.")
    run_server(app, args.server_host, args.server_port)
