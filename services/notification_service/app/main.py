"""
FastAPI application for Notification Service.

Exposes /health endpoint for liveness checks.
Runs RabbitMQ consumer as a background task on startup.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from services.notification_service.app.consumer import OrderEventConsumer

logger = logging.getLogger(__name__)

# Initialize consumer at module level
consumer = OrderEventConsumer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI.
    Starts consumer on app startup; stops on shutdown.
    """
    # Startup
    logger.info("NotificationService: starting consumer")
    import asyncio

    consumer_task = asyncio.create_task(consumer.start())

    yield  # App is running

    # Shutdown
    logger.info("NotificationService: stopping consumer")
    consumer.stop()
    try:
        consumer_task.cancel()
        await consumer_task
    except asyncio.CancelledError:
        pass


# Create FastAPI app
app = FastAPI(
    title="Notification Service",
    description="Consumes order events and dispatches notifications",
    version="1.0.0",
    lifespan=lifespan,
)


class HealthResponse(BaseModel):
    """Health check response."""

    status: str


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns:
        HealthResponse with status "ok" if service is ready.
    """
    return HealthResponse(status="ok")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "notification-service",
        "version": "1.0.0",
        "status": "running",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8004,
        log_level="info",
    )
