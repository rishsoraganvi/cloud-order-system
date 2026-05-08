# Architecture Overview

This document describes the service topology and communication patterns for the Cloud-Native E-Commerce Order Processing System.

Services
- `user-service` (FastAPI): Authentication, user profiles, JWT issuance.
- `product-service` (Spring Boot): Product catalog and stock management.
- `order-service` (FastAPI): Order placement, reservation, state machine.
- `notification-service` (Python): Sends emails and webhooks; uses factory pattern.
- `api-gateway` (Nginx): Reverse proxy and TLS termination.

Datastore
- Each service uses a dedicated PostgreSQL instance (db1..db4) following the database-per-service pattern.

Messaging
- `rabbitmq` provides asynchronous communication for order events and notifications.

Local orchestration
- `docker-compose.yml` defines all services, databases, and message broker for local development.

Deployment
- Primary target: Oracle Cloud Always Free (ARM A1) using OCIR for container registry.
- CI/CD: GitHub Actions builds images and pushes to OCIR; deployment may be an SSH-based pull on the Always Free host or scripted OCI compute tasks.

Security
- JWT-based stateless auth; secrets stored in environment or secret manager (OCI Vault recommended).
