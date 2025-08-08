"""
Unit tests for TrackedProxy and method tracking
"""

import inspect
from unittest.mock import Mock, patch

import pytest

from cmdrdata_openai.proxy import (
    OPENAI_TRACK_METHODS,
    TrackedProxy,
    track_assistant_run,
    track_audio,
    track_chat_completion,
    track_completion,
    track_embeddings,
    track_fine_tuning,
    track_images,
    track_moderations,
)
from cmdrdata_openai.tracker import UsageTracker


class TestTrackedProxy:
    """Test suite for TrackedProxy"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_client = Mock()
        self.mock_tracker = Mock(spec=UsageTracker)
        self.track_methods = {"test_method": Mock(), "chat.completions.create": Mock()}

    def test_proxy_initialization(self):
        """Test TrackedProxy initialization"""
        proxy = TrackedProxy(
            client=self.mock_client,
            tracker=self.mock_tracker,
            track_methods=self.track_methods,
        )

        assert proxy._client is self.mock_client
        assert proxy._tracker is self.mock_tracker
        assert proxy._track_methods == self.track_methods
        assert proxy._tracked_attributes == {}

    def test_getattr_simple_attribute(self):
        """Test __getattr__ for simple attributes"""
        self.mock_client.simple_attr = "test_value"

        proxy = TrackedProxy(
            client=self.mock_client, tracker=self.mock_tracker, track_methods={}
        )

        assert proxy.simple_attr == "test_value"
        assert "simple_attr" in proxy._tracked_attributes

    def test_getattr_tracked_method(self):
        """Test __getattr__ for tracked methods"""
        mock_method = Mock(return_value="method_result")
        self.mock_client.test_method = mock_method

        proxy = TrackedProxy(
            client=self.mock_client,
            tracker=self.mock_tracker,
            track_methods={"test_method": Mock()},
        )

        # Get the wrapped method
        wrapped_method = proxy.test_method

        # Call the wrapped method
        result = wrapped_method()

        # Verify original method was called
        mock_method.assert_called_once()
        assert result == "method_result"

        # Verify method is cached
        assert "test_method" in proxy._tracked_attributes

    def test_getattr_nested_attributes(self):
        """Test __getattr__ for nested attributes"""
        # Set up nested structure
        self.mock_client.chat = Mock()
        self.mock_client.chat.completions = Mock()
        self.mock_client.chat.completions.create = Mock(return_value="chat_result")

        proxy = TrackedProxy(
            client=self.mock_client,
            tracker=self.mock_tracker,
            track_methods={"chat.completions.create": Mock()},
        )

        # Access nested attribute
        chat_proxy = proxy.chat

        # Should be a TrackedProxy itself
        assert isinstance(chat_proxy, TrackedProxy)
        assert chat_proxy._client is self.mock_client.chat

        # Access deeper
        completions_proxy = chat_proxy.completions
        assert isinstance(completions_proxy, TrackedProxy)

        # Call the tracked method
        result = completions_proxy.create()
        assert result == "chat_result"

    def test_getattr_nonexistent_attribute(self):
        """Test __getattr__ for non-existent attributes"""
        # Create a more restrictive mock that doesn't auto-create attributes
        restrictive_mock = Mock(spec=[])  # Empty spec means no allowed attributes

        proxy = TrackedProxy(
            client=restrictive_mock, tracker=self.mock_tracker, track_methods={}
        )

        with pytest.raises(
            AttributeError, match="'Mock' object has no attribute 'nonexistent'"
        ):
            _ = proxy.nonexistent

    def test_setattr_client_attribute(self):
        """Test __setattr__ for client attributes"""
        proxy = TrackedProxy(
            client=self.mock_client, tracker=self.mock_tracker, track_methods={}
        )

        proxy.new_attr = "new_value"

        # Should set on the underlying client
        assert self.mock_client.new_attr == "new_value"

    def test_setattr_private_attribute(self):
        """Test __setattr__ for private attributes"""

        # Use a simple object instead of Mock to avoid auto-creation of attributes
        class SimpleClient:
            pass

        simple_client = SimpleClient()

        proxy = TrackedProxy(
            client=simple_client, tracker=self.mock_tracker, track_methods={}
        )

        proxy._private_attr = "private_value"

        # Should set on the proxy itself
        assert proxy._private_attr == "private_value"
        assert not hasattr(simple_client, "_private_attr")

    def test_dir_method(self):
        """Test __dir__ method includes both proxy and client attributes"""
        self.mock_client.client_attr = "value"

        proxy = TrackedProxy(
            client=self.mock_client, tracker=self.mock_tracker, track_methods={}
        )

        proxy.proxy_attr = "proxy_value"

        dir_result = dir(proxy)

        # Should include client attributes
        assert "client_attr" in dir_result
        # Should include proxy attributes (but not private ones starting with _)
        assert "proxy_attr" in dir_result

    def test_wrap_method_basic(self):
        """Test _wrap_method basic functionality"""
        mock_method = Mock(return_value="result")
        mock_tracker_func = Mock()

        proxy = TrackedProxy(
            client=self.mock_client,
            tracker=self.mock_tracker,
            track_methods={"test_method": mock_tracker_func},
        )

        wrapped = proxy._wrap_method(mock_method, "test_method")

        # Call wrapped method
        result = wrapped("arg1", kwarg1="value1")

        # Verify original method was called
        mock_method.assert_called_once_with("arg1", kwarg1="value1")
        assert result == "result"

        # Verify tracker was called
        mock_tracker_func.assert_called_once()

    def test_wrap_method_with_tracking_parameters(self):
        """Test _wrap_method extracts tracking parameters"""
        mock_method = Mock(return_value="result")
        mock_tracker_func = Mock()

        proxy = TrackedProxy(
            client=self.mock_client,
            tracker=self.mock_tracker,
            track_methods={"test_method": mock_tracker_func},
        )

        wrapped = proxy._wrap_method(mock_method, "test_method")

        # Call with tracking parameters
        result = wrapped(
            "arg1", kwarg1="value1", customer_id="test-customer", track_usage=True
        )

        # Verify tracking parameters were removed from kwargs
        mock_method.assert_called_once_with("arg1", kwarg1="value1")

        # Verify tracker was called with correct parameters
        call_args = mock_tracker_func.call_args
        assert call_args[1]["customer_id"] == "test-customer"
        assert call_args[1]["tracker"] is self.mock_tracker
        assert call_args[1]["method_name"] == "test_method"

    def test_wrap_method_tracking_disabled(self):
        """Test _wrap_method when tracking is disabled"""
        mock_method = Mock(return_value="result")
        mock_tracker_func = Mock()

        proxy = TrackedProxy(
            client=self.mock_client,
            tracker=self.mock_tracker,
            track_methods={"test_method": mock_tracker_func},
        )

        wrapped = proxy._wrap_method(mock_method, "test_method")

        # Call with tracking disabled
        result = wrapped("arg1", track_usage=False)

        # Verify original method was called
        mock_method.assert_called_once_with("arg1")

        # Verify tracker was NOT called
        mock_tracker_func.assert_not_called()

    def test_wrap_method_preserves_signature(self):
        """Test _wrap_method preserves original method signature"""

        def original_method(arg1: str, arg2: int = 10) -> str:
            """Original method docstring"""
            return f"{arg1}_{arg2}"

        proxy = TrackedProxy(
            client=self.mock_client,
            tracker=self.mock_tracker,
            track_methods={"test_method": Mock()},
        )

        wrapped = proxy._wrap_method(original_method, "test_method")

        # Check that metadata is preserved
        assert wrapped.__name__ == "original_method"
        assert wrapped.__doc__ == "Original method docstring"

        # Check signature (if available)
        try:
            original_sig = inspect.signature(original_method)
            wrapped_sig = inspect.signature(wrapped)
            # Signatures should be the same
            assert str(original_sig) == str(wrapped_sig)
        except (ValueError, TypeError):
            # Signature inspection might fail in some environments
            pass

    def test_wrap_method_exception_handling(self):
        """Test _wrap_method handles exceptions properly"""

        def failing_method():
            raise ValueError("Method failed")

        mock_tracker_func = Mock()

        proxy = TrackedProxy(
            client=self.mock_client,
            tracker=self.mock_tracker,
            track_methods={"test_method": mock_tracker_func},
        )

        wrapped = proxy._wrap_method(failing_method, "test_method")

        # Call should raise the original exception
        with pytest.raises(ValueError, match="Method failed"):
            wrapped()

        # Tracker should be called with error information when method fails
        mock_tracker_func.assert_called_once()
        call_args = mock_tracker_func.call_args[1]
        assert call_args["error_occurred"] is True
        assert call_args["error_type"] == "unknown_error"
        assert call_args["error_message"] == "Method failed"

    def test_wrap_method_tracker_exception_handling(self):
        """Test _wrap_method handles tracker exceptions gracefully"""
        mock_method = Mock(return_value="result")
        mock_tracker_func = Mock(side_effect=Exception("Tracker failed"))

        proxy = TrackedProxy(
            client=self.mock_client,
            tracker=self.mock_tracker,
            track_methods={"test_method": mock_tracker_func},
        )

        wrapped = proxy._wrap_method(mock_method, "test_method")

        with patch("cmdrdata_openai.proxy.logger") as mock_logger:
            # Should not raise exception even if tracker fails
            result = wrapped()

            # Original method should still return its result
            assert result == "result"

            # Warning should be logged
            mock_logger.warning.assert_called_once()

    def test_repr_method(self):
        """Test __repr__ method"""
        proxy = TrackedProxy(
            client=self.mock_client, tracker=self.mock_tracker, track_methods={}
        )

        repr_str = repr(proxy)
        assert "TrackedProxy" in repr_str
        assert repr(self.mock_client) in repr_str


class TestTrackingFunctions:
    """Test suite for tracking functions"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_tracker = Mock()
        self.mock_result = Mock()
        self.mock_result.model = "gpt-5"
        self.mock_result.usage = Mock()
        self.mock_result.usage.prompt_tokens = 10
        self.mock_result.usage.completion_tokens = 15
        self.mock_result.id = "chatcmpl-test123"
        self.mock_result.created = 1234567890
        self.mock_result.choices = [Mock()]
        self.mock_result.choices[0].finish_reason = "stop"

    def test_track_chat_completion_success(self):
        """Test successful chat completion tracking"""
        with patch(
            "cmdrdata_openai.proxy.get_effective_customer_id"
        ) as mock_get_customer:
            mock_get_customer.return_value = "test-customer"

            track_chat_completion(
                result=self.mock_result,
                customer_id="test-customer",
                tracker=self.mock_tracker,
                method_name="chat.completions.create",
                args=(),
                kwargs={"model": "gpt-5"},
            )

            # Verify tracker was called
            self.mock_tracker.track_usage_background.assert_called_once()
            call_kwargs = self.mock_tracker.track_usage_background.call_args[1]

            assert call_kwargs["customer_id"] == "test-customer"
            assert call_kwargs["model"] == "gpt-5"
            assert call_kwargs["input_tokens"] == 10
            assert call_kwargs["output_tokens"] == 15
            assert call_kwargs["provider"] == "openai"
            assert call_kwargs["metadata"]["response_id"] == "chatcmpl-test123"
            assert call_kwargs["metadata"]["finish_reason"] == "stop"

    def test_track_chat_completion_no_customer_id(self):
        """Test chat completion tracking without customer ID"""
        with patch(
            "cmdrdata_openai.proxy.get_effective_customer_id"
        ) as mock_get_customer:
            with patch("cmdrdata_openai.proxy.logger") as mock_logger:
                mock_get_customer.return_value = None

                track_chat_completion(
                    result=self.mock_result,
                    customer_id=None,
                    tracker=self.mock_tracker,
                    method_name="chat.completions.create",
                    args=(),
                    kwargs={},
                )

                # Verify warning was logged
                mock_logger.warning.assert_called_once_with(
                    "No customer_id provided for tracking. Set customer_id parameter or use set_customer_context()"
                )

                # Verify tracker was NOT called
                self.mock_tracker.track_usage_background.assert_not_called()

    def test_track_chat_completion_no_usage_data(self):
        """Test chat completion tracking without usage data"""
        self.mock_result.usage = None

        with patch(
            "cmdrdata_openai.proxy.get_effective_customer_id"
        ) as mock_get_customer:
            mock_get_customer.return_value = "test-customer"

            track_chat_completion(
                result=self.mock_result,
                customer_id="test-customer",
                tracker=self.mock_tracker,
                method_name="chat.completions.create",
                args=(),
                kwargs={},
            )

            # Verify tracker was NOT called (no usage data)
            self.mock_tracker.track_usage_background.assert_not_called()

    def test_track_chat_completion_exception_handling(self):
        """Test chat completion tracking handles exceptions gracefully"""
        # Make the result object raise an exception
        self.mock_result.usage = Mock()
        self.mock_result.usage.prompt_tokens = 10
        # Remove completion_tokens to cause AttributeError
        del self.mock_result.usage.completion_tokens

        with patch(
            "cmdrdata_openai.proxy.get_effective_customer_id"
        ) as mock_get_customer:
            with patch("cmdrdata_openai.proxy.logger") as mock_logger:
                mock_get_customer.return_value = "test-customer"

                # Should not raise exception
                track_chat_completion(
                    result=self.mock_result,
                    customer_id="test-customer",
                    tracker=self.mock_tracker,
                    method_name="chat.completions.create",
                    args=(),
                    kwargs={},
                )

                # Warning should be logged
                mock_logger.warning.assert_called_once()

    def test_track_completion_success(self):
        """Test successful legacy completion tracking"""
        # Modify result for legacy completion format
        self.mock_result.model = "text-davinci-003"

        with patch(
            "cmdrdata_openai.proxy.get_effective_customer_id"
        ) as mock_get_customer:
            mock_get_customer.return_value = "test-customer"

            track_completion(
                result=self.mock_result,
                customer_id="test-customer",
                tracker=self.mock_tracker,
                method_name="completions.create",
                args=(),
                kwargs={"model": "text-davinci-003"},
            )

            # Verify tracker was called
            self.mock_tracker.track_usage_background.assert_called_once()
            call_kwargs = self.mock_tracker.track_usage_background.call_args[1]

            assert call_kwargs["customer_id"] == "test-customer"
            assert call_kwargs["model"] == "text-davinci-003"
            assert call_kwargs["input_tokens"] == 10
            assert call_kwargs["output_tokens"] == 15
            assert call_kwargs["provider"] == "openai"

    def test_track_embeddings_success(self):
        """Test successful embeddings tracking"""
        # Set up embeddings response
        mock_embedding_result = Mock()
        mock_embedding_result.model = "text-embedding-ada-002"
        mock_embedding_result.usage = Mock()
        mock_embedding_result.usage.prompt_tokens = 100
        mock_embedding_result.data = [Mock()]
        mock_embedding_result.data[0].embedding = [0.1, 0.2, 0.3]
        mock_embedding_result.id = "emb_123"
        mock_embedding_result.created = 1234567890

        with patch(
            "cmdrdata_openai.proxy.get_effective_customer_id"
        ) as mock_get_customer:
            mock_get_customer.return_value = "test-customer"

            track_embeddings(
                result=mock_embedding_result,
                customer_id="test-customer",
                tracker=self.mock_tracker,
                method_name="embeddings.create",
                args=(),
                kwargs={"input": ["test text"], "model": "text-embedding-ada-002"},
            )

            # Verify tracker was called
            self.mock_tracker.track_usage_background.assert_called_once()
            call_kwargs = self.mock_tracker.track_usage_background.call_args[1]

            assert call_kwargs["customer_id"] == "test-customer"
            assert call_kwargs["model"] == "text-embedding-ada-002"
            assert call_kwargs["input_tokens"] == 100
            assert call_kwargs["output_tokens"] == 0
            assert call_kwargs["provider"] == "openai"
            assert call_kwargs["metadata"]["response_id"] == "emb_123"
            assert call_kwargs["metadata"]["created"] == 1234567890
            assert call_kwargs["metadata"]["embedding_count"] == 1

    def test_track_images_success(self):
        """Test successful image generation tracking"""
        # Set up image response
        mock_image_result = Mock()
        mock_image_result.data = [Mock(), Mock()]  # 2 images
        mock_image_result.data[0].url = "https://example.com/image1.png"
        mock_image_result.data[1].url = "https://example.com/image2.png"
        mock_image_result.created = 1234567890

        with patch(
            "cmdrdata_openai.proxy.get_effective_customer_id"
        ) as mock_get_customer:
            mock_get_customer.return_value = "test-customer"

            track_images(
                result=mock_image_result,
                customer_id="test-customer",
                tracker=self.mock_tracker,
                method_name="images.generate",
                args=(),
                kwargs={
                    "prompt": "a cat",
                    "n": 2,
                    "size": "1024x1024",
                    "model": "dall-e-3",
                },
            )

            # Verify tracker was called
            self.mock_tracker.track_usage_background.assert_called_once()
            call_kwargs = self.mock_tracker.track_usage_background.call_args[1]

            assert call_kwargs["customer_id"] == "test-customer"
            assert call_kwargs["model"] == "dall-e-3"
            assert call_kwargs["input_tokens"] == 0  # Images don't use text tokens
            assert call_kwargs["output_tokens"] == 0
            assert call_kwargs["provider"] == "openai"
            assert call_kwargs["metadata"]["image_count"] == 2
            assert call_kwargs["metadata"]["size"] == "1024x1024"
            assert call_kwargs["metadata"]["operation"] == "generate"
            assert call_kwargs["metadata"]["created"] == 1234567890

    def test_track_audio_success(self):
        """Test successful audio processing tracking"""
        # Set up audio transcription response
        mock_audio_result = Mock()
        mock_audio_result.text = "Hello, this is a transcription"

        with patch(
            "cmdrdata_openai.proxy.get_effective_customer_id"
        ) as mock_get_customer:
            mock_get_customer.return_value = "test-customer"

            track_audio(
                result=mock_audio_result,
                customer_id="test-customer",
                tracker=self.mock_tracker,
                method_name="audio.transcriptions.create",
                args=(),
                kwargs={"file": "audio.mp3", "model": "whisper-1", "language": "en"},
            )

            # Verify tracker was called
            self.mock_tracker.track_usage_background.assert_called_once()
            call_kwargs = self.mock_tracker.track_usage_background.call_args[1]

            assert call_kwargs["customer_id"] == "test-customer"
            assert call_kwargs["model"] == "whisper-1"
            assert call_kwargs["input_tokens"] == 0
            assert call_kwargs["output_tokens"] == 0
            assert call_kwargs["provider"] == "openai"
            assert call_kwargs["metadata"]["operation"] == "create"
            assert call_kwargs["metadata"]["text_length"] == 30
            assert call_kwargs["metadata"]["language"] == "en"

    def test_track_moderations_success(self):
        """Test successful moderation tracking"""
        # Set up moderation response
        mock_moderation_result = Mock()
        mock_moderation_result.results = [Mock()]
        mock_moderation_result.results[0].flagged = False
        mock_moderation_result.results[0].categories = Mock()
        mock_moderation_result.results[0].category_scores = Mock()
        mock_moderation_result.model = "text-moderation-latest"
        mock_moderation_result.id = "modr-123"

        with patch(
            "cmdrdata_openai.proxy.get_effective_customer_id"
        ) as mock_get_customer:
            mock_get_customer.return_value = "test-customer"

            track_moderations(
                result=mock_moderation_result,
                customer_id="test-customer",
                tracker=self.mock_tracker,
                method_name="moderations.create",
                args=(),
                kwargs={"input": "test content", "model": "text-moderation-latest"},
            )

            # Verify tracker was called
            self.mock_tracker.track_usage_background.assert_called_once()
            call_kwargs = self.mock_tracker.track_usage_background.call_args[1]

            assert call_kwargs["customer_id"] == "test-customer"
            assert call_kwargs["model"] == "text-moderation-latest"
            assert call_kwargs["input_tokens"] == 0
            assert call_kwargs["output_tokens"] == 0
            assert call_kwargs["provider"] == "openai"
            assert call_kwargs["metadata"]["flagged"] is False
            assert call_kwargs["metadata"]["response_id"] == "modr-123"

    def test_track_fine_tuning_success(self):
        """Test successful fine-tuning tracking"""
        # Set up fine-tuning job response
        mock_ft_result = Mock()
        mock_ft_result.id = "ftjob-123"
        mock_ft_result.model = "gpt-5"
        mock_ft_result.training_file = "file-123"
        mock_ft_result.status = "queued"
        mock_ft_result.created_at = 1234567890

        with patch(
            "cmdrdata_openai.proxy.get_effective_customer_id"
        ) as mock_get_customer:
            mock_get_customer.return_value = "test-customer"

            track_fine_tuning(
                result=mock_ft_result,
                customer_id="test-customer",
                tracker=self.mock_tracker,
                method_name="fine_tuning.jobs.create",
                args=(),
                kwargs={"training_file": "file-123", "model": "gpt-5"},
            )

            # Verify tracker was called
            self.mock_tracker.track_usage_background.assert_called_once()
            call_kwargs = self.mock_tracker.track_usage_background.call_args[1]

            assert call_kwargs["customer_id"] == "test-customer"
            assert call_kwargs["model"] == "gpt-5"
            assert call_kwargs["input_tokens"] == 0
            assert call_kwargs["output_tokens"] == 0
            assert call_kwargs["provider"] == "openai"
            assert call_kwargs["metadata"]["job_id"] == "ftjob-123"
            assert call_kwargs["metadata"]["training_file"] == "file-123"
            assert call_kwargs["metadata"]["status"] == "queued"
            assert call_kwargs["metadata"]["model"] == "gpt-5"

    def test_track_assistant_run_success(self):
        """Test successful assistant run tracking"""
        # Set up assistant run response
        mock_run_result = Mock()
        mock_run_result.id = "run_123"
        mock_run_result.assistant_id = "asst_123"
        mock_run_result.thread_id = "thread_123"
        mock_run_result.status = "queued"
        mock_run_result.model = "gpt-5"
        mock_run_result.usage = Mock()
        mock_run_result.usage.prompt_tokens = 50
        mock_run_result.usage.completion_tokens = 100
        mock_run_result.created_at = 1234567890

        with patch(
            "cmdrdata_openai.proxy.get_effective_customer_id"
        ) as mock_get_customer:
            mock_get_customer.return_value = "test-customer"

            track_assistant_run(
                result=mock_run_result,
                customer_id="test-customer",
                tracker=self.mock_tracker,
                method_name="beta.threads.runs.create",
                args=(),
                kwargs={"thread_id": "thread_123", "assistant_id": "asst_123"},
            )

            # Verify tracker was called
            self.mock_tracker.track_usage_background.assert_called_once()
            call_kwargs = self.mock_tracker.track_usage_background.call_args[1]

            assert call_kwargs["customer_id"] == "test-customer"
            assert call_kwargs["model"] == "gpt-5"
            assert call_kwargs["input_tokens"] == 50
            assert call_kwargs["output_tokens"] == 100
            assert call_kwargs["provider"] == "openai"
            assert call_kwargs["metadata"]["run_id"] == "run_123"
            assert call_kwargs["metadata"]["assistant_id"] == "asst_123"
            assert call_kwargs["metadata"]["thread_id"] == "thread_123"
            assert call_kwargs["metadata"]["status"] == "queued"


class TestOpenAITrackMethods:
    """Test suite for OPENAI_TRACK_METHODS configuration"""

    def test_openai_track_methods_configuration(self):
        """Test OPENAI_TRACK_METHODS contains expected methods"""
        expected_methods = {
            "chat.completions.create": track_chat_completion,
            "completions.create": track_completion,
            "embeddings.create": track_embeddings,
            "images.generate": track_images,
            "images.edit": track_images,
            "images.create_variation": track_images,
            "audio.transcriptions.create": track_audio,
            "audio.translations.create": track_audio,
            "audio.speech.create": track_audio,
            "moderations.create": track_moderations,
            "fine_tuning.jobs.create": track_fine_tuning,
            "beta.threads.runs.create": track_assistant_run,
            "beta.threads.runs.create_and_poll": track_assistant_run,
        }

        for method_name, expected_function in expected_methods.items():
            assert method_name in OPENAI_TRACK_METHODS, f"Missing method: {method_name}"
            assert callable(
                OPENAI_TRACK_METHODS[method_name]
            ), f"Method {method_name} not callable"
            assert (
                OPENAI_TRACK_METHODS[method_name] == expected_function
            ), f"Wrong function for {method_name}"

        # Verify we have the expected total count
        assert (
            len(OPENAI_TRACK_METHODS) == 13
        ), f"Expected 13 methods, got {len(OPENAI_TRACK_METHODS)}"

    def test_proxy_integration_all_methods(self):
        """Test that all tracking methods work through proxy integration"""
        mock_client = Mock()
        mock_tracker = Mock()

        # Set up nested mock structure for OpenAI client
        mock_client.chat = Mock()
        mock_client.chat.completions = Mock()
        mock_client.chat.completions.create = Mock(return_value="chat_result")

        mock_client.completions = Mock()
        mock_client.completions.create = Mock(return_value="completion_result")

        mock_client.embeddings = Mock()
        mock_client.embeddings.create = Mock(return_value="embedding_result")

        mock_client.images = Mock()
        mock_client.images.generate = Mock(return_value="image_result")
        mock_client.images.edit = Mock(return_value="image_edit_result")
        mock_client.images.create_variation = Mock(return_value="image_var_result")

        mock_client.audio = Mock()
        mock_client.audio.transcriptions = Mock()
        mock_client.audio.transcriptions.create = Mock(
            return_value="transcription_result"
        )
        mock_client.audio.translations = Mock()
        mock_client.audio.translations.create = Mock(return_value="translation_result")
        mock_client.audio.speech = Mock()
        mock_client.audio.speech.create = Mock(return_value="speech_result")

        mock_client.moderations = Mock()
        mock_client.moderations.create = Mock(return_value="moderation_result")

        mock_client.fine_tuning = Mock()
        mock_client.fine_tuning.jobs = Mock()
        mock_client.fine_tuning.jobs.create = Mock(return_value="ft_result")

        mock_client.beta = Mock()
        mock_client.beta.threads = Mock()
        mock_client.beta.threads.runs = Mock()
        mock_client.beta.threads.runs.create = Mock(return_value="run_result")
        mock_client.beta.threads.runs.create_and_poll = Mock(
            return_value="run_poll_result"
        )

        proxy = TrackedProxy(
            client=mock_client, tracker=mock_tracker, track_methods=OPENAI_TRACK_METHODS
        )

        # Test each method through proxy
        test_cases = [
            (lambda: proxy.chat.completions.create(), "chat_result"),
            (lambda: proxy.completions.create(), "completion_result"),
            (lambda: proxy.embeddings.create(), "embedding_result"),
            (lambda: proxy.images.generate(), "image_result"),
            (lambda: proxy.images.edit(), "image_edit_result"),
            (lambda: proxy.images.create_variation(), "image_var_result"),
            (lambda: proxy.audio.transcriptions.create(), "transcription_result"),
            (lambda: proxy.audio.translations.create(), "translation_result"),
            (lambda: proxy.audio.speech.create(), "speech_result"),
            (lambda: proxy.moderations.create(), "moderation_result"),
            (lambda: proxy.fine_tuning.jobs.create(), "ft_result"),
            (lambda: proxy.beta.threads.runs.create(), "run_result"),
            (lambda: proxy.beta.threads.runs.create_and_poll(), "run_poll_result"),
        ]

        for test_func, expected_result in test_cases:
            result = test_func()
            assert result == expected_result


if __name__ == "__main__":
    pytest.main([__file__])
