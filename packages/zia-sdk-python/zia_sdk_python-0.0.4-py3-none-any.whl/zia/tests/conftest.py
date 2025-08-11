# tests/conftest.py
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from zia import Config, Zia


@pytest.fixture(scope="session", autouse=True)
def load_environment():
    """
    Auto-load secrets for *all* tests.
    This runs automatically for every test session.
    """
    # Try to load from .env file manually if python-dotenv is available
    try:
        from dotenv import load_dotenv

        env_file = Path(".env.test") if Path(".env.test").exists() else Path(".env")
        if env_file.exists():
            print(f"📂 Loading environment from: {env_file}")
            load_dotenv(env_file, override=False)
        else:
            print(f"⚠️  No .env file found at: {env_file}")
    except ImportError:
        print("⚠️  python-dotenv not available, using environment variables only")

    api_key = os.getenv("NEUROLABS_API_KEY")
    if api_key:
        print(f"🔑 Environment loaded. API Key: {api_key[:8]}...")
    else:
        print("⚠️  NEUROLABS_API_KEY not found in environment")


@pytest.fixture
def config():
    """Create a test configuration for unit tests."""
    return Config(
        api_key="test-api-key",
        base_url="https://api.test.com/v2",
        timeout=5.0,
        max_retries=1,
    )


@pytest.fixture
def client(config):
    """Create a test client for unit tests (mocked)."""
    return Zia(
        api_key=config.api_key,
        base_url=config.base_url,
        timeout=config.timeout,
        max_retries=config.max_retries,
    )


@pytest.fixture
def api_key():
    load_dotenv()
    """Get API key from environment for integration tests."""
    key = os.getenv("NEUROLABS_API_KEY")
    if not key:
        pytest.skip("NEUROLABS_API_KEY environment variable not set")
    return key


@pytest.fixture
def integration_client():
    load_dotenv()
    """Create a real client for integration tests."""
    key = os.getenv("NEUROLABS_API_KEY")
    if not key:
        pytest.skip("NEUROLABS_API_KEY environment variable not set")

    print(f"🔧 Creating integration client with API key: {key[:8]}...")
    return Zia(api_key=key)


@pytest.fixture
def test_image_path():
    """Get path to test image."""
    image_path = (
        Path(__file__).parent.parent.parent / "data" / "display" / "pocm_ab.jpeg"
    )
    if not image_path.exists():
        pytest.skip(f"Test image not found: {image_path}")
    return image_path


@pytest.fixture
def test_thumbnail_path():
    """Get path to test image."""
    image_path = (
        Path(__file__).parent.parent.parent
        / "data"
        / "display"
        / "bud_light_thumbnail.png"
    )
    if not image_path.exists():
        pytest.skip(f"Test image not found: {image_path}")
    return image_path
