# prompter
Provides instruction stream and interconnecting API to AI agents.

## Server configuration

The Express server now proxies all persistence calls to the FastAPI-based AgentAPI. Configure it via the following environment variables:

- `AGENT_API_BASE` – Base URL for the AgentAPI (default: `http://localhost:5333`).
- `PROMPTER_PROJECT` – Default project name used when clients omit one (default: `default`).

## Client configuration

The Vite-powered Prompter UI now talks directly to the FastAPI AgentAPI for reading/writing instruction documents. Customize it with these environment variables (set via `.env` or the shell before running `npm run dev`/`build` in `client/`):

- `VITE_AGENT_API_BASE` – Base URL (or relative path) to the AgentAPI. Defaults to `http://localhost:5333`.
- `VITE_PROMPTER_PROJECT` / `VITE_PROJECT_NAME` – Optional overrides for the default project shown when no `?project=` query string is provided (defaults to `default`).
