"""Main entry point for the Document Search MCP Server."""

import asyncio
import logging
import sys
from pathlib import Path

import click

from .server.mcp_server import DocumentSearchServer


def setup_logging(level: str = "INFO") -> None:
    """Set up logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr)  # Use stderr to avoid interfering with MCP stdio
        ],
    )


@click.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    default="config/config.yaml",
    help="Path to configuration file",
)
@click.option(
    "--log-level",
    "-l",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default="INFO",
    help="Logging level",
)
def main(config: Path, log_level: str) -> None:
    """Run the Document Search MCP Server.

    Args:
        config: Path to configuration file
        log_level: Logging level
    """
    setup_logging(log_level)

    logger = logging.getLogger(__name__)
    logger.info("Starting Document Search MCP Server")

    try:
        # Create and run the server
        server = DocumentSearchServer(config_path=config)
        asyncio.run(server.run())

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server failed: {e}")
        logger.exception("Full exception details:")
        sys.exit(1)


if __name__ == "__main__":
    main()
