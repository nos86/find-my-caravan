from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.api.routes import (
    analytics,
    features,
    health,
    imports,
    listings,
    map,
    sources,
)

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("find-my-caravan backend starting", version="0.1.0")
    yield
    logger.info("find-my-caravan backend shutting down")


def create_app() -> FastAPI:
    app = FastAPI(
        title="find-my-caravan API",
        version="0.1.0",
        description="Backend API for the find-my-caravan camper listing aggregator",
        lifespan=lifespan,
        docs_url=f"{settings.API_PREFIX}/docs",
        redoc_url=f"{settings.API_PREFIX}/redoc",
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
    )

    # CORS – allow all origins in development; restrict via env in production.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    prefix = settings.API_PREFIX

    app.include_router(health.router, prefix=prefix)
    app.include_router(sources.router, prefix=prefix)
    app.include_router(imports.router, prefix=prefix)
    app.include_router(listings.router, prefix=prefix)
    app.include_router(features.router, prefix=prefix)
    app.include_router(analytics.router, prefix=prefix)
    app.include_router(map.router, prefix=prefix)

    return app


app = create_app()
