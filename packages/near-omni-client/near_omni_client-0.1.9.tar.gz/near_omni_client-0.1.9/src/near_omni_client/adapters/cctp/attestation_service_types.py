from typing import Literal

from pydantic import BaseModel


class Message(BaseModel):
    """Model representing a message in the attestation service."""

    message: str | None
    eventNonce: str
    attestation: str | None
    cctpVersion: int
    status: Literal["pending_confirmations", "complete"]


class GetMessagesResponse(BaseModel):
    """Response model for getting messages from the attestation service."""

    messages: list[Message]


class GetMessagesBadRequestResponse(BaseModel):
    """Response model for bad request errors when getting messages."""

    error: str


class GetMessagesNotFoundResponse(BaseModel):
    """Response model for not found errors when getting messages."""

    code: int
    error: str
