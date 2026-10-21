from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Status(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"


class TicketCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=100)
    description: str | None = None
    priority: Priority = Priority.MEDIUM
    status: Status = Status.OPEN


class TicketUpdate(BaseModel):
    """PATCH body: only status and/or priority may change."""

    model_config = ConfigDict(extra="forbid")

    status: Status | None = None
    priority: Priority | None = None

    @model_validator(mode="after")
    def at_least_one_field(self):
        if self.status is None and self.priority is None:
            raise ValueError("Provide at least one of: status, priority")
        return self


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    priority: Priority
    status: Status
    created_at: datetime


class OldestUnresolved(BaseModel):
    id: int
    title: str


class TicketSummary(BaseModel):
    total: int
    open: int
    in_progress: int
    resolved: int
    high_priority: int
    oldest_unresolved: OldestUnresolved | None
