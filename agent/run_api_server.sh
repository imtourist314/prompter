source .venv/bin/activate

uvicorn agent_api.main:app --host 0.0.0.0 --port 5333 --reload
