from .interfaces.signer import ISigner


class LocalEthSigner(ISigner):
    """Local Ethereum signer implementation."""

    def __init__(self, private_key: str):
        self.private_key = private_key

    def sign(self, data: bytes) -> bytes:
        """Sign arbitrary bytes with the private key."""
        return self.private_key.sign(data)
