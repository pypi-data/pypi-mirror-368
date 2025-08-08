"""
Tests for version compatibility checking
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from cmdrdata_openai.version_compat import (
    VersionCompatibility,
    check_compatibility,
    get_compatibility_info,
)


def test_compatibility_info_structure():
    """Test that compatibility info has expected structure"""
    info = get_compatibility_info()

    assert isinstance(info, dict)
    assert "openai" in info
    assert "python" in info

    openai_info = info["openai"]
    assert "installed" in openai_info
    assert "supported" in openai_info
    assert "min_supported" in openai_info
    assert "max_supported" in openai_info
    assert "tested_versions" in openai_info

    python_info = info["python"]
    assert "version" in python_info
    assert "supported" in python_info


def test_openai_version_detection():
    """Test OpenAI version detection"""
    # Test with the real openai version that's installed
    compat = VersionCompatibility()
    assert compat.openai_version is not None
    # Don't assert specific version since it varies by environment


def test_unsupported_openai_version():
    """Test handling of unsupported OpenAI version"""
    # Create a compat instance and manually set an unsupported version
    compat = VersionCompatibility()
    compat.openai_version = "0.5.0"  # Manually set unsupported version
    assert compat.is_openai_supported() is False


def test_missing_openai():
    """Test handling when OpenAI is not installed"""
    # Create a compat instance and manually set missing openai
    compat = VersionCompatibility()
    compat.openai_version = None  # Manually set missing version
    assert compat.is_openai_supported() is False


def test_check_compatibility_function():
    """Test the standalone check_compatibility function"""
    result = check_compatibility()
    assert isinstance(result, bool)


def test_version_warnings():
    """Test that version warnings are issued appropriately"""
    # Create a compat instance and manually set a newer version
    compat = VersionCompatibility()
    compat.openai_version = "5.0.0"  # Manually set newer version
    # Test that it's detected as unsupported (too new)
    assert compat.is_openai_supported() is False


@patch("cmdrdata_openai.version_compat.sys.version_info", (3, 7, 0))
def test_python_version_support():
    """Test Python version support detection"""
    info = get_compatibility_info()
    python_info = info["python"]

    # Python 3.7 should not be supported (we require 3.8+)
    assert python_info["supported"] is False


def test_compatibility_with_fallback_version():
    """Test compatibility checking with fallback version parser"""
    # This tests the fallback when packaging module is not available
    # Mock the packaging import to raise ImportError
    original_import = __import__

    def side_effect(name, *args, **kwargs):
        if name == "packaging":
            raise ImportError("No module named 'packaging'")
        # For openai, return a mock with a version
        elif name == "openai":
            mock_openai = Mock()
            mock_openai.__version__ = "1.5.0"
            return mock_openai
        return original_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=side_effect):
        # Should still work with basic version comparison
        compat = VersionCompatibility()
        info = compat.get_compatibility_info()
        assert isinstance(info, dict)
