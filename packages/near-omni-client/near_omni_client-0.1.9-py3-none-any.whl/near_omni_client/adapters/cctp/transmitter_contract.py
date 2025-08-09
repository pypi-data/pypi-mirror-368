from web3 import Web3

from near_omni_client.networks import Network
from near_omni_client.wallets import Wallet


class TransmitterContract:
    """Transmitter contract for handling cross-chain messages."""

    # addresses obtained from https://developers.circle.com/stablecoins/evm-smart-contracts
    contract_addresses = {
        Network.BASE_SEPOLIA: Web3.to_checksum_address(
            "0xe737e5cebeeba77efe34d4aa090756590b1ce275"
        ),  # domain 6
        Network.BASE_MAINNET: Web3.to_checksum_address(
            "0x81D40F21F12A8F0E3252Bccb954D722d4c464B64"
        ),  # domain 6
        Network.ETHEREUM_SEPOLIA: Web3.to_checksum_address(
            "0xe737e5cebeeba77efe34d4aa090756590b1ce275"
        ),  # domain 0
        Network.ETHEREUM_MAINNET: Web3.to_checksum_address(
            "0x81D40F21F12A8F0E3252Bccb954D722d4c464B64"
        ),  # domain 0
        Network.OPTIMISM_SEPOLIA: Web3.to_checksum_address(
            "0xE737e5cEBEEBa77EFE34D4aa090756590b1CE275"
        ),  # domain 2
        Network.OPTIMISM_MAINNET: Web3.to_checksum_address(
            "0x81D40F21F12A8F0E3252Bccb954D722d4c464B64"
        ),  # domain 2
        Network.ARBITRUM_SEPOLIA: Web3.to_checksum_address(
            "0xE737e5cEBEEBa77EFE34D4aa090756590b1CE275"
        ),  # domain 3
        Network.ARBITRUM_MAINNET: Web3.to_checksum_address(
            "0x81D40F21F12A8F0E3252Bccb954D722d4c464B64"
        ),  # domain 3
    }
    abi = [
        {
            "name": "receiveMessage",
            "type": "function",
            "inputs": [
                {"name": "message", "type": "bytes"},
                {"name": "attestation", "type": "bytes"},
            ],
            "outputs": [{"name": "", "type": "bool"}],
            "stateMutability": "nonpayable",
        }
    ]

    def __init__(self, network: Network, wallet: Wallet):
        self.network = network
        self.contract_address = self.contract_addresses.get(network)
        self.wallet = wallet

        if not self.contract_address:
            raise ValueError(f"Unsupported network: {network}")

        self.contract_address = Web3.to_checksum_address(self.contract_address)
        self.contract = Web3().eth.contract(
            None, abi=self.abi
        )  # @dev intentionally without provider

    @staticmethod
    def get_address_for_network(network) -> str:
        """Get the contract address for the specified network."""
        result = TransmitterContract.contract_addresses.get(network)
        if not result:
            raise ValueError(f"Unsupported network: {network}")
        return result

    def mint_usdc(
        self,
        attestation_message: str,
        attestation: str,
        gas_limit: int = 10000000,
        wait: bool = True,
    ) -> str:
        """Mint USDC by sending a message to the transmitter contract."""
        tx = self.contract.functions.receiveMessage(
            attestation_message, attestation
        ).build_transaction(
            {
                "from": self.wallet.get_wallet_address(),
                "to": self.contract_address,
                "gas": gas_limit,
                "nonce": self.wallet.get_nonce(self.network),
                "chainId": self.wallet.get_chain_id(self.network),
                "maxFeePerGas": Web3.to_wei(2, "gwei"),
                "maxPriorityFeePerGas": Web3.to_wei(1, "gwei"),
            }
        )

        return self.wallet.send_transaction(self.network, tx, wait)
