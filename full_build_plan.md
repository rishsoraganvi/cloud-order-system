# Full Build Plan: Cloud-Native E-Commerce Order Processing System
### Microservices Architecture | Python (FastAPI) + Java (Spring Boot) | AWS | CI/CD

---

## What Changed (No Go)

Go has been replaced entirely. The API Gateway now uses **nginx** (config-only, no coding required) and the Product Service moves to **Java (Spring Boot)**. You get full language versatility — Python and Java — both listed explicitly in the JD.

---

## Final Architecture

```
                        ┌─────────────┐
           Client ────► │  API Gateway │  (nginx — routing + rate limiting)
                        └──────┬──────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
   ┌──────▼──────┐    ┌────────▼───────┐   ┌───────▼──────┐
   │ User Service│    │ Product Service│   │ Order Service │
   │  (FastAPI)  │    │ (Spring Boot)  │   │  (FastAPI)    │
   └──────┬──────┘    └────────┬───────┘   └───────┬──────┘
          │                    │                    │
   ┌──────▼──────┐      ┌──────▼──────┐     ┌──────▼──────┐
   │  PostgreSQL │      │  PostgreSQL │     │  PostgreSQL  │
   └─────────────┘      └─────────────┘     └──────┬──────┘
                                                    │ publishes event
                                            ┌───────▼──────────┐
                                            │Notification Service│
                                            │    (FastAPI)       │
                                            └────────────────────┘
```

Each service has its **own database** (Database-per-Service pattern). Services communicate over HTTP REST. The Order Service publishes events to a shared message queue (RabbitMQ) that the Notification Service consumes.

---

## Services at a Glance

| Service | Language / Framework | Database | Port |
|---|---|---|---|
| API Gateway | nginx (config only) | — | 80 |
| User Service | Python 3.11 + FastAPI | PostgreSQL | 8001 |
| Product Service | Java 17 + Spring Boot 3 | PostgreSQL | 8002 |
| Order Service | Python 3.11 + FastAPI | PostgreSQL | 8003 |
| Notification Service | Python 3.11 + FastAPI | — (stateless) | 8004 |
| Message Broker | RabbitMQ | — | 5672 |

---

## Tech Stack — Mapped to JD Requirements

| JD Requirement | Implementation |
|---|---|
| Cloud-native apps & microservices | 4 independent services, each in its own container |
| Python | FastAPI for User, Order, Notification services |
| Java | Spring Boot 3 for Product Service |
| AWS / GCP / Azure | Deploy via AWS ECS (Fargate) — free tier eligible |
| RESTful APIs | All services expose REST endpoints |
| DevOps / CI-CD | GitHub Actions: lint → test → Docker build → push to ECR → deploy |
| DSA | Order state machine (graph), token bucket rate limiter in gateway config |
| Design Patterns | Repository, Factory, Observer, Strategy |
| SOLID principles | Interface-first design, SRP per service, DI throughout |

---

---

# PHASE-BY-PHASE BUILD PLAN

---

## Phase 0 — Setup & Scaffolding
**Duration: 2–3 days**

### Goals
- Dev environment ready
- Repo structure created
- Docker + Docker Compose working locally

### Step-by-Step

**1. Install prerequisites**
```
- Docker Desktop
- Python 3.11 + pip + virtualenv
- Java 17 + Maven (or Gradle)
- VS Code (with Python + Java extensions)
- Git
```

**2. Create GitHub repo**
```
cloud-order-system/
├── services/
│   ├── user-service/
│   ├── product-service/
│   ├── order-service/
│   └── notification-service/
├── gateway/
│   └── nginx.conf
├── docker-compose.yml
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── docs/
│   └── architecture.md
└── README.md
```

**3. Bootstrap each Python service**
```bash
cd services/user-service
python -m venv venv
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose pydantic
```

**4. Bootstrap Java (Product) service**
```bash
# Use Spring Initializr (start.spring.io)
# Dependencies: Spring Web, Spring Data JPA, PostgreSQL Driver, Lombok, Validation
```

**5. Write root docker-compose.yml** — spin up all 4 services + 4 PostgreSQL DBs + RabbitMQ together locally.

---

## Phase 1 — User Service (FastAPI + PostgreSQL)
**Duration: 3–4 days**

### What to Build
- `POST /users/register` — create account, hash password (bcrypt)
- `POST /users/login` — return JWT token
- `GET /users/me` — return profile (auth required)

### Key Files
```
user-service/
├── app/
│   ├── main.py            # FastAPI app entry point
│   ├── models.py          # SQLAlchemy ORM model (User table)
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── repository.py      # DB access layer (Repository Pattern)
│   ├── service.py         # Business logic (hash password, generate JWT)
│   └── router.py          # Route definitions
├── tests/
│   └── test_users.py
├── Dockerfile
└── requirements.txt
```

### Design Patterns Applied
- **Repository Pattern**: `repository.py` is the only file that touches the DB. Service layer calls the repository, not SQLAlchemy directly. This means you can swap PostgreSQL for DynamoDB by only changing `repository.py`.
- **SOLID — SRP**: `service.py` does business logic. `repository.py` does persistence. `router.py` does HTTP. No file does two jobs.
- **SOLID — DI**: Repository is injected into the service via constructor — not imported directly.

### Dockerfile (multi-stage)
```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Tests to Write
- Register a new user → expect 201
- Login with correct credentials → expect JWT in response
- Login with wrong password → expect 401
- Access `/me` without token → expect 403

---

## Phase 2 — Product Service (Java Spring Boot)
**Duration: 4–5 days**

### What to Build
- `GET /products` — paginated product list
- `GET /products/{id}` — single product detail
- `POST /products` — add product (admin only — skip auth, just add a role field)
- `PUT /products/{id}/reserve` — decrement stock (called by Order Service)

### Key Files
```
product-service/
├── src/main/java/com/store/product/
│   ├── ProductServiceApplication.java
│   ├── controller/
│   │   └── ProductController.java     # REST endpoints
│   ├── service/
│   │   └── ProductService.java        # Business logic interface + impl
│   ├── repository/
│   │   └── ProductRepository.java     # JPA Repository
│   ├── model/
│   │   └── Product.java               # JPA Entity
│   └── dto/
│       ├── ProductRequest.java
│       └── ProductResponse.java
├── src/test/
│   └── ProductServiceTest.java
└── Dockerfile
```

### Design Patterns Applied
- **Repository Pattern**: Spring Data JPA gives you this almost for free — `ProductRepository extends JpaRepository`. The controller never touches the DB directly.
- **SOLID — Interface Segregation**: `ProductService` is an interface. `ProductServiceImpl` implements it. The controller depends on the interface, not the implementation.
- **SOLID — DI**: Spring's `@Autowired` / constructor injection throughout. No `new` keyword for dependencies.
- **Strategy Pattern (bonus)**: If you add filtering (by price range, category), implement each filter as a `Specification` — clean and swappable.

### Dockerfile (multi-stage)
```dockerfile
FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn package -DskipTests

FROM eclipse-temurin:17-jre-slim
WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar
EXPOSE 8002
ENTRYPOINT ["java", "-jar", "app.jar"]
```

### Tests to Write
- Get paginated product list → expect correct page size
- Reserve stock for valid product → expect stock decremented
- Reserve stock when quantity = 0 → expect 409 Conflict

---

## Phase 3 — Order Service (FastAPI + PostgreSQL)
**Duration: 4–5 days**

### What to Build
- `POST /orders` — place an order (calls Product Service to reserve stock, then saves order)
- `GET /orders/{id}` — get order status
- `PATCH /orders/{id}/status` — update status (PENDING → CONFIRMED → SHIPPED → DELIVERED)
- Publish event to RabbitMQ when order is placed

### Order State Machine (DSA Angle)
```
PENDING ──► CONFIRMED ──► SHIPPED ──► DELIVERED
   │
   └──► CANCELLED
```
Implement this as a dict-based state transition graph:
```python
VALID_TRANSITIONS = {
    "PENDING":    ["CONFIRMED", "CANCELLED"],
    "CONFIRMED":  ["SHIPPED"],
    "SHIPPED":    ["DELIVERED"],
    "DELIVERED":  [],
    "CANCELLED":  [],
}
```
Invalid transitions raise a `400 Bad Request`. This is a **real DSA concept** (state machine / directed graph) applied practically — mention it explicitly in your README and interviews.

### Key Files
```
order-service/
├── app/
│   ├── main.py
│   ├── models.py           # Order table
│   ├── schemas.py
│   ├── repository.py       # Repository Pattern
│   ├── service.py          # State machine logic, HTTP call to Product Service
│   ├── events.py           # RabbitMQ publisher (Observer Pattern)
│   └── router.py
├── tests/
└── Dockerfile
```

### Design Patterns Applied
- **Observer Pattern**: When an order is placed, `events.py` publishes a message to RabbitMQ. Notification Service subscribes and reacts. Order Service doesn't know or care what happens next — loose coupling.
- **Repository Pattern**: Same as User Service.
- **SOLID — OCP**: Adding a new order status (e.g., RETURN_REQUESTED) only requires adding it to the state transition dict — no existing code changes.

### Inter-Service Communication
```python
# In service.py — call Product Service to reserve stock
import httpx

async def reserve_stock(product_id: str, qty: int):
    async with httpx.AsyncClient() as client:
        resp = await client.put(
            f"http://product-service:8002/products/{product_id}/reserve",
            json={"quantity": qty}
        )
    if resp.status_code == 409:
        raise InsufficientStockError()
```

---

## Phase 4 — Notification Service (FastAPI, Stateless)
**Duration: 2–3 days**

### What to Build
A **consumer** that listens to RabbitMQ and sends notifications. No database needed.

- Consume `order.placed` events from RabbitMQ
- Send email via SendGrid free tier (or just log to console for demo)
- `GET /health` — health check endpoint

### Factory Pattern — The Right Way to Show It
```python
class NotificationFactory:
    @staticmethod
    def get_notifier(channel: str) -> BaseNotifier:
        if channel == "email":
            return EmailNotifier()
        elif channel == "sms":
            return SMSNotifier()
        elif channel == "webhook":
            return WebhookNotifier()
        raise ValueError(f"Unknown channel: {channel}")
```
Each notifier implements a common `BaseNotifier` interface with a `send(payload)` method. This is textbook **Factory + SOLID (OCP + LSP)** — add a new channel without touching existing code.

---

## Phase 5 — API Gateway (nginx)
**Duration: 1 day**

No coding required. Write an `nginx.conf` that:
- Routes `/api/users/*` → user-service:8001
- Routes `/api/products/*` → product-service:8002
- Routes `/api/orders/*` → order-service:8003
- Adds rate limiting (nginx `limit_req_zone` directive)
- Sets timeout configs

```nginx
upstream user_service   { server user-service:8001; }
upstream product_service { server product-service:8002; }
upstream order_service  { server order-service:8003; }

limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

server {
    listen 80;
    location /api/users/    { proxy_pass http://user_service/; }
    location /api/products/ { proxy_pass http://product_service/; }
    location /api/orders/   { proxy_pass http://order_service/; }
}
```

This demonstrates understanding of API Gateway pattern, rate limiting, and service mesh concepts — without needing to code it.

---

## Phase 6 — CI/CD Pipeline (GitHub Actions)
**Duration: 2–3 days**

### Pipeline: `.github/workflows/ci-cd.yml`

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-python-services:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with: { python-version: '3.11' }
      - name: Test User Service
        run: |
          cd services/user-service
          pip install -r requirements.txt
          pytest tests/ -v

  test-java-service:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Java
        uses: actions/setup-java@v3
        with: { java-version: '17', distribution: 'temurin' }
      - name: Test Product Service
        run: |
          cd services/product-service
          mvn test

  build-and-push:
    needs: [test-python-services, test-java-service]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-south-1
      - name: Build & push Docker images to ECR
        run: |
          aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REGISTRY
          docker build -t user-service ./services/user-service
          docker tag user-service:latest $ECR_REGISTRY/user-service:$GITHUB_SHA
          docker push $ECR_REGISTRY/user-service:$GITHUB_SHA
```

Pipeline stages: **PR → run tests** | **Merge to main → build + push to ECR → deploy to ECS**

---

## Phase 7 — Cloud Deployment (AWS Free Tier)
**Duration: 2–3 days**

### Deploy to AWS ECS (Fargate)

1. **ECR** — Push Docker images for all 4 services
2. **ECS Cluster** — Create a Fargate cluster (no servers to manage)
3. **Task Definitions** — One per service, define CPU/memory, env vars, port mappings
4. **Services** — Run each task definition as an ECS Service with desired count = 1
5. **RDS (PostgreSQL)** — Use RDS Free Tier (db.t3.micro) for databases
6. **Application Load Balancer** — Route traffic to the correct ECS service
7. **Secrets Manager** — Store DB passwords, JWT secret (never hardcode)

> **Free tier tip**: Deploy only User Service + Order Service to AWS for the demo. Run Product + Notification locally via Docker Compose. Mention in your README: "production-ready for multi-service ECS deployment."

---

## Phase 8 — Observability & Polish
**Duration: 2 days**

### Add to every service
- `GET /health` → returns `{"status": "ok", "service": "user-service"}`
- `GET /metrics` → returns basic stats (request count, uptime)
- **Structured JSON logging** everywhere:
```python
import logging, json
logging.basicConfig(format='%(message)s')
logger = logging.getLogger(__name__)
logger.info(json.dumps({"event": "order_placed", "order_id": order.id, "user_id": user_id}))
```

### AWS CloudWatch
- ECS automatically ships container logs to CloudWatch
- Create a simple dashboard: request count per service, error rate, latency

---

## Phase 9 — README & Documentation
**Duration: 1–2 days**

This is the most underrated phase. A recruiter opening your repo will read the README before touching a single line of code.

### README Structure
```markdown
## Architecture
[ASCII diagram — copy from this document]

## Tech Stack
[Table: Service → Language → Framework → DB]

## Local Setup
git clone ...
docker-compose up --build
# All services start on their respective ports

## Running Tests
cd services/user-service && pytest
cd services/product-service && mvn test

## CI/CD
GitHub Actions pipeline: test → build → push to ECR → deploy to ECS
[Link to Actions tab]

## Design Decisions
- Database-per-Service: each microservice owns its data to ensure loose coupling
- nginx as API Gateway: lightweight, battle-tested, handles rate limiting without custom code
- RabbitMQ for events: decouples Order Service from Notification — adding Slack alerts requires zero changes to Order Service
- State machine for orders: prevents invalid transitions (can't ship a cancelled order)

## Design Patterns Used
- Repository Pattern (User, Product, Order services)
- Factory Pattern (Notification Service)
- Observer / Event-Driven (Order → Notification via RabbitMQ)
- Strategy Pattern (Product filtering)

## What I'd Do Next
- Add Kubernetes manifests (Helm charts) for orchestration
- Implement distributed tracing with OpenTelemetry + Jaeger
- Add circuit breaker with Resilience4j (Java) and tenacity (Python)
- Write an Architecture Decision Record (ADR) for each major design choice
```

---

## Full Timeline

| Phase | Task | Duration |
|---|---|---|
| 0 | Setup, scaffolding, Docker Compose | 2–3 days |
| 1 | User Service (FastAPI) | 3–4 days |
| 2 | Product Service (Spring Boot) | 4–5 days |
| 3 | Order Service + State Machine | 4–5 days |
| 4 | Notification Service + RabbitMQ | 2–3 days |
| 5 | API Gateway (nginx config) | 1 day |
| 6 | CI/CD (GitHub Actions) | 2–3 days |
| 7 | AWS ECS Deployment | 2–3 days |
| 8 | Observability + health endpoints | 2 days |
| 9 | README + documentation | 1–2 days |
| **Total** | | **~4–5 weeks** |

---

## Interview Talking Points (Prepare These)

**"Walk me through your architecture."**
> "I built 4 microservices — User and Order in Python/FastAPI, Product in Java/Spring Boot, and a stateless Notification service. They communicate via REST for synchronous calls and RabbitMQ for event-driven flows like notifications. An nginx gateway handles routing and rate limiting at the edge."

**"Why did you choose a separate database per service?"**
> "It's the Database-per-Service pattern. If all services shared one DB, a schema change in the Product table could break the Order Service. Keeping them separate means each service owns its data contract — changes are isolated."

**"How did you handle the order state transitions?"**
> "I implemented a state machine as a directed graph — a dictionary mapping each state to its valid next states. Any invalid transition raises a 400 immediately. It's O(1) lookup and makes the business rules explicit in code rather than scattered across if-statements."

**"What would you improve if you had more time?"**
> "I'd add distributed tracing with OpenTelemetry — right now I have logs per service, but I can't trace a single request across all 4 services. I'd also add a circuit breaker so if the Product Service is down, the Order Service degrades gracefully instead of failing hard."

---

*Tip: Record a 2-minute Loom video walking through the architecture and a live demo of placing an order end-to-end. Paste the link at the top of your README. Almost no other candidates do this.*
