"""Podfeed SDK - A minimal Python SDK for the Podfeed API."""

from .client import PodfeedClient
from .exceptions import PodfeedError, PodfeedAuthError, PodfeedAPIError
from .types import (
    InputContent,
    VoiceConfig,
    ContentConfig,
    AudioGenerationRequest,
    TaskProgress,
    AudioDetails,
)

__version__ = "0.3.0"
__all__ = [
    "PodfeedClient", 
    "PodfeedError", 
    "PodfeedAuthError", 
    "PodfeedAPIError",
    "InputContent",
    "VoiceConfig", 
    "ContentConfig",
    "AudioGenerationRequest",
    "TaskProgress",
    "AudioDetails",
]
