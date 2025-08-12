"""CLI module for QDrant Loader MCP Server."""

import asyncio
import json
import logging
import os
import signal
import sys
import time
from pathlib import Path

import click
from click.decorators import option
from click.types import Choice
from click.types import Path as ClickPath
from dotenv import load_dotenv

from .config import Config
from .mcp import MCPHandler
from .search.engine import SearchEngine
from .search.processor import QueryProcessor
from .transport import HTTPTransportHandler
from .utils import LoggingConfig, get_version

# Suppress asyncio debug messages to reduce noise in logs.
logging.getLogger("asyncio").setLevel(logging.WARNING)


def _setup_logging(log_level: str) -> None:
    """Set up logging configuration."""
    try:
        # Check if console logging is disabled via environment variable.
        disable_console_logging = (
            os.getenv("MCP_DISABLE_CONSOLE_LOGGING", "").lower() == "true"
        )

        if not disable_console_logging:
            LoggingConfig.setup(level=log_level.upper(), format="console")
        else:
            LoggingConfig.setup(level=log_level.upper(), format="json")
    except Exception as e:
        print(f"Failed to setup logging: {e}", file=sys.stderr)


async def read_stdin():
    """Read from stdin asynchronously."""
    loop = asyncio.get_running_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    return reader


async def shutdown(
    loop: asyncio.AbstractEventLoop, shutdown_event: asyncio.Event = None
):
    """Handle graceful shutdown."""
    logger = LoggingConfig.get_logger(__name__)
    logger.info("Shutting down...")

    # Determine configurable grace period for cooperative shutdown
    # Priority: MCP_GRACEFUL_SHUTDOWN_SECONDS; otherwise align with HTTP shutdown timeout + small buffer
    try:
        graceful_env = os.getenv("MCP_GRACEFUL_SHUTDOWN_SECONDS")
        if graceful_env is not None and graceful_env != "":
            graceful_seconds = float(graceful_env)
        else:
            graceful_seconds = float(os.getenv("MCP_HTTP_SHUTDOWN_TIMEOUT_SECONDS", "30.0")) + 1.0
    except Exception:
        graceful_seconds = 5.0

    # Signal other tasks to cooperatively shut down
    if shutdown_event:
        shutdown_event.set()

    # Cooperative grace period: allow servers/handlers to drain before forced cancel
    # Exit early if there are no other tasks remaining
    start_time = time.monotonic()
    try:
        while True:
            remaining = [t for t in asyncio.all_tasks() if t is not asyncio.current_task() and not t.done()]
            if not remaining:
                break
            if time.monotonic() - start_time >= graceful_seconds:
                break
            await asyncio.sleep(0.2)
    except asyncio.CancelledError:
        # If shutdown itself is cancelled, proceed to finalization
        pass

    # After the grace period, cancel any remaining tasks except the current one
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    for task in tasks:
        if not task.done():
            task.cancel()

    # Wait for all tasks to complete, suppressing CancelledError during shutdown
    if tasks:
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception) and not isinstance(result, asyncio.CancelledError):
                    logger.error(f"Error during task cleanup: {result}", exc_info=True)
        except Exception as e:
            if not isinstance(e, asyncio.CancelledError):
                logger.error("Error during shutdown", exc_info=True)

    logger.info("Shutdown sequence complete")


async def start_http_server(
    config: Config, log_level: str, host: str, port: int, shutdown_event: asyncio.Event
):
    """Start MCP server with HTTP transport."""
    logger = LoggingConfig.get_logger(__name__)
    search_engine = None

    try:
        logger.info(f"Starting HTTP server on {host}:{port}")

        # Initialize components
        search_engine = SearchEngine()
        query_processor = QueryProcessor(config.openai)
        mcp_handler = MCPHandler(search_engine, query_processor)

        # Initialize search engine
        try:
            await search_engine.initialize(config.qdrant, config.openai, config.search)
            logger.info("Search engine initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize search engine", exc_info=True)
            raise RuntimeError("Failed to initialize search engine") from e

        # Create HTTP transport handler
        http_handler = HTTPTransportHandler(mcp_handler, host=host, port=port)

        # Start the FastAPI server using uvicorn
        import uvicorn

        uvicorn_config = uvicorn.Config(
            app=http_handler.app,
            host=host,
            port=port,
            log_level=log_level.lower(),
            access_log=log_level.upper() == "DEBUG",
        )

        server = uvicorn.Server(uvicorn_config)
        logger.info(f"HTTP MCP server ready at http://{host}:{port}/mcp")

        # Create a task to monitor shutdown event
        async def shutdown_monitor():
            await shutdown_event.wait()
            logger.info("Shutdown signal received, stopping HTTP server...")

            # Signal uvicorn to stop gracefully
            server.should_exit = True

            # Graceful drain logic: wait for in-flight requests to finish before forcing exit
            # Configurable timeouts via environment variables
            drain_timeout = float(os.getenv("MCP_HTTP_DRAIN_TIMEOUT_SECONDS", "10.0"))
            max_shutdown_timeout = float(
                os.getenv("MCP_HTTP_SHUTDOWN_TIMEOUT_SECONDS", "30.0")
            )

            start_ts = time.monotonic()

            # 1) Prioritize draining non-streaming requests quickly
            drained_non_stream = False
            try:
                while time.monotonic() - start_ts < drain_timeout:
                    if not http_handler.has_inflight_non_streaming():
                        drained_non_stream = True
                        logger.info("Non-streaming requests drained; continuing shutdown")
                        break
                    await asyncio.sleep(0.1)
            except Exception:
                # On any error during drain check, fall through to timeout-based force
                pass

            if not drained_non_stream:
                logger.warning(
                    f"Non-streaming requests still in flight after {drain_timeout}s; proceeding with shutdown"
                )

            # 2) Allow additional time (up to max_shutdown_timeout total) for all requests to complete
            total_deadline = start_ts + max_shutdown_timeout
            try:
                while time.monotonic() < total_deadline:
                    counts = http_handler.get_inflight_request_counts()
                    if counts.get("total", 0) == 0:
                        logger.info("All in-flight requests drained; completing shutdown without force")
                        break
                    await asyncio.sleep(0.2)
            except Exception:
                pass

            # 3) If still not finished after the max timeout, force the server to exit
            if hasattr(server, "force_exit"):
                if time.monotonic() >= total_deadline:
                    logger.warning(
                        f"Forcing server exit after {max_shutdown_timeout}s shutdown timeout"
                    )
                    server.force_exit = True
                else:
                    logger.debug("Server drained gracefully; force_exit not required")

        # Start shutdown monitor task
        monitor_task = asyncio.create_task(shutdown_monitor())

        try:
            # Run the server until shutdown
            await server.serve()
        except asyncio.CancelledError:
            logger.info("Server shutdown initiated")
        except Exception as e:
            if not shutdown_event.is_set():
                logger.error(f"Server error: {e}", exc_info=True)
            else:
                logger.info(f"Server stopped during shutdown: {e}")
        finally:
            # Cancel the monitor task
            if not monitor_task.done():
                monitor_task.cancel()
                try:
                    await monitor_task
                except asyncio.CancelledError:
                    pass

    except Exception as e:
        if not shutdown_event.is_set():
            logger.error(f"Error in HTTP server: {e}", exc_info=True)
        raise
    finally:
        # Clean up search engine
        if search_engine:
            try:
                await search_engine.cleanup()
                logger.info("Search engine cleanup completed")
            except Exception as e:
                logger.error(f"Error during search engine cleanup: {e}", exc_info=True)


async def handle_stdio(config: Config, log_level: str):
    """Handle stdio communication with Cursor."""
    logger = LoggingConfig.get_logger(__name__)

    try:
        # Check if console logging is disabled
        disable_console_logging = (
            os.getenv("MCP_DISABLE_CONSOLE_LOGGING", "").lower() == "true"
        )

        if not disable_console_logging:
            logger.info("Setting up stdio handler...")

        # Initialize components
        search_engine = SearchEngine()
        query_processor = QueryProcessor(config.openai)
        mcp_handler = MCPHandler(search_engine, query_processor)

        # Initialize search engine
        try:
            await search_engine.initialize(config.qdrant, config.openai, config.search)
            if not disable_console_logging:
                logger.info("Search engine initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize search engine", exc_info=True)
            raise RuntimeError("Failed to initialize search engine") from e

        reader = await read_stdin()
        if not disable_console_logging:
            logger.info("Server ready to handle requests")

        while True:
            try:
                # Read a line from stdin
                if not disable_console_logging:
                    logger.debug("Waiting for input...")
                try:
                    line = await reader.readline()
                    if not line:
                        if not disable_console_logging:
                            logger.warning("No input received, breaking")
                        break
                except asyncio.CancelledError:
                    if not disable_console_logging:
                        logger.info("Read operation cancelled during shutdown")
                    break

                # Log the raw input
                raw_input = line.decode().strip()
                if not disable_console_logging:
                    logger.debug("Received raw input", raw_input=raw_input)

                # Parse the request
                try:
                    request = json.loads(raw_input)
                    if not disable_console_logging:
                        logger.debug("Parsed request", request=request)
                except json.JSONDecodeError as e:
                    if not disable_console_logging:
                        logger.error("Invalid JSON received", error=str(e))
                    # Send error response for invalid JSON
                    response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error",
                            "data": f"Invalid JSON received: {str(e)}",
                        },
                    }
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
                    continue

                # Validate request format
                if not isinstance(request, dict):
                    if not disable_console_logging:
                        logger.error("Request must be a JSON object")
                    response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32600,
                            "message": "Invalid Request",
                            "data": "Request must be a JSON object",
                        },
                    }
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
                    continue

                if "jsonrpc" not in request or request["jsonrpc"] != "2.0":
                    if not disable_console_logging:
                        logger.error("Invalid JSON-RPC version")
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {
                            "code": -32600,
                            "message": "Invalid Request",
                            "data": "Invalid JSON-RPC version",
                        },
                    }
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
                    continue

                # Process the request
                try:
                    response = await mcp_handler.handle_request(request)
                    if not disable_console_logging:
                        logger.debug("Sending response", response=response)
                    # Only write to stdout if response is not empty (not a notification)
                    if response:
                        sys.stdout.write(json.dumps(response) + "\n")
                        sys.stdout.flush()
                except Exception as e:
                    if not disable_console_logging:
                        logger.error("Error processing request", exc_info=True)
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": str(e),
                        },
                    }
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()

            except asyncio.CancelledError:
                if not disable_console_logging:
                    logger.info("Request handling cancelled during shutdown")
                break
            except Exception:
                if not disable_console_logging:
                    logger.error("Error handling request", exc_info=True)
                continue

        # Cleanup
        await search_engine.cleanup()

    except Exception:
        if not disable_console_logging:
            logger.error("Error in stdio handler", exc_info=True)
        raise


@click.command(name="mcp-qdrant-loader")
@option(
    "--log-level",
    type=Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    default="INFO",
    help="Set the logging level.",
)
@option(
    "--config",
    type=ClickPath(exists=True, path_type=Path),
    help="Path to configuration file (currently not implemented).",
)
@option(
    "--transport",
    type=Choice(["stdio", "http"], case_sensitive=False),
    default="stdio",
    help="Transport protocol to use (stdio for JSON-RPC over stdin/stdout, http for HTTP with SSE)",
)
@option(
    "--host",
    type=str,
    default="127.0.0.1",
    help="Host to bind HTTP server to (only used with --transport http)",
)
@option(
    "--port",
    type=int,
    default=8080,
    help="Port to bind HTTP server to (only used with --transport http)",
)
@option(
    "--env",
    type=ClickPath(exists=True, path_type=Path),
    help="Path to .env file to load environment variables from",
)
@click.version_option(
    version=get_version(),
    message="QDrant Loader MCP Server v%(version)s",
)
def cli(
    log_level: str = "INFO",
    config: Path | None = None,
    transport: str = "stdio",
    host: str = "127.0.0.1",
    port: int = 8080,
    env: Path | None = None,
) -> None:
    """QDrant Loader MCP Server.

    A Model Context Protocol (MCP) server that provides RAG capabilities
    to Cursor and other LLM applications using Qdrant vector database.

    The server supports both stdio (JSON-RPC) and HTTP (with SSE) transports
    for maximum compatibility with different MCP clients.

    Environment Variables:
        QDRANT_URL: URL of your QDrant instance (required)
        QDRANT_API_KEY: API key for QDrant authentication
        QDRANT_COLLECTION_NAME: Name of the collection to use (default: "documents")
        OPENAI_API_KEY: OpenAI API key for embeddings (required)
        MCP_DISABLE_CONSOLE_LOGGING: Set to "true" to disable console logging

    Examples:
        # Start with stdio transport (default, for Cursor/Claude Desktop)
        mcp-qdrant-loader

        # Start with HTTP transport (for web clients)
        mcp-qdrant-loader --transport http --port 8080

        # Start with environment variables from .env file
        mcp-qdrant-loader --transport http --env /path/to/.env

        # Start with debug logging
        mcp-qdrant-loader --log-level DEBUG --transport http

        # Show help
        mcp-qdrant-loader --help

        # Show version
        mcp-qdrant-loader --version
    """
    loop = None
    try:
        # Load environment variables from .env file if specified
        if env:
            load_dotenv(env)
            click.echo(f"Loaded environment variables from: {env}")

        # Setup logging
        _setup_logging(log_level)

        # Initialize configuration
        config_obj = Config()

        # Create and set the event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Create shutdown event for coordinating graceful shutdown
        shutdown_event = asyncio.Event()

        # Set up signal handlers with shutdown event
        def signal_handler():
            # Schedule shutdown on the explicit loop for clarity and correctness
            loop.create_task(shutdown(loop, shutdown_event))

        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, signal_handler)

        # Start the appropriate transport handler
        if transport.lower() == "stdio":
            loop.run_until_complete(handle_stdio(config_obj, log_level))
        elif transport.lower() == "http":
            loop.run_until_complete(
                start_http_server(config_obj, log_level, host, port, shutdown_event)
            )
        else:
            raise ValueError(f"Unsupported transport: {transport}")
    except Exception:
        logger = LoggingConfig.get_logger(__name__)
        logger.error("Error in main", exc_info=True)
        sys.exit(1)
    finally:
        if loop:
            try:
                # Cancel all remaining tasks within the loop context without resetting event loop again
                async def _cancel_and_gather_pending():
                    pending_tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
                    for t in pending_tasks:
                        t.cancel()
                    if pending_tasks:
                        await asyncio.gather(*pending_tasks, return_exceptions=True)

                loop.run_until_complete(_cancel_and_gather_pending())
            except Exception:
                logger = LoggingConfig.get_logger(__name__)
                logger.error("Error during final cleanup", exc_info=True)
            finally:
                loop.close()
                logger = LoggingConfig.get_logger(__name__)
                logger.info("Server shutdown complete")


if __name__ == "__main__":
    cli()
