from pydantic import BaseModel, model_validator

from .access_key_result import Permission


class AccessKeyInner(BaseModel):
    """Model for an access key in NEAR."""

    nonce: int
    permission: Permission

    @model_validator(mode="before")
    @classmethod
    def parse_permission(cls, data):
        """Parse the permission field to ensure it is in the correct format."""
        if (
            isinstance(data, dict)
            and isinstance(data.get("permission"), str)
            and data["permission"] == "FullAccess"
        ):
            data["permission"] = {"FullAccess": {}}
        return data


class AccessKeyEntry(BaseModel):
    """Model for an access key entry in NEAR."""

    public_key: str
    access_key: AccessKeyInner


class AccessKeyListResult(BaseModel):
    """Model for the result of a list of access keys in NEAR."""

    block_hash: str
    block_height: int
    keys: list[AccessKeyEntry]

    @classmethod
    def from_json_response(cls, rpc_response: dict) -> "AccessKeyListResult":
        """Create an AccessKeyListResult instance from a JSON-RPC response."""
        return cls.model_validate(rpc_response["result"])
