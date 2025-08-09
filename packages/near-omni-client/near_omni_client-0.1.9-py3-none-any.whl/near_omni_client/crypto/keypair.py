from .keypair_base import KeyPairBase
from .keypair_ed25519 import KeyPairEd25519
from .keypair_secp256k1 import KeyPairSecp256k1


class KeyPair:
    """Factory class for creating NEAR key pairs of different types."""

    @staticmethod
    def from_random(curve: str) -> KeyPairBase:
        """Create a random key pair for the specified curve."""
        curve = curve.lower()
        if curve == "ed25519":
            return KeyPairEd25519.from_random()
        elif curve == "secp256k1":
            return KeyPairSecp256k1.from_random()
        else:
            raise ValueError(f"Unknown curve type: {curve}")

    @staticmethod
    def from_string(encoded: str) -> KeyPairBase:
        """Create a KeyPair instance from a string representation."""
        parts = encoded.split(":")
        if len(parts) != 2:
            raise ValueError("Invalid encoded key format, must be <curve>:<encoded key>")
        curve, key = parts
        curve = curve.lower()

        if curve == "ed25519":
            return KeyPairEd25519(key)
        elif curve == "secp256k1":
            return KeyPairSecp256k1(key)
        else:
            raise ValueError(f"Unsupported curve: {curve}")
