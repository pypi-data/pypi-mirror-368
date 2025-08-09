from web3 import Web3

from near_omni_client.networks import Network
from near_omni_client.wallets import Wallet


class MessengerContract:
    """Class to interact with the Circle Cross-Chain Transfer Protocol (CCTP) Messenger contract."""

    # addresses obtained from https://developers.circle.com/stablecoins/evm-smart-contracts
    contract_addresses = {
        Network.BASE_SEPOLIA: Web3.to_checksum_address(
            "0x8fe6b999dc680ccfdd5bf7eb0974218be2542daa"
        ),  # domain 6
        Network.BASE_MAINNET: Web3.to_checksum_address(
            "0x28b5a0e9C621a5BadaA536219b3a228C8168cf5d"
        ),  # domain 6
        Network.ETHEREUM_SEPOLIA: Web3.to_checksum_address(
            "0x8fe6b999dc680ccfdd5bf7eb0974218be2542daa"
        ),  # domain 0
        Network.ETHEREUM_MAINNET: Web3.to_checksum_address(
            "0x28b5a0e9C621a5BadaA536219b3a228C8168cf5d"
        ),  # domain 0
        Network.OPTIMISM_SEPOLIA: Web3.to_checksum_address(
            "0x8FE6B999Dc680CcFDD5Bf7EB0974218be2542DAA"
        ),  # domain 2
        Network.OPTIMISM_MAINNET: Web3.to_checksum_address(
            "0x28b5a0e9C621a5BadaA536219b3a228C8168cf5d"
        ),  # domain 2
        Network.ARBITRUM_SEPOLIA: Web3.to_checksum_address(
            "0x8FE6B999Dc680CcFDD5Bf7EB0974218be2542DAA"
        ),  # domain 3
        Network.ARBITRUM_MAINNET: Web3.to_checksum_address(
            "0x28b5a0e9C621a5BadaA536219b3a228C8168cf5d"
        ),  # domain 3
    }
    abi = [
        {
            "name": "depositForBurn",
            "type": "function",
            "inputs": [
                {"name": "amount", "type": "uint256"},
                {"name": "destinationDomain", "type": "uint32"},
                {"name": "mintRecipient", "type": "bytes32"},
                {"name": "burnToken", "type": "address"},
                {"name": "destinationCaller", "type": "bytes32"},
                {"name": "maxFee", "type": "uint256"},
                {"name": "minFinalityThreshold", "type": "uint32"},
            ],
            "outputs": [],
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
        self.contract = Web3().eth.contract(None, abi=self.abi)  # No provider needed

    @staticmethod
    def get_address_for_network(network) -> str:
        """Get the contract address for the specified network."""
        result = MessengerContract.contract_addresses.get(network)
        if not result:
            raise ValueError(f"Unsupported network: {network}")
        return result

    def deposit_for_burn(
        self,
        amount: int,
        destination_domain: int,
        destination_address: str,
        token_address: str,
        destination_caller: str,
        max_fee: int,
        min_finality_threshold: int,
        gas_limit: int = 1000000,
        wait: bool = True,
    ) -> str:
        """Deposit tokens for burn on the CCTP Messenger contract."""
        tx = self.contract.functions.depositForBurn(
            amount,
            destination_domain,
            destination_address,
            token_address,
            destination_caller,
            max_fee,
            min_finality_threshold,
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
