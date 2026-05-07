import os
from fastapi import FastAPI
from . import models, router as order_router
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def create_app(database_url: str | None = None) -> FastAPI:
    database_url = database_url or os.getenv("DATABASE_URL", "sqlite:///./test.db")
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    engine = create_engine(database_url, connect_args=connect_args)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    app = FastAPI()
    app.state.db_engine = engine
    app.state.SessionLocal = SessionLocal

    models.Base.metadata.create_all(bind=engine)

    app.include_router(order_router.router)
    return app


app = create_app()
