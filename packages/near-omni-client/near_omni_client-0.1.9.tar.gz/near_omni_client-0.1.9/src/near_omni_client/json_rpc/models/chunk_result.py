from typing import Any

from pydantic import BaseModel, Field

from .block_result import CongestionInfo


class ChunkHeader(BaseModel):
    """Model for the header of a NEAR chunk."""

    balance_burnt: str
    bandwidth_requests: Any | None
    chunk_hash: str
    congestion_info: CongestionInfo
    encoded_length: int
    encoded_merkle_root: str
    gas_limit: int
    gas_used: int
    height_created: int
    height_included: int
    outcome_root: str
    outgoing_receipts_root: str
    prev_block_hash: str
    prev_state_root: str
    rent_paid: str
    shard_id: int
    signature: str
    tx_root: str
    validator_proposals: list[Any]
    validator_reward: str


class FunctionCallAction(BaseModel):
    """Model for a function call action in a NEAR transaction."""

    args: str
    deposit: str
    gas: int
    method_name: str


class Action(BaseModel):
    """Model for an action in a NEAR transaction."""

    function_call: FunctionCallAction = Field(..., alias="FunctionCall")


class Transaction(BaseModel):
    """Model for a NEAR transaction."""

    actions: list[Action]
    hash: str
    nonce: int
    priority_fee: int
    public_key: str
    receiver_id: str
    signature: str
    signer_id: str


class ChunkResult(BaseModel):
    """Model for the result of a NEAR chunk processing."""

    author: str
    header: ChunkHeader
    receipts: list[Any]
    transactions: list[Transaction]

    @classmethod
    def from_json_response(cls, rpc_response: dict) -> "ChunkResult":
        """Create a ChunkResult instance from a JSON-RPC response."""
        return cls.model_validate(rpc_response["result"])
