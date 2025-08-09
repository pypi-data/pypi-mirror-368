import pytest
from goodmem_client import (
    APIKeysApi, EmbeddersApi, MemoriesApi, SpacesApi, SystemApi, UsersApi, # APIs
    Configuration, ApiClient # Core components for instantiation
)
# You can also import a sample model if you want to check model imports
# from goodmem_client import ApiKeyResponse

def test_api_modules_are_importable():
    """Tests that all top-level API classes can be imported from the SDK package."""
    assert APIKeysApi is not None
    assert EmbeddersApi is not None
    assert MemoriesApi is not None
    assert SpacesApi is not None
    assert SystemApi is not None
    assert UsersApi is not None
    # Add asserts for any other key exports from __init__.py if you like,
    # e.g., assert ApiClient is not None, assert Configuration is not None

def test_basic_api_instantiation():
    """Tests basic instantiation of an API class with a dummy configuration."""
    # This is a very basic check. The detailed generated tests for each API
    # (e.g., test/test_system_api.py) will cover more thorough instantiation and usage.
    try:
        # For a basic instantiation test, we just need to ensure it doesn't crash.
        # A dummy host is fine if we're not making actual calls.
        config = Configuration(host="http://dummy.host.invalid/api")
        api_client = ApiClient(configuration=config)

        system_api = SystemApi(api_client=api_client)
        assert system_api is not None
        assert system_api.api_client.configuration.host == "http://dummy.host.invalid/api"

        # You could optionally instantiate others too for a broader check:
        # api_keys_api = APIKeysApi(api_client=api_client)
        # assert api_keys_api is not None

    except Exception as e:
        pytest.fail(f"Basic API instantiation failed: {e}")
