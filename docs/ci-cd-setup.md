# CI/CD Pipeline Setup Guide

## Overview

This project uses GitHub Actions to automate:
- **Linting** — Code quality checks using flake8
- **Testing** — Unit tests via pytest (Python) and mvn test (Java)
- **Building** — Docker image creation for all services
- **Pushing** — Automated deployment to AWS ECR (Elastic Container Registry)

The pipeline is triggered automatically on:
- Push to `main` branch
- Pull requests to `main` branch

---

## Prerequisites

### AWS Account Setup

1. **Create an AWS ECR Repository** for each service:
   ```bash
   aws ecr create-repository --repository-name user-service --region us-east-1
   aws ecr create-repository --repository-name product-service --region us-east-1
   aws ecr create-repository --repository-name order-service --region us-east-1
   aws ecr create-repository --repository-name notification-service --region us-east-1
   aws ecr create-repository --repository-name api-gateway --region us-east-1
   ```

2. **Create IAM User for GitHub Actions** (minimal permissions):
   - Go to AWS IAM Console → Users → Create user
   - Attach policy with ECR push permissions:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "ecr:GetAuthorizationToken",
           "ecr:BatchGetImage",
           "ecr:GetDownloadUrlForLayer",
           "ecr:PutImage",
           "ecr:InitiateLayerUpload",
           "ecr:UploadLayerPart",
           "ecr:CompleteLayerUpload"
         ],
         "Resource": "arn:aws:ecr:*:ACCOUNT_ID:repository/*"
       }
     ]
   }
   ```

3. **Generate Access Key** for the IAM user:
   - Go to IAM User → Security credentials → Create access key
   - Save AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY

---

## GitHub Secrets Configuration

GitHub Actions use **Secrets** to securely store sensitive credentials. Configure these in your repository:

### How to Set Secrets

1. Go to GitHub repository → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add each secret below with its value

### Required Secrets

| Secret Name | Value | Example |
|---|---|---|
| `AWS_ACCESS_KEY_ID` | IAM access key from step 3 above | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | IAM secret key from step 3 above | `wJalrXUtnFEMI...` |
| `AWS_REGION` | AWS region for ECR | `us-east-1` |
| `ECR_REGISTRY` | Full ECR registry URL | `123456789.dkr.ecr.us-east-1.amazonaws.com` |

### Example Secrets Setup

```bash
# After creating IAM user with access key:

# Secret 1: AWS Access Key ID
gh secret set AWS_ACCESS_KEY_ID --body "AKIAIOSFODNN7EXAMPLE"

# Secret 2: AWS Secret Access Key
gh secret set AWS_SECRET_ACCESS_KEY --body "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# Secret 3: AWS Region
gh secret set AWS_REGION --body "us-east-1"

# Secret 4: ECR Registry URL
gh secret set ECR_REGISTRY --body "123456789.dkr.ecr.us-east-1.amazonaws.com"
```

---

## Workflow Overview

### Pipeline Stages

```
1. TRIGGER
   ├─ Push to main branch
   └─ Pull request to main branch

2. LINT (parallel to tests)
   ├─ Python linting (flake8)

3. TEST (parallel jobs)
   ├─ Python services (pytest)
   └─ Java services (mvn test)

4. BUILD & PUSH (only on main branch push)
   ├─ Build all Docker images
   ├─ Tag with git SHA + latest
   └─ Push to AWS ECR
```

### Job Definitions

#### `lint-python`
- **When:** Every push and pull request
- **What:** Runs flake8 on Python services
- **Status:** Warnings allowed (continue-on-error: true)
- **Purpose:** Code quality feedback

#### `test-python`
- **When:** Every push and pull request (after lint)
- **What:** Runs pytest on User, Order, Notification services
- **Status:** Tests must pass for merge (unless skipped due to missing deps)
- **Purpose:** Unit test validation

#### `test-java`
- **When:** Every push and pull request (after lint)
- **What:** Runs `mvn test` on Product Service
- **Status:** Tests must pass for merge
- **Purpose:** Java service validation

#### `build-and-push`
- **When:** Push to main branch ONLY (not on PRs)
- **What:** Builds Docker images and pushes to ECR
- **Status:** Requires all tests to pass
- **Purpose:** Automated production deployment

---

## Workflow Execution

### On Pull Request

1. Code is committed to a feature branch
2. Pull request created against `main`
3. Workflow automatically triggers
4. **Lint** job runs (style checking)
5. **Test jobs** run in parallel (Python + Java)
6. Status check appears on PR
7. If all pass: PR can be merged
8. If any fail: PR blocked until fixed

### On Push to Main

1. Code pushed to `main` branch
2. Workflow triggers
3. **Lint** and **Test** jobs run (same as PR)
4. If all pass: **Build & Push** job starts
5. Docker images built for all services
6. Images tagged with:
   - Commit SHA (e.g., `user-service:a1b2c3d4`)
   - `latest` tag for stable release
7. Images pushed to AWS ECR
8. Automatic deployment can be triggered (ECS update)

---

## Troubleshooting

### Build Fails: Secrets Not Configured

**Error:** `aws-actions/configure-aws-credentials: Access Denied`

**Solution:**
1. Verify all 4 secrets are set in GitHub Settings → Secrets
2. Check IAM user permissions include ECR access
3. Verify AWS_REGION matches ECR region

### Build Fails: Docker Build Error

**Error:** `Docker build failed: Service not found`

**Solution:**
1. Verify all Dockerfiles are present in service directories
2. Check base image names (e.g., `nginx:alpine`, `python:3.11-slim`)
3. Ensure required dependencies are in requirements.txt or pom.xml

### Tests Fail: Missing Dependencies

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
1. Ensure requirements.txt is present and complete
2. CI workflow installs dependencies via `pip install -r requirements.txt`
3. For Java: verify pom.xml has all dependencies

### Image Push Fails: ECR Repository Not Found

**Error:** `Error response from daemon: name unknown: 123456789.dkr.ecr.us-east-1.amazonaws.com/user-service:latest`

**Solution:**
1. Verify ECR repositories exist: `aws ecr describe-repositories`
2. Check ECR registry URL in GitHub Secrets matches actual registry
3. Ensure IAM user has `ecr:CreateRepository` permissions to auto-create

---

## Local Testing

### Using `act` (GitHub Actions Emulator)

Test the workflow locally before pushing:

```bash
# Install act (see https://github.com/nektos/act)
# macOS:
brew install act

# List all workflow jobs
act -l

# Run a specific job locally
act -j test-python

# Run with secrets (create .secrets file)
echo "AWS_ACCESS_KEY_ID=AKIA..." > .secrets
act -j build-and-push --secret-file .secrets

# Dry run (show what would execute)
act --dry-run
```

### Manual Docker Build Test

Test individual service builds:

```bash
# Test User Service build
docker build -t user-service:test services/user-service/

# Test Product Service build
docker build -t product-service:test services/product-service/

# Test Order Service build
docker build -t order-service:test services/order-service/

# Test Notification Service build
docker build -t notification-service:test services/notification-service/

# Test Gateway build
docker build -t api-gateway:test gateway/

# Run image and test (example)
docker run -p 8001:8001 user-service:test
curl http://localhost:8001/health
```

---

## Monitoring & Debugging

### GitHub Actions Dashboard

1. Go to repository → **Actions** tab
2. Click workflow run to see logs
3. Click specific job to see detailed output
4. Expand "Run tests" or "Build and push" steps for logs

### Workflow Logs

Each job produces logs showing:
- Environment setup (Python version, Java version)
- Dependency installation (pip install, mvn dependency:resolve)
- Test execution output (pytest results, mvn test output)
- Docker build output (layers, size)
- Push status (successful, failed)

### Debugging Failed Jobs

**Lint failures:**
```bash
# Run locally
flake8 services/user-service/ --max-line-length=120
```

**Test failures:**
```bash
# Run locally
pytest services/user-service/tests/ -v
```

**Build failures:**
```bash
# Test Docker build locally
docker build -t test services/user-service/
docker run test pytest tests/
```

---

## Security Best Practices

1. **Rotate AWS Keys Regularly**
   - GitHub Secrets should be rotated every 90 days
   - Create new IAM user, update secrets, delete old user

2. **Minimal IAM Permissions**
   - IAM user for GitHub should only have ECR access
   - Avoid using root AWS credentials
   - Use resource-level permissions (specific repositories)

3. **Secrets Not in Code**
   - Never commit AWS keys, API keys, or tokens to git
   - Always use GitHub Secrets for sensitive data
   - Add `.secrets` to `.gitignore`

4. **Branch Protection**
   - Require CI workflow to pass before merge
   - Go to Settings → Branches → main → Require status checks to pass
   - Require at least one review before merge

---

## Integration with ECS Deployment

After images are pushed to ECR, you can automate ECS deployment:

1. **Create ECS Task Definition** with image references:
   ```json
   {
     "containerDefinitions": [
       {
         "name": "user-service",
         "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/user-service:latest",
         "portMappings": [{"containerPort": 8001}]
       }
     ]
   }
   ```

2. **Add ECS deployment step to workflow** (optional Phase 6 enhancement):
   ```yaml
   - name: Update ECS service
     run: |
       aws ecs update-service \
         --cluster ecommerce \
         --service user-service \
         --force-new-deployment
   ```

---

## Summary

| Step | Who | When | Status |
|---|---|---|---|
| Lint | GitHub Actions | Every push/PR | ⚠ Warning (non-blocking) |
| Test | GitHub Actions | Every push/PR | ✓ Pass required |
| Build | GitHub Actions | Main branch only | ✓ Pass required |
| Push | GitHub Actions | Main branch only | ✓ Automatic after build |

With this setup, every commit to main automatically rebuilds and deploys all services to AWS ECR, enabling rapid iteration and rollback via image tags.
