# coding: utf-8

"""
Tests for streaming memory retrieval functionality
Reproduces and validates fix for GitHub issue #153
"""

import json
import unittest
from unittest.mock import Mock

from goodmem_client.api_client import ApiClient
from goodmem_client.configuration import Configuration
from goodmem_client.api.memories_api import MemoriesApi


class TestStreamingMemoryRetrieve(unittest.TestCase):
    """Test suite for streaming memory retrieve functionality (Issue #153)"""
    
    def setUp(self):
        """Set up test client"""
        config = Configuration()
        config.host = "http://localhost:8080"  # Dummy host, won't be used for our deprecated method tests
        self.api_client = ApiClient(configuration=config)
        self.api_client.default_headers = {'x-api-key': 'test-api-key'}

    def test_deprecated_retrieve_memory_raises_not_implemented_error(self):
        """Test that the deprecated retrieve_memory method raises NotImplementedError"""
        memories_api = MemoriesApi(api_client=self.api_client)
        
        with self.assertRaises(NotImplementedError) as cm:
            memories_api.retrieve_memory("test message", "space-id")
            
        error_message = str(cm.exception)
        self.assertIn("retrieve_memory() does not work for streaming responses", error_message)
        self.assertIn("MemoryStreamClient.retrieve_memory_stream_chat()", error_message)
        
    def test_deprecated_retrieve_memory_advanced_raises_not_implemented_error(self):
        """Test that the deprecated retrieve_memory_advanced method raises NotImplementedError"""
        from goodmem_client.models.retrieve_memory_request import RetrieveMemoryRequest
        
        memories_api = MemoriesApi(api_client=self.api_client)
        
        # Create a minimal request object
        request = RetrieveMemoryRequest(
            message="test message",
            space_keys=[{"spaceId": "test-space-id"}]
        )
        
        with self.assertRaises(NotImplementedError) as cm:
            memories_api.retrieve_memory_advanced(request)
            
        error_message = str(cm.exception)
        self.assertIn("retrieve_memory_advanced() does not work for streaming responses", error_message)
        self.assertIn("MemoryStreamClient.retrieve_memory_stream()", error_message)

    def test_deprecated_methods_accept_arbitrary_args_kwargs(self):
        """Test that deprecated methods accept *args, **kwargs without errors (before raising NotImplementedError)"""
        memories_api = MemoriesApi(api_client=self.api_client)
        
        # Test retrieve_memory with arbitrary arguments
        with self.assertRaises(NotImplementedError):
            memories_api.retrieve_memory("arg1", "arg2", kwarg1="value1", kwarg2="value2")
            
        # Test retrieve_memory_advanced with arbitrary arguments  
        with self.assertRaises(NotImplementedError):
            memories_api.retrieve_memory_advanced("arg1", "arg2", kwarg1="value1", kwarg2="value2")


if __name__ == '__main__':
    unittest.main()