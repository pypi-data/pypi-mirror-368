from typing import Any

from pydantic import BaseModel


class CongestionInfo(BaseModel):
    """Model for congestion information in a NEAR block chunk."""

    allowed_shard: int
    buffered_receipts_gas: str
    delayed_receipts_gas: str
    receipt_bytes: int


class BlockChunk(BaseModel):
    """Model for a NEAR block chunk."""

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


class BlockHeader(BaseModel):
    """Model for the header of a NEAR block."""

    approvals: list[str | None]
    block_body_hash: str
    block_merkle_root: str
    block_ordinal: int
    challenges_result: list[Any]
    challenges_root: str
    chunk_endorsements: list[list[int]]
    chunk_headers_root: str
    chunk_mask: list[bool]
    chunk_receipts_root: str
    chunk_tx_root: str
    chunks_included: int
    epoch_id: str
    epoch_sync_data_hash: str | None
    gas_price: str
    hash: str
    height: int
    last_ds_final_block: str
    last_final_block: str
    latest_protocol_version: int
    next_bp_hash: str
    next_epoch_id: str
    outcome_root: str
    prev_hash: str
    prev_height: int
    prev_state_root: str
    random_value: str
    rent_paid: str
    signature: str
    timestamp: int
    timestamp_nanosec: str
    total_supply: str
    validator_proposals: list[Any]
    validator_reward: str


class BlockResult(BaseModel):
    """Model for the result of a NEAR block query."""

    author: str
    chunks: list[BlockChunk]
    header: BlockHeader

    @classmethod
    def from_json_response(cls, rpc_response: dict) -> "BlockResult":
        """Create a BlockResult instance from a JSON-RPC response."""
        return cls.model_validate(rpc_response["result"])
