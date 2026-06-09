from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.db import engine, init_db
from app.core.logger import configure_logging, get_logger

logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await init_db()
    logger.info("API startup complete.")
    yield
    await engine.dispose()
    logger.info("API shutdown complete.")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,  # required so the browser sends/stores the auth cookie
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.get("/health")
def health():
    return {"status": "ok"}
