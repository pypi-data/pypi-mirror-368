from typing import NamedTuple

from .public_key import PublicKey


class Signature(NamedTuple):
    """Represents a NEAR signature."""

    # The raw 65-byte signature (64-byte R||S plus 1-byte recovery ID)
    signature: bytes
    # The public key object that corresponds to the private key used to sign
    public_key: PublicKey
