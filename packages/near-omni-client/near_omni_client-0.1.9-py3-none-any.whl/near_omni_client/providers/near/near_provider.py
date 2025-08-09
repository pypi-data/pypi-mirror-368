from near_omni_client.json_rpc.client import NearClient
from near_omni_client.networks.network import Network

from ..interfaces.iprovider_factory import IProviderFactory


class NearFactoryProvider(IProviderFactory):
    """Factory provider for creating instances of NearClient."""

    URL_TESTNET = "https://test.rpc.fastnear.com"
    URL_MAINNET = "https://free.rpc.fastnear.com"

    def __init__(self):
        self.supported_networks = [
            Network.NEAR_MAINNET,
            Network.NEAR_TESTNET,
        ]

    def get_provider(self, network: Network) -> NearClient:
        """Get a NearClient instance for the specified network."""
        if not isinstance(network, Network):
            raise TypeError(f"Expected Network enum, got {type(network)}")

        if network == Network.NEAR_TESTNET:
            return NearClient(provider_url=self.URL_TESTNET)

        if network == Network.NEAR_MAINNET:
            return NearClient(provider_url=self.URL_MAINNET)

    def is_network_supported(self, network: Network) -> bool:
        """Check if the network is supported by the Near provider."""
        return network in self.supported_networks
