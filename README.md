# Drug Intelligence Cloud

The central repository for the Drug Intelligence Cloud backend and frontend Command Center.

## Architecture

- `backend/api`: FastAPI application serving the API.
- `backend/core`: The core inference and reasoning engine.
- `backend/registry`: The compiled drug registry and clinical knowledge graph.
- `frontend/console`: The frontend Command Center dashboard for observing inference records and analytics.
- `ingestion`: Providers and tools to fetch and validate raw source data offline.
- `tests`: Regression suite and end-to-end tests.

## Running Locally

```bash
docker-compose up --build
```
Or with python:
```bash
python backend/main.py
```
