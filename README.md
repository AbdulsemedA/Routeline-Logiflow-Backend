# Routeline-Logiflow-Backend

This is the production-ready logistics and dispatch system backend utilizing Django, PostGIS, DRF, Celery, and Channels. It provides a seamless integration with the existing `logiflow-dash` frontend!

## Prerequisites
- Docker & Docker Compose
- Poetry

## Running the Application

1. Build and run the entire stack (PostGIS + Redis + Django Webhook Server + Celery Background Worker):
```bash
docker compose up --build
```
This automatically spins up your database, applies migrations with the generated Django models, and launches Daphne serving ASGI WebSockets and HTTP APIs matching the exact schema requirements on `:8000`.

2. To interact with it natively:
```bash
poetry install
poetry run python manage.py runserver
```

## Features Complete
- **Accounts:** Custom User models and JWT role-based authentication.
- **Drivers:** Robust Driver geospatial schemas using PostGIS arrays and model views matching the frontend.
- **Deliveries API**: CRUD systems for dropoff and pickup geo fields mapping directly to frontend shapes.
- **Dispatch Engine**: Celery tasks finding nearest drivers using spatial index arrays.
- **Realtime**: Django Channels consumers dispatching WS updates natively to the mock Socket endpoints.
