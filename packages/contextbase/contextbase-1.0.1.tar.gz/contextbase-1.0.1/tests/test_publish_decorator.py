import pytest
from unittest.mock import Mock, patch
from contextbase.publish import publish
from contextbase.http_response import ContextbaseError


class TestPublishDecorator:
    """Test suite for the @publish decorator."""
    
    @patch('contextbase.publish.Contextbase')
    def test_decorator_basic_functionality(self, mock_contextbase_class):
        """Test that decorator publishes function result."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_client.publish.return_value = mock_response
        mock_contextbase_class.return_value = mock_client
        
        # Decorate a function
        @publish('test-context', 'test-component')
        def sample_function(x, y):
            return {"result": x + y}
        
        # Execute
        result = sample_function(1, 2)
        
        # Verify function result is returned
        assert result == {"result": 3}
        
        # Verify Contextbase was called correctly
        mock_contextbase_class.assert_called_once()
        mock_client.publish.assert_called_once_with(
            context_name='test-context',
            component_name='test-component',
            scopes=None,
            body={"result": 3}
        )
        mock_response.raise_for_status.assert_not_called()  # raise_on_error=False by default
    
    @patch('contextbase.publish.Contextbase')
    def test_decorator_with_scopes(self, mock_contextbase_class):
        """Test decorator with scopes parameter."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_client.publish.return_value = mock_response
        mock_contextbase_class.return_value = mock_client
        
        # Decorate a function with scopes
        @publish('test-context', 'test-component', scopes={'env': 'test'})
        def sample_function():
            return {"data": "test"}
        
        # Execute
        result = sample_function()
        
        # Verify
        assert result == {"data": "test"}
        mock_client.publish.assert_called_once_with(
            context_name='test-context',
            component_name='test-component',
            scopes={'env': 'test'},
            body={"data": "test"}
        )
    
    @patch('contextbase.publish.Contextbase')
    def test_decorator_with_raise_on_error_true(self, mock_contextbase_class):
        """Test decorator with raise_on_error=True."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_client.publish.return_value = mock_response
        mock_contextbase_class.return_value = mock_client
        
        # Decorate a function
        @publish('test-context', 'test-component', raise_on_error=True)
        def sample_function():
            return {"success": True}
        
        # Execute
        result = sample_function()
        
        # Verify
        assert result == {"success": True}
        mock_response.raise_for_status.assert_called_once()
    
    @patch('contextbase.publish.Contextbase')
    def test_decorator_silently_handles_publish_error(self, mock_contextbase_class):
        """Test that decorator silently handles publish errors when raise_on_error=False."""
        # Setup
        mock_client = Mock()
        mock_client.publish.side_effect = Exception("Network error")
        mock_contextbase_class.return_value = mock_client
        
        # Decorate a function
        @publish('test-context', 'test-component', raise_on_error=False)
        def sample_function():
            return {"data": "important"}
        
        # Execute - should not raise exception
        result = sample_function()
        
        # Verify function still returns result despite publish error
        assert result == {"data": "important"}
        mock_client.publish.assert_called_once()
    
    @patch('contextbase.publish.Contextbase')
    def test_decorator_raises_publish_error_when_configured(self, mock_contextbase_class):
        """Test that decorator raises publish errors when raise_on_error=True."""
        # Setup
        mock_client = Mock()
        mock_client.publish.side_effect = Exception("Network error")
        mock_contextbase_class.return_value = mock_client
        
        # Decorate a function
        @publish('test-context', 'test-component', raise_on_error=True)
        def sample_function():
            return {"data": "important"}
        
        # Execute - should raise exception
        with pytest.raises(Exception, match="Network error"):
            sample_function()
        
        mock_client.publish.assert_called_once()
    
    @patch('contextbase.publish.Contextbase')
    def test_decorator_raises_contextbase_error_when_configured(self, mock_contextbase_class):
        """Test that decorator raises ContextbaseError when response.raise_for_status() fails."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = ContextbaseError("API Error", status_code=400)
        mock_client.publish.return_value = mock_response
        mock_contextbase_class.return_value = mock_client
        
        # Decorate a function
        @publish('test-context', 'test-component', raise_on_error=True)
        def sample_function():
            return {"data": "test"}
        
        # Execute - should raise ContextbaseError
        with pytest.raises(ContextbaseError, match="API Error"):
            sample_function()
        
        mock_client.publish.assert_called_once()
        mock_response.raise_for_status.assert_called_once()
    
    @patch('contextbase.publish.Contextbase')
    def test_decorator_preserves_function_metadata(self, mock_contextbase_class):
        """Test that decorator preserves original function's metadata."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_client.publish.return_value = mock_response
        mock_contextbase_class.return_value = mock_client
        
        # Decorate a function
        @publish('test-context', 'test-component')
        def sample_function(x: int, y: int) -> dict:
            """This is a sample function that adds two numbers."""
            return {"result": x + y}
        
        # Verify metadata is preserved
        assert sample_function.__name__ == "sample_function"
        assert "sample function that adds two numbers" in sample_function.__doc__
        
        # Verify function still works
        result = sample_function(5, 3)
        assert result == {"result": 8}
    
    @patch('contextbase.publish.Contextbase')
    def test_decorator_with_complex_function_arguments(self, mock_contextbase_class):
        """Test decorator with function that has various argument types."""
        # Setup
        mock_client = Mock()
        mock_response = Mock()
        mock_client.publish.return_value = mock_response
        mock_contextbase_class.return_value = mock_client
        
        # Decorate a function with various argument types
        @publish('test-context', 'test-component')
        def complex_function(pos_arg, *args, kwarg_with_default="default", **kwargs):
            return {
                "pos_arg": pos_arg,
                "args": args,
                "kwarg_with_default": kwarg_with_default,
                "kwargs": kwargs
            }
        
        # Execute with various arguments
        result = complex_function(
            "first", 
            "second", 
            "third", 
            kwarg_with_default="custom",
            extra_kwarg="extra"
        )
        
        # Verify result
        expected_result = {
            "pos_arg": "first",
            "args": ("second", "third"),
            "kwarg_with_default": "custom",
            "kwargs": {"extra_kwarg": "extra"}
        }
        assert result == expected_result
        
        # Verify the result was published
        mock_client.publish.assert_called_once_with(
            context_name='test-context',
            component_name='test-component',
            scopes=None,
            body=expected_result
        )


if __name__ == "__main__":
    pytest.main([__file__]) 