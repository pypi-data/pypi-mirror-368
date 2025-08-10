from .http_client import HttpClient
from .file import ContextbaseFile
from typing import Optional, Dict, Any, Union
from pathlib import Path

class Contextbase:
    """
    Main client for interacting with the Contextbase API.
    
    This class provides methods to publish data to contexts and resolve/query
    context data using the Contextbase service.

    Attributes:
        http_client: The underlying HTTP client for API communication

    Example:
        >>> from contextbase import Contextbase, ContextbaseFile
        >>> client = Contextbase()
        >>> 
        >>> # Publish JSON data
        >>> response = client.publish(
        ...     context_name="analytics",
        ...     component_name="user-events",
        ...     body={"user_id": 123, "action": "login", "timestamp": "2024-01-15T10:30:00Z"}
        ... )
        >>> 
        >>> # Publish a file
        >>> file = ContextbaseFile.from_path("document.pdf")
        >>> response = client.publish(
        ...     context_name="documents",
        ...     component_name="reports", 
        ...     file=file
        ... )
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Contextbase client.
        
        Args:
            api_key: Optional API key. If not provided, will use CONTEXTBASE_API_KEY 
                    environment variable.
        """
        self.http_client = HttpClient(api_key)

    def publish(
        self, 
        context_name: str, 
        component_name: str, 
        body: Optional[Dict[str, Any]] = None, 
        file: Optional[ContextbaseFile] = None, 
        scopes: Optional[Dict[str, Any]] = None
    ):
        """
        Publish data to a context.
        
        Args:
            context_name: Name of the context to publish to
            component_name: Name of the component within the context
            body: Optional JSON data to publish
            file: ContextbaseFile object to upload
            scopes: Optional scoping information for the data
            
        Returns:
            ContextbaseResponse: Response object with success/error information
            
        Raises:
            ValueError: If neither body nor file is provided, or if file doesn't exist
            ContextbaseError: If the API request fails and raise_for_status() is called
            
        Example:
            >>> from contextbase import Contextbase, ContextbaseFile
            >>> client = Contextbase()
            
            # Method 1: Publish JSON data
            >>> response = client.publish(
            ...     context_name="analytics",
            ...     component_name="metrics",
            ...     body={"cpu_usage": 80, "memory_usage": 65}
            ... )
            
            # Method 2: Publish a file using ContextbaseFile
            >>> file = ContextbaseFile.from_path("report.pdf")
            >>> response = client.publish(
            ...     context_name="documents", 
            ...     component_name="reports",
            ...     file=file
            ... )
            
            # Method 3: Create file from data and publish
            >>> file = ContextbaseFile.from_data("Hello world", "greeting.txt")
            >>> response = client.publish(
            ...     context_name="messages",
            ...     component_name="greetings", 
            ...     file=file
            ... )
        """
        if not body and not file:
            raise ValueError("Either 'body' or 'file' is required")

        data = {"component_name": component_name}
        
        if body:
            data["body"] = body
            
        if file:
            if isinstance(file, ContextbaseFile):
                file_data = file.to_dict()
            else:
                raise ValueError("File must be a ContextbaseFile object")
            
            data["file"] = file_data
            
        if scopes:
            data["scopes"] = scopes

        response = self.http_client.post(f"/v1/contexts/{context_name}/data", data=data)
        return response

    def publish_file(
        self,
        context_name: str,
        component_name: str, 
        file: ContextbaseFile,
        scopes: Optional[Dict[str, Any]] = None
    ):
        """
        Convenience method to publish a file.
        
        Args:
            context_name: Name of the context to publish to
            component_name: Name of the component within the context
            file: ContextbaseFile object to upload
            scopes: Optional scoping information for the data
            
        Returns:
            ContextbaseResponse: Response object
            
        Example:
            >>> from contextbase import Contextbase, ContextbaseFile
            >>> client = Contextbase()
            >>> 
            >>> # Using ContextbaseFile object
            >>> file = ContextbaseFile.from_path("report.pdf")
            >>> response = client.publish_file("docs", "reports", file)
        """
        return self.publish(
            context_name=context_name,
            component_name=component_name,
            file=file,
            scopes=scopes
        )

    def resolve(
        self, 
        context_name: str, 
        scopes: Optional[Dict[str, Any]] = None, 
        query: Optional[str] = None
    ):
        """
        Resolve/query data from a context.
        
        Args:
            context_name: Name of the context to query
            scopes: Optional scoping filters for the query
            query: Optional search query string
            
        Returns:
            ContextbaseResponse: Response object containing resolved data
            
        Raises:
            ContextbaseError: If the API request fails and raise_for_status() is called
            
        Example:
            >>> client = Contextbase()
            >>> response = client.resolve("my_context", query="search term")
            >>> if response.ok:
            ...     result = response.json
            ...     print(f"Resolved context: {result}")
        """
        data = {}
        if scopes:
            data["scopes"] = scopes
        if query:
            data["query"] = query

        response = self.http_client.post(f"/v1/contexts/{context_name}/resolve", data=data)
        return response
