import asyncio
import time
import base58
import json
from typing import Optional, Dict, Any, TypedDict, List
import aiohttp
from .keypair import Ed25519Keypair

class JsonRpcError(Exception):
    """Base exception for JSON-RPC errors."""
    pass

class JsonRpcResponse(TypedDict):
    """Type definition for JSON-RPC response."""
    jsonrpc: str
    id: int
    result: Optional[Dict[str, Any]]
    error: Optional[Dict[str, Any]]

class JsonRpcClient:
    """JSON-RPC client for Calimero.
    
    This client handles communication with the Calimero JSON-RPC server,
    including request formatting, signing, and response handling.
    """
    
    # Constants
    JSONRPC_VERSION = '2.0'
    DEFAULT_TIMEOUT = 1000
    JSONRPC_PATH = '/jsonrpc/dev'
    
    def __init__(
        self,
        rpc_url: str,
        keypair: Ed25519Keypair,
        context_id: str,
        executor_public_key: str
    ):
        """Initialize the JSON-RPC client with all required parameters.
        
        Args:
            rpc_url: The URL of the Calimero JSON-RPC server.
            keypair: The Ed25519 keypair for signing requests.
            context_id: The context ID for the requests.
            executor_public_key: The public key of the executor.
        """
        self.rpc_url = rpc_url.rstrip('/')
        self.keypair = keypair
        self.context_id = context_id
        self.executor_public_key = executor_public_key
    
    def _prepare_headers(self) -> Dict[str, str]:
        """Prepare request headers with signature and timestamp.
        
        Returns:
            Dictionary containing request headers.
        """
        timestamp = str(int(time.time()))
        signature = self.keypair.sign(timestamp.encode())
        signature_b58 = base58.b58encode(signature).decode()
        
        return {
            'Content-Type': 'application/json',
            'X-Signature': signature_b58,
            'X-Timestamp': timestamp
        }
    
    def _prepare_request(self, method: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Prepare the JSON-RPC request payload.
        
        Args:
            method: The method to call.
            args: Optional arguments for the method.
            
        Returns:
            Dictionary containing the JSON-RPC request payload.
        """
        return {
            'jsonrpc': self.JSONRPC_VERSION,
            'id': 1,
            'method': 'execute',
            'params': {
                'contextId': self.context_id,
                'method': method,
                'argsJson': args or {},
                'executorPublicKey': self.executor_public_key,
                'timeout': self.DEFAULT_TIMEOUT
            }
        }
    
    async def _handle_response(self, response: aiohttp.ClientResponse) -> JsonRpcResponse:
        """Handle the JSON-RPC response.
        
        Args:
            response: The aiohttp response object.
            
        Returns:
            The parsed JSON-RPC response.
            
        Raises:
            JsonRpcError: If the response indicates an error.
        """
        try:
            data = await response.json()
            if 'error' in data and data['error']:
                raise JsonRpcError(f"JSON-RPC error: {data['error']}")
            return data
        except json.JSONDecodeError as e:
            raise JsonRpcError(f"Failed to decode JSON response: {str(e)}")
    
    async def execute(self, method: str, args: Optional[Dict[str, Any]] = None) -> JsonRpcResponse:
        """Execute a JSON-RPC method.
        
        Args:
            method: The method to call.
            args: Optional arguments for the method.
            
        Returns:
            The JSON-RPC response.
            
        Raises:
            JsonRpcError: If the request fails or returns an error.
        """
        url = f"{self.rpc_url}{self.JSONRPC_PATH}"
        headers = self._prepare_headers()
        payload = self._prepare_request(method, args)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                return await self._handle_response(response)




    



    



    

    

    

    





    

    


