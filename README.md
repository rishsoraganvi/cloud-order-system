# Cloud-Native E-Commerce Order Processing System

A production-ready, cloud-native microservices architecture for e-commerce order processing. Built with FastAPI (Python), Spring Boot (Java), and modern DevOps practices. Designed for local development and deployment to Oracle Cloud Always Free (ARM A1).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway (nginx)                      │
│                        port 80/443                           │
└───────┬───────────────────────────────────────────────────────┘
        │
    ┌───┴─────────────────────────────────────┬──────────────┐
    ↓                                           ↓              ↓
 ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
 │ User Service │  │Product Service│  │ Order Service│  │Notification  │
 │  (FastAPI)   │  │(Spring Boot)  │  │  (FastAPI)   │  │  (Python)    │
 │  port 8001   │  │  port 8002    │  │  port 8003   │  │  port 8004   │
 └──────┬───────┘  └──────┬────────┘  └──────┬───────┘  └──────┬───────┘
        │                 │                   │                │
        ↓                 ↓                   ↓                ↓
    ┌────────┐       ┌────────┐         ┌────────┐        ┌──────────┐
    │  db1   │       │  db2   │         │  db3   │        │RabbitMQ  │
    │(user)  │       │(product)         │(order) │        │(events)  │
    │5432    │       │5433    │         │5434    │        │5672      │
    └────────┘       └────────┘         └────────┘        └──────────┘
```

## Tech Stack

| Service | Language | Framework | Database |
|---------|----------|-----------|----------|
| User | Python 3.11 | FastAPI | PostgreSQL 15 |
| Product | Java 17 | Spring Boot 3 | PostgreSQL 15 |
| Order | Python 3.11 | FastAPI | PostgreSQL 15 |
| Notification | Python 3.11 | async worker | RabbitMQ 3 |
| API Gateway | Nginx | reverse proxy | — |

## Prerequisites

- Docker & Docker Compose
- Python 3.11
- Java 17 (Temurin)
- Git

## Quick Start

1. Clone the repo:

```bash
git clone <repo-url>
cd "Cloud-Native E-Commerce Order Processing System"
```

2. Copy environment config:

```bash
cp .env.example .env
# Edit .env to fill placeholder values (optional for local dev)
```

3. Start all services with Docker Compose:

```bash
docker compose up --build
```

4. Verify services are running:

```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
```

## Project Structure

- `services/user-service/` — FastAPI user service (authentication, profiles, JWT)
- `services/product-service/` — Spring Boot product service (catalog, stock reservation)
- `services/order-service/` — FastAPI order service (state machine, order placement)
- `services/notification-service/` — Python notification worker (async events)
- `gateway/` — Nginx API gateway configuration
- `docs/` — project documentation
- `.github/workflows/` — CI/CD pipeline (GitHub Actions)

## Running Tests

**Python services** (from repo root):

```bash
pytest services/user-service/tests/ -v
pytest services/order-service/tests/ -v
pytest services/notification-service/tests/ -v
```

**Java service**:

```bash
cd services/product-service && mvn test -q
```

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci-cd.yml`) runs on every push:

1. **Lint** — flake8 (Python style checks)
2. **Test** — pytest (Python) and mvn test (Java)
3. **Build & Push** — Docker images tagged with commit SHA and pushed to Oracle Cloud Container Registry (OCIR)
4. **Deploy** (optional) — SSH to Always Free host and pull latest images

See `docs/ci-cd-setup.md` for GitHub Secrets configuration and deployment setup.

## Design Decisions

- **Database-per-Service:** Each microservice owns its data; no cross-service queries. Ensures loose coupling, independent scaling, and schema evolution.

- **Nginx API Gateway:** Lightweight, production-proven reverse proxy with built-in rate limiting and TLS termination.

- **RabbitMQ for Events:** Decouples Order Service from Notification Service. Adding email, Slack, or SMS alerts requires zero changes to order processing logic.

- **State Machine for Orders:** Enforces valid transitions (pending → reserved → shipped → delivered). Prevents bugs like shipping a cancelled order.

- **JWT-Based Auth:** Stateless, scalable authentication without inter-service calls on every request.

## Design Patterns Used

- **Repository Pattern** — Data access layer abstraction (User, Product, Order services)
- **Factory Pattern** — Notification Service creates different notifier implementations (email, webhook, etc.)
- **Observer/Event-Driven** — Order events trigger notifications asynchronously via RabbitMQ
- **Strategy Pattern** — Product filtering and sorting logic (pluggable strategies)
- **State Machine** — Order lifecycle transitions with validation

## Deployment

### Local Development

```bash
docker compose up --build
```

See `startup_guide.md` for detailed local setup and troubleshooting.

### Oracle Always Free (ARM A1)

One-command deployment to your Always Free host:

```bash
./deploy.sh
```

Requires `.env` with `DEPLOY_HOST` and `DEPLOY_SSH_USER` set. See `.env.example` for details.

## What's Next

- **Kubernetes** — Helm charts for multi-node deployments
- **Distributed Tracing** — OpenTelemetry + Jaeger for observability
- **Resilience** — Circuit breakers (Resilience4j, tenacity) and retries
- **Architecture Decision Records (ADR)** — Document design choices and trade-offs
- **Load Testing** — k6 or Locust for performance validation
- **Monitoring & Alerts** — Prometheus + Grafana + PagerDuty integration

## Resources

- `startup_guide.md` — Local setup and troubleshooting
- `docs/architecture.md` — Architecture details and deployment notes
- `docs/ci-cd-setup.md` — GitHub Actions and OCIR configuration
- `.planning/` — Project phases, requirements, and roadmap
- `full_build_plan.md` — Complete phase breakdown (0–9)
