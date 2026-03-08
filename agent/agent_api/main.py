from __future__ import annotations

from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.orm import Session

from agent_shared.statuses import FileStatus

from . import crud, models, schemas
from .database import engine, get_session

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AgentAPI", version="0.1.0")

INSTRUCTION_COMPLETED_ALIAS = "completed_instructions.md"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/subscribers", response_model=schemas.SubscriberRead, status_code=status.HTTP_201_CREATED)
def create_subscriber(
    payload: schemas.SubscriberCreate,
    db: Session = Depends(get_session),
):
    try:
        subscriber = crud.create_subscriber(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return subscriber


@app.get("/subscribers", response_model=List[schemas.SubscriberRead])
def list_subscribers(
    project: Optional[str] = None,
    area: Optional[str] = None,
    component: Optional[str] = None,
    db: Session = Depends(get_session),
):
    return crud.list_subscribers(db, project, area, component)


@app.get("/projects", response_model=List[str])
def list_projects(db: Session = Depends(get_session)):
    return crud.list_unique_projects(db)


@app.get("/areas", response_model=List[str])
def list_areas(
    project: Optional[str] = Query(None),
    db: Session = Depends(get_session),
):
    return crud.list_unique_areas(db, project)


@app.get("/components", response_model=List[str])
def list_components(
    project: Optional[str] = Query(None),
    area: Optional[str] = Query(None),
    db: Session = Depends(get_session),
):
    return crud.list_unique_components(db, project, area)


@app.get("/subscribers/{subscriber_id}", response_model=schemas.SubscriberRead)
def get_subscriber(subscriber_id: int, db: Session = Depends(get_session)):
    subscriber = crud.get_subscriber(db, subscriber_id)
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    return subscriber


@app.get(
    "/subscribers/{subscriber_id}/files",
    response_model=List[schemas.SubscriptionFileRead],
)
def get_files_for_subscriber(
    subscriber_id: int,
    statuses: Optional[List[FileStatus]] = Query(None, alias="status"),
    limit: int = Query(25, gt=0, le=100),
    db: Session = Depends(get_session),
):
    subscriber = crud.get_subscriber(db, subscriber_id)
    if not subscriber:
        return []

    status_list = statuses
    if not status_list and subscriber.status_filter:
        status_list = [FileStatus(status) for status in subscriber.status_filter]

    files = crud.fetch_files_for_subscriber(db, subscriber_id, status_list, limit)
    return files


@app.get("/files", response_model=List[schemas.SubscriptionFileRead])
def list_published_files(
    project: Optional[str] = None,
    area: Optional[str] = None,
    component: Optional[str] = None,
    subscriber_id: Optional[int] = None,
    statuses: Optional[List[FileStatus]] = Query(None, alias="status"),
    limit: int = Query(100, gt=0, le=500),
    db: Session = Depends(get_session),
):
    files = crud.list_subscription_files(db, project, area, component, subscriber_id, statuses, limit)
    return files


@app.post("/files", response_model=schemas.PublishResponse, status_code=status.HTTP_201_CREATED)
def publish_file(payload: schemas.SubscriptionFileCreate, db: Session = Depends(get_session)):
    created = crud.publish_file(db, payload)
    return schemas.PublishResponse(created=created)


@app.patch("/files/{file_id}/status", response_model=schemas.SubscriptionFileRead)
def update_file_status(
    file_id: int,
    payload: schemas.FileStatusUpdate,
    db: Session = Depends(get_session),
):
    try:
        file_obj = crud.update_file_status(db, file_id, payload.status, payload.error_message)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return file_obj
