import base58
from typing import Tuple
import nacl.signing
import nacl.encoding
from typing import Optional

class KeypairError(Exception):
    """Exception raised for keypair-related errors."""
    pass

class Ed25519Keypair:
    """Ed25519 keypair implementation."""
    
    PROTOBUF_PREFIX = b'\x08\x01\x12\x40'  # 4-byte protobuf prefix for Ed25519 keypair

    def __init__(self, signing_key: nacl.signing.SigningKey):
        """Initialize with a PyNaCl signing key."""
        self._signing_key = signing_key
        self._verify_key = signing_key.verify_key

    @classmethod
    def generate(cls) -> 'Ed25519Keypair':
        """Generate a new random Ed25519 keypair."""
        signing_key = nacl.signing.SigningKey.generate()
        return cls(signing_key)

    @classmethod
    def from_base58(cls, base58_keypair: str) -> 'Ed25519Keypair':
        """Create a keypair from a base58-encoded keypair string."""
        if not base58_keypair:
            raise KeypairError("Base58 keypair cannot be None")

        try:
            # Decode base58
            key_bytes = base58.b58decode(base58_keypair)

            # Validate keypair length (should be 68 bytes: 4-byte prefix + 64-byte keypair)
            if len(key_bytes) != 68:
                raise KeypairError(f"Unexpected keypair length: {len(key_bytes)} bytes (expected 68)")

            # Validate protobuf prefix
            prefix = key_bytes[:4]
            if prefix != cls.PROTOBUF_PREFIX:
                raise KeypairError(f"Invalid protobuf prefix: {prefix.hex()} (expected {cls.PROTOBUF_PREFIX.hex()})")

            # Extract private key (first 32 bytes after prefix)
            private_key = key_bytes[4:36]
            if len(private_key) != 32:
                raise KeypairError(f"Invalid private key length: {len(private_key)} (expected 32)")

            # Create signing key from private key
            signing_key = nacl.signing.SigningKey(private_key)
            return cls(signing_key)

        except Exception as e:
            raise KeypairError(f"Failed to create keypair: {str(e)}")

    def to_base58(self) -> str:
        """Convert keypair to base58-encoded string with protobuf prefix."""
        # Get the private key bytes
        private_key = self._signing_key.encode()
        
        # Create the full keypair bytes with protobuf prefix
        keypair_bytes = self.PROTOBUF_PREFIX + private_key
        
        # Encode to base58
        return base58.b58encode(keypair_bytes).decode()

    def sign(self, message: bytes) -> bytes:
        """Sign a message."""
        return self._signing_key.sign(message).signature

    def verify(self, message: bytes, signature: bytes) -> bool:
        """Verify a signature."""
        try:
            self._verify_key.verify(message, signature)
            return True
        except nacl.exceptions.BadSignatureError:
            return False

    def get_public_key(self) -> bytes:
        """Get the public key."""
        return self._verify_key.encode()

    def get_public_key_base58(self) -> str:
        """Get the public key as base58-encoded string."""
        return base58.b58encode(self.get_public_key()).decode()

    @property
    def public_key(self) -> bytes:
        """Get the public key in raw bytes."""
        return self._verify_key.encode()
    
    @property
    def public_key_b58(self) -> str:
        """Get the public key in base58 format."""
        return base58.b58encode(self.public_key).decode()
    
    @property
    def private_key(self) -> bytes:
        """Get the private key."""
        return self._signing_key.encode()

    @property
    def private_key_base58(self) -> str:
        """Get the base58-encoded private key."""
        return base58.b58encode(self.private_key).decode()

    def sign_base58(self, message: str) -> str:
        """Sign a message and return base58-encoded signature."""
        signature = self.sign(message.encode())
        return base58.b58encode(signature).decode()

    def verify_base58(self, message: str, base58_signature: str) -> bool:
        """Verify a base58-encoded signature."""
        signature = base58.b58decode(base58_signature)
        return self.verify(message.encode(), signature) 