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
from .utils import (
    ir_results_to_dataframe,
    ir_results_to_summary_dataframe,
)

# Version is managed by Poetry in pyproject.toml
__version__ = "0.0.2"

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
    # DataFrame utilities
    "ir_results_to_dataframe",
    "ir_results_to_summary_dataframe",
]
