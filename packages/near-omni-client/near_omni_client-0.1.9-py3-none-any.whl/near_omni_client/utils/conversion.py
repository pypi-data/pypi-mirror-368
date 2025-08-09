from web3 import Web3


def address_to_bytes32(address: str) -> bytes:
    """Convert an Ethereum address to a bytes32 representation."""
    # Validate that it's a proper Ethereum address
    if not Web3.is_address(address):
        raise ValueError(f"Invalid Ethereum address: {address}")

    # Remove the '0x' prefix and left-pad with zeros to make it 32 bytes (64 hex chars)
    hex_str = address[2:].zfill(64)

    # Convert the padded hex string to bytes32
    return Web3.to_bytes(hexstr=hex_str)
