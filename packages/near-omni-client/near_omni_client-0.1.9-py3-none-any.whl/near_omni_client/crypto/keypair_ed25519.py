import os

from base58 import b58decode, b58encode
from nacl import bindings
from nacl.signing import SigningKey

from .keypair_base import KeyPairBase
from .public_key import PublicKey
from .signature import Signature
from .types import KeyPairString, KeySize, KeyType


class KeyPairEd25519(KeyPairBase):
    """Implements Ed25519 key pair functionality exactly like @near-js/utils.

    - Always decodes the extended key, uses only the first 32 bytes as secret.
    - Recalculates the public key from the secret.
    """

    def __init__(self, extended_secret_key: str):
        decoded = b58decode(extended_secret_key)
        seed = decoded[: KeySize.SECRET_KEY]  # 32 bytes
        public_key = bindings.crypto_sign_seed_keypair(seed)[0]
        self.publicKey = PublicKey(KeyType.ED25519, public_key)
        self.secretKey = b58encode(seed).decode()
        self.extendedSecretKey = extended_secret_key

    @staticmethod
    def from_random() -> "KeyPairEd25519":
        """Generate a random key pair."""
        seed = os.urandom(KeySize.SECRET_KEY)
        _, public_key = bindings.crypto_sign_seed_keypair(seed)
        extended = seed + public_key
        return KeyPairEd25519(b58encode(extended).decode())

    def sign(self, message: bytes) -> Signature:
        """Sign a message using the private key."""
        seed = b58decode(self.secretKey)
        signing_key = SigningKey(seed)
        signature = signing_key.sign(message).signature
        return Signature(signature=signature, public_key=self.publicKey)

    def verify(self, message: bytes, signature: bytes) -> bool:
        """Verify a signature against the public key."""
        return self.publicKey.verify(message, signature)

    def to_string(self) -> KeyPairString:
        """Return the key pair as a string in the format `<curve>:<extended-secret-key>`."""
        return KeyPairString(f"{KeyType.ED25519.value}:{self.extendedSecretKey}")

    def get_public_key(self) -> PublicKey:
        """Return the public key."""
        return self.publicKey

    @property
    def secret_key(self) -> str:
        """Return the base58-encoded secret key."""
        return self.secretKey

    @property
    def public_key(self) -> PublicKey:
        """Return the public key."""
        return self.publicKey
