# ROADMAP — Phase Structure

## Phase 0 — Setup & Scaffolding (2–3 days)
**Goals:** Repository skeleton, docker-compose.yml, CI seeds, documentation.

**Plans:**
- [ ] 00-01-PLAN.md — Directory structure, docker-compose, README, architecture.md

**Requirements:** SETUP-01, SETUP-02, SETUP-03

---

## Phase 1 — User Service (FastAPI + PostgreSQL) (3–4 days)
**Goals:** Implement register/login/me endpoints, JWT auth, tests, Dockerfile.

**Plans:**
- [ ] 01-01-PLAN.md — FastAPI service with Repository pattern, password hashing, JWT, tests

**Requirements:** USER-01, USER-02, USER-03

**Design Patterns:** Repository, DI, SOLID (SRP, DIP)

---

## Phase 2 — Product Service (Java Spring Boot) (4–5 days)
**Goals:** Implement CRUD and reserve endpoint, JPA models, Dockerfile, tests.

**Plans:**
- [ ] 02-01-PLAN.md — Spring Boot service with JPA, Repository pattern, atomic stock reservation, tests

**Requirements:** PRODUCT-01, PRODUCT-02, PRODUCT-03, PRODUCT-04

**Design Patterns:** Repository, Interface Segregation, SOLID (OCP)

---

## Phase 3 — Order Service (FastAPI + PostgreSQL) (4–5 days)
**Goals:** Implement order placement, state machine, RabbitMQ publishing, integration with Product Service.

**Plans:**
- [ ] 03-01-PLAN.md — Order orchestration, state machine (DSA), HTTP inter-service calls, RabbitMQ, tests

**Requirements:** ORDER-01, ORDER-02, ORDER-03, ORDER-04

**Design Patterns:** Observer (events), Repository, State Machine (DSA)

---

## Phase 4 — Notification Service (FastAPI) (2–3 days) ✅ COMPLETE
**Goals:** Implement RabbitMQ consumer, notifier implementations, factory pattern.

**Plans:**
- [x] 04-01-PLAN.md — RabbitMQ consumer, Factory pattern notifiers (email, SMS, webhook), /health endpoint

**Requirements:** NOTIF-01, NOTIF-02

**Design Patterns:** Factory, Strategy, Observer

**Status:** Phase 4 scaffolding complete. All 10 tests pass. Factory pattern implemented with EmailNotifier, SMSNotifier, WebhookNotifier. RabbitMQ consumer and /health endpoint ready. See 04-01-SUMMARY.md for details.

---

## Phase 5 — API Gateway (nginx) (1 day) ✅ COMPLETE
**Goals:** Provide nginx.conf with routing and rate limiting.

**Plans:**
- [x] 05-01-PLAN.md — nginx configuration, routing, rate limiting (token bucket), Dockerfile

**Requirements:** GATEWAY-01, GATEWAY-02

**Technology:** nginx (configuration-only)

**Status:** Phase 5 complete. nginx.conf with 3 upstreams, rate limiting (10 req/s per IP), routing to all services. See 05-01-SUMMARY.md for details.

---

## Phase 6 — CI/CD Pipeline (GitHub Actions) (2–3 days) ✅ COMPLETE
**Goals:** Implement GitHub Actions workflow: lint, test, build Docker images, push to OCIR.

**Plans:**
- [x] 06-01-PLAN.md — GitHub Actions workflow with Python/Java tests, Docker build/push, OCIR integration

**Requirements:** CICD-01, CICD-02, CICD-03

**Technology:** GitHub Actions, Oracle Cloud Container Registry (OCIR)

**Status:** Phase 6 complete. GitHub Actions workflow with 4 jobs: lint, test-python, test-java, build-and-push. All services tested and built on main branch. See 06-01-SUMMARY.md for details.

---

## How to Use This Roadmap

1. **Start with Phase 0:** Establishes repository and docker-compose orchestration.
2. **Execute Phases 1-4 in parallel (with dependencies):** User and Product services are independent; Order depends on Product Service; Notification depends on Order Service.
3. **Execute Phase 5 after core services:** Gateway routes to all services.
4. **Execute Phase 6:** Complete CI/CD pipeline for automated testing and deployment.

Each phase plan (`XX-01-PLAN.md`) contains:
- Objective and output artifacts
- 2-3 implementation tasks
- Acceptance criteria and verification steps
- STRIDE threat model for security review

Run phase plans sequentially using the `/gsd-execute-phase` command.

