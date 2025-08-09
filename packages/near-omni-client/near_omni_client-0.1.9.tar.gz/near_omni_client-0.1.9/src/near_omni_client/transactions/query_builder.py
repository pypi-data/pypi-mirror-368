from typing import Any


class QueryBuilder:
    """Builder for constructing NEAR query objects."""

    def __init__(self):
        self._contract_id: str | None = None
        self._method_name: str | None = None
        self._args: dict[str, Any] = {}

    def with_contract_id(self, contract_id: str) -> "QueryBuilder":
        """Set the contract ID for the query."""
        self._contract_id = contract_id
        return self

    def with_method_name(self, method_name: str) -> "QueryBuilder":
        """Set the method name to call on the contract."""
        self._method_name = method_name
        return self

    def with_args(self, args: dict[str, Any]) -> "QueryBuilder":
        """Set the arguments for the method call."""
        self._args = args
        return self

    def build(self) -> dict[str, Any]:
        """Build the query object."""
        if not self._contract_id:
            raise ValueError("contract_id is required")
        if not self._method_name:
            raise ValueError("method_name is required")

        return {
            "contract_id": self._contract_id,
            "method_name": self._method_name,
            "args": self._args,
        }
