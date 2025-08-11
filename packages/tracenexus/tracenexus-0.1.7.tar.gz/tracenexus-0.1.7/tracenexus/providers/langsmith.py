import asyncio
import logging
import os
from typing import Any, List, Tuple

import yaml
from langsmith import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LangSmithProvider:
    def __init__(self, api_key: str, name: str = "default"):
        self.name = name
        logger.info(
            f"Initializing LangSmith provider '{name}' with API key: {api_key[:5]}xxxxx"
        )
        self.client = Client(api_key=api_key)

    async def get_trace(self, trace_id: str) -> str:
        logger.info(f"Getting trace {trace_id} from LangSmith ({self.name})")
        try:
            run = await asyncio.to_thread(self.client.read_run, trace_id)
            return self.normalize_trace(run)
        except Exception as e:
            # Check if it's a 404 Not Found error
            error_msg = str(e).lower()
            if "404" in error_msg or "not found" in error_msg:
                logger.warning(
                    f"Trace {trace_id} not found in LangSmith instance '{self.name}'"
                )
                return f"Trace not found in {self.name}: {trace_id}"
            else:
                # For other errors, log them but still return a user-friendly message
                logger.error(
                    f"Error fetching trace from LangSmith ({self.name}): {str(e)}"
                )
                return f"Error fetching trace from {self.name}: {str(e)}"

    def normalize_trace(self, run: Any) -> str:
        trace_as_dict = run.dict()
        return yaml.dump(
            trace_as_dict, sort_keys=False, indent=2, default_flow_style=False
        )


class LangSmithProviderFactory:
    @staticmethod
    def create_providers() -> List[Tuple[str, LangSmithProvider]]:
        """Create LangSmith providers from environment variables.

        Returns:
            List of tuples (name, provider) for each configured instance
        """
        providers: List[Tuple[str, LangSmithProvider]] = []

        # Get comma-separated keys and names
        api_keys_str = os.environ.get("LANGSMITH_API_KEYS", "")
        names_str = os.environ.get("LANGSMITH_NAMES", "")

        if not api_keys_str or api_keys_str == "example":
            logger.warning("No LangSmith API keys configured")
            return providers

        # Parse comma-separated values
        api_keys = [key.strip() for key in api_keys_str.split(",") if key.strip()]
        names = [name.strip() for name in names_str.split(",") if name.strip()]

        # If names not provided or mismatch, auto-generate names
        if len(names) != len(api_keys):
            logger.warning(
                f"Names count ({len(names)}) doesn't match API keys count ({len(api_keys)}). Using auto-generated names."
            )
            names = [f"instance{i+1}" for i in range(len(api_keys))]

        # Create providers
        for api_key, name in zip(api_keys, names):
            if api_key and api_key != "example":
                provider = LangSmithProvider(api_key, name)
                providers.append((name, provider))
                logger.info(f"Created LangSmith provider: {name}")

        return providers
