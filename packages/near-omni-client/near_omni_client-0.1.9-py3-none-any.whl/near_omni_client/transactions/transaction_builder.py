from typing import Any

from py_near_primitives import Transaction as NearTransaction

from .utils import decode_key


class TransactionBuilder:
    """Builder for creating NEAR transactions."""

    def __init__(self):
        self._signer_id: str | None = None
        self._public_key: bytes | None = None
        self._nonce: int | None = None
        self._receiver_id: str | None = None
        self._block_hash: bytes | None = None
        self._actions: list[Any] = []

    def with_signer_id(self, signer_id: str) -> "TransactionBuilder":
        """Set the signer ID for the transaction."""
        self._signer_id = signer_id
        return self

    def with_public_key(self, public_key: str | bytes) -> "TransactionBuilder":
        """Set the public key for the transaction.

        Args:
            public_key: Can be:
                - bytes: Raw bytes of the public key
                - str: NEAR format "ed25519:base58_encoded"

        Returns:
            self: For method chaining

        Raises:
            ValueError: If string key is not in "ed25519:base58" format

        """
        if isinstance(public_key, bytes):
            self._public_key = public_key
            return self

        if not public_key.startswith("ed25519:"):
            raise ValueError('Public key string must be in format "ed25519:base58"')

        self._public_key = decode_key(public_key)
        return self

    def with_nonce(self, nonce: int) -> "TransactionBuilder":
        """Set the nonce for the transaction."""
        self._nonce = nonce
        return self

    def with_receiver(self, receiver_id: str) -> "TransactionBuilder":
        """Set the receiver ID for the transaction."""
        self._receiver_id = receiver_id
        return self

    def with_block_hash(self, block_hash: bytes) -> "TransactionBuilder":
        """Set the block hash for the transaction."""
        self._block_hash = block_hash
        return self

    def add_action(self, action: Any) -> "TransactionBuilder":
        """Add an action to the transaction."""
        self._actions.append(action)
        return self

    def build(self) -> NearTransaction:
        """Build the NEAR transaction object."""
        missing = [
            name
            for name, val in [
                ("signer_id", self._signer_id),
                ("public_key", self._public_key),
                ("nonce", self._nonce),
                ("receiver_id", self._receiver_id),
                ("block_hash", self._block_hash),
            ]
            if val is None
        ]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        return NearTransaction(
            self._signer_id,
            self._public_key,
            self._nonce,
            self._receiver_id,
            self._block_hash,
            self._actions,
        )
