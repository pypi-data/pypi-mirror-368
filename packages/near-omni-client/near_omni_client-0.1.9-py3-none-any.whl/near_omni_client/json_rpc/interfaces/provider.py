from abc import ABC, abstractmethod
from typing import Any


# TODO: Fix the Any return type
class IJsonRpcProvider(ABC):
    """Interface for JSON-RPC providers that can make asynchronous RPC calls."""

    @abstractmethod
    async def call(self, method: str, params: dict) -> Any:
        """Make a JSON-RPC call to the specified method with given parameters."""
        pass
