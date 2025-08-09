from web3 import Web3

from near_omni_client.networks import Network
from near_omni_client.wallets import Wallet


class USDCContract:
    """Addresses obtained from https://developers.circle.com/stablecoins/usdc-on-test-networks and https://developers.circle.com/stablecoins/usdc-on-main-networks."""

    contract_addresses = {
        Network.BASE_SEPOLIA: Web3.to_checksum_address(
            "0x036CbD53842c5426634e7929541eC2318f3dCF7e"
        ),
        Network.BASE_MAINNET: Web3.to_checksum_address(
            "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
        ),
        Network.ETHEREUM_SEPOLIA: Web3.to_checksum_address(
            "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238"
        ),
        Network.ETHEREUM_MAINNET: Web3.to_checksum_address(
            "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
        ),
        Network.OPTIMISM_SEPOLIA: Web3.to_checksum_address(
            "0x5fd84259d66Cd46123540766Be93DFE6D43130D7"
        ),
        Network.OPTIMISM_MAINNET: Web3.to_checksum_address(
            "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85"
        ),
        Network.ARBITRUM_SEPOLIA: Web3.to_checksum_address(
            "0x75faf114eafb1BDbe2F0316DF893fd58CE46AA4d"
        ),
        Network.ARBITRUM_MAINNET: Web3.to_checksum_address(
            "0xaf88d065e77c8cC2239327C5EDb3A432268e5831"
        ),
    }
    abi = [
        {
            "name": "approve",
            "type": "function",
            "inputs": [
                {"name": "spender", "type": "address"},
                {"name": "amount", "type": "uint256"},
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
        self.contract = Web3().eth.contract(None, abi=self.abi)  # no provider

    @staticmethod
    def get_address_for_network(network) -> str:
        """Get the USDC contract address for a specific network."""
        address = USDCContract.contract_addresses.get(network)
        if not address:
            raise ValueError(f"Unsupported network: {network}")
        return address

    def approve(
        self, spender: str, amount: int, gas_limit: int = 1000000, wait: bool = True
    ) -> str:
        """Approve a spender to use USDC tokens on behalf of the wallet."""
        tx = self.contract.functions.approve(spender, amount).build_transaction(
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
