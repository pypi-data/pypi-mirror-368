import pytest
import aiohttp
import os
from unittest.mock import Mock, patch
from calimero import JsonRpcClient, Ed25519Keypair, JsonRpcError

@pytest.fixture
def mock_keypair():
    """Create a mock keypair for testing."""
    keypair = Mock(spec=Ed25519Keypair)
    keypair.sign.return_value = b"signature"
    return keypair

@pytest.mark.asyncio
async def test_json_rpc_client_creation(mock_keypair):
    """Test JsonRpcClient initialization."""
    client = JsonRpcClient(
        rpc_url="http://localhost:2428",
        keypair=mock_keypair,
        context_id="test_context",
        executor_public_key="test_key"
    )
    assert client.rpc_url == "http://localhost:2428"
    assert client.context_id == "test_context"
    assert client.executor_public_key == "test_key"

@pytest.mark.asyncio
async def test_prepare_headers(mock_keypair):
    """Test header preparation."""
    client = JsonRpcClient(
        rpc_url="http://localhost:2428",
        keypair=mock_keypair,
        context_id="test_context",
        executor_public_key="test_key"
    )
    headers = client._prepare_headers()
    
    assert 'Content-Type' in headers
    assert 'X-Signature' in headers
    assert 'X-Timestamp' in headers
    assert headers['Content-Type'] == 'application/json'

@pytest.mark.asyncio
async def test_prepare_request(mock_keypair):
    """Test request preparation."""
    client = JsonRpcClient(
        rpc_url="http://localhost:2428",
        keypair=mock_keypair,
        context_id="test_context",
        executor_public_key="test_key"
    )
    request = client._prepare_request("test_method", {"arg": "value"})
    
    assert request['jsonrpc'] == '2.0'
    assert request['method'] == 'execute'
    assert request['params']['contextId'] == 'test_context'
    assert request['params']['method'] == 'test_method'
    assert request['params']['argsJson'] == {"arg": "value"}
    assert request['params']['executorPublicKey'] == 'test_key'

@pytest.mark.asyncio
async def test_execute_request(mock_keypair):
    """Test executing RPC request."""
    client = JsonRpcClient(
        rpc_url="http://localhost:2428",
        keypair=mock_keypair,
        context_id="test_context",
        executor_public_key="test_key"
    )
    
    mock_response = {
        "jsonrpc": "2.0",
        "result": {"success": True},
        "id": 1
    }
    
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value.json.return_value = mock_response
        mock_post.return_value.__aenter__.return_value.status = 200
        
        response = await client.execute("test_method", {"arg": "value"})
        assert response == mock_response
        
        # Verify request was made with correct parameters
        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]
        assert "json" in call_args
        assert call_args["json"]["method"] == "execute"
        assert call_args["json"]["params"]["contextId"] == "test_context"

@pytest.mark.asyncio
async def test_execute_request_error(mock_keypair):
    """Test error handling in RPC request."""
    client = JsonRpcClient(
        rpc_url="http://localhost:2428",
        keypair=mock_keypair,
        context_id="test_context",
        executor_public_key="test_key"
    )
    
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_post.return_value.__aenter__.return_value.json.return_value = {
            "jsonrpc": "2.0",
            "error": {"code": -32000, "message": "Error message"},
            "id": 1
        }
        mock_post.return_value.__aenter__.return_value.status = 200
        
        with pytest.raises(JsonRpcError) as exc_info:
            await client.execute("test_method", {"arg": "value"})
        assert "JSON-RPC error" in str(exc_info.value) 