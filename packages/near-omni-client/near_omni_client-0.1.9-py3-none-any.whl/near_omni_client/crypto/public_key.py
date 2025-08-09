import secp256k1
from base58 import b58decode, b58encode
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

from .types import KeySize, KeyType


class PublicKey:
    """Represents a NEAR public key."""

    def __init__(self, key_type: KeyType, data: bytes):
        if key_type == KeyType.ED25519:
            if len(data) != KeySize.PUBLIC_KEY:
                raise ValueError(f"Invalid public key size ({len(data)}), must be 32")
        elif key_type == KeyType.SECP256K1:
            if len(data) != KeySize.PUBLIC_KEY_SECP256K1:
                raise ValueError("Invalid SECP256K1 public key size")
        else:
            raise ValueError(f"Unknown key type: {key_type}")

        self._key_type = key_type
        self._data = data

    @staticmethod
    def from_string(encoded_key: str) -> "PublicKey":
        """Create a PublicKey instance from a string representation."""
        parts = encoded_key.split(":")
        if len(parts) == 1:
            raw_key = parts[0]
            decoded = b58decode(raw_key)
            inferred_type = KeyType.SECP256K1 if len(decoded) == 64 else KeyType.ED25519
            return PublicKey(inferred_type, decoded)
        elif len(parts) == 2:
            key_type = PublicKey.parse_key_type(parts[0])
            decoded = b58decode(parts[1])
            return PublicKey(key_type, decoded)
        else:
            raise ValueError("Invalid key format")

    def to_string(self) -> str:
        """Convert the public key to a string representation."""
        return f"{self.key_type.value}:{b58encode(self.data).decode()}"

    def verify(self, message: bytes, signature: bytes) -> bool:
        """Verify a signature against the public key."""
        if self._key_type == KeyType.ED25519:
            try:
                VerifyKey(self._data).verify(message, signature)
                return True
            except BadSignatureError:
                return False
        elif self._key_type == KeyType.SECP256K1:
            pub = secp256k1.PublicKey(bytes([0x04]) + self._data, raw=True)
            # Just ignore the recovery ID (last byte)
            sig_bytes = signature[:-1]
            # Parse the signature
            sig = pub.ecdsa_deserialize_compact(sig_bytes)
            # Verify
            return pub.ecdsa_verify(message, sig, raw=True)
        else:
            raise ValueError(f"Unsupported key type: {self._key_type}")

    @staticmethod
    def parse_key_type(s: str) -> KeyType:
        """Convert a string to a KeyType enum. Accepts 'ed25519' or 'secp256k1' (case-insensitive)."""
        try:
            return KeyType(s.lower())
        except ValueError as err:
            raise ValueError(f"Unknown key type: {s}") from err

    @property
    def key_type(self) -> KeyType:
        """Return the type of the public key."""
        return self._key_type

    @property
    def data(self) -> bytes:
        """Return the raw public key data."""
        return self._data
