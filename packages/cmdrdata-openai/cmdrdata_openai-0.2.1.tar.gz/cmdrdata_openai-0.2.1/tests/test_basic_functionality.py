"""
Basic functionality tests to verify the system works
"""

from unittest.mock import Mock, patch

import pytest

from cmdrdata_openai.exceptions import SecurityError, ValidationError
from cmdrdata_openai.performance import LRUCache
from cmdrdata_openai.retry import CircuitBreaker, RetryConfig
from cmdrdata_openai.security import APIKeyManager, InputSanitizer


class TestBasicFunctionality:
    """Test basic functionality works as expected"""

    def test_api_key_validation_openai(self):
        """Test OpenAI API key validation"""
        valid_key = "sk-" + "a" * 48
        result = APIKeyManager.validate_api_key(valid_key, "openai")
        assert result["valid"] is True
        assert result["format"] == "legacy"

    def test_api_key_validation_cmdrdata(self):
        """Test cmdrdata API key validation"""
        valid_key = "tk-" + "b" * 32
        result = APIKeyManager.validate_api_key(valid_key, "cmdrdata")
        assert result["valid"] is True

    def test_api_key_validation_invalid(self):
        """Test invalid API key validation"""
        with pytest.raises(ValidationError):
            APIKeyManager.validate_api_key("invalid-key", "openai")

    def test_input_sanitizer_basic(self):
        """Test basic input sanitization"""
        result = InputSanitizer.sanitize_string("hello world", "general_string")
        assert result == "hello world"

    def test_input_sanitizer_removes_null_bytes(self):
        """Test input sanitizer removes null bytes"""
        result = InputSanitizer.sanitize_string("hello\x00world", "general_string")
        assert result == "helloworld"

    def test_retry_config_creation(self):
        """Test retry configuration creation"""
        config = RetryConfig(max_attempts=3, initial_delay=1.0)
        assert config.max_attempts == 3
        assert config.initial_delay == 1.0

    def test_circuit_breaker_creation(self):
        """Test circuit breaker creation"""
        cb = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0)
        assert cb.failure_threshold == 5
        assert cb.recovery_timeout == 60.0

    def test_lru_cache_basic(self):
        """Test LRU cache basic functionality"""
        cache = LRUCache(max_size=10)

        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        assert cache.get("nonexistent") is None

    def test_api_key_sanitization_for_logging(self):
        """Test API key sanitization for logging"""
        key = "sk-abcdefghijklmnopqrstuvwxyz1234567890123456"
        sanitized = APIKeyManager.sanitize_api_key_for_logging(key)
        assert "sk-" in sanitized
        assert "456" in sanitized
        assert len(sanitized) < len(key)

    def test_url_validation_success(self):
        """Test URL validation success"""
        valid_url = "https://api.example.com/endpoint"
        result = InputSanitizer.validate_url(valid_url)
        assert result == valid_url

    def test_url_validation_failure(self):
        """Test URL validation failure"""
        with pytest.raises(ValidationError):
            InputSanitizer.validate_url("not-a-url")


if __name__ == "__main__":
    pytest.main([__file__])
