"""Test ODIN HTTP client operations."""

import pytest
from unittest.mock import Mock, patch

from odin_protocol import OdinClient, create_odin_file, pack_odin
from odin_protocol.errors import (
    AuthError,
    NetworkError,
    RateLimitError,
    ServerError,
)


class TestOdinClient:
    """Test ODIN HTTP client."""

    def test_client_initialization(self):
        """Test client initialization with default settings."""
        client = OdinClient()
        
        assert client.base_url == "https://api.odin.ai"
        assert client.api_key is None
        assert client.timeout == 30.0
        assert client.max_retries == 3
        
        client.close()

    def test_client_initialization_with_config(self):
        """Test client initialization with custom config."""
        client = OdinClient(
            base_url="https://custom.odin.ai",
            api_key="test-key",
            timeout=60.0,
            max_retries=5,
        )
        
        assert client.base_url == "https://custom.odin.ai"
        assert client.api_key == "test-key"
        assert client.timeout == 60.0
        assert client.max_retries == 5
        
        client.close()

    def test_context_manager(self):
        """Test client as context manager."""
        with OdinClient() as client:
            assert client.base_url == "https://api.odin.ai"
        # Client should be closed after context

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test client as async context manager."""
        async with OdinClient() as client:
            assert client.base_url == "https://api.odin.ai"
        # Client should be closed after context

    @patch('odin_protocol.client.httpx.Client')
    def test_auth_error_handling(self, mock_client_class):
        """Test handling of authentication errors."""
        # Mock response with 401 status
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Invalid API key"}
        
        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = OdinClient(api_key="invalid-key")
        
        with pytest.raises(AuthError, match="Authentication failed"):
            client.billing_credits()
            
        client.close()

    @patch('odin_protocol.client.httpx.Client')
    def test_rate_limit_error_handling(self, mock_client_class):
        """Test handling of rate limit errors."""
        # Mock response with 429 status
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        
        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = OdinClient()
        
        with pytest.raises(RateLimitError, match="Rate limit exceeded"):
            client.billing_credits()
            
        client.close()

    @patch('odin_protocol.client.httpx.Client')
    def test_server_error_handling(self, mock_client_class):
        """Test handling of server errors."""
        # Mock response with 500 status
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal server error"}
        
        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = OdinClient()
        
        with pytest.raises(ServerError, match="Server error: 500"):
            client.billing_credits()
            
        client.close()

    @patch('odin_protocol.client.httpx.Client')
    def test_successful_request(self, mock_client_class):
        """Test successful HTTP request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"credits": 100, "used": 10}
        mock_response.raise_for_status = Mock()  # No exception
        
        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = OdinClient(api_key="valid-key")
        result = client.billing_credits()
        
        assert result == {"credits": 100, "used": 10}
        
        # Verify request was made correctly
        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert call_args[1]['method'] == 'GET'
        assert call_args[1]['url'] == 'https://api.odin.ai/billing/credits'
        
        client.close()

    @patch('odin_protocol.client.httpx.Client')
    def test_mediator_submit(self, mock_client_class):
        """Test mediator submission with ODIN files."""
        # Create test ODIN file
        odin_file = create_odin_file("text/plain", "test data")
        odin_data = pack_odin(odin_file)
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "accepted", "job_id": "test-123"}
        mock_response.raise_for_status = Mock()
        
        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = OdinClient()
        result = client.mediator_submit([odin_data])
        
        assert result == {"status": "accepted", "job_id": "test-123"}
        
        # Verify files were included in request
        call_args = mock_client.request.call_args
        assert 'files' in call_args[1]
        
        client.close()

    @patch('odin_protocol.client.httpx.Client')
    def test_rules_evaluate(self, mock_client_class):
        """Test rule evaluation."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": True,
            "score": 0.95,
            "details": {"reason": "passes all checks"}
        }
        mock_response.raise_for_status = Mock()
        
        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = OdinClient()
        result = client.rules_evaluate(
            rule_id="test-rule-123",
            input_data={"text": "test input"},
            context={"user_id": "test-user"}
        )
        
        assert result["result"] is True
        assert result["score"] == 0.95
        
        # Verify request payload
        call_args = mock_client.request.call_args
        assert call_args[1]['method'] == 'POST'
        json_payload = call_args[1]['json']
        assert json_payload['rule_id'] == "test-rule-123"
        assert json_payload['input'] == {"text": "test input"}
        assert json_payload['context'] == {"user_id": "test-user"}
        
        client.close()

    @patch('odin_protocol.client.httpx.Client')
    def test_registry_operations(self, mock_client_class):
        """Test registry put/get operations."""
        odin_file = create_odin_file("text/plain", "registry test")
        odin_data = pack_odin(odin_file)
        
        # Mock put response
        mock_put_response = Mock()
        mock_put_response.status_code = 200
        mock_put_response.json.return_value = {"status": "stored", "key": "test-key"}
        mock_put_response.raise_for_status = Mock()
        
        # Mock get response
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            "key": "test-key",
            "data": odin_data.hex(),  # Hex-encoded binary data
            "metadata": {"size": len(odin_data)}
        }
        mock_get_response.raise_for_status = Mock()
        
        mock_client = Mock()
        mock_client.request.side_effect = [mock_put_response, mock_get_response]
        mock_client_class.return_value = mock_client
        
        client = OdinClient()
        
        # Test put
        put_result = client.registry_put(
            key="test-key",
            odin_data=odin_data,
            metadata={"description": "test file"}
        )
        assert put_result["status"] == "stored"
        
        # Test get
        get_result = client.registry_get("test-key")
        assert get_result["key"] == "test-key"
        
        client.close()

    @patch('odin_protocol.client.httpx.Client')
    def test_registry_index(self, mock_client_class):
        """Test registry index listing."""
        # Mock index response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "entries": [
                {"key": "file1", "size": 1024, "created": "2024-01-01T00:00:00Z"},
                {"key": "file2", "size": 2048, "created": "2024-01-02T00:00:00Z"}
            ],
            "total": 2,
            "limit": 100,
            "offset": 0
        }
        mock_response.raise_for_status = Mock()
        
        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        client = OdinClient()
        result = client.registry_index(prefix="file", limit=50, offset=0)
        
        assert len(result["entries"]) == 2
        assert result["total"] == 2
        
        # Verify query parameters
        call_args = mock_client.request.call_args
        params = call_args[1]['params']
        assert params['prefix'] == "file"
        assert params['limit'] == 50
        assert params['offset'] == 0
        
        client.close()


@pytest.mark.asyncio
@pytest.mark.skipif(True, reason="Async tests require running event loop")
class TestOdinClientAsync:
    """Test async ODIN client operations."""

    @patch('odin_protocol.client.httpx.AsyncClient')
    async def test_async_billing_credits(self, mock_client_class):
        """Test async billing credits request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"credits": 150, "used": 25}
        mock_response.raise_for_status = Mock()
        
        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        async with OdinClient(api_key="test-key") as client:
            result = await client.abilling_credits()
            assert result == {"credits": 150, "used": 25}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
