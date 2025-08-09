from typing import Any

from pydantic import BaseModel


class ExecutionOutcomeStatus(BaseModel):
    """Represent the status of a NEAR transaction execution outcome."""

    SuccessValue: str | None = None
    SuccessReceiptId: str | None = None
    Failure: Any | None = None


class ExecutionOutcome(BaseModel):
    """Represent a NEAR transaction execution outcome."""

    logs: list[str]
    receipt_ids: list[str]
    gas_burnt: int
    tokens_burnt: str
    executor_id: str
    status: ExecutionOutcomeStatus


class ExecutionOutcomeWithProof(BaseModel):
    """Represent a NEAR transaction outcome with proof."""

    proof: list[Any]
    block_hash: str
    id: str
    outcome: ExecutionOutcome


class TransactionSummary(BaseModel):
    """Represent a summary of a NEAR transaction."""

    signer_id: str
    public_key: str
    nonce: int
    receiver_id: str
    actions: list[dict[str, Any]]
    signature: str
    hash: str


class TransactionResult(BaseModel):
    """Represent the result of a NEAR transaction."""

    final_execution_status: str
    status: dict[str, Any]
    transaction: TransactionSummary
    transaction_outcome: ExecutionOutcomeWithProof
    receipts_outcome: list[ExecutionOutcomeWithProof]

    @classmethod
    def from_json_response(cls, rpc_response: dict) -> "TransactionResult":
        """Create a TransactionResult instance from a JSON-RPC response."""
        return cls.model_validate(rpc_response["result"])
