from web3 import Web3

from near_omni_client.networks.network import Network

from ..interfaces.iprovider_factory import IProviderFactory


class AlchemyFactoryProvider(IProviderFactory):
    """Factory provider for creating instances of Web3 for Alchemy networks."""

    BASE_URL_TEMPLATE = "https://{network}.g.alchemy.com/v2/{api_key}"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.supported_networks = [
            Network.BASE_SEPOLIA,
            Network.BASE_MAINNET,
            Network.ETHEREUM_SEPOLIA,
            Network.ETHEREUM_MAINNET,
            Network.ARBITRUM_SEPOLIA,
            Network.ARBITRUM_MAINNET,
            Network.OPTIMISM_SEPOLIA,
            Network.OPTIMISM_MAINNET,
        ]

    def get_provider(self, network: Network) -> Web3:
        """Get a Web3 instance for the specified Alchemy network."""
        if not isinstance(network, Network):
            raise TypeError(f"Expected Network enum, got {type(network)}")

        url = AlchemyFactoryProvider.BASE_URL_TEMPLATE.format(
            network=network.value, api_key=self.api_key
        )
        return Web3(Web3.HTTPProvider(url))

    def is_network_supported(self, network: Network) -> bool:
        """Check if the network is supported by the Alchemy provider."""
        return network in self.supported_networks
