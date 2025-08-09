from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any

from near_omni_client.networks.network import Network


class Wallet(ABC):
    """Base interface for blockchain wallets."""

    @abstractmethod
    def get_address(self) -> str:
        """Get the wallet's address/account ID."""
        pass

    @abstractmethod
    def get_network(self) -> Network:
        """Get the current network.

        Returns:
            Network: The network enum (e.g., ETH_MAINNET, ETH_SEPOLIA, NEAR_MAINNET, NEAR_TESTNET)

        """
        pass

    @abstractmethod
    async def get_balance(self) -> Decimal:
        """Get native token balance."""
        pass

    @abstractmethod
    async def get_public_key(self) -> str:
        """Get the wallet's public key."""
        pass

    @abstractmethod
    def get_nonce(self, network: Network) -> int:
        """Get the next nonce/transaction count for the account."""
        pass

    @abstractmethod
    async def native_transfer(self, to: str, amount: str) -> str:
        """Transfer native tokens.

        Returns: transaction hash
        """
        pass

    @abstractmethod
    async def sign_and_send_transaction(
        self,
        network: Network,
        tx_data: dict | list[Any],  # dict for ETH, list[Action] for NEAR
        wait: bool = True,
        timeout: int = 300,
    ) -> str:
        """Sign and send a raw transaction.

        Args:
            network: Network to use
            tx_data: Complete transaction data (dict for ETH, list of actions for NEAR)
            wait: Whether to wait for confirmation
            timeout: Max time to wait for confirmation in seconds

        Returns:
            str: Transaction hash

        Raises:
            TimeoutError: If wait=True and transaction is not mined within timeout
            RuntimeError: If wait=True and transaction fails on-chain

        """
        pass
