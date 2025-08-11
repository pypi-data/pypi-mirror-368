"""
Zia Image Recognition SDK

A simple, ergonomic Python SDK for the Zia Image Recognition API.
"""

# config.py in your SDK
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path.cwd() / ".env", override=False)

from .client import Zia
from .config import Config
from .exceptions import (
    NeurolabsError,
    NeurolabsAuthError,
    NeurolabsRateLimitError,
    NeurolabsValidationError,
)
from .models import (
    NLCatalogItem,
    NLCatalogItemCreate,
    NLIRTask,
    NLIRResult,
    NLIRTaskCreate,
)

# Version is managed by Poetry in pyproject.toml
__version__ = "0.0.3"

__all__ = [
    "Zia",
    "Config",
    "NeurolabsError",
    "NeurolabsAuthError",
    "NeurolabsRateLimitError",
    "NeurolabsValidationError",
    "NLCatalogItem",
    "NLCatalogItemCreate",
    "NLIRTask",
    "NLIRResult",
    "NLIRTaskCreate",
]
