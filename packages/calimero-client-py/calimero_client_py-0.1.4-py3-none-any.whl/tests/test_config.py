import pytest
import os
import tempfile
import toml
import base58
import nacl.signing
from calimero import Config, ConfigError, Ed25519Keypair

def test_config_creation(temp_config_file, mock_env_vars):
    """Test config creation."""
    config = Config.load_from_file(temp_config_file)
    assert config.node_url == "http://localhost:2428"
    assert config.context_id == "test-context"
    assert config.executor_public_key == "test-executor"
    assert config.node_name == "test-node"
    assert isinstance(config.keypair, Ed25519Keypair)

def test_config_from_file(temp_config_file, mock_env_vars):
    """Test loading config from file."""
    config = Config.load_from_file(temp_config_file)
    assert config.node_url == "http://localhost:2428"
    assert config.context_id == "test-context"
    assert config.executor_public_key == "test-executor"
    assert config.node_name == "test-node"
    assert isinstance(config.keypair, Ed25519Keypair)

def test_config_from_env(mock_env_vars, temp_config_file):
    """Test loading config from environment variables."""
    config = Config.load_from_env()
    assert config.node_url == "http://localhost:2428"
    assert config.context_id == "test-context"
    assert config.executor_public_key == "test-executor"
    assert config.node_name == "test-node"
    assert isinstance(config.keypair, Ed25519Keypair)

def test_config_missing_env_vars(monkeypatch):
    """Test config behavior when environment variables are missing."""
    # Clear environment variables
    monkeypatch.delenv('RPC_URL', raising=False)
    monkeypatch.delenv('CONTEXT_ID', raising=False)
    monkeypatch.delenv('EXECUTOR_PUBLIC_KEY', raising=False)
    monkeypatch.delenv('CALIMERO_NODE_NAME', raising=False)
    monkeypatch.delenv('CALIMERO_KEYPAIR', raising=False)

    # Should raise ConfigError when required variables are missing
    with pytest.raises(ConfigError):
        Config.load_from_env()

def test_config_with_keypair(temp_config_file, mock_env_vars):
    """Test config with keypair."""
    config = Config.load_from_file(temp_config_file)
    assert isinstance(config.keypair, Ed25519Keypair)
    assert len(config.keypair.public_key) == 32
    assert len(config.keypair.private_key) == 32

def test_config_missing_keypair():
    """Test config behavior when keypair is missing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        toml.dump({
            'network': {
                'rpc_url': 'http://localhost:2428',
                'context_id': 'test-context',
                'executor_public_key': 'test-executor',
                'node_name': 'test-node'
            }
        }, f)
        f.flush()
        
        with pytest.raises(ConfigError):
            Config.load_from_file(f.name) 