"""
TrackedOpenAI - Drop-in replacement for OpenAI SDK with automatic usage tracking
"""

import logging
import warnings
from typing import Any, Dict, Optional, Union

from .proxy import OPENAI_TRACK_METHODS, TrackedProxy
from .tracker import UsageTracker
from .version_compat import check_compatibility, get_compatibility_info

# Check version compatibility on import
if not check_compatibility():
    info = get_compatibility_info()
    if info.get("openai", {}).get("installed"):
        warnings.warn(
            f"cmdrdata-openai: OpenAI SDK version {info['openai']['installed']} may not be fully compatible. "
            f"See compatibility information with get_compatibility_info()",
            UserWarning,
        )

try:
    from openai import OpenAI
except ImportError:
    raise ImportError(
        "OpenAI SDK not found. Install it with: pip install openai>=1.0.0\n"
        "For best compatibility, use: pip install openai>=1.0.0"
    )

logger = logging.getLogger(__name__)


class TrackedOpenAI(TrackedProxy):
    """
    Drop-in replacement for OpenAI SDK with automatic usage tracking.

    This class uses dynamic proxying to automatically forward ALL method calls
    to the underlying OpenAI client while selectively adding usage tracking
    to specific methods like chat completions.

    Example usage:
        # Replace this:
        from openai import OpenAI
        client = OpenAI(api_key="...")

        # With this:
        from cmdrdata_openai import TrackedOpenAI
        client = TrackedOpenAI(
            api_key="...",
            tracker_key="your-cmdrdata-api-key"
        )

        # Everything else works exactly the same!
        response = client.chat.completions.create(
            model="gpt-5",  # Supports GPT-5, GPT-4o, GPT-4, etc.
            messages=[{"role": "user", "content": "Hello!"}],
            customer_id="customer-123"  # Added for tracking
        )

        # ALL OpenAI SDK methods work transparently:
        response = client.images.generate(prompt="A cat")
        models = client.models.list()
        files = client.files.list()
        # etc...
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        tracker_key: Optional[str] = None,
        tracker_endpoint: str = "https://api.cmdrdata.ai/api/events",
        tracker_timeout: float = 5.0,
        **kwargs,
    ):
        """
        Initialize TrackedOpenAI client.

        Args:
            api_key: OpenAI API key (can also use OPENAI_API_KEY env var)
            tracker_key: cmdrdata API key for usage tracking (required)
            tracker_endpoint: cmdrdata API endpoint URL
            tracker_timeout: Timeout for tracking requests
            **kwargs: Additional arguments passed to OpenAI client
        """
        if tracker_key is None:
            raise ValueError(
                "tracker_key is required for usage tracking. "
                "Get your API key at https://api.cmdrdata.ai"
            )

        # Initialize the underlying OpenAI client
        openai_client = OpenAI(api_key=api_key, **kwargs)

        # Initialize the usage tracker
        tracker = UsageTracker(
            api_key=tracker_key, endpoint=tracker_endpoint, timeout=tracker_timeout
        )

        # Initialize the proxy with tracking methods
        super().__init__(
            client=openai_client, tracker=tracker, track_methods=OPENAI_TRACK_METHODS
        )

        logger.info("TrackedOpenAI initialized successfully")

    @classmethod
    def get_compatibility_info(cls) -> Dict[str, Any]:
        """
        Get detailed compatibility information for the current environment.

        Returns:
            Dict containing version compatibility details
        """
        return get_compatibility_info()

    @classmethod
    def check_compatibility(cls, raise_on_incompatible: bool = False) -> bool:
        """
        Check if the current OpenAI SDK version is compatible.

        Args:
            raise_on_incompatible: If True, raise an exception if incompatible

        Returns:
            True if compatible, False otherwise

        Raises:
            RuntimeError: If incompatible and raise_on_incompatible=True
        """
        compatible = check_compatibility()

        if not compatible and raise_on_incompatible:
            info = get_compatibility_info()
            openai_info = info.get("openai", {})
            raise RuntimeError(
                f"OpenAI SDK version {openai_info.get('installed', 'unknown')} is not compatible. "
                f"Supported range: {openai_info.get('min_supported', 'unknown')} - {openai_info.get('max_supported', 'unknown')}"
            )

        return compatible

    def get_openai_client(self):
        """
        Get the underlying OpenAI client for direct access if needed.

        Returns:
            The raw OpenAI client instance
        """
        return self._client

    def get_tracker(self):
        """
        Get the usage tracker instance.

        Returns:
            The UsageTracker instance
        """
        return self._tracker
