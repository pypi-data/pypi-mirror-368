"""
Dynamic proxy classes for transparent API forwarding with usage tracking
"""

import inspect
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Union

from .context import get_effective_customer_id
from .tracker import UsageTracker

logger = logging.getLogger(__name__)


class TrackedProxy:
    """
    Base proxy class that forwards all method calls to the underlying client
    while selectively adding usage tracking to specific methods.
    """

    def __init__(
        self,
        client: Any,
        tracker: UsageTracker,
        track_methods: Dict[str, Callable] = None,
    ):
        """
        Initialize the proxy.

        Args:
            client: The underlying client (e.g., OpenAI client)
            tracker: Usage tracker instance
            track_methods: Dict mapping method names to tracking functions
        """
        # Store these with underscore prefixes to avoid conflicts
        object.__setattr__(self, "_client", client)
        object.__setattr__(self, "_tracker", tracker)
        object.__setattr__(self, "_track_methods", track_methods or {})
        object.__setattr__(self, "_tracked_attributes", {})

    def __getattr__(self, name: str) -> Any:
        """
        Dynamically forward attribute access to the underlying client.
        If the attribute is a method that should be tracked, wrap it.
        """
        # Check if we've already wrapped this attribute
        if name in self._tracked_attributes:
            return self._tracked_attributes[name]

        # Get the attribute from the underlying client
        try:
            attr = getattr(self._client, name)
        except AttributeError:
            # Don't cache non-existent attributes
            raise AttributeError(
                f"'{type(self._client).__name__}' object has no attribute '{name}'"
            )

        # If it's a callable and we have a tracker for it, wrap it
        if callable(attr) and name in self._track_methods:
            wrapped_attr = self._wrap_method(attr, name)
            self._tracked_attributes[name] = wrapped_attr
            return wrapped_attr

        # If it's another object that might need proxying, check if we should wrap it
        elif hasattr(attr, "__dict__") and not isinstance(
            attr, (str, int, float, bool, type(None))
        ):
            # This might be a sub-client (like client.chat.completions)
            # Check if any of our track methods start with this attribute name
            sub_track_methods = {
                k[len(name) + 1 :]: v
                for k, v in self._track_methods.items()
                if k.startswith(f"{name}.")
            }

            if sub_track_methods:
                wrapped_attr = TrackedProxy(attr, self._tracker, sub_track_methods)
                self._tracked_attributes[name] = wrapped_attr
                return wrapped_attr

        # For everything else, just return the original attribute
        self._tracked_attributes[name] = attr
        return attr

    def __setattr__(self, name: str, value: Any) -> None:
        """Forward attribute setting to the underlying client"""
        if name.startswith("_"):
            object.__setattr__(self, name, value)
        else:
            setattr(self._client, name, value)

    def __dir__(self):
        """Return attributes from both proxy and underlying client"""
        proxy_attrs = [
            attr for attr in object.__dir__(self) if not attr.startswith("_")
        ]
        client_attrs = dir(self._client)
        return sorted(set(proxy_attrs + client_attrs))

    def _wrap_method(self, method: Callable, method_name: str) -> Callable:
        """Wrap a method to add usage tracking"""
        tracker_func = self._track_methods[method_name]

        def wrapped(*args, **kwargs):
            # Extract customer_id, track_usage, and metadata from kwargs if present
            customer_id = kwargs.pop("customer_id", None)
            track_usage = kwargs.pop("track_usage", True)
            custom_metadata = kwargs.pop("metadata", None)

            # Generate request ID for tracking
            request_id = str(uuid.uuid4())

            # Start timing
            start_time = time.time()
            end_time = None
            error_occurred = False
            error_type = None
            error_code = None
            error_message = None
            retry_count = 0

            # Detect if this is a streaming request
            streaming = kwargs.get("stream", False)
            time_to_first_token_ms = None

            # Call the original method
            try:
                result = method(*args, **kwargs)
                end_time = time.time()

                # Track usage if enabled
                if track_usage:
                    try:
                        tracker_func(
                            result=result,
                            customer_id=customer_id,
                            tracker=self._tracker,
                            method_name=method_name,
                            args=args,
                            kwargs=kwargs,
                            custom_metadata=custom_metadata,
                            # Enhanced tracking data
                            request_start_time=start_time,
                            request_end_time=end_time,
                            error_occurred=error_occurred,
                            error_type=error_type,
                            error_code=error_code,
                            error_message=error_message,
                            request_id=request_id,
                            streaming=streaming,
                            retry_count=retry_count,
                            time_to_first_token_ms=time_to_first_token_ms,
                        )
                    except Exception as e:
                        logger.warning(f"Failed to track usage for {method_name}: {e}")

                return result

            except Exception as e:
                end_time = time.time()
                error_occurred = True

                # Categorize error types
                error_message = str(e)
                if hasattr(e, "status_code"):
                    error_code = str(e.status_code)
                    if e.status_code == 429:
                        error_type = "rate_limit"
                    elif e.status_code == 401:
                        error_type = "authentication"
                    elif e.status_code == 403:
                        error_type = "authorization"
                    elif e.status_code >= 500:
                        error_type = "server_error"
                    elif e.status_code >= 400:
                        error_type = "invalid_request"
                elif "timeout" in error_message.lower():
                    error_type = "timeout"
                elif "connection" in error_message.lower():
                    error_type = "connection_error"
                else:
                    error_type = "unknown_error"

                # Track the error if usage tracking is enabled
                if track_usage:
                    try:
                        tracker_func(
                            result=None,
                            customer_id=customer_id,
                            tracker=self._tracker,
                            method_name=method_name,
                            args=args,
                            kwargs=kwargs,
                            custom_metadata=custom_metadata,
                            # Enhanced tracking data
                            request_start_time=start_time,
                            request_end_time=end_time,
                            error_occurred=error_occurred,
                            error_type=error_type,
                            error_code=error_code,
                            error_message=error_message,
                            request_id=request_id,
                            streaming=streaming,
                            retry_count=retry_count,
                            time_to_first_token_ms=time_to_first_token_ms,
                        )
                    except Exception as track_error:
                        logger.warning(
                            f"Failed to track error for {method_name}: {track_error}"
                        )

                # Log the error but re-raise it unchanged
                logger.debug(f"Method {method_name} failed: {e}")
                raise

        # Preserve the original function signature and metadata
        wrapped.__name__ = getattr(method, "__name__", method_name)
        wrapped.__doc__ = getattr(method, "__doc__", None)

        try:
            wrapped.__signature__ = inspect.signature(method)
        except (ValueError, TypeError):
            pass

        return wrapped

    def __repr__(self):
        """Return a helpful representation"""
        return f"TrackedProxy({repr(self._client)})"


def track_chat_completion(
    result,
    customer_id,
    tracker,
    method_name,
    args,
    kwargs,
    custom_metadata=None,
    # Enhanced tracking parameters
    request_start_time=None,
    request_end_time=None,
    error_occurred=None,
    error_type=None,
    error_code=None,
    error_message=None,
    request_id=None,
    streaming=None,
    retry_count=None,
    time_to_first_token_ms=None,
):
    """Track chat completion usage"""
    try:
        effective_customer_id = get_effective_customer_id(customer_id)

        if not effective_customer_id:
            logger.warning(
                "No customer_id provided for tracking. Set customer_id parameter or use set_customer_context()"
            )
            return

        if hasattr(result, "usage") and result.usage:
            # Combine system metadata with custom metadata
            metadata = {
                "response_id": getattr(result, "id", None),
                "created": getattr(result, "created", None),
                "finish_reason": (
                    getattr(result.choices[0], "finish_reason", None)
                    if result.choices
                    else None
                ),
            }

            # Add custom metadata if provided
            if custom_metadata:
                metadata.update(custom_metadata)

            # Use the new tracker method signature with enhanced analytics
            tracker.track_usage_background(
                customer_id=effective_customer_id,
                model=getattr(result, "model", kwargs.get("model", "unknown")),
                input_tokens=result.usage.prompt_tokens if result else 0,
                output_tokens=result.usage.completion_tokens if result else 0,
                provider="openai",
                metadata=metadata,
                request_start_time=request_start_time,
                request_end_time=request_end_time,
                error_occurred=error_occurred,
                error_type=error_type,
                error_code=error_code,
                error_message=error_message,
                request_id=request_id,
                streaming=streaming,
                retry_count=retry_count,
                time_to_first_token_ms=time_to_first_token_ms,
            )

    except Exception as e:
        logger.warning(f"Failed to extract usage data from chat completion: {e}")


def track_completion(
    result,
    customer_id,
    tracker,
    method_name,
    args,
    kwargs,
    custom_metadata=None,
    # Enhanced tracking parameters
    request_start_time=None,
    request_end_time=None,
    error_occurred=None,
    error_type=None,
    error_code=None,
    error_message=None,
    request_id=None,
    streaming=None,
    retry_count=None,
    time_to_first_token_ms=None,
):
    """Track legacy completion usage"""
    try:
        effective_customer_id = get_effective_customer_id(customer_id)

        if not effective_customer_id:
            logger.warning(
                "No customer_id provided for tracking. Set customer_id parameter or use set_customer_context()"
            )
            return

        if hasattr(result, "usage") and result.usage:
            # Combine system metadata with custom metadata
            metadata = {
                "response_id": getattr(result, "id", None),
                "created": getattr(result, "created", None),
            }

            # Add custom metadata if provided
            if custom_metadata:
                metadata.update(custom_metadata)

            # Use the new tracker method signature with enhanced analytics
            tracker.track_usage_background(
                customer_id=effective_customer_id,
                model=getattr(result, "model", kwargs.get("model", "unknown")),
                input_tokens=result.usage.prompt_tokens if result else 0,
                output_tokens=result.usage.completion_tokens if result else 0,
                provider="openai",
                metadata=metadata,
                request_start_time=request_start_time,
                request_end_time=request_end_time,
                error_occurred=error_occurred,
                error_type=error_type,
                error_code=error_code,
                error_message=error_message,
                request_id=request_id,
                streaming=streaming,
                retry_count=retry_count,
                time_to_first_token_ms=time_to_first_token_ms,
            )

    except Exception as e:
        logger.warning(f"Failed to extract usage data from completion: {e}")


def track_embeddings(
    result,
    customer_id,
    tracker,
    method_name,
    args,
    kwargs,
    custom_metadata=None,
    **tracking_params,
):
    """Track embeddings usage"""
    try:
        effective_customer_id = get_effective_customer_id(customer_id)
        if not effective_customer_id:
            logger.warning("No customer_id provided for embeddings tracking")
            return

        if hasattr(result, "usage") and result.usage:
            metadata = {
                "response_id": getattr(result, "id", None),
                "created": getattr(result, "created", None),
                "embedding_count": len(result.data) if hasattr(result, "data") else 0,
            }
            if custom_metadata:
                metadata.update(custom_metadata)

            tracker.track_usage_background(
                customer_id=effective_customer_id,
                model=getattr(result, "model", kwargs.get("model", "unknown")),
                input_tokens=result.usage.prompt_tokens if result.usage else 0,
                output_tokens=0,  # Embeddings don't have output tokens
                provider="openai",
                metadata=metadata,
                **tracking_params,
            )
    except Exception as e:
        logger.warning(f"Failed to track embeddings: {e}")


def track_images(
    result,
    customer_id,
    tracker,
    method_name,
    args,
    kwargs,
    custom_metadata=None,
    **tracking_params,
):
    """Track image generation usage"""
    try:
        effective_customer_id = get_effective_customer_id(customer_id)
        if not effective_customer_id:
            logger.warning("No customer_id provided for image tracking")
            return

        # Image generation doesn't return usage in tokens but we track the operation
        metadata = {
            "created": getattr(result, "created", None),
            "image_count": len(result.data) if hasattr(result, "data") else 0,
            "size": kwargs.get("size", "1024x1024"),
            "quality": kwargs.get("quality", "standard"),
            "style": kwargs.get("style", "vivid"),
            "operation": method_name.split(".")[
                -1
            ],  # generate, edit, or create_variation
        }
        if custom_metadata:
            metadata.update(custom_metadata)

        # For images, we track as a custom event with estimated tokens
        # DALL-E doesn't report tokens, but we can estimate based on operation
        model = kwargs.get("model", "dall-e-2")

        tracker.track_usage_background(
            customer_id=effective_customer_id,
            model=model,
            input_tokens=0,  # Images don't use text tokens in the same way
            output_tokens=0,
            provider="openai",
            metadata=metadata,
            **tracking_params,
        )
    except Exception as e:
        logger.warning(f"Failed to track image generation: {e}")


def track_audio(
    result,
    customer_id,
    tracker,
    method_name,
    args,
    kwargs,
    custom_metadata=None,
    **tracking_params,
):
    """Track audio operations (transcription, translation, TTS)"""
    try:
        effective_customer_id = get_effective_customer_id(customer_id)
        if not effective_customer_id:
            logger.warning("No customer_id provided for audio tracking")
            return

        metadata = {
            "operation": method_name.split(".")[
                -1
            ],  # transcriptions, translations, or speech
        }

        # Different metadata based on operation type
        if "speech" in method_name:
            # Text-to-speech
            metadata["voice"] = kwargs.get("voice", "alloy")
            metadata["response_format"] = kwargs.get("response_format", "mp3")
            model = kwargs.get("model", "tts-1")
        else:
            # Transcription or translation
            metadata["language"] = kwargs.get("language", "auto")
            metadata["response_format"] = kwargs.get("response_format", "json")
            if hasattr(result, "text"):
                metadata["text_length"] = len(result.text)
            model = kwargs.get("model", "whisper-1")

        if custom_metadata:
            metadata.update(custom_metadata)

        # Audio operations don't report token usage directly
        tracker.track_usage_background(
            customer_id=effective_customer_id,
            model=model,
            input_tokens=0,
            output_tokens=0,
            provider="openai",
            metadata=metadata,
            **tracking_params,
        )
    except Exception as e:
        logger.warning(f"Failed to track audio operation: {e}")


def track_moderations(
    result,
    customer_id,
    tracker,
    method_name,
    args,
    kwargs,
    custom_metadata=None,
    **tracking_params,
):
    """Track moderation API usage"""
    try:
        effective_customer_id = get_effective_customer_id(customer_id)
        if not effective_customer_id:
            logger.warning("No customer_id provided for moderation tracking")
            return

        metadata = {
            "response_id": getattr(result, "id", None),
            "flagged": (
                any(r.flagged for r in result.results)
                if hasattr(result, "results")
                else False
            ),
        }
        if custom_metadata:
            metadata.update(custom_metadata)

        # Moderation is free but we track for analytics
        tracker.track_usage_background(
            customer_id=effective_customer_id,
            model=kwargs.get("model", "text-moderation-latest"),
            input_tokens=0,  # Moderation doesn't charge tokens
            output_tokens=0,
            provider="openai",
            metadata=metadata,
            **tracking_params,
        )
    except Exception as e:
        logger.warning(f"Failed to track moderation: {e}")


def track_fine_tuning(
    result,
    customer_id,
    tracker,
    method_name,
    args,
    kwargs,
    custom_metadata=None,
    **tracking_params,
):
    """Track fine-tuning job creation"""
    try:
        effective_customer_id = get_effective_customer_id(customer_id)
        if not effective_customer_id:
            logger.warning("No customer_id provided for fine-tuning tracking")
            return

        metadata = {
            "job_id": getattr(result, "id", None),
            "status": getattr(result, "status", None),
            "model": getattr(result, "model", kwargs.get("model", "unknown")),
            "training_file": kwargs.get("training_file"),
            "validation_file": kwargs.get("validation_file"),
        }
        if custom_metadata:
            metadata.update(custom_metadata)

        # Fine-tuning costs are complex, track the job creation
        tracker.track_usage_background(
            customer_id=effective_customer_id,
            model=kwargs.get("model", "gpt-5"),
            input_tokens=0,  # Actual token usage tracked separately
            output_tokens=0,
            provider="openai",
            metadata=metadata,
            **tracking_params,
        )
    except Exception as e:
        logger.warning(f"Failed to track fine-tuning job: {e}")


def track_assistant_run(
    result,
    customer_id,
    tracker,
    method_name,
    args,
    kwargs,
    custom_metadata=None,
    **tracking_params,
):
    """Track Assistant API run creation (which consumes tokens)"""
    try:
        effective_customer_id = get_effective_customer_id(customer_id)
        if not effective_customer_id:
            logger.warning("No customer_id provided for assistant run tracking")
            return

        metadata = {
            "run_id": getattr(result, "id", None),
            "thread_id": getattr(result, "thread_id", None),
            "assistant_id": getattr(result, "assistant_id", None),
            "status": getattr(result, "status", None),
        }

        # Check if usage data is available (it might be after polling)
        if hasattr(result, "usage") and result.usage:
            input_tokens = getattr(result.usage, "prompt_tokens", 0)
            output_tokens = getattr(result.usage, "completion_tokens", 0)
        else:
            input_tokens = 0
            output_tokens = 0

        if custom_metadata:
            metadata.update(custom_metadata)

        tracker.track_usage_background(
            customer_id=effective_customer_id,
            model=kwargs.get(
                "model", "gpt-5"
            ),  # Assistants support GPT-5, GPT-4o, etc.
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            provider="openai",
            metadata=metadata,
            **tracking_params,
        )
    except Exception as e:
        logger.warning(f"Failed to track assistant run: {e}")


# OpenAI tracking configuration - All methods that consume tokens or should be tracked
OPENAI_TRACK_METHODS = {
    # Text generation
    "chat.completions.create": track_chat_completion,
    "completions.create": track_completion,
    # Embeddings
    "embeddings.create": track_embeddings,
    # Images (DALL-E)
    "images.generate": track_images,
    "images.edit": track_images,
    "images.create_variation": track_images,
    # Audio (Whisper & TTS)
    "audio.transcriptions.create": track_audio,
    "audio.translations.create": track_audio,
    "audio.speech.create": track_audio,
    # Moderation (free but worth tracking)
    "moderations.create": track_moderations,
    # Fine-tuning
    "fine_tuning.jobs.create": track_fine_tuning,
    # Assistants API (Beta) - only track operations that consume tokens
    "beta.threads.runs.create": track_assistant_run,
    "beta.threads.runs.create_and_poll": track_assistant_run,
}
