# ProjectFlow – Project Management Backend

A production-oriented project management backend built with **FastAPI, PostgreSQL, SQLAlchemy, Redis, and WebSockets**.

ProjectFlow provides project and task management, JWT authentication, role-based access control, persistent notifications, and real-time communication.

## Tech Stack

- **Backend:** Python, FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Authentication:** JWT, Argon2 password hashing
- **Caching & Messaging:** Redis, Redis Pub/Sub
- **Real-time Communication:** WebSockets
- **Validation:** Pydantic
- **Testing:** Pytest
- **Infrastructure:** Docker, Docker Compose

## Features Implemented

### 1. Authentication & Authorization
- User registration and login.
- JWT-based authentication.
- Secure password hashing with Argon2.
- Protected API endpoints.
- Role-based access control for project members.

### 2. Project Management
- Create and manage projects.
- Add and manage project members.
- Project-level role permissions.
- User-specific project access.

### 3. Task Management
- Create, retrieve, update, and delete tasks.
- Assign tasks to users.
- Associate tasks with projects.
- Trigger notifications for relevant task events.

### 4. Real-time Communication
- Project-specific WebSocket connections.
- Redis Pub/Sub for cross-instance event delivery.
- Support for multiple application instances.
- User-specific notification WebSockets.

### 5. Notification System
- Persistent notifications stored in PostgreSQL.
- User-specific notification delivery.
- Retrieve notifications with pagination.
- Read/unread notification management.
- Mark individual or all notifications as read.
- Delete notifications.
- Redis-based real-time notification publishing.

### 6. Production Readiness
- Health, database, and readiness endpoints.
- Centralized exception handling.
- Standardized API error responses.
- Structured application logging.
- HTTP request logging with execution time.
- Configurable CORS.
- HTTP security headers.
- Redis-backed rate limiting for authentication endpoints.

### 7.Request ID and correlation ID tracing
- Request ID generation and propagation using UUIDs.
- Context-aware logging with Python ContextVars.
- `X-Request-ID` response headers for request tracing.
- Support for valid client-provided request IDs.

### 8. API Pagination

- Introduced a reusable generic `PaginatedResponse` schema using Pydantic.
- Added pagination metadata to project and task listing endpoints:
  - `items`
  - `total`
  - `skip`
  - `limit`
  - `has_more`
- Added total-count queries while preserving existing project ownership and task filtering.
- Added typed validation for task status, priority, and assignee query parameters.
- Updated project and task API tests for paginated responses.

### Pagination and Filtering

- Introduced a reusable generic `PaginatedResponse` schema.
- Standardized pagination metadata across Projects, Tasks, and Notifications.
- Added `skip`, `limit`, `total`, and `has_more` fields to paginated responses.
- Added task filtering by status, priority, and assignee.
- Preserved project ownership and task access-control checks.
- Added pagination and filtering test coverage.

## Architecture

ProjectFlow follows a **layered modular monolith architecture**, separating API handling, business logic, data access, and infrastructure.

```text
Client Applications
       |
       v
   FastAPI API
       |
       v
   API Routes
       |
       v
   Services Layer
   (Business Logic)
       |
       v
 Repositories Layer
   (Data Access)
       |
       v
  SQLAlchemy ORM
       |
       v
    PostgreSQL


Infrastructure:
  Redis
   |-- Rate Limiting
   |-- Pub/Sub Messaging
   |-- WebSocket Event Delivery

  WebSockets
   |-- Project Updates
   |-- User Notifications
```

## Project Structure

```text
FAST_API/
│
├── alembic/                  # Database migrations
│
├── app/
│   ├── api/
│   │   └── routes/           # API and WebSocket routes
│   │
│   ├── core/                 # Configuration, security,
│   │                         # logging, middleware, exceptions
│   │
│   ├── db/                   # Database and Redis connections
│   │
│   ├── models/               # SQLAlchemy models
│   │
│   ├── repositories/         # Database operations
│   │
│   ├── schemas/              # Pydantic schemas
│   │
│   └── services/             # Business logic and event handling
│
├── tests/
│   ├── api/
│   └── websockets/
│
├── scripts/
├── docker-compose.yml
├── alembic.ini
└── README.md
```

## Running Locally

### 1. Start infrastructure

```bash
docker compose up -d
```

This starts the configured PostgreSQL and Redis services.

### 2. Activate the virtual environment

```bash
source venv/bin/activate
```

### 3. Configure environment variables

Create a `.env` file containing the database URL, test database URL, JWT secret, Redis URL, and application configuration.

Never commit `.env` or production secrets.

### 4. Run database migrations

```bash
alembic upgrade head
```

### 5. Start the application

```bash
python -m uvicorn app.main:app --reload
```

API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Running Tests

```bash
pytest -v
```

The test suite uses a dedicated PostgreSQL test database. Ensure `TEST_DATABASE_URL` points to that database before running tests.

## Development Roadmap

- [x] FastAPI project foundation
- [x] PostgreSQL and SQLAlchemy integration
- [x] Alembic database migrations
- [x] User authentication and JWT
- [x] Project and task management
- [x] Project membership and RBAC
- [x] Project WebSockets
- [x] Automated API and WebSocket tests
- [x] Redis Pub/Sub integration
- [x] Persistent notifications
- [x] Real-time notification delivery
- [x] Centralized exception handling
- [x] Structured logging
- [x] CORS and security headers
- [x] Redis-backed authentication rate limiting
- [x] Request ID and correlation ID tracing
- [ ] Remaining production hardening
- [ ] React frontend integration

---

**Project:** ProjectFlow  
**Status:** Backend development – Production readiness  
**Architecture:** Layered Modular Monolith