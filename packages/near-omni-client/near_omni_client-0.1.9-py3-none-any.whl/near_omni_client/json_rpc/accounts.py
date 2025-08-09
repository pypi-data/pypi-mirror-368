import base64
import json

from near_omni_client.json_rpc.exceptions import ERROR_MESSAGES, ERRORS, JsonRpcError
from near_omni_client.json_rpc.interfaces.provider import IJsonRpcProvider
from near_omni_client.json_rpc.models import AccountResult, CallFunctionResult


class Accounts:
    """Class to interact with NEAR blockchain accounts via JSON RPC."""

    def __init__(self, provider: IJsonRpcProvider):
        self.provider = provider

    async def view_account(self, account_id: str, finality: str = "final") -> AccountResult:
        """Fetch account information for the given account ID."""
        try:
            res = await self.provider.call(
                "query",
                {
                    "request_type": "view_account",
                    "finality": finality,
                    "account_id": account_id,
                },
            )
            return AccountResult.from_json_response(res)
        except JsonRpcError as e:
            error = ERRORS.get(e.cause_name)
            message = ERROR_MESSAGES.get(e.cause_name, str(e))
            if error:
                raise error(message) from e
            raise

    async def call_function(
        self, account_id: str, method_name: str, args: dict, finality: str = "final"
    ) -> CallFunctionResult:
        """Call a function on a NEAR account with the given arguments."""
        try:
            encoded_args = base64.b64encode(json.dumps(args).encode("utf-8")).decode("utf-8")
            res = await self.provider.call(
                "query",
                {
                    "request_type": "call_function",
                    "finality": finality,
                    "account_id": account_id,
                    "method_name": method_name,
                    "args_base64": encoded_args,
                },
            )
            return CallFunctionResult.from_json_response(res)
        except JsonRpcError as e:
            error = ERRORS.get(e.cause_name)
            message = ERROR_MESSAGES.get(e.cause_name, str(e))
            if error:
                raise error(message) from e
            raise
