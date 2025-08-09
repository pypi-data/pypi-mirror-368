from enum import Enum

from near_omni_client.json_rpc.exceptions import ERROR_MESSAGES, ERRORS, JsonRpcError
from near_omni_client.json_rpc.interfaces.provider import IJsonRpcProvider
from near_omni_client.json_rpc.models import TransactionResult


class TxExecutionStatus(str, Enum):
    """Enum for transaction execution statuses."""

    # Transaction is waiting to be included into the block
    NONE = "NONE"
    # Transaction is included into the block. The block may be not finalized yet
    INCLUDED = "INCLUDED"
    # Transaction is included into the block +
    # All non-refund transaction receipts finished their execution.
    # The corresponding blocks for tx and each receipt may be not finalized yet
    EXECUTED_OPTIMISTIC = "EXECUTED_OPTIMISTIC"
    # Transaction is included into finalized block
    INCLUDED_FINAL = "INCLUDED_FINAL"
    # Transaction is included into finalized block +
    # All non-refund transaction receipts finished their execution.
    # The corresponding blocks for each receipt may be not finalized yet
    EXECUTED = "EXECUTED"
    # Transaction is included into finalized block +
    # Execution of all transaction receipts is finalized, including refund receipts
    FINAL = "FINAL"


class Transactions:
    """Class for sending transactions using a JSON-RPC provider."""

    def __init__(self, provider: IJsonRpcProvider):
        self.provider = provider

    async def send_transaction(
        self,
        *,
        signed_tx_base64: str,
        wait_until: TxExecutionStatus | None = None,
    ) -> TransactionResult:
        """Send a signed transaction to the NEAR network."""
        params: dict[str, object] = {"signed_tx_base64": signed_tx_base64}
        if wait_until is not None:
            params["wait_until"] = wait_until
        try:
            res = await self.provider.call("send_tx", params)
            return TransactionResult.from_json_response(res)
        except JsonRpcError as e:
            error = ERRORS.get(e.cause_name)
            message = ERROR_MESSAGES.get(e.cause_name, str(e))
            if error:
                raise error(message) from e
            raise
