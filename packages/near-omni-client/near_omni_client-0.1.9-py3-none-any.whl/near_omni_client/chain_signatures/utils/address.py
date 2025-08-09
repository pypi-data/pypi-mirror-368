import hashlib

from base58 import b58encode
from eth_hash.auto import keccak

from near_omni_client.chain_signatures.segwit_addr import bech32_encode, convertbits


def get_evm_address(public_key: bytes) -> str:
    """Compute the Ethereum address from an uncompressed public key.

    The public key is expected to be 65 bytes with a leading 0x04.
    According to Ethereum specifications, the 0x04 is dropped and the
    Keccak-256 hash is computed on the remaining 64 bytes (the X and Y coordinates).
    The last 20 bytes of the hash are used as the Ethereum address.

    :param public_key: Uncompressed public key (65 bytes)
    :return: Ethereum address as a hex string (prefixed with "0x")
    """
    # Drop the 0x04 prefix if present
    pubkey_no_prefix = public_key[1:] if public_key[0] == 4 else public_key

    # Calcula el hash Keccak directamente sobre los datos
    hash_bytes = keccak(pubkey_no_prefix)
    eth_address = hash_bytes[-20:]
    return "0x" + eth_address.hex()


def get_btc_legacy_address(public_key: bytes, network: str = "bitcoin") -> str:
    """Compute the Bitcoin legacy (P2PKH) address from a public key.

    Steps:
      1. Compute SHA256, then RIPEMD160 of the public key.
      2. Prepend the version byte: 0x00 for Bitcoin mainnet, 0x6f for testnet.
      3. Compute the checksum: first 4 bytes of double SHA256 of the payload.
      4. Concatenate payload and checksum, then encode using Base58.

    :param public_key: Public key bytes (can be uncompressed or compressed)
    :param network: 'bitcoin' (mainnet) or 'testnet'
    :return: Base58Check encoded Bitcoin legacy address.
    """
    sha256_hash = hashlib.sha256(public_key).digest()
    ripemd160_hash = hashlib.new("ripemd160", sha256_hash).digest()

    version_byte = b"\x00" if network == "bitcoin" else b"\x6f"
    payload = version_byte + ripemd160_hash
    # Compute checksum: first 4 bytes of double SHA256 of the payload
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    full_payload = payload + checksum
    address = b58encode(full_payload).decode()
    return address


def get_btc_segwit_address(public_key: bytes, network: str = "bitcoin") -> str:
    """Compute the Bitcoin SegWit (P2WPKH) address from a public key.

    Steps:
      1. Compute SHA256, then RIPEMD160 of the public key.
      2. Convert the resulting 20-byte hash (witness program) from 8-bit to 5-bit groups.
      3. Prepend the witness version (0 for P2WPKH).
      4. Encode using Bech32 with HRP: "bc" for mainnet, "tb" for testnet.

    :param public_key: Public key bytes.
    :param network: 'bitcoin' (mainnet) or 'testnet'
    :return: SegWit address in Bech32 format.
    """
    sha256_hash = hashlib.sha256(public_key).digest()
    ripemd160_hash = hashlib.new("ripemd160", sha256_hash).digest()

    witness_version = 0
    # Convert the 20-byte hash to 5-bit groups.
    converted = convertbits(list(ripemd160_hash), 8, 5, True)
    if converted is None:
        raise ValueError("Error converting hash to 5-bit groups for Bech32 encoding")
    data = [witness_version] + converted
    hrp = "bc" if network == "bitcoin" else "tb"
    segwit_addr = bech32_encode(hrp, data, "bech32")
    return segwit_addr
