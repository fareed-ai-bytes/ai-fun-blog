import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)

    app = FastAPI(title="Blog Platform API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Content-Type", "X-Request-ID"],
        max_age=600,
    )
    app.include_router(api_router)
    return app


app = create_app()
