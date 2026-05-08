#!/usr/bin/env bash
set -euo pipefail

# deploy.sh — deploy stack to remote Oracle Always Free host via SSH
# Requires: .env file with DEPLOY_SSH_USER and DEPLOY_HOST set. Optionally include
# OCIR_AUTH_TOKEN, OCI_NAMESPACE, OCIR_REGISTRY in .env for remote docker login.

if [ ! -f .env ]; then
  echo ".env file not found in repo root. Copy .env.example -> .env and populate values." >&2
  exit 1
fi

# Load environment variables from .env
export $(grep -v '^#' .env | xargs)

if [ -z "${DEPLOY_HOST:-}" ] || [ -z "${DEPLOY_SSH_USER:-}" ]; then
  echo "DEPLOY_HOST and DEPLOY_SSH_USER must be set in .env" >&2
  exit 1
fi

REMOTE_DIR=/opt/ecommerce
SSH_OPTS='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'

echo "Preparing remote directory ${REMOTE_DIR} on ${DEPLOY_SSH_USER}@${DEPLOY_HOST}..."
ssh ${SSH_OPTS} ${DEPLOY_SSH_USER}@${DEPLOY_HOST} "sudo mkdir -p ${REMOTE_DIR} && sudo chown $(whoami) ${REMOTE_DIR} || true"

echo "Copying compose files and .env to remote host..."
scp ${SSH_OPTS} docker-compose.yml ${DEPLOY_SSH_USER}@${DEPLOY_HOST}:${REMOTE_DIR}/docker-compose.yml
scp ${SSH_OPTS} docker-compose.oci.yml ${DEPLOY_SSH_USER}@${DEPLOY_HOST}:${REMOTE_DIR}/docker-compose.oci.yml
scp ${SSH_OPTS} .env ${DEPLOY_SSH_USER}@${DEPLOY_HOST}:${REMOTE_DIR}/.env

echo "Running remote update (docker login -> pull -> up)"
ssh ${SSH_OPTS} ${DEPLOY_SSH_USER}@${DEPLOY_HOST} bash -lc "\
  set -euo pipefail; \
  cd ${REMOTE_DIR}; \
  if [ -f .env ]; then export \\$(grep -v '^#' .env | xargs); fi; \
  if [ -n \"\${OCIR_AUTH_TOKEN:-}\" ] && [ -n \"\${OCI_NAMESPACE:-}\" ]; then \
    echo \"Logging into OCIR...\"; \
    echo \"\${OCIR_AUTH_TOKEN}\" | docker login \${OCIR_REGISTRY} -u \${OCI_NAMESPACE} --password-stdin || true; \
  fi; \
  docker compose -f docker-compose.yml -f docker-compose.oci.yml pull || true; \
  docker compose -f docker-compose.yml -f docker-compose.oci.yml up -d --remove-orphans; \
  docker image prune -f || true"

echo "Deployment finished."
