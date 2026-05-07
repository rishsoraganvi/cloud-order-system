# Resume, Interview Guide & Results Tracker
### Cloud-Native E-Commerce Order Processing System

---

## PART 1 — RESUME POINTS

> Copy the block that matches your resume stage. Use the "In Progress" version while building, swap to "Completed" when done.

---

### Project Title Line
```
Cloud-Native E-Commerce Order Processing System | Python · Java · Docker · RabbitMQ · GitHub Actions
```

---

### While Building (In Progress)

```
Cloud-Native E-Commerce Order Processing System                              [github.com/yourname/cloud-order-system]
Python (FastAPI) · Java (Spring Boot 3) · PostgreSQL · RabbitMQ · Docker · nginx · GitHub Actions

• Architected a distributed backend decomposed into 4 independent microservices following the
  Database-per-Service pattern, ensuring loose coupling and independent deployability

• Built RESTful APIs across Python (FastAPI) and Java (Spring Boot 3), applying SOLID principles —
  Repository Pattern for DB abstraction, Factory Pattern for notification channel selection,
  and Observer Pattern via RabbitMQ for event-driven order notifications

• Implemented an order state machine (directed graph) enforcing valid status transitions
  (PENDING → CONFIRMED → SHIPPED → DELIVERED), preventing illegal state changes at O(1) lookup

• Configured nginx as an API Gateway with upstream routing across all services and
  request rate limiting using the token bucket algorithm

• Containerized all services using multi-stage Docker builds; orchestrated local dev
  environment via Docker Compose with isolated PostgreSQL instances per service

• Established a CI/CD pipeline using GitHub Actions — runs unit tests across Python (pytest)
  and Java (JUnit) services on every PR, blocks merge on test failure
```

---

### After Completion (All Phases Done, No Cloud Deployment)

```
Cloud-Native E-Commerce Order Processing System                              [github.com/yourname/cloud-order-system]
Python (FastAPI) · Java (Spring Boot 3) · PostgreSQL · RabbitMQ · Docker · nginx · GitHub Actions

• Designed and built a production-ready distributed backend with 4 microservices handling
  user auth, product catalog, order processing, and event-driven notifications — each independently
  containerized and deployable

• Applied SOLID principles and design patterns throughout: Repository Pattern decouples DB from
  business logic, Factory Pattern drives pluggable notification channels (email/SMS/webhook),
  Observer Pattern via RabbitMQ decouples Order and Notification services

• Implemented JWT-based authentication in User Service (FastAPI) and a paginated product
  catalog with stock reservation in Product Service (Spring Boot 3 + JPA)

• Enforced order lifecycle via a state machine modelled as a directed graph — invalid transitions
  (e.g., CANCELLED → SHIPPED) rejected at API layer with O(1) lookup

• Delivered full CI/CD pipeline via GitHub Actions: lint → pytest / JUnit → Docker build →
  image push on merge to main; structured JSON logging and /health endpoints across all services

• Architected for Oracle Cloud Always Free deployment (ARM A1, 24 GB RAM) with environment-based
  config separation (local Docker Compose / production OCI) ready for one-command deployment
```

---

### After Cloud Deployment (OCI)

Add this bullet to the "Completed" block above:
```
• Deployed all services to Oracle Cloud Infrastructure (OCI) ARM A1 instance (4 OCPUs, 24 GB RAM)
  via Docker Compose; connected to OCI Autonomous Database — zero infrastructure cost using
  Always Free tier, with free Load Balancer routing traffic to nginx gateway
```

---

## PART 2 — INTERVIEW GUIDE

---

### Q1: "Walk me through your project."

**What they want:** Architecture clarity. Can you explain a system end-to-end without rambling?

**Answer:**
> "I built a cloud-native order processing backend decomposed into four microservices — User, Product, Order, and Notification. User and Order are in Python using FastAPI, Product is in Java with Spring Boot 3, and Notification is a stateless Python consumer. Each service has its own PostgreSQL database — the Database-per-Service pattern — so no service touches another's data directly. An nginx gateway sits in front and routes requests based on path prefix, with rate limiting configured at that layer. When an order is placed, the Order Service calls the Product Service over HTTP to reserve stock, saves the order, then publishes an event to RabbitMQ. The Notification Service subscribes to that queue and sends the appropriate alert. Everything runs in Docker containers, wired together with Docker Compose locally, and the CI/CD pipeline on GitHub Actions runs tests and builds images on every push."

**Do:** Draw a quick box diagram on paper/whiteboard if given the chance.
**Don't:** List every file or class — stay at architecture level first, drill down only if asked.

---

### Q2: "Why microservices and not a monolith?"

**What they want:** Do you understand trade-offs, or did you just follow a tutorial?

**Answer:**
> "For a project at this scale, a monolith would honestly be simpler to build. I chose microservices deliberately because the JD asks for cloud-native architecture and microservices experience — and I wanted to actually feel the trade-offs rather than just read about them. The real benefit I got was independent deployability: if I update the Notification Service, I don't rebuild or redeploy the Order Service. The cost I paid was inter-service HTTP calls adding latency and complexity — for example, the Order Service now has to handle the case where the Product Service is down during a stock reservation. I dealt with that by returning a 503 with a retry hint rather than silently failing."

---

### Q3: "Explain the design patterns you used."

**What they want:** Can you apply patterns correctly, not just name-drop them?

**Answer (walk through each one concretely):**

> **Repository Pattern** — "In every service, I have a `repository.py` or `ProductRepository` interface that's the only layer allowed to touch the database. The service layer calls the repository, never SQLAlchemy or JPA directly. This means if I swap PostgreSQL for a different database, I change one file — nothing in business logic breaks. It also makes unit testing clean: I mock the repository and test the service logic in isolation."

> **Factory Pattern** — "In the Notification Service, a `NotificationFactory` takes a channel string — email, SMS, or webhook — and returns the appropriate notifier object. Each notifier implements a common `BaseNotifier` interface with a `send()` method. Adding a Slack notifier means creating one new class and one new branch in the factory — zero changes to existing code. That's Open/Closed Principle in action."

> **Observer Pattern** — "The Order Service doesn't call the Notification Service directly. It publishes an `order.placed` event to RabbitMQ and moves on. The Notification Service independently subscribes and reacts. This means I could add a second subscriber — say, an analytics service — without touching Order Service at all. Loose coupling."

---

### Q4: "Tell me about the state machine in your Order Service."

**What they want:** DSA applied to a real problem.

**Answer:**
> "Order statuses aren't free-form — there are specific valid progressions. I modelled this as a directed graph where each state maps to its allowed next states: PENDING can go to CONFIRMED or CANCELLED, CONFIRMED can go to SHIPPED, and so on. I store this as a Python dictionary, so checking whether a transition is valid is O(1) — just a key lookup and a membership check. Any attempt to make an invalid transition — like shipping a cancelled order — raises a 400 immediately at the service layer, before touching the database. It keeps the business rules explicit and centralized rather than scattered across if-statements throughout the codebase."

---

### Q5: "How does your CI/CD pipeline work?"

**What they want:** Do you understand DevOps fundamentals beyond just using Git?

**Answer:**
> "I have a GitHub Actions workflow that triggers on every push and pull request to main. It runs in two parallel jobs — one runs pytest for the three Python services, the other runs JUnit for the Spring Boot service. If either job fails, the workflow fails and the PR is blocked from merging. On a successful merge to main, a third job builds Docker images for all four services using multi-stage Dockerfiles — the builder stage compiles/installs dependencies, the final stage only copies the artifact, keeping images small. The images are tagged with the git commit SHA for traceability. The pipeline is architected to push those images to a container registry and trigger deployment, though that last step is pending the OCI setup."

---

### Q6: "Why did you use RabbitMQ instead of calling the Notification Service directly?"

**What they want:** Do you understand async communication and its trade-offs?

**Answer:**
> "If Order Service called Notification Service directly over HTTP, two problems arise: first, Order Service has to wait for the notification to complete before returning a response to the user — that's unnecessary latency. Second, if Notification Service is down, the order placement fails, which is wrong — an email failing shouldn't roll back a valid order. RabbitMQ decouples them: Order Service publishes the event and returns immediately. If Notification Service is down, the message sits in the queue and gets processed when it recovers. The trade-off is eventual delivery — the user might get their email a few seconds late — but that's an acceptable trade-off for this use case."

---

### Q7: "What would you improve if you had more time?"

**What they want:** Senior engineering mindset — do you see beyond what you built?

**Answer:**
> "Three things. First, distributed tracing — right now I have structured JSON logs per service, but I can't trace a single request across all four services end-to-end. I'd add OpenTelemetry and a Jaeger instance to correlate requests by trace ID. Second, a circuit breaker on the Order → Product Service HTTP call using the `tenacity` library in Python — right now if Product Service is slow, Order Service hangs. A circuit breaker would fail fast and return a degraded response after a threshold. Third, I'd write Architecture Decision Records documenting why I made each major design choice — that's a practice I only learned about mid-project."

---

### Q8: "You used both Python and Java in the same system — why not pick one?"

**What they want:** Thoughtful language choice, not just "the JD said so."

**Answer:**
> "The JD lists Python, Java, and Go. I know Python and Java, so I used both deliberately to demonstrate I can work in a polyglot system — which is the reality in microservices teams. I used FastAPI for the user-facing services because Python's async support and Pydantic's schema validation make it fast to build clean REST APIs. I used Spring Boot for the Product Service because Java's type system and Spring Data JPA make the repository pattern very explicit — it's a good fit for a data-heavy CRUD service with paginated queries. In a real team, you pick the right tool per service rather than forcing uniformity."

---

### Q9: "How did you handle authentication across services?"

**What they want:** Security awareness in distributed systems.

**Answer:**
> "The User Service issues a JWT token on login. The API Gateway (nginx) passes the Authorization header downstream unchanged. Each service that needs auth — currently Order Service — validates the JWT independently using the same secret key, without calling back to the User Service. This is stateless auth — no inter-service call needed for every request. The trade-off is token revocation is harder; you'd need a blocklist or short expiry. For this project I used 30-minute expiry tokens, which is a reasonable balance."

---

### Q10: "Have you deployed this to the cloud?"

**What they want:** Honesty + awareness.

**Answer (if not deployed):**
> "Not yet — I designed it for deployment to Oracle Cloud Infrastructure's Always Free tier. The ARM A1 instance gives 24 GB RAM which comfortably runs all four containers, and OCI's Autonomous Database replaces the managed PostgreSQL. I ran into the region capacity issue for the A1 shape in India — it's a known problem with OCI's free tier — so I'm working around it. The architecture, Dockerfiles, and environment configs are fully deployment-ready; it's purely an infrastructure availability issue, not a code issue."

---

## PART 3 — RESULTS TRACKER

> Fill this in as you build. Use concrete numbers wherever possible — even small numbers are better than vague claims. These go directly into your resume bullets and STAR answers.

---

### Metrics to Track While Building

| Metric | Target | Your Result |
|---|---|---|
| Number of independent services | 4 | ___ |
| Number of REST endpoints total | ~12–15 | ___ |
| Test coverage (Python services) | >70% | ___% |
| Test coverage (Java service) | >70% | ___% |
| Number of unit tests written | >20 | ___ |
| Docker image size (each service) | <200 MB | ___ MB |
| CI pipeline run time | <3 min | ___ min |
| Average API response time (local) | <100ms | ___ ms |
| Lines of code (approx) | — | ___ |
| Time to complete project | ~4–5 weeks | ___ weeks |

---

### STAR Stories to Prepare

These are structured answers for behavioral questions using your project as evidence.

**"Tell me about a technical challenge you faced."**
```
Situation:  When building the Order Service, I needed order status changes to be
            strictly controlled — no arbitrary transitions allowed.
Task:       Design a validation mechanism that's both correct and efficient.
Action:     Modelled valid transitions as a directed graph (Python dict). Any status
            update request first checks if the transition is in the allowed set — O(1)
            lookup. Invalid transitions raise a 400 before touching the database.
Result:     Zero invalid state changes possible at the API layer. The business rules
            are explicit in one place — adding a new status means one dict update,
            not hunting through if-statements.
```

**"Tell me about a time you made a design decision."**
```
Situation:  The Order Service needed to trigger notifications when an order is placed.
Task:       Decide between direct HTTP call vs. event-driven messaging.
Action:     Chose RabbitMQ. Direct HTTP would couple the two services — a notification
            failure would fail the entire order. RabbitMQ decouples them: order saves
            successfully, event sits in queue, notification delivers asynchronously.
Result:     Order Service response time is unaffected by notification delays.
            Notification Service can be restarted independently without losing events.
```

**"Tell me about a time you applied software engineering best practices."**
```
Situation:  Four services, three languages/frameworks, all needing database access.
Task:       Keep database logic from leaking into business logic across all services.
Action:     Applied Repository Pattern consistently — one repository class/interface
            per service, the only layer permitted to run queries. Service layer receives
            domain objects, not database rows. Wrote unit tests mocking the repository.
Result:     Swapping database (e.g., PostgreSQL → Oracle Autonomous DB) requires
            changing one file per service. All business logic tests run without a
            real database, making CI fast and reliable.
```

---

### Links to Have Ready

```
GitHub Repo:       github.com/yourname/cloud-order-system
README:            github.com/yourname/cloud-order-system#readme
Live Demo (if any): ___
Loom Walkthrough:  loom.com/share/___  ← record a 2-min architecture + demo video
```

---

*Last updated: fill in when you submit your application.*
