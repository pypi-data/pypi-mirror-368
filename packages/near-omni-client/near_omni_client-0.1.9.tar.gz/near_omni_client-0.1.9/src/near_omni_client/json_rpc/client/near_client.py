import base58

from near_omni_client.crypto import PublicKey
from near_omni_client.json_rpc.access_keys import AccessKey
from near_omni_client.json_rpc.accounts import Accounts
from near_omni_client.json_rpc.interfaces.provider import IJsonRpcProvider
from near_omni_client.json_rpc.providers import JsonRpcProvider
from near_omni_client.json_rpc.transactions import Transactions, TxExecutionStatus


class NearClient:
    """Unified NEAR client that encapsulates all JSON RPC services. Provides a clean interface to interact with the NEAR blockchain."""

    def __init__(
        self,
        provider_url: str | None = None,
        provider: IJsonRpcProvider | None = None,
        network: str = "testnet",
    ):
        """Initialize the NEAR client with either a provider URL or a provider instance.

        Args:
            provider_url: URL to the NEAR RPC endpoint (optional if provider is given)
            provider: A JSON RPC provider instance (optional if provider_url is given)
            network: Network identifier ('mainnet', 'testnet', etc.)

        """
        if provider is None and provider_url is None:
            # Default to testnet if neither is provided, more info https://docs.near.org/api/rpc/providers
            provider_url = "https://test.rpc.fastnear.com"

        if provider is None:
            provider = JsonRpcProvider(provider_url)

        self.provider = provider
        self.network = network

        # Initialize all service components
        self.accounts = Accounts(provider)
        self.access_keys = AccessKey(provider)
        self.transactions = Transactions(provider)

    async def view_account(self, account_id: str):
        """Get account information.

        Args:
            account_id: NEAR account ID

        Returns:
            Account information

        """
        return await self.accounts.view_account(account_id)

    async def call_contract(self, contract_id: str, method: str, args: dict):
        """Call a view method on a contract.

        Args:
            contract_id: Contract account ID
            method: Method name to call
            args: Method arguments as a dictionary

        Returns:
            Function call result

        """
        return await self.accounts.call_function(contract_id, method, args)

    async def view_access_key(self, account_id: str, public_key: str | PublicKey):
        """Fetch an access key for the given account and public key.

        Args:
            account_id: NEAR account ID
            public_key: Public key as string or PublicKey instance

        Returns:
            Access key information

        """
        if isinstance(public_key, PublicKey):
            public_key = public_key.to_string()

        return await self.access_keys.view_access_key(account_id, public_key)

    async def send_raw_transaction(self, signed_tx_base64: str, wait_until: str = "final"):
        """Send a signed transaction.

        Args:
            signed_tx_base64: Base64 encoded signed transaction
            wait_until: Transaction finality to wait for

        Returns:
            Transaction execution result

        """
        # Convert string status to enum
        wait_status = getattr(TxExecutionStatus, wait_until.upper())

        return await self.transactions.send_transaction(
            signed_tx_base64=signed_tx_base64, wait_until=wait_status
        )

    async def get_nonce_and_block_hash(self, account_id: str, public_key: str | PublicKey):
        """Get the next nonce and recent block hash needed for transaction creation.

        Args:
            account_id: NEAR account ID
            public_key: Public key as string or PublicKey instance

        Returns:
            Dictionary with nonce and block_hash

        """
        access_key = await self.view_access_key(account_id, public_key)

        return {
            "nonce": access_key.nonce + 1,  # Increment nonce for next transaction
            "block_hash": base58.b58decode(access_key.block_hash),
        }
