from enum import Enum
from typing import NewType


class KeySize:
    """Constants for key sizes in bytes."""

    SECRET_KEY = 32
    PUBLIC_KEY = 32
    PUBLIC_KEY_SECP256K1 = 64  # uncompressed without 0x04


class KeyType(str, Enum):
    """Enum for different types of NEAR keys."""

    ED25519 = "ed25519"
    SECP256K1 = "secp256k1"


# A string like "ed25519:xxxxx" or "secp256k1:yyyyy"
KeyPairString = NewType("KeyPairString", str)
