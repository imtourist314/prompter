from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List

from agent_shared.statuses import FileStatus

from .actions import ActionExecutionError, run_action
from .client import AgentApiClient
from .config import CONFIG_PATH, DEFAULT_REFRESH_INTERVAL, load_config, save_config

logger = logging.getLogger("agent_daemon")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def normalize_statuses(values: Iterable[str] | None, *, default_to_pending: bool = True) -> List[str]:
    provided = list(values) if values is not None else []
    candidates = provided if provided else ([FileStatus.PENDING.value] if default_to_pending else [])
    normalized: List[str] = []
    for value in candidates:
        if value is None:
            continue
        try:
            normalized.append(FileStatus(value.upper()).value)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"Invalid status value: {value}") from exc
    if normalized:
        return normalized
    return [FileStatus.PENDING.value] if default_to_pending else []


def parse_timestamp(value: str | None) -> str | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid timestamp: {value}") from exc
    return dt.isoformat()


def print_table(headers: List[str], rows: List[List[str]]) -> None:
    if not rows:
        return
    widths = [len(header) for header in headers]
    for row in rows:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(cell))
    header_line = " | ".join(header.ljust(widths[idx]) for idx, header in enumerate(headers))
    separator = "-+-".join("-" * width for width in widths)
    print(header_line)
    print(separator)
    for row in rows:
        print(" | ".join(cell.ljust(widths[idx]) for idx, cell in enumerate(row)))


def run_pi_script(directory: Path, file_path: Path) -> None:
    script_path = directory / "scripts" / "pi_run.sh"
    if not script_path.is_file():
        raise RuntimeError(f"Required script not found: {script_path}")
    try:
        subprocess.run(
            [str(script_path), str(file_path)],
            check=True,
            capture_output=True,
            text=True,
            cwd=str(directory),
        )
    except subprocess.CalledProcessError as exc:
        output = exc.stderr or exc.stdout or str(exc)
        raise RuntimeError(f"pi_run.sh failed: {output}") from exc
    except OSError as exc:  # pragma: no cover - system dependent
        raise RuntimeError(f"Unable to execute {script_path}: {exc}") from exc


def register_subscriber(args: argparse.Namespace) -> None:
    config = load_config()
    api_base = args.api_base or config.get("api_base")
    destination_dir = Path(args.directory).expanduser()
    destination_dir.mkdir(parents=True, exist_ok=True)
    status_values = normalize_statuses(args.status)
    payload = {
        "project": args.project,
        "area": args.area,
        "status_filter": status_values,
        "timestamp_from": parse_timestamp(args.timestamp_from),
        "destination_directory": str(destination_dir),
        "refresh_interval": args.refresh or DEFAULT_REFRESH_INTERVAL,
    }
    with AgentApiClient(api_base) as client:
        subscriber = client.register_subscriber(payload)
    subscriber_id = subscriber["id"]
    config["api_base"] = api_base
    config.setdefault("subscribers", {})
    config["subscribers"][subscriber_id] = {
        "subscriber_id": subscriber_id,
        "project": subscriber["project"],
        "area": subscriber["area"],
        "directory": payload["destination_directory"],
        "status_filter": payload["status_filter"],
        "refresh_interval": payload["refresh_interval"],
        "timestamp_from": payload["timestamp_from"],
        "actions": args.action or [],
    }
    config["refresh_interval"] = args.refresh or config.get("refresh_interval", DEFAULT_REFRESH_INTERVAL)
    save_config(config)
    logger.info("Registered subscriber %s saved to %s", subscriber_id, CONFIG_PATH)


def publish_file(args: argparse.Namespace) -> None:
    if not args.file_name and not args.content:
        logger.error("You must provide --file-name or --content when publishing")
        sys.exit(1)

    def _load_content(value: str) -> str:
        candidate = Path(value).expanduser()
        if candidate.is_file():
            return candidate.read_text()
        return value

    file_name: str
    content: str

    if args.file_name and not args.content:
        source_path = Path(args.file_name).expanduser()
        if not source_path.is_file():
            logger.error("File '%s' does not exist and no --content was provided", source_path)
            sys.exit(1)
        file_name = source_path.name
        content = source_path.read_text()
    elif args.content:
        content = _load_content(args.content)
        if args.file_name:
            file_name = args.file_name
        else:
            file_name = f"published_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
    else:
        logger.error("Unable to determine publish payload")
        sys.exit(1)

    payload = {
        "file_name": file_name,
        "project": args.project,
        "area": args.area,
        "description": args.description,
        "content": content,
    }
    config = load_config()
    api_base = args.api_base or config.get("api_base")
    with AgentApiClient(api_base) as client:
        resp = client.publish_file(payload)
    logger.info("Published file; created entries: %s", json.dumps(resp, indent=2))


def list_subscribers_command(args: argparse.Namespace) -> None:
    config = load_config()
    api_base = args.api_base or config.get("api_base")
    with AgentApiClient(api_base) as client:
        subscribers = client.list_subscribers(args.project, args.area)
    if not subscribers:
        logger.info("No subscribers found.")
        return
    rows: List[List[str]] = []
    for subscriber in subscribers:
        statuses = subscriber.get("status_filter") or []
        rows.append(
            [
                str(subscriber.get("id", "")),
                str(subscriber.get("project", "")),
                str(subscriber.get("area", "")),
                ", ".join(str(status) for status in statuses) if statuses else "-",
            ]
        )
    print_table(["ID", "Project", "Area", "Statuses"], rows)


def list_published_files_command(args: argparse.Namespace) -> None:
    config = load_config()
    api_base = args.api_base or config.get("api_base")
    status_filter: List[str] | None = None
    if args.status:
        normalized = normalize_statuses(args.status, default_to_pending=False)
        status_filter = normalized or None
    with AgentApiClient(api_base) as client:
        files = client.list_published_files(
            project=args.project,
            area=args.area,
            subscriber_id=args.subscriber_id,
            statuses=status_filter,
            limit=args.limit,
        )
    if not files:
        logger.info("No published files found.")
        return
    rows: List[List[str]] = []
    for entry in files:
        rows.append(
            [
                str(entry.get("id", "")),
                str(entry.get("subscriber_id", "")),
                str(entry.get("project", "")),
                str(entry.get("area", "")),
                str(entry.get("file_name", "")),
                str(entry.get("status", "")),
                str(entry.get("created_at", "")),
            ]
        )
    print_table(["ID", "Subscriber", "Project", "Area", "File", "Status", "Created"], rows)


def run_loop(args: argparse.Namespace) -> None:
    while True:
        config = load_config()
        api_base = args.api_base or config.get("api_base")
        refresh = args.refresh or config.get("refresh_interval", DEFAULT_REFRESH_INTERVAL)
        subscribers: Dict[str, Dict[str, Any]] = config.get("subscribers", {})
        if not subscribers:
            logger.warning("No subscribers registered. Use 'agent-daemon register' first.")
            if args.once:
                return
            time.sleep(refresh)
            continue
        with AgentApiClient(api_base) as client:
            for subscriber in subscribers.values():
                process_subscriber(client, subscriber, args.limit)
        if args.once:
            break
        time.sleep(refresh)


def process_subscriber(client: AgentApiClient, subscriber: Dict[str, Any], limit: int) -> None:
    subscriber_id = subscriber["subscriber_id"]
    statuses = subscriber.get("status_filter") or [FileStatus.PENDING.value]
    try:
        files = client.list_files(subscriber_id, statuses, limit)
    except Exception as exc:  # pragma: no cover
        logger.error("Failed to fetch files for %s: %s", subscriber_id, exc)
        return

    for file_entry in files:
        handle_file(client, subscriber, file_entry)


def handle_file(client: AgentApiClient, subscriber: Dict[str, Any], file_entry: Dict[str, Any]) -> None:
    subscriber_id = subscriber["subscriber_id"]
    directory = Path(subscriber["directory"]).expanduser()
    directory.mkdir(parents=True, exist_ok=True)
    agent_directory = directory / ".agent"
    agent_directory.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    stored_file_name = f"{file_entry['file_name']}.{timestamp}"
    target_path = agent_directory / stored_file_name

    logger.info("Delivering file %s to %s", file_entry["file_name"], target_path)
    try:
        target_path.write_text(file_entry["content"])
    except OSError as exc:
        logger.error("Failed to write file %s: %s", target_path, exc)
        client.update_file_status(file_entry["id"], FileStatus.ERRORED.value, str(exc))
        return

    client.update_file_status(file_entry["id"], FileStatus.DELIVERED.value)
    client.update_file_status(file_entry["id"], FileStatus.RUNNING.value)

    logger.info("Starting LLM CLI processing for %s", target_path.name)
    try:
        run_pi_script(directory, target_path)
    except RuntimeError as exc:
        logger.error("pi_run.sh execution failed for file %s: %s", file_entry["id"], exc)
        client.update_file_status(file_entry["id"], FileStatus.ERRORED.value, str(exc))
        return
    logger.info("LLM CLI finished processing %s", target_path.name)

    actions: List[str] = subscriber.get("actions", [])
    context = {
        "subscriber_id": subscriber_id,
        "project": subscriber.get("project"),
        "area": subscriber.get("area"),
        "file_name": file_entry["file_name"],
        "stored_file_name": stored_file_name,
    }

    try:
        for action_cmd in actions:
            logger.info("Running action '%s' for file %s", action_cmd, file_entry["id"])
            run_action(action_cmd, file_path=target_path, context=context)
    except ActionExecutionError as exc:
        logger.error("Action failed for file %s: %s", file_entry["id"], exc)
        client.update_file_status(file_entry["id"], FileStatus.ERRORED.value, str(exc))
        return

    client.update_file_status(file_entry["id"], FileStatus.COMPLETED.value)
    logger.info("Completed processing of file %s", file_entry["id"])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AgentDaemon CLI")
    parser.add_argument("--api-base", default=None, help="AgentAPI base URL")
    subparsers = parser.add_subparsers(dest="command", required=True)

    register_parser = subparsers.add_parser("register", help="Register a new project subscription")
    register_parser.add_argument("--project", required=True)
    register_parser.add_argument("--area", required=True)
    register_parser.add_argument("--directory", required=True, help="Destination directory for delivered files")
    register_parser.add_argument("--status", action="append", help="Status filter (repeatable)")
    register_parser.add_argument("--timestamp-from", dest="timestamp_from", help="ISO timestamp filter")
    register_parser.add_argument("--refresh", type=int, default=None, help="Refresh interval in seconds")
    register_parser.add_argument(
        "--action",
        action="append",
        help="Command template to execute per file (use {file} placeholder)",
    )
    register_parser.set_defaults(func=register_subscriber)

    subscribers_parser = subparsers.add_parser("subscribers", help="List registered subscribers")
    subscribers_parser.add_argument("--project", help="Filter by project")
    subscribers_parser.add_argument("--area", help="Filter by area")
    subscribers_parser.set_defaults(func=list_subscribers_command)

    files_parser = subparsers.add_parser("files", help="List published files")
    files_parser.add_argument("--project", help="Filter by project")
    files_parser.add_argument("--area", help="Filter by area")
    files_parser.add_argument("--subscriber-id", dest="subscriber_id", type=int, help="Filter by subscriber ID")
    files_parser.add_argument("--status", action="append", help="Status filter (repeatable)")
    files_parser.add_argument("--limit", type=int, default=50, help="Maximum number of files to return")
    files_parser.set_defaults(func=list_published_files_command)

    run_parser = subparsers.add_parser("run", help="Run the daemon loop")
    run_parser.add_argument("--refresh", type=int, default=None)
    run_parser.add_argument("--limit", type=int, default=25)
    run_parser.add_argument("--once", action="store_true", help="Run a single iteration")
    run_parser.set_defaults(func=run_loop)

    publish_parser = subparsers.add_parser("publish", help="Publish a file via the API")
    publish_parser.add_argument("--project", required=True)
    publish_parser.add_argument("--area", required=True)
    publish_parser.add_argument(
        "--file-name",
        help="Path to a file to upload or explicit file name to store",
    )
    publish_parser.add_argument(
        "--content",
        help="Literal text to publish or path to a file whose contents should be sent directly",
    )
    publish_parser.add_argument("--description", default=None)
    publish_parser.set_defaults(func=publish_file)

    return parser


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
