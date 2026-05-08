# CI/CD Pipeline Setup Guide - Oracle Cloud Always Free

## Overview

This project uses GitHub Actions to automate:
- Linting - Code quality checks using flake8
- Testing - Unit tests via pytest (Python) and mvn test (Java)
- Building - Docker image creation for all services
- Pushing - Automated image push to Oracle Cloud Container Registry (OCIR)
- Deploying - Optional deployment to Oracle Cloud Always Free (ARM A1, 24 GB RAM)

The pipeline is triggered automatically on:
- Push to `main` branch
- Pull requests to `main` branch

---

## Prerequisites

### Oracle Cloud Account Setup

1. Sign up for Oracle Cloud Always Free and open the OCI Console.
2. Identify your OCI region (example: `us-phoenix-1`).
3. Enable access to Oracle Cloud Container Registry (OCIR).
4. Find your tenancy namespace:
   ```bash
   oci os ns get --auth api_key
   ```
5. Create an API key for your OCI user:
   - OCI Console -> Profile -> My profile -> API keys -> Add API key
   - Save key fingerprint, tenancy OCID, and user OCID

### OCIR Repository Convention

Images are pushed to:
`<region>.ocir.io/<namespace>/<service>:<tag>`

Example:
`us-phoenix-1.ocir.io/mytenancy/user-service:latest`

---

## GitHub Secrets Configuration

Configure these repository secrets:

| Secret Name | Description | Example |
|---|---|---|
| `OCI_REGION` | OCI region | `us-phoenix-1` |
| `OCI_NAMESPACE` | OCI namespace | `mytenancy` |
| `OCI_TENANCY_OCID` | Tenancy OCID | `ocid1.tenancy.oc1...` |
| `OCI_USER_OCID` | User OCID | `ocid1.user.oc1...` |
| `OCI_FINGERPRINT` | API key fingerprint | `aa:bb:cc:...` |
| `OCI_PRIVATE_KEY` | API private key PEM (multiline) | `-----BEGIN PRIVATE KEY-----...` |
| `OCIR_REGISTRY` | OCIR registry host | `us-phoenix-1.ocir.io` |

Optional deployment secrets:

| Secret Name | Description |
|---|---|
| `OCI_COMPUTE_HOST` | Always Free VM public IP or hostname |
| `OCI_COMPUTE_USER` | SSH user (for Ubuntu images typically `ubuntu`) |
| `OCI_SSH_PRIVATE_KEY` | SSH key for deploy step |

---

## Workflow Overview

### Pipeline Stages

1. Trigger
   - Push to main
   - Pull request to main
2. Lint
   - flake8 checks for Python services
3. Test
   - pytest for Python services
   - mvn test for Product service
4. Build and Push (main only)
   - Build all Docker images
   - Tag with commit SHA and latest
   - Push to OCIR
5. Deploy (optional)
   - Pull images on Oracle Cloud Always Free instance
   - Restart services with docker compose

### Job Definitions

#### `lint-python`
- Runs on every push and PR
- Runs flake8 on Python services

#### `test-python`
- Runs on every push and PR
- Runs pytest for User, Order, and Notification services

#### `test-java`
- Runs on every push and PR
- Runs `mvn test` for Product service

#### `build-and-push`
- Runs only on push to `main`
- Builds and pushes service images to OCIR

#### `deploy` (optional)
- Manual or environment-gated
- Deploys latest OCIR images to Oracle Cloud Always Free VM

---

## On Push to Main

1. Lint and tests run.
2. If all checks pass, Docker images are built.
3. Images are tagged:
   - `<service>:<short-sha>`
   - `<service>:latest`
4. Images are pushed to OCIR.
5. Optional deploy job updates Oracle Cloud Always Free environment.

---

## Troubleshooting

### Build fails: OCI auth error

Typical causes:
- Invalid `OCI_PRIVATE_KEY`
- Wrong `OCI_FINGERPRINT`
- Incorrect OCID values

Checks:
- Validate API key in OCI Console
- Confirm region and namespace values
- Confirm key format is unchanged

### Push fails: unauthorized

- Verify OCIR login uses username format:
  `<namespace>/<identity-provider>/<username>`
- Verify `OCIR_REGISTRY` value matches region

### Push fails: repository not found

- Ensure target path is correct: `<region>.ocir.io/<namespace>/<repo>`
- Push once manually to create repository if policy requires it

---

## Local Validation

### Validate images locally

```bash
docker build -t user-service:test services/user-service/
docker build -t product-service:test services/product-service/
docker build -t order-service:test services/order-service/
docker build -t notification-service:test services/notification-service/
docker build -t api-gateway:test gateway/
```

### Validate workflow with act

```bash
act -l
act -j test-python
act -j build-and-push --secret-file .secrets
```

---

## Security Best Practices

1. Rotate OCI API keys regularly.
2. Use least-privilege OCI policies for registry and compute access.
3. Store all secrets in GitHub Secrets, never in source code.
4. Require branch protection and passing checks before merge.
5. Keep container images patched and rebuild frequently.

---

## Oracle Cloud Always Free Deployment

### Environment-based configuration

Use separate environment files:
- `.env.development`
- `.env.staging`
- `.env.production`

Run with environment-specific compose overlays:

```bash
# Development
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Production (Oracle Cloud Always Free)
docker compose -f docker-compose.yml -f docker-compose.oci.yml up -d
```

### One-command deployment

```bash
./deploy.sh production
```

`deploy.sh` should:
1. Pull latest OCIR images.
2. Export production environment variables.
3. Restart services with the OCI compose overlay.
4. Run health checks through gateway endpoints.

---

## Summary

| Step | Tool | When | Target |
|---|---|---|---|
| Lint | GitHub Actions + flake8 | Every push/PR | Code quality |
| Test | GitHub Actions + pytest/mvn | Every push/PR | Test coverage |
| Build | GitHub Actions + Docker | Main branch only | Docker images |
| Push | GitHub Actions + OCIR | Main branch only | Oracle Container Registry |
| Deploy | Manual or workflow | On demand | Oracle Cloud Always Free |

With this setup, every commit to `main` can build and publish images to OCIR, with optional one-command deployment to Oracle Cloud Always Free.
