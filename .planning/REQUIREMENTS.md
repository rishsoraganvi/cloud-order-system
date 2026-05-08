# REQUIREMENTS — Cloud-Native E-Commerce Order Processing System

Scope
-----
This document captures scoped, falsifiable requirements mapped to the phase plan in `full_build_plan.md`.

Functional Requirements (by service)
-----------------------------------
- User Service (Phase 1)
  - `POST /users/register` creates user and stores hashed password (bcrypt). Returns 201 on success.
  - `POST /users/login` returns a signed JWT on valid credentials.
  - `GET /users/me` returns authenticated user's profile; returns 401/403 when unauthenticated.

- Product Service (Phase 2)
  - `GET /products` returns paginated list (page, size params supported).
  - `GET /products/{id}` returns product details for valid id.
  - `POST /products` accepts product creation payload; returns 201.
  - `PUT /products/{id}/reserve` decrements stock atomically; returns 409 on insufficient stock.

- Order Service (Phase 3)
  - `POST /orders` places an order: reserves stock via Product Service and persists order.
  - `GET /orders/{id}` returns order status and details.
  - `PATCH /orders/{id}/status` validates state transitions per state machine.
  - Publish `order.placed` event to RabbitMQ on successful order placement.

- Notification Service (Phase 4)
  - Consume `order.placed` events and emit notifications (email/log). Provide `GET /health`.

Non-Functional Requirements
-------------------------
- Services must run in containers with Docker; local orchestration via `docker-compose` for dev.
- CI/CD: GitHub Actions must lint, test, build Docker images, and push to OCIR on `main`.
- Observability: basic health endpoints and logs; include request-level logging for services.
- Security: JWT-based auth for protected endpoints; secrets not hard-coded.

Acceptance Criteria
-------------------
- End-to-end local run via `docker-compose up` with all services, DBs, and RabbitMQ.
- Automated tests for User and Order services run in CI and pass.
- Product service built via Maven/Gradle and packaged as Docker image in CI.

