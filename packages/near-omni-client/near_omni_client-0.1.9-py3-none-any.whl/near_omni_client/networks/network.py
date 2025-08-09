from enum import Enum

BASE_DOMAIN = "6"
ETHEREUM_DOMAIN = "0"
ARBITRUM_DOMAIN = "3"
OPTIMISM_DOMAIN = "2"


class Network(Enum):
    """Enum representing different blockchain networks."""

    LOCALHOST = "localhost"
    BASE_SEPOLIA = "base-sepolia"
    BASE_MAINNET = "base-mainnet"
    ETHEREUM_SEPOLIA = "eth-sepolia"
    ETHEREUM_MAINNET = "eth-mainnet"
    NEAR_MAINNET = "near-mainnet"
    NEAR_TESTNET = "near-testnet"
    OPTIMISM_SEPOLIA = "opt-sepolia"
    OPTIMISM_MAINNET = "opt-mainnet"
    ARBITRUM_SEPOLIA = "arb-sepolia"
    ARBITRUM_MAINNET = "arb-mainnet"

    @staticmethod
    def parse(value: str) -> "Network":
        """Parse a string value into a Network enum."""
        try:
            return Network(value)
        except KeyError as err:
            raise ValueError(f"Invalid network value: {value}") from err

    @property
    def domain(self) -> str:
        """Return the domain associated with the network."""
        if self in {Network.BASE_SEPOLIA, Network.BASE_MAINNET}:
            return BASE_DOMAIN
        elif self in {Network.ETHEREUM_SEPOLIA, Network.ETHEREUM_MAINNET}:
            return ETHEREUM_DOMAIN
        elif self in {Network.OPTIMISM_SEPOLIA, Network.OPTIMISM_MAINNET}:
            return OPTIMISM_DOMAIN
        elif self in {Network.ARBITRUM_SEPOLIA, Network.ARBITRUM_MAINNET}:
            return ARBITRUM_DOMAIN
        else:
            raise ValueError(f"Unknown domain for network {self}")
