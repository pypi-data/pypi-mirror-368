import base58


def decode_key(key_str):
    """Decode a public key string into bytes."""
    if ":" in key_str:
        _, key_data = key_str.split(":", 1)
        return base58.b58decode(key_data)
