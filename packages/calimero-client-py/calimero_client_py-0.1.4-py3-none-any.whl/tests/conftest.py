import pytest
import os
from pathlib import Path
import tempfile
import toml
import base58
import nacl.signing
from calimero import Ed25519Keypair, Config

def create_test_keypair():
    """Create a test keypair with proper encoding."""
    signing_key = nacl.signing.SigningKey.generate()
    keypair_bytes = b'\x08\x01\x12\x40' + signing_key.encode() + signing_key.verify_key.encode()
    return base58.b58encode(keypair_bytes).decode()

@pytest.fixture
def temp_config_file():
    """Create a temporary TOML config file."""
    keypair_base58 = create_test_keypair()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        toml.dump({
            'identity': {
                'keypair': keypair_base58
            },
            'network': {
                'rpc_url': 'http://localhost:2428',
                'context_id': 'test-context',
                'executor_public_key': 'test-executor',
                'node_name': 'test-node'
            }
        }, f)
        return f.name

@pytest.fixture
def ed25519_keypair():
    """Create a test Ed25519 keypair."""
    signing_key = nacl.signing.SigningKey.generate()
    return Ed25519Keypair(signing_key)

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables."""
    keypair_base58 = create_test_keypair()
    monkeypatch.setenv('RPC_URL', 'http://localhost:2428')
    monkeypatch.setenv('CONTEXT_ID', 'test-context')
    monkeypatch.setenv('EXECUTOR_PUBLIC_KEY', 'test-executor')
    monkeypatch.setenv('CALIMERO_NODE_NAME', 'test-node')
    monkeypatch.setenv('CALIMERO_KEYPAIR', keypair_base58)
    return monkeypatch

@pytest.fixture
def config(temp_config_file, mock_env_vars):
    """Create a test Config instance."""
    return Config.load_from_file(temp_config_file)

@pytest.fixture
def mock_ws_url():
    """Return a mock WebSocket URL for testing."""
    return "ws://localhost:2428/ws"

@pytest.fixture
def mock_rpc_url():
    """Return a mock RPC URL for testing."""
    return "http://localhost:2428/jsonrpc" 