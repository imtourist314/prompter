# Prompt Agent

This repository implements two cooperating components:

1. **AgentAPI** – a FastAPI service (port 5333) that stores subscriber registrations and subscription files in a PostgreSQL database.
2. **AgentDaemon** – a long-running Python client that registers projects, polls the API for matching files, delivers them to local directories, triggers follow-up actions, and reports status transitions.

## Project layout

```
agent_api/           FastAPI service source
agent_daemon/        Daemon/client implementation
pyproject.toml       Project metadata & dependencies
prompt_agent.md      Original specification
```

## Prerequisites

- Python 3.10+
- PostgreSQL database (optional for local dev; SQLite URL works for testing)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Configure environment (see `.env.example`) with your database URL.

## Running AgentAPI

```bash
export DATABASE_URL="postgresql+psycopg://user:pass@localhost:5432/agent"
uvicorn agent_api.main:app --host 0.0.0.0 --port 5333 --reload
```

## Running AgentDaemon

Register a project:

```bash
agent-daemon register \
  --project ACME_Widgets \
  --area front-end \
  --directory /data/example/project1 \
  --api-base http://localhost:5333
```

Start the daemon loop:

```bash
agent-daemon run --api-base http://localhost:5333
```

Inspect configured subscribers (optionally filter by project/area):

```bash
agent-daemon subscribers --api-base http://localhost:5333
```

List published files with optional filters (project, area, subscriber, status, limit):

```bash
agent-daemon files --status COMPLETED --limit 10 --api-base http://localhost:5333
```

Publish a file for testing:

```bash
curl -X POST http://localhost:5333/files \
  -H 'Content-Type: application/json' \
  -d '{
    "file_name":"spec.md",
    "project":"ACME_Widgets",
    "area":"front-end",
    "description":"Updated spec",
    "content":"## Notes\n..."
  }'
```

You can also publish via the daemon CLI. Provide either a local file (and let the daemon read its contents) or inline
text:

```bash
# publish the contents of ./spec.md (no need to repeat the content argument)
agent-daemon publish \
  --project ACME_Widgets \
  --area front-end \
  --file-name ./spec.md

# publish inline text; omit --file-name to auto-generate a timestamped name
agent-daemon publish \
  --project ACME_Widgets \
  --area front-end \
  --content "## Release notes\n..."
```

## API surface (AgentAPI)

| Method & Path | Description |
|---------------|-------------|
| `GET /health` | Service heartbeat |
| `POST /subscribers` | Register a subscriber (project, area, filters, directory) |
| `GET /subscribers` | List subscribers, optional `project`/`area` filters |
| `GET /subscribers/{id}` | Retrieve a single subscriber |
| `GET /subscribers/{id}/files?status=PENDING&limit=25` | Fetch matching files (defaults to subscriber's status filter) |
| `GET /files?project=...&status=...` | List published files with optional project/area/subscriber/status filters |
| `POST /files` | Publish a new file (distributed to all matching subscribers) |
| `PATCH /files/{id}/status` | Advance a file through the lifecycle |

All timestamps are UTC ISO-8601 strings. The database URL comes from `DATABASE_URL` (see `.env.example`).

## AgentDaemon configuration

- Default config path: `~/.agent_daemon/config.json` (override via `AGENT_DAEMON_HOME`).
- Stored keys:
  ```json
  {
    "api_base": "http://localhost:5333",
    "refresh_interval": 60,
    "subscribers": {
      "<subscriber_id>": {
        "subscriber_id": "...",
        "project": "ACME_Widgets",
        "area": "front-end",
        "directory": "/data/example/project1",
        "status_filter": ["PENDING"],
        "actions": ["pi_run.sh gpt-4o {file}"]
      }
    }
  }
  ```
- Actions are shell command templates. Each receives a `{file}` placeholder plus `{project}`, `{area}`, `{subscriber_id}`, and `{file_name}` in the template context.

## Status lifecycle

`PENDING -> DELIVERED -> RUNNING -> COMPLETED | ERRORED`

`agent-daemon` enforces this sequence for every downloaded file and reports failures back to the API.

## Tests / linting

(Not yet implemented.)
