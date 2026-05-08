# Cloud-Native E-Commerce Order Processing System

Project scaffold for a cloud-native, microservices-based e-commerce order processing system. Designed for local development with Docker Compose and deployment to Oracle Cloud Always Free ARM A1 instances.

Prerequisites
- Docker & Docker Compose
- Python 3.11
- Java 17 (Temurin)
- Git

Quick start
1. Clone the repo:

```bash
git clone <repo-url>
cd Cloud-Native\ E-Commerce\ Order\ Processing\ System
```

2. Start services locally:

```bash
docker compose up --build
```

3. Test user service:

```bash
curl http://localhost:8001/health
```

Project layout
- `services/user-service` — FastAPI user service
- `services/product-service` — Spring Boot product service
- `services/order-service` — FastAPI order service
- `services/notification-service` — Python notification worker
- `gateway/` — Nginx API gateway configuration
- `docs/` — project documentation

See `docs/architecture.md` for design details and deployment notes.
