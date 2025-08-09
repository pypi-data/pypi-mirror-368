from near_omni_client.json_rpc.exceptions import ERROR_MESSAGES, ERRORS, JsonRpcError
from near_omni_client.json_rpc.interfaces.provider import IJsonRpcProvider
from near_omni_client.json_rpc.models import BlockResult


class Block:
    """Class to interact with NEAR blockchain blocks via JSON RPC."""

    def __init__(self, provider: IJsonRpcProvider):
        self.provider = provider

    async def view_block(
        self, *, finality: str | None = None, block_id: int | str | None = None
    ) -> BlockResult:
        """Get information about a block by its finality or block ID."""
        if finality and block_id:
            raise ValueError("Cannot provide both finality and block_id")

        try:
            params = {"finality": finality} if finality else {"block_id": block_id}
            res = await self.provider.call("block", params)
            return BlockResult.from_json_response(res)
        except JsonRpcError as e:
            error = ERRORS.get(e.cause_name)
            message = ERROR_MESSAGES.get(e.cause_name, str(e))
            if error:
                raise error(message) from e
            raise
