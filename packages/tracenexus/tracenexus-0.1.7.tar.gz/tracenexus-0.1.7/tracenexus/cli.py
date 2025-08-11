import argparse
import logging
import os

from dotenv import find_dotenv, load_dotenv

from .server.mcp_server import TraceNexusServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(find_dotenv())


def main():
    parser = argparse.ArgumentParser(
        description="TraceNexus: MCP server for LLM tracing platforms (runs BOTH transports)"
    )
    parser.add_argument(
        "--http-port",
        type=int,
        default=52734,
        help="Port for streamable-http transport (Cursor)",
    )
    parser.add_argument(
        "--sse-port",
        type=int,
        default=52735,
        help="Port for SSE transport (Windsurf)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address to bind to",
    )
    parser.add_argument(
        "--mount-path",
        type=str,
        default="/mcp",
        help="Path to mount the MCP endpoints (streamable-http)",
    )
    args = parser.parse_args()

    # Check for LangSmith configuration
    langsmith_keys = os.environ.get("LANGSMITH_API_KEYS", "example").lower()
    langsmith_names = os.environ.get("LANGSMITH_NAMES", "")

    if langsmith_keys == "example" or not langsmith_keys:
        logger.warning(
            "WARNING: LANGSMITH_API_KEYS is not configured. Please set comma-separated API keys."
        )
    else:
        keys_count = len([k for k in langsmith_keys.split(",") if k.strip()])
        names_count = (
            len([n for n in langsmith_names.split(",") if n.strip()])
            if langsmith_names
            else 0
        )
        if names_count > 0 and names_count != keys_count:
            logger.warning(
                f"WARNING: LANGSMITH_NAMES count ({names_count}) doesn't match LANGSMITH_API_KEYS count ({keys_count})"
            )

    # Check for Langfuse configuration
    langfuse_public_keys = os.environ.get("LANGFUSE_PUBLIC_KEYS", "example").lower()
    langfuse_secret_keys = os.environ.get("LANGFUSE_SECRET_KEYS", "example").lower()
    langfuse_hosts = os.environ.get("LANGFUSE_HOSTS", "example").lower()
    langfuse_names = os.environ.get("LANGFUSE_NAMES", "")

    if langfuse_public_keys == "example" or not langfuse_public_keys:
        logger.warning(
            "WARNING: LANGFUSE_PUBLIC_KEYS is not configured. Please set comma-separated public keys."
        )
    else:
        pub_keys_count = len([k for k in langfuse_public_keys.split(",") if k.strip()])
        secret_keys_count = len(
            [k for k in langfuse_secret_keys.split(",") if k.strip()]
        )
        hosts_count = len([h for h in langfuse_hosts.split(",") if h.strip()])
        names_count = (
            len([n for n in langfuse_names.split(",") if n.strip()])
            if langfuse_names
            else 0
        )

        if pub_keys_count != secret_keys_count:
            logger.warning(
                f"WARNING: LANGFUSE_PUBLIC_KEYS count ({pub_keys_count}) doesn't match LANGFUSE_SECRET_KEYS count ({secret_keys_count})"
            )
        if pub_keys_count != hosts_count:
            logger.warning(
                f"WARNING: LANGFUSE keys count ({pub_keys_count}) doesn't match LANGFUSE_HOSTS count ({hosts_count})"
            )
        if names_count > 0 and names_count != pub_keys_count:
            logger.warning(
                f"WARNING: LANGFUSE_NAMES count ({names_count}) doesn't match keys count ({pub_keys_count})"
            )
    server = TraceNexusServer()
    server.run(
        http_port=args.http_port,
        sse_port=args.sse_port,
        mount_path=args.mount_path,
        host=args.host,
    )


if __name__ == "__main__":
    main()
