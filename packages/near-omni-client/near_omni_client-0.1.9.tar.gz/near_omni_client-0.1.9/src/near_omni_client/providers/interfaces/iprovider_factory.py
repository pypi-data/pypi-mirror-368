from abc import ABC, abstractmethod

from web3 import Web3

from near_omni_client.json_rpc.client import NearClient
from near_omni_client.networks.network import Network


class IProviderFactory(ABC):
    """Interface for provider factories that create instances of Web3 or NearClient."""

    @abstractmethod
    def get_provider(self, network: Network) -> Web3 | NearClient:
        """Get a provider instance for the specified network."""
        pass

    @abstractmethod
    def is_network_supported(self, network: Network) -> bool:
        """Check if the network is supported by the provider factory."""
        pass
