class JsonRpcError(Exception):
    """Exception class for handling JSON-RPC errors.

    This class is designed to parse and store error information from a JSON-RPC response.
    The error information is expected to be in the following format:
    {
        "name": <ERROR_TYPE>,
        "cause": { "name": <ERROR_CAUSE>, "info": {...} },
        "code": int,    # legacy
        "data": str,    # legacy
        "message": str  # legacy
    }
    """

    def __init__(self, error_json: dict):
        self.error_type = error_json.get("name")
        cause = error_json.get("cause", {})
        self.cause_name = cause.get("name")
        self.cause_info = cause.get("info")
        self.code = error_json.get("code")  # legacy
        self.data = error_json.get("data")  # legacy
        self.message = error_json.get("message")  # legacy
        super().__init__(f"[{self.cause_name or self.error_type}] {self.message}")

    @classmethod
    def from_response(cls, error_json: dict):
        """Create a JsonRpcError instance from a JSON-RPC error response.

        Args:
            error_json (dict): The JSON-RPC error response containing error details.

        Returns:
            JsonRpcError: An instance of JsonRpcError initialized with the provided error details.

        """
        return cls(error_json)
