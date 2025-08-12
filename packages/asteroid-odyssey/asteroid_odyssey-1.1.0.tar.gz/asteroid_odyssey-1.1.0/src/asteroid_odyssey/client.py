"""
Asteroid Agents Python SDK - High-Level Client Interface

Provides a clean, easy-to-use interface for interacting with the Asteroid Agents API,
similar to the TypeScript SDK.

This module provides a high-level client that wraps the generated OpenAPI client
without modifying any generated files.
"""

import time
import os
import logging
from typing import Dict, Any, Optional, List, Union, Tuple
from .openapi_client import (
    Configuration,
    ApiClient,
    APIApi,
    ExecutionApi,
    ExecutionStatusResponse,
    ExecutionResultResponse,
    BrowserSessionRecordingResponse,
    UploadExecutionFiles200Response,
    Status,
    StructuredAgentExecutionRequest
)
from .openapi_client.exceptions import ApiException


class AsteroidClient:
    """
    High-level client for the Asteroid Agents API.
    
    This class provides a convenient interface for executing agents and managing
    their execution lifecycle, similar to the TypeScript SDK.
    """
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Create an API client with the provided API key.
        
        Args:
            api_key: Your API key for authentication
            base_url: Optional base URL (defaults to https://odyssey.asteroid.ai/api/v1)
        
        Example:
            client = AsteroidClient('your-api-key')
        """
        if api_key is None:
            raise TypeError("API key cannot be None")
        
        # Configure the API client
        config = Configuration(
            host=base_url or "https://odyssey.asteroid.ai/api/v1",
            api_key={'ApiKeyAuth': api_key}
        )
        
        self.api_client = ApiClient(config)
        self.api_api = APIApi(self.api_client)
        self.execution_api = ExecutionApi(self.api_client)
        
    def execute_agent(self, agent_id: str, execution_data: Dict[str, Any], agent_profile_id: Optional[str] = None) -> str: 
        """
        Execute an agent with the provided parameters.
        
        Args:
            agent_id: The ID of the agent to execute
            execution_data: The execution parameters
            agent_profile_id: Optional ID of the agent profile
            
        Returns:
            The execution ID
            
        Raises:
            Exception: If the execution request fails
            
        Example:
            execution_id = client.execute_agent('my-agent-id', {'input': 'some dynamic value'}, 'agent-profile-id')
        """
        req = StructuredAgentExecutionRequest(dynamic_data=execution_data, agent_profile_id=agent_profile_id)
        try:
            response = self.execution_api.execute_agent_structured(agent_id, req)
            return response.execution_id
        except ApiException as e:
            raise Exception(f"Failed to execute agent: {e}")
    
    def get_execution_status(self, execution_id: str) -> ExecutionStatusResponse:
        """
        Get the current status for an execution.
        
        Args:
            execution_id: The execution identifier
            
        Returns:
            The execution status details
            
        Raises:
            Exception: If the status request fails
            
        Example:
            status = client.get_execution_status(execution_id)
            print(status.status)
        """
        try:
            return self.execution_api.get_execution_status(execution_id)
        except ApiException as e:
            raise Exception(f"Failed to get execution status: {e}")
    
    def get_execution_result(self, execution_id: str) -> Dict[str, Any]:
        """
        Get the final result of an execution.
        
        Args:
            execution_id: The execution identifier
            
        Returns:
            The result object of the execution
            
        Raises:
            Exception: If the result request fails or execution failed
            
        Example:
            result = client.get_execution_result(execution_id)
            print(result)
        """
        try:
            response = self.execution_api.get_execution_result(execution_id)
            
            if response.error:
                raise Exception(response.error)
            
            return response.execution_result or {}
        except ApiException as e:
            raise Exception(f"Failed to get execution result: {e}")
    
    def wait_for_execution_result(
        self, 
        execution_id: str, 
        interval: float = 1.0, 
        timeout: float = 3600.0
    ) -> Dict[str, Any]:
        """
        Wait for an execution to reach a terminal state and return the result.
        
        Continuously polls the execution status until it's either "completed", 
        "cancelled", or "failed".
        
        Args:
            execution_id: The execution identifier
            interval: Polling interval in seconds (default is 1.0)
            timeout: Maximum wait time in seconds (default is 3600 - 1 hour)
            
        Returns:
            The execution result if completed
            
        Raises:
            Exception: If the execution ends as "cancelled" or "failed", or times out
            
        Example:
            result = client.wait_for_execution_result(execution_id, interval=2.0)
        """
        start_time = time.time()
        
        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time >= timeout:
                raise Exception(f"Execution {execution_id} timed out after {timeout}s")
            
            status_response = self.get_execution_status(execution_id)
            current_status = status_response.status
            
            if current_status == Status.COMPLETED:
                return self.get_execution_result(execution_id)
            elif current_status in [Status.FAILED, Status.CANCELLED]:
                reason = f" - {status_response.reason}" if status_response.reason else ""
                raise Exception(f"Execution {execution_id} ended with status: {current_status.value}{reason}")
            
            # Wait for the specified interval before polling again
            time.sleep(interval)
    
    def upload_execution_files(
        self, 
        execution_id: str, 
        files: List[Union[bytes, str, Tuple[str, bytes]]],
        default_filename: str = "file.txt"
    ) -> UploadExecutionFiles200Response:
        """
        Upload files to an execution.
        
        Args:
            execution_id: The execution identifier
            files: List of files to upload. Each file can be:
                   - bytes: Raw file content (will use default_filename)
                   - str: File path as string (will read file and use filename)
                   - Tuple[str, bytes]: (filename, file_content) tuple
            default_filename: Default filename to use when file is provided as bytes
            
        Returns:
            The upload response containing message and file IDs
            
        Raises:
            Exception: If the upload request fails
            
        Example:
            # Upload with file content (file should be in your current working directory)
            with open('hello.txt', 'r') as f:
                file_content = f.read()
            
            response = client.upload_execution_files(execution_id, [file_content.encode()])
            print(f"Uploaded files: {response.file_ids}")
            
            # Upload with filename and content
            files = [('hello.txt', file_content.encode())]
            response = client.upload_execution_files(execution_id, files)
            
            # Or create content directly
            hello_content = "Hello World!".encode()
            response = client.upload_execution_files(execution_id, [hello_content])
        """
        try:
            # Process files to ensure proper format
            processed_files = []
            for file_item in files:
                if isinstance(file_item, tuple):
                    # Already in (filename, content) format
                    filename, content = file_item
                    if isinstance(content, str):
                        content = content.encode()
                    processed_files.append((filename, content))
                elif isinstance(file_item, str):
                    # Check if string is a file path that exists, otherwise treat as content
                    if os.path.isfile(file_item):
                        # File path - read the file
                        filename = os.path.basename(file_item)
                        with open(file_item, 'rb') as f:
                            content = f.read()
                        processed_files.append((filename, content))
                    else:
                        # String content - encode and use default filename
                        content = file_item.encode()
                        processed_files.append((default_filename, content))
                elif isinstance(file_item, bytes):
                    # Raw bytes - use default filename
                    processed_files.append((default_filename, file_item))
                else:
                    # Other types - convert to string content and encode
                    content = str(file_item).encode()
                    processed_files.append((default_filename, content))
            
            response = self.execution_api.upload_execution_files(execution_id, files=processed_files)
            return response
        except ApiException as e:
            raise Exception(f"Failed to upload execution files: {e}")
    
    def get_browser_session_recording(self, execution_id: str) -> str:
        """
        Get the browser session recording URL for a completed execution.
        
        Args:
            execution_id: The execution identifier
            
        Returns:
            The URL of the browser session recording
            
        Raises:
            Exception: If the recording request fails
            
        Example:
            recording_url = client.get_browser_session_recording(execution_id)
            print(f"Recording available at: {recording_url}")
        """
        try:
            response = self.execution_api.get_browser_session_recording(execution_id)
            return response.recording_url
        except ApiException as e:
            raise Exception(f"Failed to get browser session recording: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_value, tb):
        """Context manager exit: clean up API client connection pool."""
        try:
            # Try to grab the pool_manager; if any attr is missing, skip
            try:
                pool_manager = self.api_client.rest_client.pool_manager
            except AttributeError:
                pool_manager = None

            if pool_manager:
                pool_manager.clear()
        except Exception as e:
            # Log but don't mask the original exception (if any)
            logging.warning("Failed to clear connection pool: %s", e)

        # Returning False allows any exception in the 'with' block to propagate
        return False


# Convenience functions that mirror the TypeScript SDK pattern
def create_client(api_key: str, base_url: Optional[str] = None) -> AsteroidClient:
    """
    Create an API client with a provided API key.
    
    This is a convenience function that creates an AsteroidClient instance.
    
    Args:
        api_key: Your API key
        base_url: Optional base URL
        
    Returns:
        A configured AsteroidClient instance
        
    Example:
        client = create_client('your-api-key')
    """
    return AsteroidClient(api_key, base_url)

def execute_agent(client: AsteroidClient, agent_id: str, execution_data: Dict[str, Any], agent_profile_id: Optional[str] = None) -> str:
    """
    Execute an agent with the provided parameters.
    
    Args:
        client: The AsteroidClient instance
        agent_id: The ID of the agent to execute
        execution_data: The execution parameters
        agent_profile_id: Optional ID of the agent profile
        
    Returns:
        The execution ID
        
    Example:
        execution_id = execute_agent(client, 'my-agent-id', {'input': 'some dynamic value'}, 'agent-profile-id')
    """
    return client.execute_agent(agent_id, execution_data, agent_profile_id)



def get_execution_status(client: AsteroidClient, execution_id: str) -> ExecutionStatusResponse:
    """
    Get the current status for an execution.
    
    Args:
        client: The AsteroidClient instance
        execution_id: The execution identifier
        
    Returns:
        The execution status details
        
    Example:
        status = get_execution_status(client, execution_id)
        print(status.status)
    """
    return client.get_execution_status(execution_id)


def get_execution_result(client: AsteroidClient, execution_id: str) -> Dict[str, Any]:
    """
    Get the final result of an execution.
    
    Args:
        client: The AsteroidClient instance
        execution_id: The execution identifier
        
    Returns:
        The result object of the execution
        
    Example:
        result = get_execution_result(client, execution_id)
        print(result)
    """
    return client.get_execution_result(execution_id)


def wait_for_execution_result(
    client: AsteroidClient, 
    execution_id: str, 
    interval: float = 1.0, 
    timeout: float = 3600.0
) -> Dict[str, Any]:
    """
    Wait for an execution to reach a terminal state and return the result.
    
    Args:
        client: The AsteroidClient instance
        execution_id: The execution identifier
        interval: Polling interval in seconds (default is 1.0)
        timeout: Maximum wait time in seconds (default is 3600 - 1 hour)
        
    Returns:
        The execution result if completed
        
    Example:
        result = wait_for_execution_result(client, execution_id, interval=2.0)
    """
    return client.wait_for_execution_result(execution_id, interval, timeout)


def upload_execution_files(
    client: AsteroidClient, 
    execution_id: str, 
    files: List[Union[bytes, str, Tuple[str, bytes]]],
    default_filename: str = "file.txt"
) -> UploadExecutionFiles200Response:
    """
    Upload files to an execution.
    
    Args:
        client: The AsteroidClient instance
        execution_id: The execution identifier
        files: List of files to upload
        default_filename: Default filename to use when file is provided as bytes
        
    Returns:
        The upload response containing message and file IDs
        
    Example:
        # Create a simple text file with "Hello World!" content
        hello_content = "Hello World!".encode()
        response = upload_execution_files(client, execution_id, [hello_content])
        print(f"Uploaded files: {response.file_ids}")
        
        # Or specify filename with content
        files = [('hello.txt', "Hello World!".encode())]
        response = upload_execution_files(client, execution_id, files)
    """
    return client.upload_execution_files(execution_id, files, default_filename)


def get_browser_session_recording(client: AsteroidClient, execution_id: str) -> str:
    """
    Get the browser session recording URL for a completed execution.
    
    Args:
        client: The AsteroidClient instance
        execution_id: The execution identifier
        
    Returns:
        The URL of the browser session recording
        
    Example:
        recording_url = get_browser_session_recording(client, execution_id)
        print(f"Recording available at: {recording_url}")
    """
    return client.get_browser_session_recording(execution_id)


# Re-export common types for convenience
__all__ = [
    'AsteroidClient',
    'create_client',
    'execute_agent',
    'get_execution_status',
    'get_execution_result',
    'wait_for_execution_result',
    'upload_execution_files',
    'get_browser_session_recording'
] 