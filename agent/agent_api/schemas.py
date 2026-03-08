from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from agent_shared.statuses import FileStatus


class SubscriberBase(BaseModel):
    project: str = Field(..., min_length=1)
    area: str = Field(..., min_length=1)
    component: str = Field(..., min_length=1)
    status_filter: List[FileStatus] = Field(default_factory=lambda: [FileStatus.PENDING])
    timestamp_from: Optional[datetime] = None
    destination_directory: Optional[str] = None
    refresh_interval: int = Field(default=60, gt=0)


class SubscriberCreate(SubscriberBase):
    pass


class SubscriberRead(SubscriberBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubscriptionFileBase(BaseModel):
    file_name: str
    project: str
    area: str
    component: str
    description: Optional[str] = None
    content: str


class SubscriptionFileCreate(SubscriptionFileBase):
    status: FileStatus = Field(default=FileStatus.PENDING)


class SubscriptionFileRead(SubscriptionFileBase):
    id: int
    subscriber_id: int
    status: FileStatus
    created_at: datetime
    updated_at: datetime
    delivered_at: Optional[datetime]
    run_started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class FileStatusUpdate(BaseModel):
    status: FileStatus
    error_message: Optional[str] = None


class PublishResponse(BaseModel):
    created: List[SubscriptionFileRead]

    model_config = ConfigDict(from_attributes=True)
