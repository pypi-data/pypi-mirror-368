class UnknownBlockError(Exception):
    """Exception raised when a block is not found or invalid."""

    pass


class InvalidAccountError(Exception):
    """Exception raised when an account ID is invalid."""

    pass


class UnknownAccountError(Exception):
    """Exception raised when an account is not found or invalid."""

    pass


class UnknownAccessKeyError(Exception):
    """Exception raised when an access key is not found or invalid."""

    pass


class UnavailableShardError(Exception):
    """Exception raised when a requested shard is not available in the node."""

    pass


class NoSyncedBlocksError(Exception):
    """Exception raised when no synced blocks are available in the node."""

    pass


class InternalError(Exception):
    """Exception raised for internal errors in the JSON-RPC provider."""

    pass


class ParseError(Exception):
    """Exception raised for errors in parsing JSON-RPC requests or responses."""

    pass


ERRORS = {
    "UNKNOWN_BLOCK": UnknownBlockError,
    "INVALID_ACCOUNT": InvalidAccountError,
    "UNKNOWN_ACCOUNT": UnknownAccountError,
    "UNKNOWN_ACCESS_KEY": UnknownAccessKeyError,
    "UNAVAILABLE_SHARD": UnavailableShardError,
    "NO_SYNCED_BLOCKS": NoSyncedBlocksError,
    "INTERNAL_ERROR": InternalError,
    "PARSE_ERROR": ParseError,
}


ERROR_MESSAGES = {
    "UNKNOWN_BLOCK": "The block has not been produced or has been garbage-collected.",
    "INVALID_ACCOUNT": "The account ID format is invalid.",
    "UNKNOWN_ACCOUNT": "The account doesn't exist or has been deleted.",
    "UNKNOWN_ACCESS_KEY": "The public key is not associated with the account.",
    "UNAVAILABLE_SHARD": "The shard is not tracked by this RPC node.",
    "NO_SYNCED_BLOCKS": "The node is still syncing and has no blocks.",
    "INTERNAL_ERROR": "Something went wrong with the node. Try again later.",
    "PARSE_ERROR": "Invalid JSON-RPC request parameters.",
}
