from contextlib import contextmanager
from contextvars import ContextVar
from typing import Iterator, Optional

from lighthouse._client.client import lighthouse
from lighthouse._client.resource_manager import lighthouseResourceManager
from lighthouse.logger import lighthouse_logger

# Context variable to track the current lighthouse_public_key in execution context
_current_public_key: ContextVar[Optional[str]] = ContextVar(
    "lighthouse_public_key", default=None
)


@contextmanager
def _set_current_public_key(public_key: Optional[str]) -> Iterator[None]:
    """Context manager to set and restore the current public key in execution context.

    Args:
        public_key: The public key to set in context. If None, context is not modified.

    Yields:
        None
    """
    if public_key is None:
        yield  # Don't modify context if no key provided
        return

    token = _current_public_key.set(public_key)
    try:
        yield
    finally:
        _current_public_key.reset(token)


def get_client(*, public_key: Optional[str] = None) -> lighthouse:
    """Get or create a lighthouse client instance.

    Returns an existing lighthouse client or creates a new one if none exists. In multi-project setups,
    providing a public_key is required. Multi-project support is experimental - see lighthouse docs.

    Behavior:
    - Single project: Returns existing client or creates new one
    - Multi-project: Requires public_key to return specific client
    - No public_key in multi-project: Returns disabled client to prevent data leakage

    The function uses a singleton pattern per public_key to conserve resources and maintain state.

    Args:
        public_key (Optional[str]): Project identifier
            - With key: Returns client for that project
            - Without key: Returns single client or disabled client if multiple exist

    Returns:
        lighthouse: Client instance in one of three states:
            1. Client for specified public_key
            2. Default client for single-project setup
            3. Disabled client when multiple projects exist without key

    Security:
        Disables tracing when multiple projects exist without explicit key to prevent
        cross-project data leakage. Multi-project setups are experimental.

    Example:
        ```python
        # Single project
        client = get_client()  # Default client

        # In multi-project usage:
        client_a = get_client(public_key="project_a_key")  # Returns project A's client
        client_b = get_client(public_key="project_b_key")  # Returns project B's client

        # Without specific key in multi-project setup:
        client = get_client()  # Returns disabled client for safety
        ```
    """
    with lighthouseResourceManager._lock:
        active_instances = lighthouseResourceManager._instances

        # If no explicit public_key provided, check execution context
        if not public_key:
            public_key = _current_public_key.get(None)

        if not public_key:
            if len(active_instances) == 0:
                # No clients initialized yet, create default instance
                return lighthouse()

            if len(active_instances) == 1:
                # Only one client exists, safe to use without specifying key
                instance = list(active_instances.values())[0]

                # Initialize with the credentials bound to the instance (api_key or legacy)
                return lighthouse(
                    api_key=getattr(instance, "api_key", None) or None,
                    public_key=getattr(instance, "public_key", None) or None,
                    secret_key=getattr(instance, "secret_key", None) or None,
                    host=instance.host,
                    tracing_enabled=instance.tracing_enabled,
                )

            else:
                # Multiple clients exist but no key specified - disable tracing
                # to prevent cross-project data leakage
                lighthouse_logger.warning(
                    "No 'lighthouse_public_key' passed to decorated function, but multiple lighthouse clients are instantiated in current process. Skipping tracing for this function to avoid cross-project leakage."
                )
                return lighthouse(
                    tracing_enabled=False, public_key="fake", secret_key="fake"
                )

        else:
            # Specific key provided, look up existing instance
            target_instance: Optional[lighthouseResourceManager] = active_instances.get(
                public_key, None
            )

            if target_instance is None:
                # No instance found with this key - client not initialized properly
                lighthouse_logger.warning(
                    f"No lighthouse client with public key {public_key} has been initialized. Skipping tracing for decorated function."
                )
                return lighthouse(
                    tracing_enabled=False, public_key="fake", secret_key="fake"
                )

            # target_instance is guaranteed to be not None at this point
            return lighthouse(
                public_key=public_key,
                secret_key=target_instance.secret_key,
                host=target_instance.host,
                tracing_enabled=target_instance.tracing_enabled,
            )
