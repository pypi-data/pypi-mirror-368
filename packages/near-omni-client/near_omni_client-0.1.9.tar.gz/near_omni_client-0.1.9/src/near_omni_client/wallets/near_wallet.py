from decimal import Decimal
from typing import Any

from near_omni_client.crypto.keypair import KeyPair
from near_omni_client.networks import Network
from near_omni_client.providers import IProviderFactory

from .interfaces.wallet import Wallet


class NearWallet(Wallet):
    """A NEAR wallet implementation that supports basic wallet operations."""

    def __init__(
        self,
        keypair: KeyPair,
        account_id: str,
        provider_factory: IProviderFactory,
        supported_networks: list[Network],
    ):
        self.keypair = keypair
        self.account_id = account_id
        self.provider_factory = provider_factory
        self.supported_networks = supported_networks

        # Validate network support
        unsupported = [
            n for n in self.supported_networks if not self.provider_factory.is_network_supported(n)
        ]
        if unsupported:
            raise ValueError(
                f"Provider does not support the following networks: {[n.name for n in unsupported]}"
            )

    def get_address(self) -> str:
        """Get the address of the NEAR wallet."""
        return self.account_id

    def get_network(self) -> Network:
        """Get the default network for the NEAR wallet."""
        return self.supported_networks[0]  # Default network

    async def get_balance(self) -> Decimal:
        """Get the balance of the NEAR wallet."""
        account = await self._get_account()
        balance = await account.get_balance()
        return Decimal(balance["available"])

    async def get_public_key(self) -> str:
        """Get the public key of the NEAR wallet."""
        return self.keypair.get_public_key().to_string()

    def get_nonce(self, network: Network) -> int:
        """Get the nonce for the NEAR wallet."""
        raise NotImplementedError("get_nonce not implemented for NEAR wallet")

    async def native_transfer(self, to: str, amount: str, network: Network) -> str:
        """Transfer native NEAR tokens to another account."""
        account = await self._get_account()
        amount_yocto = int(Decimal(amount) * 10**24)  # Convert to yoctoNEAR
        result = await account.send_money(to, amount_yocto)
        return result["transaction"]["hash"]

    async def sign_and_send_transaction(
        self,
        network: Network,
        tx_data: dict | list[Any],
        wait: bool = True,
        timeout: int = 300,
    ) -> str:
        """Sign and send a transaction to the NEAR network."""
        raise NotImplementedError("sign_and_send_transaction not implemented for NEAR wallet")

    async def _get_account(self):
        # Implementation depends on your NEAR client setup
        pass
