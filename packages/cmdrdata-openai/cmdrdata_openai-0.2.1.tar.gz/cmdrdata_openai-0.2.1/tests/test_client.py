"""
Unit tests for TrackedOpenAI client
"""

import os
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from cmdrdata_openai import TrackedOpenAI
from cmdrdata_openai.exceptions import ConfigurationError, ValidationError
from cmdrdata_openai.tracker import UsageTracker


class TestTrackedOpenAI:
    """Test suite for TrackedOpenAI client"""

    def setup_method(self):
        """Set up test fixtures"""
        self.valid_openai_key = "sk-" + "a" * 48
        self.valid_tracker_key = "tk-" + "a" * 32
        self.mock_openai_client = Mock()
        self.mock_tracker = Mock(spec=UsageTracker)

    @patch("cmdrdata_openai.client.OpenAI")
    @patch("cmdrdata_openai.client.UsageTracker")
    def test_initialization_success(self, mock_tracker_class, mock_openai_class):
        """Test successful TrackedOpenAI initialization"""
        mock_openai_class.return_value = self.mock_openai_client
        mock_tracker_class.return_value = self.mock_tracker

        client = TrackedOpenAI(
            api_key=self.valid_openai_key, tracker_key=self.valid_tracker_key
        )

        # Verify OpenAI client was created
        mock_openai_class.assert_called_once_with(api_key=self.valid_openai_key)

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
            TrackedOpenAI(api_key=self.valid_openai_key)

    def test_initialization_invalid_api_key(self):
        """Test initialization with invalid API key"""
        # Invalid API key format should still initialize successfully
        # API key validation happens when making actual requests to OpenAI
        client = TrackedOpenAI(
            api_key="invalid-key", tracker_key=self.valid_tracker_key
        )
        assert client is not None

    @patch("cmdrdata_openai.client.OpenAI")
    @patch("cmdrdata_openai.client.UsageTracker")
    def test_initialization_custom_endpoint(
        self, mock_tracker_class, mock_openai_class
    ):
        """Test initialization with custom tracker endpoint"""
        mock_openai_class.return_value = self.mock_openai_client
        mock_tracker_class.return_value = self.mock_tracker

        custom_endpoint = "https://custom.example.com/api/events"

        TrackedOpenAI(
            api_key=self.valid_openai_key,
            tracker_key=self.valid_tracker_key,
            tracker_endpoint=custom_endpoint,
            tracker_timeout=10.0,
        )

        mock_tracker_class.assert_called_once_with(
            api_key=self.valid_tracker_key, endpoint=custom_endpoint, timeout=10.0
        )

    @patch("cmdrdata_openai.client.OpenAI")
    @patch("cmdrdata_openai.client.UsageTracker")
    def test_get_openai_client(self, mock_tracker_class, mock_openai_class):
        """Test getting the underlying OpenAI client"""
        mock_openai_class.return_value = self.mock_openai_client
        mock_tracker_class.return_value = self.mock_tracker

        client = TrackedOpenAI(
            api_key=self.valid_openai_key, tracker_key=self.valid_tracker_key
        )

        underlying_client = client.get_openai_client()
        assert underlying_client is self.mock_openai_client

    @patch("cmdrdata_openai.client.OpenAI")
    @patch("cmdrdata_openai.client.UsageTracker")
    def test_get_tracker(self, mock_tracker_class, mock_openai_class):
        """Test getting the tracker instance"""
        mock_openai_class.return_value = self.mock_openai_client
        mock_tracker_class.return_value = self.mock_tracker

        client = TrackedOpenAI(
            api_key=self.valid_openai_key, tracker_key=self.valid_tracker_key
        )

        tracker = client.get_tracker()
        assert tracker is self.mock_tracker

    def test_compatibility_check_warning(self):
        """Test compatibility warning mechanism"""
        import warnings

        from cmdrdata_openai.version_compat import VersionCompatibility

        # Test with a version that should trigger a warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # Create instance and manually set version to trigger warning
            compat = VersionCompatibility()
            compat.openai_version = "0.9.0"  # Below minimum version
            compat._validate_openai_version()

            # Check if warning was emitted
            assert len(w) > 0
            assert "below minimum supported version" in str(w[0].message)

    @patch("cmdrdata_openai.client.OpenAI")
    @patch("cmdrdata_openai.client.UsageTracker")
    def test_check_compatibility_method(self, mock_tracker_class, mock_openai_class):
        """Test compatibility check method"""
        mock_openai_class.return_value = self.mock_openai_client
        mock_tracker_class.return_value = self.mock_tracker

        with patch("cmdrdata_openai.client.check_compatibility") as mock_check:
            mock_check.return_value = True

            result = TrackedOpenAI.check_compatibility()
            assert result is True
            mock_check.assert_called_once()

    @patch("cmdrdata_openai.client.OpenAI")
    @patch("cmdrdata_openai.client.UsageTracker")
    def test_check_compatibility_raise_on_incompatible(
        self, mock_tracker_class, mock_openai_class
    ):
        """Test compatibility check with raise on incompatible"""
        mock_openai_class.return_value = self.mock_openai_client
        mock_tracker_class.return_value = self.mock_tracker

        with patch("cmdrdata_openai.client.check_compatibility") as mock_check:
            with patch("cmdrdata_openai.client.get_compatibility_info") as mock_info:
                mock_check.return_value = False
                mock_info.return_value = {
                    "openai": {
                        "installed": "0.28.0",
                        "min_supported": "1.0.0",
                        "max_supported": "2.0.0",
                    }
                }

                with pytest.raises(RuntimeError, match="is not compatible"):
                    TrackedOpenAI.check_compatibility(raise_on_incompatible=True)

    @patch("cmdrdata_openai.client.OpenAI")
    @patch("cmdrdata_openai.client.UsageTracker")
    def test_get_compatibility_info_method(self, mock_tracker_class, mock_openai_class):
        """Test get compatibility info method"""
        mock_openai_class.return_value = self.mock_openai_client
        mock_tracker_class.return_value = self.mock_tracker

        with patch("cmdrdata_openai.client.get_compatibility_info") as mock_info:
            expected_info = {"openai": {"version": "1.0.0"}}
            mock_info.return_value = expected_info

            result = TrackedOpenAI.get_compatibility_info()
            assert result == expected_info
            mock_info.assert_called_once()


class TestTrackedOpenAIIntegration:
    """Integration tests for TrackedOpenAI client"""

    def setup_method(self):
        """Set up test fixtures"""
        self.valid_openai_key = "sk-" + "a" * 48
        self.valid_tracker_key = "tk-" + "a" * 32

    @patch("cmdrdata_openai.client.OpenAI")
    @patch("cmdrdata_openai.client.UsageTracker")
    def test_proxy_method_delegation(self, mock_tracker_class, mock_openai_class):
        """Test that methods are properly delegated to OpenAI client"""
        mock_openai_instance = Mock()
        mock_openai_class.return_value = mock_openai_instance
        mock_tracker_class.return_value = Mock()

        # Mock a method on the OpenAI client
        mock_openai_instance.models = Mock()
        mock_openai_instance.models.list = Mock(return_value="model_list_result")

        client = TrackedOpenAI(
            api_key=self.valid_openai_key, tracker_key=self.valid_tracker_key
        )

        # Access the models.list method through the proxy
        result = client.models.list()

        # Verify the method was called on the underlying client
        mock_openai_instance.models.list.assert_called_once()
        assert result == "model_list_result"

    @patch("cmdrdata_openai.client.OpenAI")
    @patch("cmdrdata_openai.client.UsageTracker")
    def test_tracked_method_with_usage_tracking(
        self, mock_tracker_class, mock_openai_class
    ):
        """Test that tracked methods properly invoke usage tracking"""
        mock_openai_instance = Mock()
        mock_openai_class.return_value = mock_openai_instance
        mock_tracker_instance = Mock()
        mock_tracker_class.return_value = mock_tracker_instance

        # Mock the chat completion response
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

        # Mock the OpenAI client's chat completion method
        mock_openai_instance.chat = Mock()
        mock_openai_instance.chat.completions = Mock()
        mock_openai_instance.chat.completions.create = Mock(return_value=mock_response)

        client = TrackedOpenAI(
            api_key=self.valid_openai_key, tracker_key=self.valid_tracker_key
        )

        # Make a tracked call
        result = client.chat.completions.create(
            model="gpt-5",
            messages=[{"role": "user", "content": "Hello"}],
            customer_id="test-customer",
        )

        # Verify the OpenAI method was called
        mock_openai_instance.chat.completions.create.assert_called_once_with(
            model="gpt-5", messages=[{"role": "user", "content": "Hello"}]
        )

        # Verify the response is returned
        assert result == mock_response

        # Verify tracking was attempted (the actual tracking logic is tested separately)
        assert mock_tracker_instance.track_usage_background.called


if __name__ == "__main__":
    pytest.main([__file__])
