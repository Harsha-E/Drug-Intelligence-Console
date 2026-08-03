# Deployment Guide

This guide covers deploying the Clinical Intelligence Command Center.

## Docker Deployment

The system is fully containerized. A multi-stage Dockerfile is provided in the repository root.

```bash
# Build the image
docker build -t dic-command-center:latest .

# Run the container
docker run -p 8000:8000 dic-command-center:latest
```

## GitHub Actions

A CI/CD workflow is located in `.github/workflows/deploy.yml`. It runs automatically on push and pull requests to `main`, validating the build and running basic pytest sanity checks.

## Health and Metrics

- **Health Check**: `GET /api/v1/history` serves as an implicit health check ensuring the API is responsive.
- **Metrics**: The Command Center UI automatically calculates and displays execution latency, total completed analyses, and registry versions on the "Overview" or "Live Requests" dashboard.

## API Key Management

The Command Center UI includes an API Keys module. 
**Important**: The UI does NOT invent API key capabilities. It pings the backend `OPTIONS /api/v1/auth/keys`. If the backend does not implement this endpoint, the UI will degrade gracefully into a "Backend Not Available" state.
