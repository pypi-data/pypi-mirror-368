import base64
import json

from near_omni_client.json_rpc.client import NearClient
from near_omni_client.signers import NearKeypairSigner
from near_omni_client.transactions import ActionFactory, TransactionBuilder

from .interfaces.signer import ISigner


class MpcSigner(ISigner):
    """MPC Signer implementation for NEAR transactions."""

    def __init__(
        self,
        client: NearClient,
        signer: NearKeypairSigner,
        account_id: str,
        contract_id: str,
        path: str,
    ):
        self._near_client = client
        self.signer_account = signer
        self.account_id = account_id
        self.contract_id = contract_id
        self.path = path

    async def sign(self, data: bytes) -> bytes:
        """Sign arbitrary bytes with the MPC signer."""
        encoded_hash = base64.b64encode(data).decode()

        # get nonce and block hash for the transaction
        tx_meta = await self._near_client.get_nonce_and_block_hash(
            account_id=self.account_id, public_key=self.public_key
        )

        action = ActionFactory.function_call(
            method_name="sign_hash",
            args={"hash": encoded_hash, "path": self.path},
            gas=300_000_000_000_000,
            deposit=1,
        )

        # build the transaction
        tx = (
            TransactionBuilder()
            .with_signer_id(self.account_id)
            .with_public_key(self.public_key)
            .with_nonce(tx_meta["nonce"])
            .with_receiver(self.contract_id)
            .with_block_hash(tx_meta["block_hash"])
            .add_action(action)
            .build()
        )

        # sign the transaction and get the signed transaction in base64 format
        signed_tx_base64 = self._signer.sign_base64(tx)

        # send the signed transaction (to be signed) to the NEAR network
        result = await self._client.send_raw_transaction(signed_tx_base64)

        return self._extract_signature_from_result(result)

    def _extract_signature_from_result(self, result):
        """Extract the signature from the transaction result."""
        if hasattr(result, "status"):
            if isinstance(result.status, dict) and "SuccessValue" in result.status:
                success_value = result.status["SuccessValue"]
                decoded_bytes = base64.b64decode(success_value)
                decoded_json = json.loads(decoded_bytes.decode("utf-8"))
                return decoded_json
            else:
                print(
                    f"Debug - result.status keys: {result.status.keys() if hasattr(result.status, 'keys') else 'No keys'}"
                )
                raise Exception(f"Unexpected result structure: {result.status}")
        else:
            print("Debug - result has no status attribute")
            return None
