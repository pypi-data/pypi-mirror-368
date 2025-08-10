from .http_client import HttpClient
from typing import Optional, Dict, Any

class Contextbase:
    """
    Main client for interacting with the Contextbase API.
    
    This class provides methods to publish data to contexts and resolve/query
    context data using the Contextbase service.

    Attributes:
        http_client: The underlying HTTP client for API communication

    Example:
        >>> from contextbase import Contextbase
        >>> client = Contextbase()
        >>> response = client.publish("my-context", "component", body={"data": "value"})
        >>> if response.ok:
        ...     print("Published successfully!")
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
        file: Optional[Dict[str, str]] = None, 
        scopes: Optional[Dict[str, Any]] = None
    ):
        """
        Publish data to a context.
        
        Args:
            context_name: Name of the context to publish to
            component_name: Name of the component within the context
            body: Optional JSON data to publish
            file: Optional file data with structure:
                 {'mime_type': str, 'base64': str, 'name': str (optional)}
            scopes: Optional scoping information for the data
            
        Returns:
            ContextbaseResponse: Response object with success/error information
            
        Raises:
            ValueError: If neither body nor file is provided
            ContextbaseError: If the API request fails and raise_for_status() is called
            
        Example:
            >>> client = Contextbase()
            >>> response = client.publish(
            ...     "my_context", 
            ...     "data_component", 
            ...     body={"key": "value"}
            ... )
            >>> if response.ok:
            ...     print("Data published successfully!")
        """
        if not body and not file:
            raise ValueError("Either 'body' or 'file' is required")

        data = {"component_name": component_name}
        if body:
            data["body"] = body
        if file:
            data["file"] = file
        if scopes:
            data["scopes"] = scopes

        response = self.http_client.post(f"/v1/contexts/{context_name}/data", data=data)
        return response

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
            ...     print(f"Resolved context: #{result}")
        """
        data = {}
        if scopes:
            data["scopes"] = scopes
        if query:
            data["query"] = query

        response = self.http_client.post(f"/v1/contexts/{context_name}/resolve", data=data)
        return response
