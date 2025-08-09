# coding: utf-8

"""
Streaming client for GoodMem API

This module provides a convenient streaming interface for the GoodMem memory retrieval API,
handling both SSE (Server-Sent Events) and NDJSON streaming formats.
"""

import json
import logging
import re
from typing import Any, Dict, Generator, List, Optional, Union
from urllib.parse import urlencode

import urllib3
from pydantic import BaseModel, Field

from goodmem_client.api.memories_api import MemoriesApi
from goodmem_client.api_client import ApiClient
from goodmem_client.models.memory import Memory


class AbstractReply(BaseModel):
    """Generated abstractive reply with relevance information"""
    text: str = Field(description="Generated abstractive reply text")
    relevance_score: float = Field(description="Relevance score for this reply (0.0 to 1.0)", alias="relevanceScore")
    result_set_id: Optional[str] = Field(default=None, description="Optional link to a specific result set", alias="resultSetId")


class ChunkReference(BaseModel):
    """Reference to a memory chunk with pointer to its parent memory"""
    result_set_id: str = Field(description="Result set ID that produced this chunk", alias="resultSetId")
    chunk: Dict[str, Any] = Field(description="The memory chunk data")
    memory_index: int = Field(description="Index of the chunk's memory in the client's memories array", alias="memoryIndex")
    relevance_score: float = Field(description="Relevance score for this chunk (0.0 to 1.0)", alias="relevanceScore")


class RetrievedItem(BaseModel):
    """A retrieved result that can be either a Memory or MemoryChunk"""
    memory: Optional[Dict[str, Any]] = Field(default=None, description="Complete memory object (if retrieved)")
    chunk: Optional[ChunkReference] = Field(default=None, description="Reference to a memory chunk (if retrieved)")


class ResultSetBoundary(BaseModel):
    """Marks the BEGIN/END of a logical result set (e.g. vector match, rerank)"""
    result_set_id: str = Field(description="Unique result set ID (UUID)", alias="resultSetId")
    kind: str = Field(description="Boundary type: 'BEGIN' or 'END'")
    stage_name: str = Field(description="Free-form stage label for logging", alias="stageName")
    expected_items: Optional[int] = Field(default=None, description="Hint for progress bars", alias="expectedItems")


class GoodMemStatus(BaseModel):
    """Warning or non-fatal status with granular codes (operation continues)"""
    code: str = Field(description="Status code for the warning or informational message")
    message: str = Field(description="Human-readable status message")


class RetrieveMemoryEvent(BaseModel):
    """Streaming event from memory retrieval operation"""
    result_set_boundary: Optional[ResultSetBoundary] = Field(default=None, description="Result set boundary marker", alias="resultSetBoundary")
    retrieved_item: Optional[RetrievedItem] = Field(default=None, description="A retrieved memory or chunk", alias="retrievedItem")
    abstract_reply: Optional[AbstractReply] = Field(default=None, description="Generated abstractive reply", alias="abstractReply")
    memory_definition: Optional[Dict[str, Any]] = Field(default=None, description="Memory object to add to client's memories array", alias="memoryDefinition")
    status: Optional[GoodMemStatus] = Field(default=None, description="Warning or non-fatal status message")


class MemoryStreamClient:
    """
    Streaming client for memory retrieval operations.

    This client provides a convenient Python interface for consuming streaming
    memory retrieval results from the GoodMem API.

    Authentication:
        Configure API key authentication using the standard OpenAPI Configuration:

        # Recommended approach
        from goodmem_client.configuration import Configuration
        from goodmem_client.api_client import ApiClient

        configuration = Configuration()
        configuration.host = "http://localhost:8080"
        configuration.api_key = {"ApiKeyAuth": "your-api-key"}

        api_client = ApiClient(configuration=configuration)
        stream_client = MemoryStreamClient(api_client)

        # Legacy approach (still supported for backward compatibility)
        api_client.default_headers["x-api-key"] = "your-api-key"
    """

    def __init__(self, api_client: Optional[ApiClient] = None):
        """
        Initialize the streaming client.

        Args:
            api_client: Optional ApiClient instance. If None, uses the default.
        """
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client
        self.memories_api = MemoriesApi(api_client)

    def retrieve_memory_stream_chat(
        self,
        message: str,
        space_ids: Optional[List[str]] = None,
        requested_size: Optional[int] = None,
        fetch_memory: Optional[bool] = None,
        fetch_memory_content: Optional[bool] = None,
        format: str = "ndjson",
        pp_llm_id: Optional[str] = None,
        pp_reranker_id: Optional[str] = None,
        pp_relevance_threshold: Optional[float] = None,
        pp_llm_temp: Optional[float] = None,
        pp_max_results: Optional[int] = None,
        pp_chronological_resort: Optional[bool] = None
    ) -> Generator[RetrieveMemoryEvent, None, None]:
        """
        Stream semantic memory retrieval results using ChatPostProcessor.

        This is a convenience method that automatically configures the ChatPostProcessor
        with the provided parameters. For custom post-processors, use retrieve_memory_stream().

        Args:
            message: Primary query/message for semantic search
            space_ids: List of space UUIDs to search within
            requested_size: Maximum number of memories to retrieve
            fetch_memory: Whether to fetch memory definitions (defaults to true)
            fetch_memory_content: Whether to fetch original content for memories (defaults to false)
            format: Streaming format - either "ndjson" or "sse" (default: "ndjson")
            pp_llm_id: UUID of LLM to use for ChatPostProcessor generation
            pp_reranker_id: UUID of reranker to use for ChatPostProcessor
            pp_relevance_threshold: Minimum relevance score for ChatPostProcessor
            pp_llm_temp: LLM temperature for ChatPostProcessor generation
            pp_max_results: Maximum results for ChatPostProcessor
            pp_chronological_resort: Whether ChatPostProcessor should resort by creation time

        Yields:
            RetrieveMemoryEvent: Parsed streaming events

        Raises:
            ValueError: If format is not "ndjson" or "sse"
            Exception: If API request fails
        """
        if format not in ("ndjson", "sse"):
            raise ValueError("format must be either 'ndjson' or 'sse'")

        # Build query parameters for GET endpoint
        params = {"message": message}
        if space_ids:
            params["spaceIds"] = ",".join(space_ids)
        else:
            raise ValueError("space_ids must not be None or empty. Please provide at least one space ID.")

        if requested_size is not None:
            params["requestedSize"] = str(requested_size)
        if fetch_memory is not None:
            params["fetchMemory"] = str(fetch_memory).lower()
        if fetch_memory_content is not None:
            params["fetchMemoryContent"] = str(fetch_memory_content).lower()

        # Add ChatPostProcessor parameters with pp_ prefix
        if pp_llm_id is not None:
            params["pp_llm_id"] = pp_llm_id
        if pp_reranker_id is not None:
            params["pp_reranker_id"] = pp_reranker_id
        if pp_relevance_threshold is not None:
            params["pp_relevance_threshold"] = str(pp_relevance_threshold)
        if pp_llm_temp is not None:
            params["pp_llm_temp"] = str(pp_llm_temp)
        if pp_max_results is not None:
            params["pp_max_results"] = str(pp_max_results)
        if pp_chronological_resort is not None:
            params["pp_chronological_resort"] = str(pp_chronological_resort).lower()

        # Set appropriate Accept header
        accept_header = "application/x-ndjson" if format == "ndjson" else "text/event-stream"

        # Build the URL for GET endpoint
        host = self.api_client.configuration.host
        url = f"{host}/v1/memories:retrieve?{urlencode(params)}"

        # Get authentication headers
        headers = {"Accept": accept_header}

        # Add API key using backward-compatible resolution
        api_key = self._get_api_key()
        if api_key:
            headers['x-api-key'] = api_key

        # Make the streaming request
        http = urllib3.PoolManager()
        response = http.request("GET", url, headers=headers, preload_content=False)

        if response.status != 200:
            error_data = response.read().decode('utf-8')
            try:
                # Try to parse JSON error response for more detailed error information
                error_json = json.loads(error_data)
                error_message = error_json.get('error', error_data)
                raise Exception(f"API request failed with status {response.status}: {error_message}")
            except json.JSONDecodeError:
                # Fall back to raw error text if JSON parsing fails
                raise Exception(f"API request failed with status {response.status}: {error_data}")

        try:
            if format == "ndjson":
                yield from self._parse_ndjson_stream(response)
            else:
                yield from self._parse_sse_stream(response)
        finally:
            response.close()

    def _get_api_key(self) -> Optional[str]:
        """
        Get API key from configuration with backward compatibility.

        Tries multiple sources in order of preference:
        1. OpenAPI-standard configuration.get_api_key_with_prefix("ApiKeyAuth")
        2. Manual headers (backward compatibility for existing users)

        Returns:
            str: The API key if found, None otherwise
        """
        # Primary: Use proper OpenAPI configuration
        if hasattr(self.api_client, 'configuration'):
            try:
                api_key = self.api_client.configuration.get_api_key_with_prefix("ApiKeyAuth")
                if api_key:
                    return api_key
            except (AttributeError, KeyError):
                pass

        # Fallback: Check manual headers (backward compatibility)
        if hasattr(self.api_client, 'default_headers') and 'x-api-key' in self.api_client.default_headers:
            return self.api_client.default_headers['x-api-key']

        return None

    def retrieve_memory_stream(
        self,
        message: str,
        space_ids: Optional[List[str]] = None,
        requested_size: Optional[int] = None,
        fetch_memory: Optional[bool] = None,
        fetch_memory_content: Optional[bool] = None,
        format: str = "ndjson",
        post_processor_name: Optional[str] = None,
        post_processor_config: Optional[Dict[str, Any]] = None
    ) -> Generator[RetrieveMemoryEvent, None, None]:
        """
        Stream semantic memory retrieval results using advanced POST endpoint.

        Args:
            message: Primary query/message for semantic search
            space_ids: List of space UUIDs to search within
            requested_size: Maximum number of memories to retrieve
            fetch_memory: Whether to fetch memory definitions (defaults to true)
            fetch_memory_content: Whether to fetch original content for memories (defaults to false)
            format: Streaming format - either "ndjson" or "sse" (default: "ndjson")
            post_processor_name: Name of the post-processor to use (e.g., "com.goodmem.retrieval.postprocess.ChatPostProcessorFactory")
            post_processor_config: Configuration parameters for the post-processor as a dictionary

        Yields:
            RetrieveMemoryEvent: Parsed streaming events

        Raises:
            ValueError: If format is not "ndjson" or "sse"
            Exception: If API request fails
        """
        if format not in ("ndjson", "sse"):
            raise ValueError("format must be either 'ndjson' or 'sse'")

        # Build request body
        request_body: Dict[str, Any] = {
            "message": message,
            "spaceKeys": []
        }

        # Validate space IDs
        if not space_ids:
            raise ValueError("space_ids must not be None or empty. Please provide at least one space ID.")

        # Add space IDs as space keys
        for space_id in space_ids:
            request_body["spaceKeys"].append({"spaceId": space_id})

        # Add optional parameters
        if requested_size is not None:
            request_body["requestedSize"] = requested_size
        if fetch_memory is not None:
            request_body["fetchMemory"] = fetch_memory
        if fetch_memory_content is not None:
            request_body["fetchMemoryContent"] = fetch_memory_content

        # Add post-processor configuration
        if post_processor_name is not None:
            post_processor: Dict[str, Any] = {"name": post_processor_name}
            if post_processor_config is not None:
                post_processor["config"] = post_processor_config
            request_body["postProcessor"] = post_processor

        # Set appropriate Accept header
        accept_header = "application/x-ndjson" if format == "ndjson" else "text/event-stream"

        # Build the URL (POST endpoint)
        host = self.api_client.configuration.host
        url = f"{host}/v1/memories:retrieve"

        # Get authentication headers
        headers = {
            "Accept": accept_header,
            "Content-Type": "application/json"
        }

        # Add API key using backward-compatible resolution
        api_key = self._get_api_key()
        if api_key:
            headers['x-api-key'] = api_key

        # Serialize request body to JSON
        request_json = json.dumps(request_body)

        # Make the streaming request
        http = urllib3.PoolManager()
        response = http.request("POST", url, body=request_json, headers=headers, preload_content=False)

        if response.status != 200:
            error_data = response.read().decode('utf-8')
            try:
                # Try to parse JSON error response for more detailed error information
                error_json = json.loads(error_data)
                error_message = error_json.get('error', error_data)
                raise Exception(f"API request failed with status {response.status}: {error_message}")
            except json.JSONDecodeError:
                # Fall back to raw error text if JSON parsing fails
                raise Exception(f"API request failed with status {response.status}: {error_data}")

        try:
            if format == "ndjson":
                yield from self._parse_ndjson_stream(response)
            else:
                yield from self._parse_sse_stream(response)
        finally:
            response.close()

    def _parse_ndjson_stream(self, response) -> Generator[RetrieveMemoryEvent, None, None]:
        """Parse NDJSON streaming response."""
        buffer = ""

        for chunk_bytes in response.stream(1024):
            if not chunk_bytes:
                continue

            try:
                buffer += chunk_bytes.decode('utf-8', errors='replace')
            except UnicodeDecodeError:
                # Skip chunks with encoding issues
                continue

            # Process complete lines (JSON objects separated by newlines)
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                line = line.strip()

                if not line:
                    continue

                try:
                    event_data = json.loads(line)
                    event = RetrieveMemoryEvent.model_validate(event_data)
                    yield event
                except json.JSONDecodeError as e:
                    logging.debug(f"Failed to parse NDJSON line: {e}. Line content: {line[:100]}{'...' if len(line) > 100 else ''}")
                    continue
                except Exception as e:
                    logging.debug(f"Failed to validate NDJSON event: {e}. Line content: {line[:100]}{'...' if len(line) > 100 else ''}")
                    continue

    def _parse_sse_stream(self, response) -> Generator[RetrieveMemoryEvent, None, None]:
        """Parse Server-Sent Events streaming response."""
        buffer = ""

        for chunk_bytes in response.stream(1024):
            if not chunk_bytes:
                continue

            try:
                buffer += chunk_bytes.decode('utf-8', errors='replace')
            except UnicodeDecodeError:
                # Skip chunks with encoding issues
                continue

            # Process complete SSE events
            while '\n\n' in buffer:
                event_text, buffer = buffer.split('\n\n', 1)
                event = self._parse_sse_event(event_text)
                if event:
                    yield event

    def _parse_sse_event(self, event_text: str) -> Optional[RetrieveMemoryEvent]:
        """Parse a single SSE event."""
        lines = event_text.strip().split('\n')
        event_type = None
        data = None

        for line in lines:
            if line.startswith('event:'):
                event_type = line[6:].strip()
            elif line.startswith('data:'):
                data = line[5:].strip()

        # Skip close events and events without data
        if event_type == "close" or not data:
            return None

        try:
            event_data = json.loads(data)
            return RetrieveMemoryEvent.model_validate(event_data)
        except (json.JSONDecodeError, Exception):
            return None


# Convenience function for easy access
def create_stream_client(api_client: Optional[ApiClient] = None) -> MemoryStreamClient:
    """
    Create a new MemoryStreamClient instance.

    Args:
        api_client: Optional ApiClient instance. If None, uses the default.

    Returns:
        MemoryStreamClient: New streaming client instance
    """
    return MemoryStreamClient(api_client)