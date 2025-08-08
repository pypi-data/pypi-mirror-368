"""
Usage tracking client for sending events to cmdrdata backend
"""

import asyncio
import logging
import random
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Dict, Optional

try:
    import httpx
except ImportError:
    # Fallback to requests for simpler installations
    import requests

    httpx = None

from .exceptions import NetworkError, TrackingError, ValidationError

# InputValidator functionality is now in security module
from .logging_config import get_logger
from .performance import PerformanceContext, timed
from .retry import DEFAULT_RETRY_CONFIG, CircuitBreaker, RetryConfig, retry_with_backoff
from .security import APIKeyManager, InputSanitizer

logger = get_logger(__name__)


class UsageTracker:
    """
    Client for sending usage events to cmdrdata backend.

    Handles both sync and async sending with retry logic and error handling.
    """

    def __init__(
        self,
        api_key: str,
        endpoint: str = "https://api.cmdrdata.ai/api/events",
        timeout: float = 5.0,
        max_retries: int = 3,
    ):
        """
        Initialize the usage tracker.

        Args:
            api_key: cmdrdata API key for authentication
            endpoint: cmdrdata API endpoint URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        # Validate inputs
        if not api_key or not isinstance(api_key, str) or api_key.strip() == "":
            raise ValidationError("API key is required")

        # Validate API key format
        try:
            APIKeyManager.validate_api_key(api_key, "cmdrdata")
        except Exception:
            raise ValidationError("Invalid API key format")

        if not endpoint or not isinstance(endpoint, str) or endpoint.strip() == "":
            raise ValidationError("Endpoint is required")

        # Validate endpoint URL
        try:
            InputSanitizer.validate_url(endpoint)
        except Exception:
            raise ValidationError("Invalid endpoint URL")

        # Validate timeout
        try:
            InputSanitizer.validate_timeout(timeout)
        except Exception:
            raise ValidationError("Invalid timeout")

        self.api_key = api_key
        self.endpoint = endpoint
        self.timeout = timeout
        self.max_retries = max_retries
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "cmdrdata-openai/0.1.0",
        }

        # Thread pool for async usage tracking in sync contexts
        self._executor = ThreadPoolExecutor(max_workers=2)

    def track_usage(
        self,
        customer_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        provider: str = "openai",
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        # New parameters for enhanced analytics
        request_start_time: Optional[float] = None,
        request_end_time: Optional[float] = None,
        error_occurred: Optional[bool] = None,
        error_type: Optional[str] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        request_id: Optional[str] = None,
        streaming: Optional[bool] = None,
        retry_count: Optional[int] = None,
        time_to_first_token_ms: Optional[int] = None,
    ) -> bool:
        """
        Track usage synchronously.

        Args:
            customer_id: Customer identifier
            model: AI model used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            provider: AI provider (default: openai)
            metadata: Additional metadata about the request
            timestamp: Event timestamp (defaults to now)

        Returns:
            True if tracking succeeded, False otherwise
        """
        try:
            # Validate inputs first
            self._validate_tracking_inputs(
                customer_id, model, input_tokens, output_tokens, provider, metadata
            )

            # Sanitize and prepare the data
            event_data = self._sanitize_tracking_data(
                customer_id,
                model,
                input_tokens,
                output_tokens,
                provider,
                metadata,
                timestamp,
                request_start_time,
                request_end_time,
                error_occurred,
                error_type,
                error_code,
                error_message,
                request_id,
                streaming,
                retry_count,
                time_to_first_token_ms,
            )

            # Track usage with retry logic
            return self._track_usage_with_retry(event_data)

        except ValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Error tracking usage: {e}")
            return False

    async def track_usage_async(
        self,
        customer_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        provider: str = "openai",
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        # New parameters for enhanced analytics
        request_start_time: Optional[float] = None,
        request_end_time: Optional[float] = None,
        error_occurred: Optional[bool] = None,
        error_type: Optional[str] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        request_id: Optional[str] = None,
        streaming: Optional[bool] = None,
        retry_count: Optional[int] = None,
        time_to_first_token_ms: Optional[int] = None,
    ) -> bool:
        """
        Track usage asynchronously.

        Args:
            customer_id: Customer identifier
            model: AI model used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            provider: AI provider (default: openai)
            metadata: Additional metadata about the request
            timestamp: Event timestamp (defaults to now)

        Returns:
            True if tracking succeeded, False otherwise
        """
        base_data = {
            "customer_id": customer_id,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "provider": provider,
            "metadata": metadata or {},
            "timestamp": int((timestamp or datetime.utcnow()).timestamp()),
            "version": "0.1.0",
        }

        # Add analytics data
        analytics_data = self._build_analytics_data(
            request_start_time,
            request_end_time,
            error_occurred,
            error_type,
            error_code,
            error_message,
            request_id,
            streaming,
            retry_count,
            time_to_first_token_ms,
        )

        event_data = {**base_data, **analytics_data}

        try:
            if httpx:
                # Use httpx if available (preferred for async)
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        self.endpoint, json=event_data, headers=self.headers
                    )

                    if response.status_code == 200:
                        logger.debug(
                            f"Successfully tracked usage for customer {customer_id}"
                        )
                        return True
                    else:
                        logger.warning(
                            f"Failed to track usage: {response.status_code} {response.text}"
                        )
                        return False
            else:
                # Fallback to sync version in thread pool
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(
                    self._executor,
                    self.track_usage,
                    customer_id,
                    model,
                    input_tokens,
                    output_tokens,
                    provider,
                    metadata,
                    timestamp,
                    request_start_time,
                    request_end_time,
                    error_occurred,
                    error_type,
                    error_code,
                    error_message,
                    request_id,
                    streaming,
                    retry_count,
                    time_to_first_token_ms,
                )

        except Exception as e:
            logger.error(f"Error tracking usage: {e}")
            return False

    def track_usage_background(
        self,
        customer_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        provider: str = "openai",
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        # New parameters for enhanced analytics
        request_start_time: Optional[float] = None,
        request_end_time: Optional[float] = None,
        error_occurred: Optional[bool] = None,
        error_type: Optional[str] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        request_id: Optional[str] = None,
        streaming: Optional[bool] = None,
        retry_count: Optional[int] = None,
        time_to_first_token_ms: Optional[int] = None,
    ) -> None:
        """
        Track usage in background thread (fire-and-forget).

        This method never blocks the main thread and is ideal for
        production use where tracking failures shouldn't affect
        the main application flow.

        Args:
            customer_id: Customer identifier
            model: AI model used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            provider: AI provider (default: openai)
            metadata: Additional metadata about the request
            timestamp: Event timestamp (defaults to now)
        """
        self._executor.submit(
            self.track_usage,
            customer_id,
            model,
            input_tokens,
            output_tokens,
            provider,
            metadata,
            timestamp,
            request_start_time,
            request_end_time,
            error_occurred,
            error_type,
            error_code,
            error_message,
            request_id,
            streaming,
            retry_count,
            time_to_first_token_ms,
        )

    def _validate_tracking_inputs(
        self,
        customer_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        provider: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Validate tracking inputs"""
        if not customer_id or not isinstance(customer_id, str):
            raise ValidationError("Customer ID is required")

        InputSanitizer.validate_customer_id(customer_id)
        InputSanitizer.validate_model_name(model)
        InputSanitizer.validate_token_count(input_tokens)
        InputSanitizer.validate_token_count(output_tokens)

        if metadata is not None:
            InputSanitizer.validate_metadata(metadata)

    def _sanitize_tracking_data(
        self,
        customer_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        provider: str,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        request_start_time: Optional[float] = None,
        request_end_time: Optional[float] = None,
        error_occurred: Optional[bool] = None,
        error_type: Optional[str] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        request_id: Optional[str] = None,
        streaming: Optional[bool] = None,
        retry_count: Optional[int] = None,
        time_to_first_token_ms: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Sanitize and prepare tracking data"""
        sanitized_metadata = {}
        if metadata:
            sanitized_metadata = InputSanitizer.sanitize_metadata(metadata)

        base_data = {
            "customer_id": InputSanitizer.sanitize_string(customer_id, "customer_id"),
            "model": InputSanitizer.sanitize_string(model, "model_name"),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "provider": InputSanitizer.sanitize_string(provider, "general_string"),
            "metadata": sanitized_metadata,
            "timestamp": int((timestamp or datetime.utcnow()).timestamp()),
            "version": "0.1.0",
        }

        # Add analytics data
        analytics_data = self._build_analytics_data(
            request_start_time,
            request_end_time,
            error_occurred,
            error_type,
            error_code,
            error_message,
            request_id,
            streaming,
            retry_count,
            time_to_first_token_ms,
        )

        return {**base_data, **analytics_data}

    def _track_usage_with_retry(self, event_data: Dict[str, Any]) -> bool:
        """Track usage with exponential backoff retry logic"""
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                if httpx:
                    with httpx.Client(timeout=self.timeout) as client:
                        response = client.post(
                            self.endpoint, json=event_data, headers=self.headers
                        )

                        if response.status_code == 200:
                            return True
                        # Retry on server errors (5xx) and rate limiting (429)
                        elif response.status_code >= 500 or response.status_code == 429:
                            last_exception = NetworkError(
                                f"Server error: {response.status_code}"
                            )
                            logger.warning(
                                f"Attempt {attempt + 1} failed: {last_exception}"
                            )
                        # Do not retry on other client errors (4xx)
                        elif response.status_code >= 400:
                            raise TrackingError(
                                f"Client error: {response.status_code} {response.text}"
                            )
                        else:
                            return False  # Should not happen, but for completeness
                else:
                    # Fallback to requests
                    import requests

                    response = requests.post(
                        self.endpoint,
                        json=event_data,
                        headers=self.headers,
                        timeout=self.timeout,
                    )
                    if response.status_code == 200:
                        return True
                    elif response.status_code >= 500 or response.status_code == 429:
                        last_exception = NetworkError(
                            f"Server error: {response.status_code}"
                        )
                        logger.warning(
                            f"Attempt {attempt + 1} failed: {last_exception}"
                        )
                    elif response.status_code >= 400:
                        raise TrackingError(
                            f"Client error: {response.status_code} {response.text}"
                        )
                    else:
                        return False

            except NetworkError as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1} failed with network error: {e}")
            except TrackingError:
                # Re-raise tracking errors (like client errors) immediately
                raise
            except Exception as e:
                # Handle httpx.RequestError or requests.exceptions.RequestException
                handled = False
                if httpx:
                    try:
                        if hasattr(httpx, "RequestError") and isinstance(
                            e, httpx.RequestError
                        ):
                            last_exception = e
                            logger.warning(
                                f"Attempt {attempt + 1} failed with network error: {e}"
                            )
                            handled = True
                    except AttributeError:
                        pass
                else:
                    try:
                        import requests

                        if isinstance(e, requests.exceptions.RequestException):
                            last_exception = e
                            logger.warning(
                                f"Attempt {attempt + 1} failed with network error: {e}"
                            )
                            handled = True
                    except ImportError:
                        pass

                if not handled:
                    raise

            # Exponential backoff with jitter
            if attempt < self.max_retries:
                backoff_time = (2**attempt) + (random.uniform(0, 1))
                logger.debug(f"Retrying in {backoff_time:.2f} seconds...")
                time.sleep(backoff_time)

        logger.error(
            f"All {self.max_retries + 1} tracking attempts failed. Last error: {last_exception}"
        )
        raise TrackingError(
            "Tracking failed after multiple retries"
        ) from last_exception

    def _build_analytics_data(
        self,
        request_start_time: Optional[float] = None,
        request_end_time: Optional[float] = None,
        error_occurred: Optional[bool] = None,
        error_type: Optional[str] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        request_id: Optional[str] = None,
        streaming: Optional[bool] = None,
        retry_count: Optional[int] = None,
        time_to_first_token_ms: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Build analytics data for enhanced tracking"""
        analytics_data = {}

        # Latency data
        if request_start_time is not None or request_end_time is not None:
            latency_data = {}
            if request_start_time is not None:
                latency_data["request_start_time"] = int(request_start_time)
            if request_end_time is not None:
                latency_data["request_end_time"] = int(request_end_time)
            if request_start_time is not None and request_end_time is not None:
                latency_data["duration_ms"] = int(
                    (request_end_time - request_start_time) * 1000
                )
            if time_to_first_token_ms is not None:
                latency_data["time_to_first_token_ms"] = time_to_first_token_ms
            analytics_data["latency"] = latency_data

        # Error data
        error_data = {
            "occurred": error_occurred if error_occurred is not None else False,
            "type": error_type,
            "code": error_code,
            "message": (
                error_message[:500] if error_message else None
            ),  # Truncate long messages
        }
        analytics_data["error"] = error_data

        # Request data
        request_data = {
            "id": request_id or str(uuid.uuid4()),
            "streaming": streaming if streaming is not None else False,
            "retry_count": retry_count if retry_count is not None else 0,
            "success": not (error_occurred if error_occurred is not None else False),
        }
        analytics_data["request"] = request_data

        return analytics_data

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the tracker"""
        return {
            "healthy": True,
            "endpoint": self.endpoint,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "circuit_breaker_state": "CLOSED",
        }

    def __del__(self):
        """Cleanup thread pool on deletion."""
        if hasattr(self, "_executor"):
            self._executor.shutdown(wait=False)
