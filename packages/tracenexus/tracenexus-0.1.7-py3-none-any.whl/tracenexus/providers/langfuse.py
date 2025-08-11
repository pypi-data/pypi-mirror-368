import asyncio
import logging
import os
from typing import Any, List, Tuple

import yaml
from langfuse import Langfuse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LangfuseProvider:
    def __init__(
        self, public_key: str, secret_key: str, host: str, name: str = "default"
    ):
        self.name = name
        logger.info(f"Initializing Langfuse provider '{name}' with host: {host}")
        logger.info(
            f"Public key: {public_key[:5]}-xxxxx, Secret key: {secret_key[:5]}-xxxxx"
        )
        self.client = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host,
        )

    async def get_trace(self, trace_id: str) -> str:
        logger.info(f"Getting trace {trace_id} from Langfuse ({self.name})")
        try:
            fetch_response = await asyncio.to_thread(self.client.fetch_trace, trace_id)
            return self.normalize_trace(fetch_response.data)
        except Exception as e:
            # Check if it's a not found error
            error_msg = str(e).lower()
            if (
                "404" in error_msg
                or "not found" in error_msg
                or "trace not found" in error_msg
            ):
                logger.warning(
                    f"Trace {trace_id} not found in Langfuse instance '{self.name}'"
                )
                return f"Trace not found in {self.name}: {trace_id}"
            else:
                # For other errors, log them but still return a user-friendly message
                logger.error(
                    f"Error fetching trace from Langfuse ({self.name}): {str(e)}"
                )
                return f"Error fetching trace from {self.name}: {str(e)}"

    def normalize_trace(self, trace_data: Any) -> str:
        trace_as_dict = trace_data.dict()
        return yaml.dump(
            trace_as_dict,
            sort_keys=False,
            indent=2,
            default_flow_style=False,
            allow_unicode=True,
        )


class LangfuseProviderFactory:
    @staticmethod
    def create_providers() -> List[Tuple[str, LangfuseProvider]]:
        """Create Langfuse providers from environment variables.

        Returns:
            List of tuples (name, provider) for each configured instance
        """
        providers: List[Tuple[str, LangfuseProvider]] = []

        # Get comma-separated configuration values
        public_keys_str = os.environ.get("LANGFUSE_PUBLIC_KEYS", "")
        secret_keys_str = os.environ.get("LANGFUSE_SECRET_KEYS", "")
        hosts_str = os.environ.get("LANGFUSE_HOSTS", "")
        names_str = os.environ.get("LANGFUSE_NAMES", "")

        if not public_keys_str or public_keys_str == "example":
            logger.warning("No Langfuse public keys configured")
            return providers

        # Parse comma-separated values
        public_keys = [key.strip() for key in public_keys_str.split(",") if key.strip()]
        secret_keys = [key.strip() for key in secret_keys_str.split(",") if key.strip()]
        hosts = [host.strip() for host in hosts_str.split(",") if host.strip()]
        names = [name.strip() for name in names_str.split(",") if name.strip()]

        # Validate configuration counts
        if len(public_keys) != len(secret_keys):
            logger.error(
                f"Langfuse public keys count ({len(public_keys)}) doesn't match secret keys count ({len(secret_keys)})"
            )
            return providers

        if len(public_keys) != len(hosts):
            logger.error(
                f"Langfuse keys count ({len(public_keys)}) doesn't match hosts count ({len(hosts)})"
            )
            return providers

        # If names not provided or mismatch, auto-generate names
        if len(names) != len(public_keys):
            logger.warning(
                f"Langfuse names count ({len(names)}) doesn't match keys count ({len(public_keys)}). Using auto-generated names."
            )
            names = [f"instance{i+1}" for i in range(len(public_keys))]

        # Create providers
        for public_key, secret_key, host, name in zip(
            public_keys, secret_keys, hosts, names
        ):
            if (
                public_key
                and public_key != "example"
                and secret_key
                and secret_key != "example"
            ):
                provider = LangfuseProvider(public_key, secret_key, host, name)
                providers.append((name, provider))
                logger.info(f"Created Langfuse provider: {name}")

        return providers
