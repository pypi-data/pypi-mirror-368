from typing import Any

from web3 import Web3
from web3.exceptions import TimeExhausted

from near_omni_client.chain_signatures.kdf import Kdf
from near_omni_client.chain_signatures.utils import get_evm_address
from near_omni_client.networks import Network
from near_omni_client.providers import IProviderFactory

from .interfaces.wallet import Wallet


class MPCWallet(Wallet):
    """MPC wallet implementation using Chain signatures and web3.py."""

    def __init__(
        self,
        path: str,
        account_id: str,
        near_network: Network,
        provider_factory: IProviderFactory,
        supported_networks: list[Network],
    ):
        self.path = path
        self.account_id = account_id
        self.near_network = near_network.value.replace("near-", "")
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

    def get_web3(self, network: Network) -> Web3:
        """Get a Web3 instance for the specified network."""
        return self.provider_factory.get_provider(network)

    def get_address(self) -> str:
        """Get the Ethereum address of the wallet."""
        return get_evm_address(self.get_public_key())

    def get_network(self) -> str:
        """Get the current network."""
        return self.supported_networks[0].name  # Default network

    def get_chain_id(self, network: Network) -> int:
        """Get the chain ID for the specified network."""
        return self.get_web3(network).eth.chain_id

    async def get_balance(self, network: Network) -> int:
        """Get the balance of the wallet in Ether for the specified network."""
        web3 = self.get_web3(network)
        balance = await web3.eth.get_balance(self.get_address())
        return Web3.from_wei(balance, "ether")

    async def get_public_key(self) -> str:
        """Get the public key of the wallet."""
        return Kdf.get_derived_public_key(self.account_id, self.path, network=self.near_network)

    def get_nonce(self, network: Network) -> int:
        """Get the next nonce/transaction count for the account."""
        return self.get_web3(network).eth.get_transaction_count(self.get_address())

    async def native_transfer(self, to: str, amount: str, network: Network) -> str:
        """Transfer native ETH tokens to another address."""
        web3 = self.get_web3(network)

        tx = {
            "nonce": await web3.eth.get_transaction_count(self.get_address()),
            "to": to,
            "value": web3.to_wei(amount, "ether"),
            "gas": 21000,  # TODO: Fix for EIP-1559
            "gasPrice": await web3.eth.gas_price,  # TODO: Fix for EIP-1559
            "chainId": web3.eth.chain_id,
        }

        signed_tx = web3.eth.account.sign_transaction(
            tx, self.private_key
        )  # TODO: Replace with MPC signing
        tx_hash = await web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash.hex()

    def send_transaction(
        self, network: Network, tx_data: dict, wait: bool = True, timeout: int = 300
    ) -> str:
        """Sign and send a raw transaction."""
        web3 = self.get_web3(network)

        # Sign the transaction
        signed_tx = web3.eth.account.sign_transaction(tx_data, self.private_key)

        # Send the transaction
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"Transaction sent: 0x{tx_hash.hex()}")

        # Wait for confirmation if requested
        if wait:
            try:
                receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
                if receipt.status == 1:
                    print(f"Transaction confirmed: 0x{tx_hash.hex()}")
                else:
                    raise RuntimeError(f"Transaction failed on-chain: 0x{tx_hash.hex()}")
            except TimeExhausted as err:
                raise TimeoutError(
                    f"Transaction not confirmed within {timeout} seconds: 0x{tx_hash.hex()}"
                ) from err

        return tx_hash.hex()

    def get_transaction_receipt(self, network: Network, tx_hash: str):
        """Get the transaction receipt for a given transaction hash."""
        return self.get_web3(network).eth.waitForTransactionReceipt(tx_hash)

    def wait_for_receipt(self, network: Network, tx_hash: str, timeout: int = 300):
        """Wait for a transaction receipt with a timeout."""
        try:
            receipt = self.get_web3(network).eth.wait_for_transaction_receipt(
                tx_hash, timeout=timeout
            )
            return receipt
        except TimeExhausted as err:
            raise TimeoutError(
                f"Transaction {tx_hash.hex()} was not confirmed after {timeout} seconds."
            ) from err

    async def sign_and_send_transaction(
        self,
        network: Network,
        tx_data: dict | list[Any],
        wait: bool = True,
        timeout: int = 300,
    ) -> str:
        """Sign and send a raw transaction."""
        raise NotImplementedError("sign_and_send_transaction not implemented for NEAR wallet")
