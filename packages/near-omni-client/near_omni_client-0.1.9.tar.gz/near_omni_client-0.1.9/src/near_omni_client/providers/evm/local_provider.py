from web3 import Web3

from near_omni_client.networks.network import Network

from ..interfaces.iprovider_factory import IProviderFactory


class LocalProvider(IProviderFactory):
    """Factory provider for creating instances of Web3 for local Ethereum nodes."""

    BASE_URL_TEMPLATE = "http://{network}:{port}/"
    PORT = 8545  # Default port for local Ethereum nodes

    def __init__(self):
        self.supported_networks = [
            Network.LOCALHOST,
        ]

    def get_provider(self, network: Network) -> Web3:
        """Get a Web3 instance for the specified local network."""
        if not isinstance(network, Network):
            raise TypeError(f"Expected Network enum, got {type(network)}")

        url = LocalProvider.BASE_URL_TEMPLATE.format(network=network.value, port=self.PORT)
        return Web3(Web3.HTTPProvider(url))

    def is_network_supported(self, network: Network) -> bool:
        """Check if the network is supported by the local provider."""
        return network in self.supported_networks
