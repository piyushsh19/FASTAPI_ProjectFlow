# ProjectFlow – Project Management Backend

A production-oriented project management backend built with **FastAPI, PostgreSQL, SQLAlchemy, Redis, and WebSockets**.

ProjectFlow provides project and task management, JWT authentication, role-based access control, persistent notifications, and real-time communication.

## Tech Stack

| Category | Technology |
|---|---|
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Authentication | JWT, Argon2 |
| Caching & Messaging | Redis, Redis Pub/Sub |
| Real-time Communication | WebSockets |
| Validation | Pydantic |
| Configuration | Pydantic Settings |
| Testing | Pytest |
| Infrastructure | Docker, Docker Compose |

## Features Implemented

### 1. Authentication and Authorization

- User registration and login.
- JWT-based authentication.
- Secure password hashing with Argon2.
- Protected API endpoints.
- Centralized JWT creation and validation.
- Required JWT claims validation (`sub` and `exp`).
- JWT signature and expiration verification.
- Rejection of malformed tokens and invalid user identifiers.
- Rejection of tokens associated with nonexistent users.
- Unified JWT validation across HTTP and WebSocket authentication.
- Password validation with minimum and maximum length restrictions.
- Protection against authentication user-enumeration timing differences.

### 2. Project Management

- Create, retrieve, update, and delete projects.
- Project ownership management.
- Add and manage project members.
- Project-level role-based access control.
- Shared project access for authorized members.
- Project listing with pagination and sorting.
- Authorization checks for project operations.

### 3. Role-Based Access Control (RBAC)

ProjectFlow supports four project roles:

| Permission | Owner | Admin | Member | Viewer |
|---|---|---|---|---|
| View project | Yes | Yes | Yes | Yes |
| Create tasks | Yes | Yes | Yes | No |
| Update tasks | Yes | Yes | Yes | No |
| Delete tasks | Yes | Yes | No | No |
| Manage members | Yes | Yes | No | No |
| Update project details | Yes | Yes | No | No |
| Delete project | Yes | No | No | No |

Additional authorization rules:

- Project owners have full administrative control.
- Admins can manage ordinary project members and viewers.
- Only owners can grant or revoke admin privileges.
- Admins cannot modify or remove other admins.
- Admins cannot change their own role.
- Only project owners can delete projects.
- Project members can view the project member list.

### 4. Task Management

- Create, retrieve, update, and delete tasks.
- Assign tasks to users.
- Associate tasks with projects.
- Task status and priority management.
- Filter tasks by status, priority, and assignee.
- Paginated task listing.
- Configurable task sorting.
- Project membership and authorization checks.
- Notifications for relevant task events.

### 5. Real-time Communication

- Project-specific WebSocket connections.
- User-specific notification WebSockets.
- Redis Pub/Sub for cross-instance event delivery.
- Support for multiple application instances.
- Real-time project event delivery.
- Real-time notification delivery.

### 6. Notification System

- Persistent notifications stored in PostgreSQL.
- User-specific notification delivery.
- Retrieve notifications with pagination.
- Read/unread notification management.
- Mark individual notifications as read.
- Mark all notifications as read.
- Delete notifications.
- Redis-based real-time notification publishing.

### 7. Production Readiness and API Security

- Health, database, and readiness endpoints.
- Centralized exception handling.
- Standardized API error responses.
- Structured application logging.
- HTTP request logging with execution time.
- Configurable CORS.
- HTTP security headers.
- Redis-backed authentication rate limiting.
- Request ID generation and propagation.
- Context-aware logging using Python ContextVars.
- `X-Request-ID` response headers.
- Support for valid client-provided request IDs.

### 8. API Pagination and Filtering

- Reusable generic `PaginatedResponse` schema using Pydantic.
- Standardized pagination across Projects, Tasks, and Notifications.
- Pagination metadata:
  - `items`
  - `total`
  - `skip`
  - `limit`
  - `has_more`
- Database-level total-count queries.
- Task filtering by status, priority, and assignee.
- Typed validation for query parameters.
- Preserved project ownership and task access-control checks.
- Automated pagination and filtering tests.

### 9. API Sorting

**Project sorting**

Supported fields:
- `created_at`
- `updated_at`
- `name`

**Task sorting**

Supported fields:
- `created_at`
- `updated_at`
- `title`
- `priority`
- `due_date`

Additional capabilities:

- Ascending (`asc`) and descending (`desc`) sorting.
- Query parameter validation using allowed values and Literal types.
- Database-level sorting using SQLAlchemy.
- Deterministic secondary sorting by record ID.
- Preserved filtering, pagination, and authorization behavior.

### 10. Database Indexing

- Composite indexes for frequently queried project, task, and notification data.
- Optimized project listing by owner and creation date.
- Optimized task listing and filtering.
- Optimized notification listing and unread notification queries.
- Foreign-key lookup indexes.
- Removed redundant standalone indexes replaced by composite indexes.
- Reversible Alembic migrations for schema changes.

### 11. Database Constraints and Referential Integrity

- PostgreSQL CHECK constraints for project statuses.
- CHECK constraints for task statuses and priorities.
- CHECK constraints for project member roles.
- Valid values enforced at the database level.
- Foreign-key relationships and deletion rules.
- Unique project membership constraints.
- Reversible Alembic migrations.
- Database schema consistency verification using `alembic check`.

### 12. Configuration and Environment Management

- Centralized application configuration using Pydantic Settings.
- Environment validation for development, testing, and production.
- Production safeguards for debug mode and JWT secret strength.
- Logging-level validation.
- CORS origin validation.
- `.env.example` configuration template.
- Pinned dependencies in `requirements.txt`.
- Externalized PostgreSQL Docker credentials.
- Application secrets excluded from version control.
- Automated configuration validation tests.

## Architecture

ProjectFlow follows a **Layered Modular Monolith Architecture**, separating API handling, business logic, data access, and infrastructure.

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
                   SQLAlchemy
                        |
                        v
                    PostgreSQL


Infrastructure:

    Redis
      |
      |-- Rate Limiting
      |
      |-- Pub/Sub Messaging
      |
      |-- WebSocket Event Delivery


    WebSockets
      |
      |-- Project Updates
      |
      |-- User Notifications
```

### Architecture Responsibilities

| Layer | Responsibility |
|---|---|
| API Routes | HTTP endpoints and WebSocket connections |
| Schemas | Request and response validation |
| Services | Business logic and authorization |
| Repositories | Database operations |
| Models | SQLAlchemy database models |
| Core | Configuration, security, logging, middleware |
| Database | PostgreSQL and Redis connections |

## Project Structure

```text
FAST_API/
│
├── alembic/
│   └── versions/                 # Database migrations
│
├── app/
│   ├── api/
│   │   └── routes/               # API and WebSocket routes
│   │
│   ├── core/                     # Configuration, security,
│   │                             # logging, middleware, exceptions
│   │
│   ├── db/                       # Database and Redis connections
│   │
│   ├── models/                   # SQLAlchemy models
│   │
│   ├── repositories/             # Database operations
│   │
│   ├── schemas/                  # Pydantic schemas
│   │
│   └── services/                 # Business logic and event handling
│
├── tests/
│   ├── api/
│   └── websockets/
│
├── scripts/
│
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
├── .env.example
└── README.md
```

## Running Locally

### Prerequisites

- Python 3.12+
- Docker
- Docker Compose
- Git

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd FAST_API
```

### 2. Create and activate a virtual environment

```bash
python3.12 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Start infrastructure

```bash
docker compose up -d
```

This starts the configured PostgreSQL and Redis services.

### 5. Configure environment variables

Create a `.env` file using `.env.example` as a reference.

Configure the required values, including:

- Database URL
- Test database URL
- JWT secret
- Redis URL
- Application environment
- Logging configuration
- CORS origins

Never commit `.env` or production secrets.

### 6. Run database migrations

```bash
alembic upgrade head
```

### 7. Start the application

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

### API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc


## Running with Docker

ProjectFlow can run as a complete Docker Compose application with three services:

- **API:** FastAPI application running on port `8000`.
- **PostgreSQL:** Database running on port `5433` on the host.
- **Redis:** Cache and messaging service running on port `6379` on the host.

### Prerequisites

- Docker Desktop
- Docker Compose

### 1. Configure environment variables

Create your `.env` file:

```bash
cp .env.example .env
```

Configure the required environment variables:

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `DATABASE_URL_DOCKER`
- `SECRET_KEY`
- `DATABASE_URL`
- `TEST_DATABASE_URL`

Use the Docker service name `postgres` in `DATABASE_URL_DOCKER`:

```env
DATABASE_URL_DOCKER=postgresql+psycopg://projectflow_user:your_password@postgres:5432/projectflow_db
```

Ensure the password in the database URL matches `POSTGRES_PASSWORD`. URL-encode special characters in the URL password.

Never commit `.env` or production secrets.

### 2. Build and start services

Build the API image:

```bash
docker compose build api
```

Start PostgreSQL and Redis:

```bash
docker compose up -d postgres redis
```

Start the API:

```bash
docker compose up -d api
```

Alternatively, start all services together:

```bash
docker compose up -d --build
```

### 3. Run database migrations

Apply Alembic migrations:

```bash
docker compose run --rm api alembic upgrade head
```

### 4. Verify service health

Check container status:

```bash
docker compose ps
```

Check API readiness:

```bash
curl http://localhost:8000/health/ready
```

The readiness endpoint verifies PostgreSQL and Redis connectivity.

### 5. Access API documentation

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 6. View application logs

```bash
docker compose logs -f api
```

View all service logs:

```bash
docker compose logs -f
```

### 7. Stop services

Stop containers without deleting persistent database data:

```bash
docker compose down
```

Start them again:

```bash
docker compose up -d
```

**Important:** Avoid `docker compose down -v` unless you intentionally want to delete the persistent PostgreSQL and Redis volumes.


## Running Tests

Ensure PostgreSQL and Redis are running and `TEST_DATABASE_URL` points to the dedicated test database.

Run the complete test suite:

```bash
pytest -v
```

Or:

```bash
pytest -q
```

Run individual test modules:

```bash
pytest -q tests/api/test_projects.py
pytest -q tests/api/test_tasks.py
pytest -q tests/api/test_members.py
pytest -q tests/api/test_rbac.py
```

## Development Roadmap

### Completed

- [x] FastAPI project foundation
- [x] PostgreSQL and SQLAlchemy integration
- [x] Alembic database migrations
- [x] User authentication and JWT
- [x] Project and task management
- [x] Project membership and RBAC foundation
- [x] Project WebSockets
- [x] Automated API and WebSocket tests
- [x] Redis Pub/Sub integration
- [x] Persistent notifications
- [x] Real-time notification delivery
- [x] Health and readiness endpoints
- [x] Centralized exception handling
- [x] Structured logging
- [x] CORS and security headers
- [x] Redis-backed authentication rate limiting
- [x] Request ID and correlation ID tracing
- [x] Pagination and filtering
- [x] Configurable project and task sorting
- [x] Database indexing
- [x] Database constraints
- [x] Configuration and environment management
- [x] JWT authentication hardening
- [x] Password security and validation
- [x] Project and member RBAC authorization


### Phase 11: Production Readiness

- [x] Task-level authorization audit
- [x] WebSocket authorization audit
- [x] RBAC regression tests
- [x] Production Docker setup
- [x] Multi-stage Docker build
- [x] Non-root API container
- [x] Production and development dependency separation
- [x] Docker Compose integration for PostgreSQL, Redis, and FastAPI
- [x] Container health checks
- [x] Database readiness verification
- [x] Docker restart and database persistence verification
- [ ] Logging and observability review
- [ ] Integration testing
- [ ] OpenAPI documentation review
- [ ] Final production-readiness review


### Upcoming

- [ ] React frontend integration
- [ ] Frontend and backend integration
- [ ] Deployment and production infrastructure

---

## Project Information

**Project:** ProjectFlow

**Status:** Backend development – Production readiness

**Architecture:** Layered Modular Monolith

**Backend:** FastAPI

**Database:** PostgreSQL

**Messaging:** Redis and Redis Pub/Sub

**Real-time Communication:** WebSockets

**Testing:** Pytest
