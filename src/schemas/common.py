from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error class or type name")
    message: str = Field(..., description="Human-readable error explanation")
    details: Any | None = Field(None, description="Optional extra error details")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Error occurrence timestamp"
    )


class MessageResponse(BaseModel):
    message: str = Field(..., description="Success message content")


class HealthResponse(BaseModel):
    status: str = Field(default="healthy", description="Application health status")
    version: str = Field(..., description="Application version")
    database: str = Field(..., description="Database connection status")
