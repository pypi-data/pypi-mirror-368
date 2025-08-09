from abc import ABC, abstractmethod

from .public_key import PublicKey
from .signature import Signature
from .types import KeyPairString


class KeyPairBase(ABC):
    """Abstract base class for NEAR key pairs."""

    @abstractmethod
    def sign(self, message: bytes) -> Signature:
        """Sign a message using the private key."""
        pass

    @abstractmethod
    def verify(self, message: bytes, signature: bytes) -> bool:
        """Verify a signature against the public key."""
        pass

    @property
    @abstractmethod
    def public_key(self) -> PublicKey:
        """Return the public key associated with this key pair."""
        pass

    @property
    @abstractmethod
    def secret_key(self) -> str:
        """Return the base58-encoded secret key."""
        pass

    @abstractmethod
    def to_string(self) -> KeyPairString:
        """Return the key pair as a string representation."""
        pass
