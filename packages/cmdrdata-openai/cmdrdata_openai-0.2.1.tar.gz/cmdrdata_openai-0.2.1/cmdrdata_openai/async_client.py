"""
AsyncTrackedOpenAI - Async version with automatic usage tracking
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

try:
    from openai import AsyncOpenAI
    from openai.types.chat import ChatCompletion
    from openai.types.completion import Completion
except ImportError:
    raise ImportError(
        "OpenAI SDK not found. Install it with: pip install openai>=1.0.0"
    )

from .context import get_effective_customer_id
from .tracker import UsageTracker

logger = logging.getLogger(__name__)


class AsyncTrackedChatCompletions:
    """Async wrapper for OpenAI chat completions with usage tracking"""

    def __init__(self, openai_chat_completions, tracker: UsageTracker):
        self._openai_completions = openai_chat_completions
        self._tracker = tracker

    async def create(
        self, *, customer_id: Optional[str] = None, track_usage: bool = True, **kwargs
    ) -> ChatCompletion:
        """
        Create a chat completion with automatic usage tracking.

        Args:
            customer_id: Customer ID for tracking (overrides context)
            track_usage: Whether to track usage for this request
            **kwargs: All standard OpenAI chat completion parameters

        Returns:
            ChatCompletion object from OpenAI
        """
        # Make the actual OpenAI API call
        response = await self._openai_completions.create(**kwargs)

        # Track usage if enabled and customer ID is available
        if track_usage:
            effective_customer_id = get_effective_customer_id(customer_id)

            if effective_customer_id and hasattr(response, "usage") and response.usage:
                # Extract metadata from the response
                metadata = {
                    "response_id": getattr(response, "id", None),
                    "created": getattr(response, "created", None),
                    "finish_reason": None,
                    "system_fingerprint": getattr(response, "system_fingerprint", None),
                }

                # Get finish reason from first choice if available
                if hasattr(response, "choices") and response.choices:
                    choice = response.choices[0]
                    if hasattr(choice, "finish_reason"):
                        metadata["finish_reason"] = choice.finish_reason

                # Track the usage asynchronously
                await self._tracker.track_usage_async(
                    customer_id=effective_customer_id,
                    model=response.model,
                    input_tokens=response.usage.prompt_tokens,
                    output_tokens=response.usage.completion_tokens,
                    provider="openai",
                    metadata=metadata,
                    timestamp=datetime.utcnow(),
                )

                logger.debug(
                    f"Tracked {response.usage.total_tokens} tokens for {effective_customer_id}"
                )
            elif not effective_customer_id:
                logger.warning("No customer_id provided for usage tracking")

        return response


class AsyncTrackedCompletions:
    """Async wrapper for OpenAI legacy completions with usage tracking"""

    def __init__(self, openai_completions, tracker: UsageTracker):
        self._openai_completions = openai_completions
        self._tracker = tracker

    async def create(
        self, *, customer_id: Optional[str] = None, track_usage: bool = True, **kwargs
    ) -> Completion:
        """
        Create a completion with automatic usage tracking.

        Args:
            customer_id: Customer ID for tracking (overrides context)
            track_usage: Whether to track usage for this request
            **kwargs: All standard OpenAI completion parameters

        Returns:
            Completion object from OpenAI
        """
        # Make the actual OpenAI API call
        response = await self._openai_completions.create(**kwargs)

        # Track usage if enabled and customer ID is available
        if track_usage:
            effective_customer_id = get_effective_customer_id(customer_id)

            if effective_customer_id and hasattr(response, "usage") and response.usage:
                # Extract metadata from the response
                metadata = {
                    "response_id": getattr(response, "id", None),
                    "created": getattr(response, "created", None),
                    "finish_reason": None,
                }

                # Get finish reason from first choice if available
                if hasattr(response, "choices") and response.choices:
                    choice = response.choices[0]
                    if hasattr(choice, "finish_reason"):
                        metadata["finish_reason"] = choice.finish_reason

                # Track the usage asynchronously
                await self._tracker.track_usage_async(
                    customer_id=effective_customer_id,
                    model=response.model,
                    input_tokens=response.usage.prompt_tokens,
                    output_tokens=response.usage.completion_tokens,
                    provider="openai",
                    metadata=metadata,
                    timestamp=datetime.utcnow(),
                )

                logger.debug(
                    f"Tracked {response.usage.total_tokens} tokens for {effective_customer_id}"
                )
            elif not effective_customer_id:
                logger.warning("No customer_id provided for usage tracking")

        return response


class AsyncTrackedChat:
    """Async wrapper for OpenAI chat with usage tracking"""

    def __init__(self, openai_chat, tracker: UsageTracker):
        self.completions = AsyncTrackedChatCompletions(openai_chat.completions, tracker)


class AsyncTrackedOpenAI:
    """
    Async drop-in replacement for OpenAI SDK with automatic usage tracking.

    Example usage:
        # Replace this:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key="...")

        # With this:
        from cmdrdata_openai import AsyncTrackedOpenAI
        client = AsyncTrackedOpenAI(
            api_key="...",
            tracker_key="your-cmdrdata-api-key"
        )

        # Everything else works the same!
        response = await client.chat.completions.create(
            model="gpt-5",  # Supports GPT-5, GPT-4o, GPT-4, etc.
            messages=[{"role": "user", "content": "Hello!"}],
            customer_id="customer-123"  # Added for tracking
        )
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
        Initialize AsyncTrackedOpenAI client.

        Args:
            api_key: OpenAI API key (can also use OPENAI_API_KEY env var)
            tracker_key: cmdrdata API key for usage tracking (required)
            tracker_endpoint: cmdrdata API endpoint URL
            tracker_timeout: Timeout for tracking requests
            **kwargs: Additional arguments passed to AsyncOpenAI client
        """
        if tracker_key is None:
            raise ValueError(
                "tracker_key is required for usage tracking. "
                "Get your API key at https://api.cmdrdata.ai"
            )

        # Initialize the underlying AsyncOpenAI client
        self._openai = AsyncOpenAI(api_key=api_key, **kwargs)

        # Initialize the usage tracker
        self._tracker = UsageTracker(
            api_key=tracker_key, endpoint=tracker_endpoint, timeout=tracker_timeout
        )

        # Create tracked wrappers
        self.chat = AsyncTrackedChat(self._openai.chat, self._tracker)
        self.completions = AsyncTrackedCompletions(
            self._openai.completions, self._tracker
        )

    def __getattr__(self, name):
        """
        Delegate all other attributes to the underlying AsyncOpenAI client.

        This ensures that AsyncTrackedOpenAI works as a drop-in replacement
        for any OpenAI SDK features we haven't explicitly wrapped.
        """
        return getattr(self._openai, name)

    def get_openai_client(self):
        """
        Get the underlying AsyncOpenAI client for direct access if needed.

        Returns:
            The raw AsyncOpenAI client instance
        """
        return self._openai

    def get_tracker(self):
        """
        Get the usage tracker instance.

        Returns:
            The UsageTracker instance
        """
        return self._tracker
