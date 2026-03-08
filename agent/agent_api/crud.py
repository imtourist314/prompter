from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Sequence

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from agent_shared.statuses import FileStatus

from .models import Subscriber, SubscriptionFile
from .schemas import SubscriberCreate, SubscriptionFileCreate

ALLOWED_TRANSITIONS = {
    FileStatus.PENDING: {FileStatus.DELIVERED, FileStatus.ERRORED},
    FileStatus.DELIVERED: {FileStatus.RUNNING, FileStatus.ERRORED},
    FileStatus.RUNNING: {FileStatus.COMPLETED, FileStatus.ERRORED},
    FileStatus.COMPLETED: set(),
    FileStatus.ERRORED: set(),
}


def _normalize_status_filter(statuses: Iterable[FileStatus | str] | None) -> List[str]:
    normalized: set[str] = set()
    for status in statuses or []:
        if status is None:
            continue
        if isinstance(status, FileStatus):
            normalized.add(status.value)
            continue
        normalized.add(FileStatus(status.upper()).value)
    if not normalized:
        normalized.add(FileStatus.PENDING.value)
    return sorted(normalized)


def create_subscriber(db: Session, payload: SubscriberCreate) -> Subscriber:
    normalized_statuses = _normalize_status_filter(payload.status_filter)
    existing = db.execute(
        select(Subscriber).where(
            Subscriber.project == payload.project,
            Subscriber.area == payload.area,
            Subscriber.component == payload.component,
            Subscriber.status_filter == normalized_statuses,
        )
    ).scalar_one_or_none()
    if existing:
        raise ValueError("Subscriber already exists for this project, area, component, and status filter")

    payload_data = payload.model_dump()
    payload_data["status_filter"] = normalized_statuses

    subscriber = Subscriber(**payload_data)
    db.add(subscriber)
    db.commit()
    db.refresh(subscriber)
    return subscriber


def list_subscribers(
    db: Session,
    project: str | None = None,
    area: str | None = None,
    component: str | None = None,
) -> List[Subscriber]:
    stmt = select(Subscriber)
    if project:
        stmt = stmt.where(Subscriber.project == project)
    if area:
        stmt = stmt.where(Subscriber.area == area)
    if component:
        stmt = stmt.where(Subscriber.component == component)
    result = db.execute(stmt.order_by(Subscriber.created_at.asc()))
    return list(result.scalars().all())


def get_subscriber(db: Session, subscriber_id: int) -> Subscriber | None:
    return db.get(Subscriber, subscriber_id)


def publish_file(db: Session, payload: SubscriptionFileCreate) -> Sequence[SubscriptionFile]:
    now = datetime.utcnow()
    subscribers = db.execute(
        select(Subscriber).where(
            and_(
                Subscriber.project == payload.project,
                Subscriber.area == payload.area,
                Subscriber.component == payload.component,
            )
        )
    ).scalars().all()

    created: list[SubscriptionFile] = []
    target_status = payload.status or FileStatus.PENDING
    for subscriber in subscribers:
        if subscriber.timestamp_from and now < subscriber.timestamp_from:
            continue
        subscription_file = SubscriptionFile(
            subscriber_id=subscriber.id,
            project=payload.project,
            area=payload.area,
            component=payload.component,
            file_name=payload.file_name,
            description=payload.description,
            content=payload.content,
            status=target_status,
        )
        db.add(subscription_file)
        created.append(subscription_file)

    db.commit()
    for file_obj in created:
        db.refresh(file_obj)
    return created


def fetch_files_for_subscriber(
    db: Session,
    subscriber_id: int,
    statuses: Iterable[FileStatus] | None = None,
    limit: int = 25,
) -> List[SubscriptionFile]:
    stmt = select(SubscriptionFile).where(SubscriptionFile.subscriber_id == subscriber_id)
    if statuses:
        stmt = stmt.where(SubscriptionFile.status.in_(list(statuses)))
    stmt = stmt.order_by(SubscriptionFile.created_at.asc()).limit(limit)
    result = db.execute(stmt)
    files = list(result.scalars().all())
    return files


def list_subscription_files(
    db: Session,
    project: str | None = None,
    area: str | None = None,
    component: str | None = None,
    subscriber_id: int | None = None,
    statuses: Iterable[FileStatus] | None = None,
    limit: int = 100,
) -> List[SubscriptionFile]:
    stmt = select(SubscriptionFile)
    if project:
        stmt = stmt.where(SubscriptionFile.project == project)
    if area:
        stmt = stmt.where(SubscriptionFile.area == area)
    if component:
        stmt = stmt.where(SubscriptionFile.component == component)
    if subscriber_id:
        stmt = stmt.where(SubscriptionFile.subscriber_id == subscriber_id)
    if statuses:
        stmt = stmt.where(SubscriptionFile.status.in_(list(statuses)))
    stmt = stmt.order_by(SubscriptionFile.created_at.desc()).limit(limit)
    result = db.execute(stmt)
    return list(result.scalars().all())


def list_unique_projects(db: Session) -> List[str]:
    stmt = select(Subscriber.project).distinct().order_by(Subscriber.project.asc())
    return list(db.execute(stmt).scalars().all())


def list_unique_areas(db: Session, project: str | None = None) -> List[str]:
    stmt = select(Subscriber.area).distinct()
    if project:
        stmt = stmt.where(Subscriber.project == project)
    stmt = stmt.order_by(Subscriber.area.asc())
    return list(db.execute(stmt).scalars().all())


def list_unique_components(db: Session, project: str | None = None, area: str | None = None) -> List[str]:
    stmt = select(Subscriber.component).distinct()
    if project:
        stmt = stmt.where(Subscriber.project == project)
    if area:
        stmt = stmt.where(Subscriber.area == area)
    stmt = stmt.order_by(Subscriber.component.asc())
    return list(db.execute(stmt).scalars().all())


def update_file_status(db: Session, file_id: int, new_status: FileStatus, error_message: str | None = None) -> SubscriptionFile:
    file_obj = db.get(SubscriptionFile, file_id)
    if not file_obj:
        raise FileNotFoundError("File not found")

    allowed = ALLOWED_TRANSITIONS.get(file_obj.status, set())
    if new_status not in allowed and file_obj.status != new_status:
        raise ValueError(f"Invalid status transition {file_obj.status} -> {new_status}")

    file_obj.status = new_status
    now = datetime.utcnow()
    if new_status == FileStatus.DELIVERED:
        file_obj.delivered_at = now
    elif new_status == FileStatus.RUNNING:
        file_obj.run_started_at = now
    elif new_status == FileStatus.COMPLETED:
        file_obj.completed_at = now
        file_obj.error_message = None
    elif new_status == FileStatus.ERRORED:
        file_obj.error_message = error_message

    db.add(file_obj)
    db.commit()
    db.refresh(file_obj)
    return file_obj
