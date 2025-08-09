from typing import Any

import httpx

from near_omni_client.json_rpc.exceptions import JsonRpcError
from near_omni_client.json_rpc.interfaces.provider import IJsonRpcProvider


class JsonRpcProvider(IJsonRpcProvider):
    """A JSON-RPC provider for making asynchronous RPC calls."""

    def __init__(self, rpc_url: str, timeout: float = 60.0):
        self.rpc_url = rpc_url
        self.timeout = timeout

    async def call(self, method: str, params: dict) -> Any:
        """Make a JSON-RPC call to the specified method with given parameters."""
        payload = {
            "jsonrpc": "2.0",
            "id": "dontcare",
            "method": method,
            "params": params,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(self.rpc_url, json=payload)
            data = response.json()

            if "error" in data:
                raise JsonRpcError.from_response(data["error"])
            return data
