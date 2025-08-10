from .contextbase import Contextbase
from .file import ContextbaseFile
from functools import wraps
from typing import Dict, Any, Optional, Callable, TypeVar, Union

# Type variable for the decorated function
F = TypeVar('F', bound=Callable[..., Any])

def publish(
    context_name: str, 
    component_name: str, 
    scopes: Optional[Dict[str, Any]] = None, 
    raise_on_error: bool = False,
    as_file: bool = False,
    file_name: Optional[str] = None
) -> Callable[[F], F]:
    """
    Decorator factory for publishing function results to Contextbase.

    This decorator automatically publishes the return value of a function
    to a specified Contextbase context after the function executes.

    Args:
        context_name: Name of the context to publish to
        component_name: Name of the component within the context
        scopes: Optional scoping information for the published data
        raise_on_error: If True, raises ContextbaseError on API failures.
                       If False, silently continues on API errors.
        as_file: If True, treats the return value as file content and uploads it as a file.
                When True, the function should return bytes or str content.
        file_name: Name for the file when as_file=True. If not provided, uses "output.txt"

    Returns:
        Decorator function that wraps the original function

    Example:
        >>> @publish('ml-models', 'prediction-service', raise_on_error=True)
        ... def predict(features):
        ...     return {"prediction": 0.95, "confidence": 0.87}
        ...
        >>> result = predict([1, 2, 3])  # Function runs normally
        >>> # Result is automatically published to Contextbase
        
    Example with file output:
        >>> @publish(
        ...     context_name='reports', 
        ...     component_name='daily-summary',
        ...     as_file=True,
        ...     file_name='summary.txt'
        ... )
        ... def generate_report():
        ...     return "Daily Summary: Everything looks good!"
        ...
        >>> report = generate_report()  # Content uploaded as a file
        
    Example with scopes:
        >>> @publish(
        ...     context_name='analytics',
        ...     component_name='user-events', 
        ...     scopes={'environment': 'production'},
        ...     raise_on_error=False
        ... )
        ... def track_user_action(user_id, action):
        ...     return {"user_id": user_id, "action": action, "timestamp": time.time()}
    """

    def decorator(func: F) -> F:
        """The actual decorator that wraps the function."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Execute the original function first
            result = func(*args, **kwargs)
            
            # Attempt to publish the result to Contextbase
            try:
                cb = Contextbase()
                
                if as_file:
                    # Create ContextbaseFile object from function result
                    file_name_final = file_name or f"{func.__name__}_output.txt"
                    file_obj = ContextbaseFile.from_data(
                        content=result,
                        name=file_name_final
                    )
                    
                    response = cb.publish(
                        context_name=context_name,
                        component_name=component_name,
                        file=file_obj,
                        scopes=scopes
                    )
                else:
                    response = cb.publish(
                        context_name=context_name,
                        component_name=component_name,
                        scopes=scopes,
                        body=result
                    )
                
                if raise_on_error:
                    response.raise_for_status()
                    
            except Exception as e:
                if raise_on_error:
                    raise
                pass
            
            return result
            
        return wrapper  # type: ignore
    return decorator
