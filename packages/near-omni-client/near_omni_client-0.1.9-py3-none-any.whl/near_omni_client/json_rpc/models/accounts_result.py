from pydantic import BaseModel


class AccountResult(BaseModel):
    """Model for the result of an account query in NEAR."""

    amount: str
    block_hash: str
    block_height: int
    code_hash: str
    locked: str
    storage_paid_at: int
    storage_usage: int

    @classmethod
    def from_json_response(cls, rpc_response: dict) -> "AccountResult":
        """Create an AccountResult instance from a JSON-RPC response."""
        return cls.model_validate(rpc_response["result"])


class CallFunctionResult(BaseModel):
    """Model for the result of a function call in NEAR."""

    block_hash: str
    block_height: int
    logs: list[str]
    result: list[int]  # bytes as list of integers

    @classmethod
    def from_json_response(cls, rpc_response: dict) -> "CallFunctionResult":
        """Create a CallFunctionResult instance from a JSON-RPC response."""
        return cls.model_validate(rpc_response["result"])

    def decoded_result(self) -> str:
        """Decode the result from a list of integers to a UTF-8 string."""
        return bytes(self.result).decode("utf-8")
