from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

import httpx


class AgentApiClient:
    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(base_url=self.base_url, timeout=self.timeout)

    def close(self) -> None:
        self._client.close()

    def register_subscriber(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = self._client.post("/subscribers", json=payload)
        resp.raise_for_status()
        return resp.json()

    def list_subscribers(
        self,
        project: Optional[str] = None,
        area: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {}
        if project:
            params["project"] = project
        if area:
            params["area"] = area
        resp = self._client.get("/subscribers", params=params or None)
        resp.raise_for_status()
        return resp.json()

    def list_files(
        self,
        subscriber_id: str,
        statuses: Optional[Iterable[str]] = None,
        limit: int = 25,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"limit": limit}
        if statuses:
            params["status"] = list(statuses)
        resp = self._client.get(f"/subscribers/{subscriber_id}/files", params=params)
        resp.raise_for_status()
        return resp.json()

    def list_published_files(
        self,
        project: Optional[str] = None,
        area: Optional[str] = None,
        subscriber_id: Optional[int | str] = None,
        statuses: Optional[Iterable[str]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"limit": limit}
        if project:
            params["project"] = project
        if area:
            params["area"] = area
        if subscriber_id:
            params["subscriber_id"] = subscriber_id
        if statuses:
            params["status"] = list(statuses)
        resp = self._client.get("/files", params=params)
        resp.raise_for_status()
        return resp.json()

    def update_file_status(
        self,
        file_id: str,
        status: str,
        error_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {"status": status}
        if error_message:
            payload["error_message"] = error_message
        resp = self._client.patch(f"/files/{file_id}/status", json=payload)
        resp.raise_for_status()
        return resp.json()

    def publish_file(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = self._client.post("/files", json=payload)
        resp.raise_for_status()
        return resp.json()

    def health(self) -> Dict[str, Any]:
        resp = self._client.get("/health")
        resp.raise_for_status()
        return resp.json()

    def __enter__(self) -> "AgentApiClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        self.close()
