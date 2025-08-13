import pytest
import nacl.signing
import base58
from calimero import Ed25519Keypair, KeypairError

def test_keypair_creation():
    """Test creating a keypair."""
    # Generate a new keypair
    signing_key = nacl.signing.SigningKey.generate()
    keypair = Ed25519Keypair(signing_key)
    
    # Verify public key
    assert keypair.public_key == signing_key.verify_key.encode()
    assert keypair.public_key_b58 == base58.b58encode(signing_key.verify_key.encode()).decode()

def test_keypair_from_base58():
    """Test creating keypair from base58-encoded keypair with protobuf prefix."""
    # Generate a new keypair
    signing_key = nacl.signing.SigningKey.generate()
    
    # Create keypair bytes with protobuf prefix
    keypair_bytes = b'\x08\x01\x12\x40' + signing_key.encode() + signing_key.verify_key.encode()
    keypair_base58 = base58.b58encode(keypair_bytes).decode()
    
    # Create keypair from base58
    keypair = Ed25519Keypair.from_base58(keypair_base58)
    
    # Verify public key
    assert keypair.public_key == signing_key.verify_key.encode()
    assert keypair.public_key_b58 == base58.b58encode(signing_key.verify_key.encode()).decode()

def test_sign_and_verify():
    """Test signing and verifying messages."""
    # Generate a new keypair
    signing_key = nacl.signing.SigningKey.generate()
    keypair = Ed25519Keypair(signing_key)
    
    # Sign a message
    message = b"test message"
    signature = keypair.sign(message)
    
    # Verify the signature
    assert keypair.verify(message, signature)
    
    # Verify with wrong message
    assert not keypair.verify(b"wrong message", signature)

def test_sign_and_verify_base58():
    """Test signing and verifying messages with base58 encoding."""
    # Generate a new keypair
    signing_key = nacl.signing.SigningKey.generate()
    keypair = Ed25519Keypair(signing_key)
    
    # Sign a message
    message = "test message"
    signature_base58 = keypair.sign_base58(message)
    
    # Verify the signature
    assert keypair.verify_base58(message, signature_base58)
    
    # Verify with wrong message
    assert not keypair.verify_base58("wrong message", signature_base58)

def test_invalid_base58():
    """Test handling of invalid base58 string."""
    with pytest.raises(KeypairError):
        Ed25519Keypair.from_base58("")

def test_invalid_keypair_length():
    """Test handling of invalid keypair length."""
    # Generate a keypair with wrong length
    signing_key = nacl.signing.SigningKey.generate()
    keypair_bytes = b'\x08\x01\x12\x40' + signing_key.encode()  # Missing verify key
    keypair_base58 = base58.b58encode(keypair_bytes).decode()
    
    with pytest.raises(KeypairError):
        Ed25519Keypair.from_base58(keypair_base58)

def test_invalid_protobuf_prefix():
    """Test handling of invalid protobuf prefix."""
    # Generate a keypair with wrong prefix
    signing_key = nacl.signing.SigningKey.generate()
    keypair_bytes = b'\x00\x00\x00\x00' + signing_key.encode() + signing_key.verify_key.encode()
    keypair_base58 = base58.b58encode(keypair_bytes).decode()
    
    with pytest.raises(KeypairError):
        Ed25519Keypair.from_base58(keypair_base58) 