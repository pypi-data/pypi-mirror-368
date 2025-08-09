from near_omni_client.json_rpc.exceptions import ERROR_MESSAGES, ERRORS, JsonRpcError
from near_omni_client.json_rpc.interfaces.provider import IJsonRpcProvider
from near_omni_client.json_rpc.models import AccessKeyListResult, AccessKeyResult


class AccessKey:
    """Class to interact with NEAR blockchain access keys via JSON RPC."""

    def __init__(self, provider: IJsonRpcProvider):
        self.provider = provider

    async def view_access_key(
        self, account_id: str, public_key: str, finality: str = "final"
    ) -> AccessKeyResult:
        """Fetch an access key for the given account and public key."""
        try:
            res = await self.provider.call(
                "query",
                {
                    "request_type": "view_access_key",
                    "finality": finality,
                    "account_id": account_id,
                    "public_key": public_key,
                },
            )
            return AccessKeyResult.from_json_response(res)
        except JsonRpcError as e:
            error = ERRORS.get(e.cause_name)
            message = ERROR_MESSAGES.get(e.cause_name, str(e))
            if error:
                raise error(message) from e
            raise

    async def view_access_key_list(
        self, account_id: str, finality: str = "final"
    ) -> AccessKeyListResult:
        """Fetch a list of access keys for the given account."""
        try:
            res = await self.provider.call(
                "query",
                {
                    "request_type": "view_access_key_list",
                    "finality": finality,
                    "account_id": account_id,
                },
            )
            return AccessKeyListResult.from_json_response(res)
        except JsonRpcError as e:
            error = ERRORS.get(e.cause_name)
            message = ERROR_MESSAGES.get(e.cause_name, str(e))
            if error:
                raise error(message) from e
            raise
