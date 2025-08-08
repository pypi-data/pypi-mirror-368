"""
Unit tests for UsageTracker
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from cmdrdata_openai.exceptions import NetworkError, TrackingError, ValidationError
from cmdrdata_openai.tracker import UsageTracker


class TestUsageTracker:
    """Test suite for UsageTracker"""

    def setup_method(self):
        """Set up test fixtures"""
        self.valid_api_key = "tk-" + "a" * 32
        self.valid_endpoint = "https://api.example.com/events"
        self.customer_id = "test-customer-123"
        self.model = "gpt-5"
        self.input_tokens = 10
        self.output_tokens = 15

    def test_initialization_success(self):
        """Test successful UsageTracker initialization"""
        tracker = UsageTracker(
            api_key=self.valid_api_key,
            endpoint=self.valid_endpoint,
            timeout=10.0,
            max_retries=5,
        )

        assert tracker.api_key == self.valid_api_key
        assert tracker.endpoint == self.valid_endpoint
        assert tracker.timeout == 10.0
        assert tracker.max_retries == 5
        assert "Authorization" in tracker.headers
        assert tracker.headers["Authorization"] == f"Bearer {self.valid_api_key}"
        assert tracker.headers["Content-Type"] == "application/json"
        assert tracker.headers["User-Agent"] == "cmdrdata-openai/0.1.0"

    def test_initialization_missing_api_key(self):
        """Test initialization failure when API key is missing"""
        with pytest.raises(ValidationError, match="API key is required"):
            UsageTracker(api_key="")

    def test_initialization_invalid_api_key_format(self):
        """Test initialization with invalid API key format"""
        with pytest.raises(ValidationError, match="Invalid API key"):
            UsageTracker(api_key="invalid-key-format")

    def test_initialization_missing_endpoint(self):
        """Test initialization failure when endpoint is missing"""
        with pytest.raises(ValidationError, match="Endpoint is required"):
            UsageTracker(api_key=self.valid_api_key, endpoint="")

    def test_initialization_invalid_endpoint(self):
        """Test initialization with invalid endpoint URL"""
        with pytest.raises(ValidationError, match="Invalid endpoint URL"):
            UsageTracker(api_key=self.valid_api_key, endpoint="not-a-valid-url")

    def test_initialization_invalid_timeout(self):
        """Test initialization with invalid timeout"""
        with pytest.raises(ValidationError, match="Invalid timeout"):
            UsageTracker(api_key=self.valid_api_key, timeout=-1)

    def test_initialization_default_values(self):
        """Test initialization with default values"""
        tracker = UsageTracker(api_key=self.valid_api_key)

        assert tracker.endpoint == "https://api.cmdrdata.ai/api/events"
        assert tracker.timeout == 5.0
        assert tracker.max_retries == 3

    def test_validate_tracking_inputs_success(self):
        """Test successful input validation"""
        tracker = UsageTracker(api_key=self.valid_api_key)

        # Should not raise any exceptions
        tracker._validate_tracking_inputs(
            customer_id=self.customer_id,
            model=self.model,
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            provider="openai",
            metadata={"test": "value"},
        )

    def test_validate_tracking_inputs_missing_customer_id(self):
        """Test input validation with missing customer ID"""
        tracker = UsageTracker(api_key=self.valid_api_key)

        with pytest.raises(ValidationError, match="Customer ID is required"):
            tracker._validate_tracking_inputs(
                customer_id="",
                model=self.model,
                input_tokens=self.input_tokens,
                output_tokens=self.output_tokens,
                provider="openai",
                metadata=None,
            )

    def test_validate_tracking_inputs_invalid_tokens(self):
        """Test input validation with invalid token counts"""
        tracker = UsageTracker(api_key=self.valid_api_key)

        with pytest.raises(ValidationError, match="Token count cannot be negative"):
            tracker._validate_tracking_inputs(
                customer_id=self.customer_id,
                model=self.model,
                input_tokens=-1,
                output_tokens=self.output_tokens,
                provider="openai",
                metadata=None,
            )

    def test_validate_tracking_inputs_invalid_metadata(self):
        """Test input validation with invalid metadata"""
        tracker = UsageTracker(api_key=self.valid_api_key)

        with pytest.raises(ValidationError, match="Metadata must be a dictionary"):
            tracker._validate_tracking_inputs(
                customer_id=self.customer_id,
                model=self.model,
                input_tokens=self.input_tokens,
                output_tokens=self.output_tokens,
                provider="openai",
                metadata="invalid",
            )

    def test_sanitize_tracking_data(self):
        """Test data sanitization"""
        tracker = UsageTracker(api_key=self.valid_api_key)

        metadata = {"key1": "value1", "key2": 123}
        timestamp = datetime.utcnow()

        sanitized = tracker._sanitize_tracking_data(
            customer_id=self.customer_id,
            model=self.model,
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            provider="openai",
            metadata=metadata,
            timestamp=timestamp,
        )

        assert sanitized["customer_id"] == self.customer_id
        assert sanitized["model"] == self.model
        assert sanitized["input_tokens"] == self.input_tokens
        assert sanitized["output_tokens"] == self.output_tokens
        assert sanitized["total_tokens"] == self.input_tokens + self.output_tokens
        assert sanitized["provider"] == "openai"
        assert sanitized["metadata"] == metadata
        assert sanitized["timestamp"] == int(timestamp.timestamp())
        assert sanitized["version"] == "0.1.0"

    @patch("cmdrdata_openai.tracker.httpx")
    def test_track_usage_with_retry_success_httpx(self, mock_httpx):
        """Test successful usage tracking with httpx"""
        tracker = UsageTracker(api_key=self.valid_api_key)

        # Mock httpx client and response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.post.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        event_data = {
            "customer_id": self.customer_id,
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.input_tokens + self.output_tokens,
            "provider": "openai",
            "metadata": {},
            "timestamp": datetime.utcnow().isoformat(),
            "version": "0.1.0",
        }

        result = tracker._track_usage_with_retry(event_data)

        assert result is True
        mock_client.post.assert_called_once_with(
            tracker.endpoint, json=event_data, headers=tracker.headers
        )

    def test_track_usage_with_retry_success_requests(self):
        """Test successful usage tracking with requests fallback"""
        # Patch httpx to be None and mock the requests import
        with patch("cmdrdata_openai.tracker.httpx", None):
            # Mock the requests module that gets imported in the fallback path
            mock_requests = Mock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_requests.post.return_value = mock_response

            with patch.dict("sys.modules", {"requests": mock_requests}):
                tracker = UsageTracker(api_key=self.valid_api_key)

                event_data = {
                    "customer_id": self.customer_id,
                    "model": self.model,
                    "input_tokens": self.input_tokens,
                    "output_tokens": self.output_tokens,
                    "total_tokens": self.input_tokens + self.output_tokens,
                    "provider": "openai",
                    "metadata": {},
                    "timestamp": datetime.utcnow().isoformat(),
                    "version": "0.1.0",
                }

                result = tracker._track_usage_with_retry(event_data)

                assert result is True
                mock_requests.post.assert_called_once_with(
                    tracker.endpoint,
                    json=event_data,
                    headers=tracker.headers,
                    timeout=tracker.timeout,
                )

    @patch("cmdrdata_openai.tracker.httpx")
    def test_track_usage_with_retry_rate_limited(self, mock_httpx):
        """Test usage tracking with rate limit response"""
        tracker = UsageTracker(api_key=self.valid_api_key)

        # Mock httpx client and rate limit response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 429
        mock_client.post.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        event_data = {"test": "data"}

        with pytest.raises(
            TrackingError, match="Tracking failed after multiple retries"
        ):
            tracker._track_usage_with_retry(event_data)

    @patch("cmdrdata_openai.tracker.httpx")
    def test_track_usage_with_retry_server_error(self, mock_httpx):
        """Test usage tracking with server error response"""
        tracker = UsageTracker(api_key=self.valid_api_key)

        # Mock httpx client and server error response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_client.post.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        event_data = {"test": "data"}

        with pytest.raises(
            TrackingError, match="Tracking failed after multiple retries"
        ):
            tracker._track_usage_with_retry(event_data)

    @patch("cmdrdata_openai.tracker.httpx")
    def test_track_usage_with_retry_client_error(self, mock_httpx):
        """Test usage tracking with client error response"""
        tracker = UsageTracker(api_key=self.valid_api_key)

        # Mock httpx client and client error response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_client.post.return_value = mock_response
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        event_data = {"test": "data"}

        with pytest.raises(TrackingError, match="Client error"):
            tracker._track_usage_with_retry(event_data)

    @patch("cmdrdata_openai.tracker.httpx")
    def test_track_usage_with_retry_network_error(self, mock_httpx):
        """Test usage tracking with network error"""
        tracker = UsageTracker(api_key=self.valid_api_key, max_retries=1)

        # Mock httpx client to raise RequestError
        mock_client = Mock()
        mock_client.post.side_effect = Exception("Connection failed")
        mock_httpx.Client.return_value.__enter__.return_value = mock_client
        mock_httpx.RequestError = Exception

        event_data = {"test": "data"}

        with patch("time.sleep") as mock_sleep:
            with pytest.raises(
                TrackingError, match="Tracking failed after multiple retries"
            ):
                tracker._track_usage_with_retry(event_data)
            # Called for the initial attempt + 1 retry
            assert mock_client.post.call_count == 2
            mock_sleep.assert_called_once()

    @patch("cmdrdata_openai.tracker.httpx")
    def test_track_usage_retry_on_server_error_then_success(self, mock_httpx):
        """Test that the tracker retries on a 500 error and then succeeds."""
        tracker = UsageTracker(api_key=self.valid_api_key, max_retries=2)

        mock_client = Mock()
        # First call fails with 500, second call succeeds with 200
        mock_response_fail = Mock(status_code=500, text="Server Error")
        mock_response_success = Mock(status_code=200)
        mock_client.post.side_effect = [mock_response_fail, mock_response_success]
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        event_data = {"test": "data"}

        with patch("time.sleep") as mock_sleep:
            result = tracker._track_usage_with_retry(event_data)
            assert result is True
            assert mock_client.post.call_count == 2
            mock_sleep.assert_called_once()

    @patch("cmdrdata_openai.tracker.httpx")
    def test_track_usage_no_retry_on_client_error(self, mock_httpx):
        """Test that the tracker does not retry on a 400 client error."""
        tracker = UsageTracker(api_key=self.valid_api_key, max_retries=2)

        mock_client = Mock()
        mock_response_fail = Mock(status_code=400, text="Bad Request")
        mock_client.post.return_value = mock_response_fail
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        event_data = {"test": "data"}

        with patch("time.sleep") as mock_sleep:
            with pytest.raises(TrackingError, match="Client error: 400 Bad Request"):
                tracker._track_usage_with_retry(event_data)
            # Should only be called once, no retries
            assert mock_client.post.call_count == 1
            mock_sleep.assert_not_called()

    @patch("cmdrdata_openai.tracker.httpx")
    def test_track_usage_exhausts_retries(self, mock_httpx):
        """Test that the tracker gives up after exhausting all retries."""
        tracker = UsageTracker(api_key=self.valid_api_key, max_retries=2)

        mock_client = Mock()
        mock_response_fail = Mock(status_code=503, text="Service Unavailable")
        # All calls will fail
        mock_client.post.side_effect = [
            mock_response_fail,
            mock_response_fail,
            mock_response_fail,
        ]
        mock_httpx.Client.return_value.__enter__.return_value = mock_client

        event_data = {"test": "data"}

        with patch("time.sleep") as mock_sleep:
            with pytest.raises(
                TrackingError, match="Tracking failed after multiple retries"
            ):
                tracker._track_usage_with_retry(event_data)
            # Initial call + 2 retries
            assert mock_client.post.call_count == 3
            assert mock_sleep.call_count == 2

    def test_track_usage_success(self):
        """Test successful track_usage method"""
        tracker = UsageTracker(api_key=self.valid_api_key)

        with patch.object(tracker, "_validate_tracking_inputs") as mock_validate:
            with patch.object(tracker, "_sanitize_tracking_data") as mock_sanitize:
                with patch.object(tracker, "_track_usage_with_retry") as mock_track:
                    mock_sanitize.return_value = {"sanitized": "data"}
                    mock_track.return_value = True

                    result = tracker.track_usage(
                        customer_id=self.customer_id,
                        model=self.model,
                        input_tokens=self.input_tokens,
                        output_tokens=self.output_tokens,
                    )

                    assert result is True
                    mock_validate.assert_called_once()
                    mock_sanitize.assert_called_once()
                    mock_track.assert_called_once_with({"sanitized": "data"})

    def test_track_usage_validation_error(self):
        """Test track_usage with validation error"""
        tracker = UsageTracker(api_key=self.valid_api_key)

        with pytest.raises(ValidationError):
            tracker.track_usage(
                customer_id="",  # Invalid customer ID
                model=self.model,
                input_tokens=self.input_tokens,
                output_tokens=self.output_tokens,
            )

    @pytest.mark.asyncio
    async def test_track_usage_async_success(self):
        """Test successful async usage tracking"""
        tracker = UsageTracker(api_key=self.valid_api_key)

        # Mock httpx AsyncClient
        with patch("cmdrdata_openai.tracker.httpx") as mock_httpx:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_client.post.return_value = mock_response
            mock_httpx.AsyncClient.return_value.__aenter__.return_value = mock_client

            result = await tracker.track_usage_async(
                customer_id=self.customer_id,
                model=self.model,
                input_tokens=self.input_tokens,
                output_tokens=self.output_tokens,
            )

            assert result is True
            mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_track_usage_async_fallback(self):
        """Test async usage tracking fallback to sync"""
        tracker = UsageTracker(api_key=self.valid_api_key)

        # Mock httpx as None to test fallback
        with patch("cmdrdata_openai.tracker.httpx", None):
            with patch.object(tracker, "track_usage") as mock_sync_track:
                mock_sync_track.return_value = True

                result = await tracker.track_usage_async(
                    customer_id=self.customer_id,
                    model=self.model,
                    input_tokens=self.input_tokens,
                    output_tokens=self.output_tokens,
                )

                assert result is True
                mock_sync_track.assert_called_once()

    def test_track_usage_background(self):
        """Test background usage tracking"""
        tracker = UsageTracker(api_key=self.valid_api_key)

        with patch.object(tracker._executor, "submit") as mock_submit:
            tracker.track_usage_background(
                customer_id=self.customer_id,
                model=self.model,
                input_tokens=self.input_tokens,
                output_tokens=self.output_tokens,
            )

            mock_submit.assert_called_once()
            # Verify the first argument is the track_usage method
            assert mock_submit.call_args[0][0] == tracker.track_usage

    def test_get_health_status(self):
        """Test health status method"""
        tracker = UsageTracker(
            api_key=self.valid_api_key,
            endpoint=self.valid_endpoint,
            timeout=10.0,
            max_retries=5,
        )

        status = tracker.get_health_status()

        assert status["endpoint"] == self.valid_endpoint
        assert status["timeout"] == 10.0
        assert status["max_retries"] == 5
        assert "circuit_breaker_state" in status
        assert status["healthy"] is True

    def test_cleanup_on_deletion(self):
        """Test thread pool cleanup on object deletion"""
        tracker = UsageTracker(api_key=self.valid_api_key)

        with patch.object(tracker._executor, "shutdown") as mock_shutdown:
            del tracker
            mock_shutdown.assert_called_once_with(wait=False)


if __name__ == "__main__":
    pytest.main([__file__])
