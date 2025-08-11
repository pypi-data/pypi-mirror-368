import logging
import multiprocessing
from typing import Any, Dict, cast

from fastmcp import FastMCP

from ..providers import (
    LangfuseProvider,
    LangfuseProviderFactory,
    LangSmithProvider,
    LangSmithProviderFactory,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TraceNexusServer:
    def __init__(self) -> None:
        # Create two FastMCP instances - one for each transport
        self.mcp_http: FastMCP = FastMCP("TraceNexus-HTTP")
        self.mcp_sse: FastMCP = FastMCP("TraceNexus-SSE")

        # Instantiate LangSmith providers (multiple instances)
        self.langsmith_providers: Dict[str, LangSmithProvider] = {}
        for name, provider in LangSmithProviderFactory.create_providers():  # type: ignore[assignment]
            self.langsmith_providers[name] = provider  # type: ignore[assignment]

        # Instantiate Langfuse providers (multiple instances)
        self.langfuse_providers: Dict[str, LangfuseProvider] = {}
        for name, provider in LangfuseProviderFactory.create_providers():  # type: ignore[assignment]
            self.langfuse_providers[name] = provider  # type: ignore[assignment]

        self.register_tools()

    def register_tools(self) -> None:
        # Register tools on both FastMCP instances
        for mcp_instance in [self.mcp_http, self.mcp_sse]:

            # Register a tool for each LangSmith instance
            for name, provider in self.langsmith_providers.items():
                # Create a closure to capture the provider
                def create_langsmith_tool(
                    provider_instance: LangSmithProvider, provider_name: str
                ) -> Any:
                    @mcp_instance.tool(
                        name=f"langsmith_{provider_name}_get_trace",
                        description=f"Get a trace from LangSmith instance '{provider_name}' by trace ID",
                    )
                    async def langsmith_get_trace(trace_id: str) -> str:
                        """
                        Get a trace from LangSmith by its ID.

                        Args:
                            trace_id: The ID of the trace to retrieve

                        Returns:
                            The trace data in YAML format
                        """
                        result = await provider_instance.get_trace(trace_id)
                        return cast(str, result)

                    return langsmith_get_trace

                create_langsmith_tool(provider, name)

            # Register a tool for each Langfuse instance
            for name, provider in self.langfuse_providers.items():  # type: ignore[assignment]
                # Create a closure to capture the provider
                def create_langfuse_tool(
                    provider_instance: LangfuseProvider, provider_name: str
                ) -> Any:
                    @mcp_instance.tool(
                        name=f"langfuse_{provider_name}_get_trace",
                        description=f"Get a trace from Langfuse instance '{provider_name}' by trace ID",
                    )
                    async def langfuse_get_trace(trace_id: str) -> str:
                        """
                        Get a trace from Langfuse by its ID.

                        Args:
                            trace_id: The ID of the trace to retrieve

                        Returns:
                            The trace data in YAML format
                        """
                        result = await provider_instance.get_trace(trace_id)
                        return cast(str, result)

                    return langfuse_get_trace

                create_langfuse_tool(provider, name)  # type: ignore[arg-type]

        # Add other provider tools here as they are developed  # e.g., datadog_get_trace, newrelic_get_trace

    def run(
        self,
        http_port: int = 52734,
        sse_port: int = 52735,
        mount_path: str = "/mcp",
        host: str = "127.0.0.1",
    ):
        logger.info("Starting TraceNexus with DUAL transport support:")
        logger.info(
            f"  📡 Streamable-HTTP (Cursor): http://{host}:{http_port}{mount_path}"
        )
        logger.info(f"  🌊 SSE (Windsurf): http://{host}:{sse_port}/sse")

        # Start both transports in separate processes
        def run_http_server():
            # Create a new server instance in this process for HTTP
            server = TraceNexusServer()
            logger.info(f"Starting HTTP transport on port {http_port}")
            server.mcp_http.run(
                transport="streamable-http",
                port=http_port,
                path=mount_path,
            )

        # Start HTTP server in a separate process
        http_process = multiprocessing.Process(target=run_http_server, daemon=True)
        http_process.start()

        # Start SSE server in main thread (so Ctrl+C works properly)
        # This uses the existing server instance created by CLI
        try:
            logger.info(f"Starting SSE transport on port {sse_port}")
            self.mcp_sse.run(
                transport="sse",
                host=host,
                port=sse_port,
                path="/sse",
            )
        except KeyboardInterrupt:
            logger.info("Shutting down TraceNexus server...")
            http_process.terminate()
        except Exception as e:
            logger.error(f"Error running server: {e}")
            raise
