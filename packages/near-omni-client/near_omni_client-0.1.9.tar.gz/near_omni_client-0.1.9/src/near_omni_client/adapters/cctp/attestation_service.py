import time

import requests
from pydantic import ValidationError

from near_omni_client.networks import Network

from .attestation_service_types import (
    GetMessagesBadRequestResponse,
    GetMessagesNotFoundResponse,
    GetMessagesResponse,
)


class AttestationService:
    """Service for retrieving attestations from Circle's attestation service."""

    MAINNET_BASE_URL = "https://iris-api.circle.com/v2/messages"
    SANDBOX_BASE_URL = "https://iris-api-sandbox.circle.com/v2/messages"
    network_urls = {
        Network.BASE_SEPOLIA: f"{SANDBOX_BASE_URL}/{Network.BASE_SEPOLIA.domain}?transactionHash={{}}",
        Network.BASE_MAINNET: f"{MAINNET_BASE_URL}/{Network.BASE_MAINNET.domain}?transactionHash={{}}",
        Network.ETHEREUM_SEPOLIA: f"{SANDBOX_BASE_URL}/{Network.ETHEREUM_SEPOLIA.domain}?transactionHash={{}}",
        Network.ETHEREUM_MAINNET: f"{MAINNET_BASE_URL}/{Network.ETHEREUM_MAINNET.domain}?transactionHash={{}}",
        Network.OPTIMISM_SEPOLIA: f"{SANDBOX_BASE_URL}/{Network.OPTIMISM_SEPOLIA.domain}?transactionHash={{}}",
        Network.OPTIMISM_MAINNET: f"{MAINNET_BASE_URL}/{Network.OPTIMISM_MAINNET.domain}?transactionHash={{}}",
        Network.ARBITRUM_SEPOLIA: f"{SANDBOX_BASE_URL}/{Network.ARBITRUM_SEPOLIA.domain}?transactionHash={{}}",
        Network.ARBITRUM_MAINNET: f"{MAINNET_BASE_URL}/{Network.ARBITRUM_MAINNET.domain}?transactionHash={{}}",
    }

    def __init__(self, network: Network):
        self.network = network
        self.url = self.network_urls.get(network)
        if not self.url:
            raise ValueError(f"Unsupported network: {network}")

    def retrieve_attestation(self, transaction_hash: str):
        """Retrieve the attestation for a given transaction hash."""
        url = self.url.format(transaction_hash)
        print(f"Retrieving attestation from {url}")
        if not self.url:
            raise ValueError(f"Unsupported network: {self.network}")
        if not transaction_hash:
            raise ValueError("Transaction hash is required")
        if not isinstance(transaction_hash, str):
            raise ValueError("Transaction hash must be a string")
        if len(transaction_hash) != 66:
            raise ValueError("Transaction hash must be 66 characters long")
        if not transaction_hash.startswith("0x"):
            raise ValueError("Transaction hash must start with '0x'")

        while True:
            try:
                response = requests.get(url)

                if response.status_code == 200:
                    try:
                        print("Response received (200)")
                        print(f"Response: {response.text}")
                        data = GetMessagesResponse(**response.json())
                        message = data.messages[0]
                        if message.status == "complete":
                            print("Attestation retrieved successfully")
                            print(f"Attestation: {message.model_dump()}")
                            return message
                        print("Waiting for attestation...")
                    except ValidationError as e:
                        print("Invalid response format (200):", e)

                elif response.status_code == 400:
                    try:
                        err = GetMessagesBadRequestResponse(**response.json())
                        print(f"Bad request: {err.error}")
                    except ValidationError as e:
                        print("Invalid error format (400):", e)

                elif response.status_code == 404:
                    try:
                        err = GetMessagesNotFoundResponse(**response.json())
                        print(f"Not found ({err.code}): {err.error}")
                    except ValidationError as e:
                        print("Invalid error format (404):", e)

                else:
                    print(f"Unhandled error ({response.status_code}): {response.text}")

            except requests.exceptions.RequestException as e:
                print(f"Network error: {e}")

            time.sleep(5)
