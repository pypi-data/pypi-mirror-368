"""
cmdrdata-openai: Drop-in replacement for OpenAI Python SDK with automatic usage tracking

This package provides a TrackedOpenAI client that maintains full compatibility with the
OpenAI SDK while automatically tracking token usage for billing and analytics.

Key Features:
- Drop-in replacement for OpenAI SDK
- Automatic token usage tracking
- Customer-based usage attribution
- Full async/sync support
- Zero performance impact on failures
- Comprehensive error handling

Quick Start:
    from cmdrdata_openai import TrackedOpenAI

    client = TrackedOpenAI(
        api_key="your-openai-key",
        tracker_key="your-tracker-api-key"
    )

    response = client.chat.completions.create(
        model="gpt-5",  # Supports GPT-5, GPT-4o, GPT-4, etc.
        messages=[{"role": "user", "content": "Hello!"}],
        customer_id="customer-123"
    )

Context-based tracking:
    from cmdrdata_openai import TrackedOpenAI, set_customer_context

    set_customer_context("customer-123")
    response = client.chat.completions.create(...)
    # Automatically tracked for customer-123
"""

from .async_client import AsyncTrackedOpenAI
from .client import TrackedOpenAI
from .context import (
    clear_customer_context,
    customer_context,
    get_customer_context,
    set_customer_context,
)
from .version_compat import check_compatibility, get_compatibility_info

__version__ = "0.1.0"
__author__ = "cmdrdata"
__email__ = "hello@cmdrdata.ai"

__all__ = [
    # Main clients
    "TrackedOpenAI",
    "AsyncTrackedOpenAI",
    # Context management
    "set_customer_context",
    "clear_customer_context",
    "get_customer_context",
    "customer_context",
    # Compatibility
    "check_compatibility",
    "get_compatibility_info",
]

# Package metadata
__title__ = "cmdrdata-openai"
__description__ = (
    "Drop-in replacement for OpenAI Python SDK with automatic usage tracking"
)
__url__ = "https://github.com/cmdrdata-ai/cmdrdata-openai"
__license__ = "MIT"
