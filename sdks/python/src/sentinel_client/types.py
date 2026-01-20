from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class AccessStatus(str, Enum):
    APPROVED = "APPROVED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    DENIED = "DENIED"


class AccessIntent(BaseModel):
    summary: str
    description: str
    task_id: str


class AccessRequest(BaseModel):
    agent_id: str
    resource_id: str
    intent: AccessIntent
    ttl_seconds: int = Field(..., gt=0)


class SecretPayload(BaseModel):
    type: str
    value: str
    expires_at: str


class AccessResponse(BaseModel):
    request_id: str
    status: AccessStatus
    secret: Optional[SecretPayload] = None
    message: Optional[str] = None
    polling_url: Optional[str] = None
    reason: Optional[str] = None
