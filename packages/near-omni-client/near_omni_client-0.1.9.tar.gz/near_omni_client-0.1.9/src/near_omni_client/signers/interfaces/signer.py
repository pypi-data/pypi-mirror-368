from abc import ABC, abstractmethod


class ISigner(ABC):
    """Interface for signers that can sign arbitrary bytes."""

    @abstractmethod
    def sign(self, data: bytes) -> bytes:
        """Sign arbitrary bytes with the signer."""
        pass
