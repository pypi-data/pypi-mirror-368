"""
Version compatibility and detection for cmdrdata-openai
"""

import sys
import warnings
from typing import Any, Dict, Optional, Tuple

try:
    from packaging import version
except ImportError:
    # Fallback version parsing
    class FakeVersion:
        def __init__(self, v):
            self.v = v

        def __lt__(self, other):
            return self.v < other.v

        def __le__(self, other):
            return self.v <= other.v

        def __gt__(self, other):
            return self.v > other.v

        def __ge__(self, other):
            return self.v >= other.v

        def __eq__(self, other):
            return self.v == other.v

        def __str__(self):
            return self.v

    def parse(v):
        return FakeVersion(v)

    version = type("Version", (), {"parse": parse})()


class VersionCompatibility:
    """Handles version detection and compatibility warnings for OpenAI"""

    # Supported OpenAI version ranges
    SUPPORTED_OPENAI_VERSIONS = {
        "min": "1.0.0",
        "max": "2.0.0",  # Updated for latest versions
        "tested": [
            "1.0.0",
            "1.10.0",
            "1.20.0",
            "1.30.0",
            "1.40.0",
            "1.50.0",
            "1.51.0",
            "1.52.0",
            "1.53.0",
            "1.54.0",
        ],
        "latest_tested": "1.54.0",
    }

    def __init__(self):
        self.openai_version = None
        self._check_openai_version()

    def _check_openai_version(self):
        """Check installed version of OpenAI SDK"""
        try:
            import openai

            self.openai_version = openai.__version__
            self._validate_openai_version()
        except ImportError:
            warnings.warn(
                "OpenAI SDK not found. Please install it: pip install openai>=1.0.0",
                UserWarning,
                stacklevel=3,
            )

    def _validate_openai_version(self):
        """Validate OpenAI version and show warnings if needed"""
        if not self.openai_version:
            return

        current = version.parse(self.openai_version)
        min_version = version.parse(self.SUPPORTED_OPENAI_VERSIONS["min"])
        max_version = version.parse(self.SUPPORTED_OPENAI_VERSIONS["max"])

        if current < min_version:
            warnings.warn(
                f"cmdrdata-openai: OpenAI SDK version {self.openai_version} is below minimum "
                f"supported version {self.SUPPORTED_OPENAI_VERSIONS['min']}. "
                f"Please upgrade: pip install openai>={self.SUPPORTED_OPENAI_VERSIONS['min']}",
                UserWarning,
                stacklevel=3,
            )
        elif current >= max_version:
            warnings.warn(
                f"cmdrdata-openai: OpenAI SDK version {self.openai_version} is newer than tested version. "
                f"cmdrdata-openai was tested up to version {self.SUPPORTED_OPENAI_VERSIONS['latest_tested']}. "
                f"Functionality may be limited. Please check for cmdrdata-openai updates.",
                UserWarning,
                stacklevel=3,
            )
        # Only warn for significantly older untested versions, not newer ones
        elif (
            current < version.parse("1.40.0")
            and str(current) not in self.SUPPORTED_OPENAI_VERSIONS["tested"]
        ):
            warnings.warn(
                f"cmdrdata-openai: OpenAI SDK version {self.openai_version} has not been fully tested. "
                f"Latest tested version: {self.SUPPORTED_OPENAI_VERSIONS['latest_tested']}. "
                f"Consider upgrading for best compatibility.",
                UserWarning,
                stacklevel=3,
            )

    def is_openai_supported(self) -> bool:
        """Check if OpenAI version is supported"""
        if not self.openai_version:
            return False

        current = version.parse(self.openai_version)
        min_version = version.parse(self.SUPPORTED_OPENAI_VERSIONS["min"])
        max_version = version.parse(self.SUPPORTED_OPENAI_VERSIONS["max"])

        return min_version <= current < max_version

    def get_compatibility_info(self) -> Dict[str, Any]:
        """Get comprehensive compatibility information"""
        return {
            "openai": {
                "installed": self.openai_version,
                "supported": self.is_openai_supported(),
                "min_supported": self.SUPPORTED_OPENAI_VERSIONS["min"],
                "max_supported": self.SUPPORTED_OPENAI_VERSIONS["max"],
                "tested_versions": self.SUPPORTED_OPENAI_VERSIONS["tested"],
            },
            "python": {
                "version": f"{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}",
                "supported": sys.version_info >= (3, 8),
            },
        }


# Global instance
_version_compat = VersionCompatibility()


def check_compatibility() -> bool:
    """
    Check if the current environment is compatible with cmdrdata-openai.

    Returns:
        True if compatible, False otherwise
    """
    return _version_compat.is_openai_supported()


def get_compatibility_info() -> Dict[str, Any]:
    """
    Get detailed compatibility information.

    Returns:
        Dictionary with compatibility details
    """
    return _version_compat.get_compatibility_info()
