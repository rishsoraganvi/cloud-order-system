Initial Research — Architecture Notes
====================================

Summary
-------
The system is a 4-service microservices topology with an nginx API Gateway and RabbitMQ for async events. Each service is containerized and has a dedicated PostgreSQL instance (except Notification which is stateless).

Architecture Diagram (text)

Client -> nginx API Gateway -> { UserService, ProductService, OrderService }
OrderService -> RabbitMQ -> NotificationService

Key Observations
----------------
- Database-per-service simplifies scaling and ownership but increases operational overhead (multiple Postgres instances).
- Product service in Java introduces multi-language CI complexity; ensure GitHub Actions handles both Python and Java builds.
- RabbitMQ is a good fit for order events; consider idempotency and deduplication for consumers.

Suggested Research Follow-ups
----------------------------
- Deployment options: AWS ECS (Fargate) vs EKS — pros/cons for cost and operational complexity.
- Local developer DX: provide `docker-compose.yml` to run all services + 4 Postgres instances + RabbitMQ.
- Security: JWT best practices, secrets management (AWS Secrets Manager or Parameter Store).
