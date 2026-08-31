from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from contextlib import asynccontextmanager

from config.logging import logger
from database.database import init_db

import time

from routes.auth import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting...")
    await init_db()
    logger.info("Database initialized successfully.")
    yield
    logger.info("Application shutting down...")


app = FastAPI(
    title="ORCA API",
    version="1.0",
    description="This API provides access to ORCA App",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start
    logger.info(
        "%s %s | %d | %.4fs",
        request.method,
        request.url.path,
        response.status_code,
        process_time,
    )
    return response


@app.get("/")
async def root():
    return {
        "message": "ORCA 🌊🌊",
        "docs": "/scalar"
    }


@app.get("/scalar", include_in_schema=False)
def scalar():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API"
    )

app.include_router(auth_router)
