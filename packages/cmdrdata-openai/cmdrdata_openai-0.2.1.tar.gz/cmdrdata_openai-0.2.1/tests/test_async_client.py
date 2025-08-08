"""
Unit tests for AsyncTrackedOpenAI client
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from cmdrdata_openai import AsyncTrackedOpenAI
from cmdrdata_openai.exceptions import ValidationError


class TestAsyncTrackedOpenAI:
    """Test suite for AsyncTrackedOpenAI client"""

    def setup_method(self):
        """Set up test fixtures"""
        self.valid_openai_key = "sk-" + "a" * 48
        self.valid_tracker_key = "tk-" + "a" * 32
        self.mock_async_openai_client = Mock()
        self.mock_tracker = Mock()

    @patch("cmdrdata_openai.async_client.AsyncOpenAI")
    @patch("cmdrdata_openai.async_client.UsageTracker")
    def test_initialization_success(self, mock_tracker_class, mock_async_openai_class):
        """Test successful AsyncTrackedOpenAI initialization"""
        mock_async_openai_class.return_value = self.mock_async_openai_client
        mock_tracker_class.return_value = self.mock_tracker

        client = AsyncTrackedOpenAI(
            api_key=self.valid_openai_key, tracker_key=self.valid_tracker_key
        )

        # Verify AsyncOpenAI client was created
        mock_async_openai_class.assert_called_once_with(api_key=self.valid_openai_key)

        # Verify tracker was created
        mock_tracker_class.assert_called_once_with(
            api_key=self.valid_tracker_key,
            endpoint="https://api.cmdrdata.ai/api/events",
            timeout=5.0,
        )

        assert client is not None

    def test_initialization_missing_tracker_key(self):
        """Test initialization failure when tracker_key is missing"""
        with pytest.raises(ValueError, match="tracker_key is required"):
            AsyncTrackedOpenAI(api_key=self.valid_openai_key)

    @patch("cmdrdata_openai.async_client.AsyncOpenAI")
    @patch("cmdrdata_openai.async_client.UsageTracker")
    def test_initialization_custom_endpoint(
        self, mock_tracker_class, mock_async_openai_class
    ):
        """Test initialization with custom tracker endpoint"""
        mock_async_openai_class.return_value = self.mock_async_openai_client
        mock_tracker_class.return_value = self.mock_tracker

        custom_endpoint = "https://custom.example.com/api/events"

        AsyncTrackedOpenAI(
            api_key=self.valid_openai_key,
            tracker_key=self.valid_tracker_key,
            tracker_endpoint=custom_endpoint,
            tracker_timeout=10.0,
        )

        mock_tracker_class.assert_called_once_with(
            api_key=self.valid_tracker_key, endpoint=custom_endpoint, timeout=10.0
        )

    @patch("cmdrdata_openai.async_client.AsyncOpenAI")
    @patch("cmdrdata_openai.async_client.UsageTracker")
    def test_get_openai_client(self, mock_tracker_class, mock_async_openai_class):
        """Test getting the underlying AsyncOpenAI client"""
        mock_async_openai_class.return_value = self.mock_async_openai_client
        mock_tracker_class.return_value = self.mock_tracker

        client = AsyncTrackedOpenAI(
            api_key=self.valid_openai_key, tracker_key=self.valid_tracker_key
        )

        underlying_client = client.get_openai_client()
        assert underlying_client is self.mock_async_openai_client

    @patch("cmdrdata_openai.async_client.AsyncOpenAI")
    @patch("cmdrdata_openai.async_client.UsageTracker")
    def test_get_tracker(self, mock_tracker_class, mock_async_openai_class):
        """Test getting the tracker instance"""
        mock_async_openai_class.return_value = self.mock_async_openai_client
        mock_tracker_class.return_value = self.mock_tracker

        client = AsyncTrackedOpenAI(
            api_key=self.valid_openai_key, tracker_key=self.valid_tracker_key
        )

        tracker = client.get_tracker()
        assert tracker is self.mock_tracker

    @patch("cmdrdata_openai.async_client.AsyncOpenAI")
    @patch("cmdrdata_openai.async_client.UsageTracker")
    def test_attribute_delegation(self, mock_tracker_class, mock_async_openai_class):
        """Test that attributes are properly delegated to AsyncOpenAI client"""
        mock_async_openai_class.return_value = self.mock_async_openai_client
        mock_tracker_class.return_value = self.mock_tracker

        # Mock some attributes on the AsyncOpenAI client
        self.mock_async_openai_client.models = Mock()
        self.mock_async_openai_client.fine_tuning = Mock()

        client = AsyncTrackedOpenAI(
            api_key=self.valid_openai_key, tracker_key=self.valid_tracker_key
        )

        # Test attribute delegation
        assert client.models is self.mock_async_openai_client.models
        assert client.fine_tuning is self.mock_async_openai_client.fine_tuning


class TestAsyncTrackedChatCompletions:
    """Test suite for AsyncTrackedChatCompletions"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_openai_completions = Mock()
        self.mock_tracker = Mock()

    @pytest.mark.asyncio
    async def test_create_with_tracking_success(self):
        """Test successful chat completion with tracking"""
        from cmdrdata_openai.async_client import AsyncTrackedChatCompletions

        # Mock the response
        mock_response = Mock()
        mock_response.model = "gpt-5"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 15
        mock_response.usage.total_tokens = 25
        mock_response.id = "chatcmpl-test123"
        mock_response.created = 1234567890
        mock_response.choices = [Mock()]
        mock_response.choices[0].finish_reason = "stop"

        # Mock the OpenAI completion call
        self.mock_openai_completions.create = AsyncMock(return_value=mock_response)

        # Mock the tracker
        self.mock_tracker.track_usage_async = AsyncMock(return_value=True)

        completions = AsyncTrackedChatCompletions(
            self.mock_openai_completions, self.mock_tracker
        )

        # Test the call
        result = await completions.create(
            model="gpt-5",
            messages=[{"role": "user", "content": "Hello"}],
            customer_id="test-customer",
        )

        # Verify OpenAI was called
        self.mock_openai_completions.create.assert_called_once_with(
            model="gpt-5", messages=[{"role": "user", "content": "Hello"}]
        )

        # Verify tracking was called
        self.mock_tracker.track_usage_async.assert_called_once()

        # Verify response is returned
        assert result == mock_response

    @pytest.mark.asyncio
    async def test_create_without_tracking(self):
        """Test chat completion without tracking"""
        from cmdrdata_openai.async_client import AsyncTrackedChatCompletions

        # Mock the response
        mock_response = Mock()
        mock_response.model = "gpt-5"

        # Mock the OpenAI completion call
        self.mock_openai_completions.create = AsyncMock(return_value=mock_response)

        completions = AsyncTrackedChatCompletions(
            self.mock_openai_completions, self.mock_tracker
        )

        # Test the call with tracking disabled
        result = await completions.create(
            model="gpt-5",
            messages=[{"role": "user", "content": "Hello"}],
            track_usage=False,
        )

        # Verify OpenAI was called
        self.mock_openai_completions.create.assert_called_once_with(
            model="gpt-5", messages=[{"role": "user", "content": "Hello"}]
        )

        # Verify tracking was NOT called
        self.mock_tracker.track_usage_async.assert_not_called()

        # Verify response is returned
        assert result == mock_response

    @pytest.mark.asyncio
    async def test_create_no_customer_id(self):
        """Test chat completion without customer ID logs warning"""
        from cmdrdata_openai.async_client import AsyncTrackedChatCompletions

        # Mock the response
        mock_response = Mock()
        mock_response.model = "gpt-5"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 15

        # Mock the OpenAI completion call
        self.mock_openai_completions.create = AsyncMock(return_value=mock_response)

        completions = AsyncTrackedChatCompletions(
            self.mock_openai_completions, self.mock_tracker
        )

        with patch("cmdrdata_openai.async_client.logger") as mock_logger:
            # Test the call without customer_id
            result = await completions.create(
                model="gpt-5", messages=[{"role": "user", "content": "Hello"}]
            )

            # Verify warning was logged
            mock_logger.warning.assert_called_once_with(
                "No customer_id provided for usage tracking"
            )

        # Verify tracking was NOT called
        self.mock_tracker.track_usage_async.assert_not_called()

        # Verify response is returned
        assert result == mock_response

    @pytest.mark.asyncio
    async def test_create_no_usage_data(self):
        """Test chat completion without usage data in response"""
        from cmdrdata_openai.async_client import AsyncTrackedChatCompletions

        # Mock the response without usage data
        mock_response = Mock()
        mock_response.model = "gpt-5"
        mock_response.usage = None

        # Mock the OpenAI completion call
        self.mock_openai_completions.create = AsyncMock(return_value=mock_response)

        completions = AsyncTrackedChatCompletions(
            self.mock_openai_completions, self.mock_tracker
        )

        # Test the call
        result = await completions.create(
            model="gpt-5",
            messages=[{"role": "user", "content": "Hello"}],
            customer_id="test-customer",
        )

        # Verify tracking was NOT called (no usage data)
        self.mock_tracker.track_usage_async.assert_not_called()

        # Verify response is returned
        assert result == mock_response


class TestAsyncTrackedCompletions:
    """Test suite for AsyncTrackedCompletions (legacy completions)"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_openai_completions = Mock()
        self.mock_tracker = Mock()

    @pytest.mark.asyncio
    async def test_create_with_tracking_success(self):
        """Test successful legacy completion with tracking"""
        from cmdrdata_openai.async_client import AsyncTrackedCompletions

        # Mock the response
        mock_response = Mock()
        mock_response.model = "text-davinci-003"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 15
        mock_response.usage.total_tokens = 25
        mock_response.id = "cmpl-test123"
        mock_response.created = 1234567890
        mock_response.choices = [Mock()]
        mock_response.choices[0].finish_reason = "stop"

        # Mock the OpenAI completion call
        self.mock_openai_completions.create = AsyncMock(return_value=mock_response)

        # Mock the tracker
        self.mock_tracker.track_usage_async = AsyncMock(return_value=True)

        completions = AsyncTrackedCompletions(
            self.mock_openai_completions, self.mock_tracker
        )

        # Test the call
        result = await completions.create(
            model="text-davinci-003", prompt="Hello", customer_id="test-customer"
        )

        # Verify OpenAI was called
        self.mock_openai_completions.create.assert_called_once_with(
            model="text-davinci-003", prompt="Hello"
        )

        # Verify tracking was called
        self.mock_tracker.track_usage_async.assert_called_once()

        # Verify response is returned
        assert result == mock_response


class TestAsyncTrackedChat:
    """Test suite for AsyncTrackedChat"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_openai_chat = Mock()
        self.mock_tracker = Mock()

    def test_initialization(self):
        """Test AsyncTrackedChat initialization"""
        from cmdrdata_openai.async_client import AsyncTrackedChat

        # Mock completions attribute
        self.mock_openai_chat.completions = Mock()

        chat = AsyncTrackedChat(self.mock_openai_chat, self.mock_tracker)

        # Verify completions wrapper was created
        assert hasattr(chat, "completions")
        assert chat.completions is not None


if __name__ == "__main__":
    pytest.main([__file__])
