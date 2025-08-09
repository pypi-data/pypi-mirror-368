import base64

from near_omni_client.crypto import KeyPair, KeyPairBase
from near_omni_client.transactions import Transaction

from .interfaces.signer import ISigner


class NearKeypairSigner(ISigner):
    """Signer implementation using NEAR KeyPair (ED25519 or SECP256K1)."""

    def __init__(self, key: str | KeyPairBase):
        """Initialize KeypairSigner with a private key or KeyPair instance.

        Args:
            key: Either a string in format "curve:encoded_key" or a KeyPairBase instance

        """
        if isinstance(key, str):
            self._key_pair = KeyPair.from_string(key)
        else:
            self._key_pair = key

    @property
    def public_key(self):
        """Get the public key associated with this signer."""
        return self._key_pair.public_key

    @property
    def account_id(self) -> str | None:
        """Get the account ID if available."""
        return getattr(self, "_account_id", None)

    @account_id.setter
    def account_id(self, value: str):
        """Set the account ID for this signer."""
        self._account_id = value

    def sign(self, data: bytes) -> bytes:
        """Sign arbitrary bytes with the private key.

        Args:
            data: Raw bytes to sign

        Returns:
            Signature bytes

        """
        signature = self._key_pair.sign(data)
        return signature.signature

    def sign_base64(self, tx: Transaction) -> str:
        """Sign a transaction and return the base64 encoded signed transaction.

        Args:
            tx: Transaction to sign

        Returns:
            Base64 encoded signed transaction

        """
        # Serialize transaction to bytes
        message = tx.get_message_to_sign()

        # Sign the serialized transaction
        signature = self.sign_bytes(message)

        # Create signed transaction
        signed_tx = tx.create_signed_transaction(signature)

        # Serialize and encode in base64
        serialized_signed_tx = signed_tx.serialize()
        return base64.b64encode(serialized_signed_tx).decode("utf-8")

    def verify(self, message: bytes, signature: bytes) -> bool:
        """Verify a signature for a message.

        Args:
            message: The original message that was signed
            signature: The signature to verify

        Returns:
            True if the signature is valid, False otherwise

        """
        return self._key_pair.verify(message, signature)
