Project: Cloud-Native E-Commerce Order Processing System
==============================================

Overview
--------
This project implements a cloud-native, containerized e-commerce order processing system using a microservices architecture. The design uses language-appropriate frameworks: Python (FastAPI) for User, Order, and Notification services, and Java (Spring Boot) for the Product service. Services run in containers and are deployable to Oracle Cloud Always Free (ARM A1, 24 GB RAM).

Architectural Summary
---------------------
- API Gateway: nginx (routing + rate limiting)
- Services: User (FastAPI), Product (Spring Boot), Order (FastAPI), Notification (FastAPI)
- Each service owns its own PostgreSQL database (Database-per-Service)
- Message broker: RabbitMQ for Order → Notification events

Key Decisions
-------------
- Use HTTP REST for service-to-service calls; async HTTP client in Python services.
- Product service implemented in Java 17 + Spring Boot per JD requirements.
- CI/CD via GitHub Actions (lint → test → Docker build → push to OCIR → deploy)

Primary Artifacts
-----------------
- .planning/REQUIREMENTS.md — scoped requirements by phase
- .planning/ROADMAP.md — phase-by-phase roadmap
- .planning/STATE.md — project memory and metadata
- .planning/research/ — domain research and notes

Source Reference
----------------
This project was initialized from `full_build_plan.md` and follows its phase-by-phase plan.

Next Step
---------
Run `/gsd-plan-phase 1` to begin Phase 1 (User Service) implementation.

Status
------
- Phase 1 PLAN.md created at `.planning/phases/01-user-service/01-01-PLAN.md`.


