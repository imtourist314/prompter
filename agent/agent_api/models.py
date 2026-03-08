from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text, UniqueConstraint, Index
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from agent_shared.statuses import FileStatus

from .settings import get_settings

try:
    from sqlalchemy.dialects.postgresql import JSONB as PGJSONB
except ModuleNotFoundError:  # pragma: no cover - optional
    PGJSONB = None  # type: ignore


def _resolve_json_type():
    backend_name = make_url(get_settings().database_url).get_backend_name()
    if backend_name.startswith("postgres") and PGJSONB is not None:
        return PGJSONB
    return SQLiteJSON


JSONType = _resolve_json_type()


class Base(DeclarativeBase):
    pass


class Subscriber(Base):
    __tablename__ = "prm_subscriber"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project: Mapped[str] = mapped_column(String(128), nullable=False)
    area: Mapped[str] = mapped_column(String(128), nullable=False)
    component: Mapped[str] = mapped_column(String(128), nullable=False)
    status_filter: Mapped[List[str]] = mapped_column(JSONType, default=lambda: [FileStatus.PENDING.value])
    timestamp_from: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    destination_directory: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    refresh_interval: Mapped[int] = mapped_column(Integer, default=60)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    files: Mapped[List[SubscriptionFile]] = relationship(back_populates="subscriber", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("project", "area", "component", "status_filter", name="uq_subscriber_project_area_component_status"),
        Index("ix_subscriber_project", "project"),
        Index("ix_subscriber_area", "area"),
        Index("ix_subscriber_component", "component"),
    )


class SubscriptionFile(Base):
    __tablename__ = "prm_subscription_file"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subscriber_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("prm_subscriber.id", ondelete="CASCADE"),
        nullable=False,
    )
    project: Mapped[str] = mapped_column(String(128), nullable=False)
    area: Mapped[str] = mapped_column(String(128), nullable=False)
    component: Mapped[str] = mapped_column(String(128), nullable=False)
    file_name: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(512))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[FileStatus] = mapped_column(SAEnum(FileStatus), default=FileStatus.PENDING)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    run_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    subscriber: Mapped[Subscriber] = relationship(back_populates="files")

    __table_args__ = (
        Index("ix_subscription_file_project", "project"),
        Index("ix_subscription_file_area", "area"),
        Index("ix_subscription_file_component", "component"),
        Index("ix_subscription_file_subscriber", "subscriber_id"),
    )
