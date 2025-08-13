import os
from pathlib import Path
from typing import Optional, Dict, Any
import toml
from pydantic import BaseModel, ConfigDict
from .keypair import Ed25519Keypair

class IdentityConfig(BaseModel):
    peer_id: str
    keypair: str

class SwarmConfig(BaseModel):
    listen: list[str]

class ServerConfig(BaseModel):
    listen: list[str]
    admin: Dict[str, bool]
    jsonrpc: Dict[str, bool]
    websocket: Dict[str, bool]

class ConfigError(Exception):
    """Exception raised for configuration-related errors."""
    pass

class Config:
    """Configuration for Calimero client."""
    
    def __init__(self, file_path: str):
        """Initialize with a TOML file path."""
        self._config_data = self._load_toml(file_path)
        
        # Load keypair
        keypair_value = self._config_data.get('identity', {}).get('keypair')
        if not keypair_value:
            raise ConfigError("'keypair' not found in [identity] section")
        self.keypair = Ed25519Keypair.from_base58(keypair_value)
        
        # Load network configuration
        network = self._config_data.get('network', {})
        self.node_url = network.get('rpc_url')
        self.context_id = network.get('context_id')
        self.executor_public_key = network.get('executor_public_key')
        self.node_name = network.get('node_name')
        
        # Validate required fields
        if not self.node_url:
            raise ConfigError("'rpc_url' not found in [network] section")
        if not self.context_id:
            raise ConfigError("'context_id' not found in [network] section")
        if not self.executor_public_key:
            raise ConfigError("'executor_public_key' not found in [network] section")
        if not self.node_name:
            raise ConfigError("'node_name' not found in [network] section")
    
    def __getitem__(self, key: str) -> Any:
        """Allow dynamic access to raw config data."""
        return self._config_data[key]
    
    def __getattr__(self, name: str) -> Any:
        """Allow dynamic access to config sections."""
        if name in self._config_data:
            return self._config_data[name]
        raise AttributeError(f"'Config' object has no attribute '{name}'")
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'Config':
        """Load configuration from a TOML file."""
        return cls(file_path)
    
    @classmethod
    def get_default_config_path(cls) -> Path:
        """Get the default configuration path."""
        node_name = os.getenv('CALIMERO_NODE_NAME', 'node1')
        return Path.home() / '.calimero' / node_name / 'config.toml'
    
    def _load_toml(self, file_path: str) -> dict:
        """Load and parse TOML file."""
        try:
            with open(file_path, 'r') as f:
                return toml.load(f)
        except Exception as e:
            raise ConfigError(f"Failed to load config file: {str(e)}")
    
    @classmethod
    def load_from_env(cls) -> 'Config':
        """Load configuration from environment variables."""
        import tempfile
        
        # Create temporary TOML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            config_data = {
                'identity': {
                    'keypair': os.getenv('CALIMERO_KEYPAIR')
                },
                'network': {
                    'rpc_url': os.getenv('RPC_URL', 'http://localhost:2428'),
                    'context_id': os.getenv('CONTEXT_ID'),
                    'executor_public_key': os.getenv('EXECUTOR_PUBLIC_KEY'),
                    'node_name': os.getenv('CALIMERO_NODE_NAME')
                }
            }
            toml.dump(config_data, f)
            f.flush()
            return cls(f.name) 